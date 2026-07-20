"""Injection-recovery study for the RogueLens microlensing model.

The experiment injects synthetic point-lens events into Gaussian noise,
fits them with RogueLens, and measures detection and parameter-recovery
performance as a function of lens mass, impact parameter, and noise.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from roguelens.fitting import fit_pspl
from roguelens.model import light_curve
from roguelens.presets import PRESETS

PRESET_KEYS = ("mars", "earth", "neptune", "jupiter")
NOISE_LEVELS = (0.005, 0.01, 0.02, 0.05)
IMPACT_PARAMETERS = (0.1, 0.3, 0.5, 1.0)

N_POINTS = 300
WINDOW_IN_TE = 6.0
DELTA_CHI2_THRESHOLD = 25.0


def _time_grid(t_e_days: float) -> np.ndarray:
    """Create an observation window centred on the event peak."""
    half_window = 0.5 * WINDOW_IN_TE * t_e_days
    return np.linspace(-half_window, half_window, N_POINTS)


def _detection_fields(fit) -> dict[str, float | bool]:
    """Convert a fit result into detection metrics."""
    delta_chi2 = (
        float(fit.chi2_flat - fit.chi2)
        if fit.success and np.isfinite(fit.chi2)
        else float("nan")
    )

    detected = bool(
        fit.success
        and np.isfinite(delta_chi2)
        and delta_chi2 >= DELTA_CHI2_THRESHOLD
    )

    return {
        "fit_success": bool(fit.success),
        "detected": detected,
        "delta_chi2": delta_chi2,
        "reduced_chi2": float(fit.reduced_chi2),
    }


def run_event_trial(
    preset_key: str,
    u0_true: float,
    noise_fraction: float,
    seed: int,
) -> dict[str, float | int | str | bool]:
    """Inject and fit one synthetic microlensing event."""
    preset = PRESETS[preset_key]
    t_e_true = float(preset.t_e_days)
    time_days = _time_grid(t_e_true)

    baseline_flux = preset.source_flux + preset.blend_flux
    noise_std = noise_fraction * baseline_flux

    injected = light_curve(
        time_days,
        u0=u0_true,
        t0=0.0,
        t_e=t_e_true,
        source_flux=preset.source_flux,
        blend_flux=preset.blend_flux,
        noise_std=noise_std,
        random_seed=seed,
    )

    errors = np.full_like(injected.flux, noise_std)
    fit = fit_pspl(injected.time_days, injected.flux, errors)
    detection = _detection_fields(fit)

    u0_fit = float(fit.params.get("u0", np.nan))
    t0_fit = float(fit.params.get("t0", np.nan))
    t_e_fit = float(fit.params.get("t_e", np.nan))

    return {
        "trial_type": "injected_event",
        "preset": preset_key,
        "lens_mass_earth": float(preset.lens_mass_earth),
        "u0_true": float(u0_true),
        "t_e_true_days": t_e_true,
        "noise_fraction": float(noise_fraction),
        "seed": int(seed),
        **detection,
        "u0_fit": u0_fit,
        "t0_fit_days": t0_fit,
        "t_e_fit_days": t_e_fit,
        "u0_relative_error": (
            abs(u0_fit - u0_true) / u0_true
            if np.isfinite(u0_fit)
            else np.nan
        ),
        "t_e_relative_error": (
            abs(t_e_fit - t_e_true) / t_e_true
            if np.isfinite(t_e_fit)
            else np.nan
        ),
    }


def run_flat_control(
    noise_fraction: float,
    seed: int,
) -> dict[str, float | int | str | bool]:
    """Fit a noisy constant star to measure false-positive detections."""
    reference_t_e = float(PRESETS["earth"].t_e_days)
    time_days = _time_grid(reference_t_e)

    rng = np.random.default_rng(seed)
    errors = np.full_like(time_days, noise_fraction)
    flux = 1.0 + rng.normal(
        0.0,
        noise_fraction,
        size=time_days.shape,
    )

    fit = fit_pspl(time_days, flux, errors)
    detection = _detection_fields(fit)

    return {
        "trial_type": "flat_control",
        "preset": "flat_control",
        "lens_mass_earth": np.nan,
        "u0_true": np.nan,
        "t_e_true_days": np.nan,
        "noise_fraction": float(noise_fraction),
        "seed": int(seed),
        **detection,
        "u0_fit": float(fit.params.get("u0", np.nan)),
        "t0_fit_days": float(fit.params.get("t0", np.nan)),
        "t_e_fit_days": float(fit.params.get("t_e", np.nan)),
        "u0_relative_error": np.nan,
        "t_e_relative_error": np.nan,
    }


def run_study(seed_count: int) -> pd.DataFrame:
    """Run all event and control trials."""
    rows: list[dict[str, float | int | str | bool]] = []

    total_events = (
        len(PRESET_KEYS)
        * len(IMPACT_PARAMETERS)
        * len(NOISE_LEVELS)
        * seed_count
    )

    print(f"Running {total_events} injected events...")

    completed = 0

    for preset_key in PRESET_KEYS:
        for u0_true in IMPACT_PARAMETERS:
            for noise_fraction in NOISE_LEVELS:
                for seed in range(seed_count):
                    rows.append(
                        run_event_trial(
                            preset_key,
                            u0_true,
                            noise_fraction,
                            seed,
                        )
                    )

                    completed += 1

                    if completed % 100 == 0 or completed == total_events:
                        print(f"Completed {completed}/{total_events}")

    control_count = len(NOISE_LEVELS) * seed_count
    print(f"Running {control_count} flat controls...")

    for noise_fraction in NOISE_LEVELS:
        for seed in range(seed_count):
            rows.append(
                run_flat_control(
                    noise_fraction,
                    100_000 + seed,
                )
            )

    return pd.DataFrame(rows)


def save_summaries(
    results: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Save grouped event and control statistics."""
    events = results[
        results["trial_type"] == "injected_event"
    ].copy()

    controls = results[
        results["trial_type"] == "flat_control"
    ].copy()

    event_summary = (
        events.groupby(
            ["preset", "u0_true", "noise_fraction"],
            as_index=False,
        )
        .agg(
            trials=("detected", "size"),
            successful_fits=("fit_success", "sum"),
            detections=("detected", "sum"),
            detection_rate=("detected", "mean"),
            median_t_e_relative_error=(
                "t_e_relative_error",
                "median",
            ),
            median_u0_relative_error=(
                "u0_relative_error",
                "median",
            ),
        )
        .sort_values(
            ["preset", "u0_true", "noise_fraction"]
        )
    )

    control_summary = (
        controls.groupby(
            "noise_fraction",
            as_index=False,
        )
        .agg(
            trials=("detected", "size"),
            false_positives=("detected", "sum"),
            false_positive_rate=("detected", "mean"),
        )
        .sort_values("noise_fraction")
    )

    event_summary.to_csv(
        output_dir / "injection_recovery_summary.csv",
        index=False,
    )

    control_summary.to_csv(
        output_dir / "flat_control_summary.csv",
        index=False,
    )


def save_plots(
    results: pd.DataFrame,
    plot_dir: Path,
) -> None:
    """Create detection and recovery plots."""
    events = results[
        results["trial_type"] == "injected_event"
    ].copy()

    controls = results[
        results["trial_type"] == "flat_control"
    ].copy()

    events["noise_percent"] = (
        100.0 * events["noise_fraction"]
    )

    controls["noise_percent"] = (
        100.0 * controls["noise_fraction"]
    )

    detection = (
        events.groupby(
            ["preset", "noise_percent"],
            as_index=False,
        )["detected"]
        .mean()
        .sort_values("noise_percent")
    )

    fig, ax = plt.subplots(figsize=(7.5, 4.8))

    for preset_key in PRESET_KEYS:
        subset = detection[
            detection["preset"] == preset_key
        ]

        ax.plot(
            subset["noise_percent"],
            100.0 * subset["detected"],
            marker="o",
            label=PRESETS[preset_key].label,
        )

    ax.set_xlabel(
        "Gaussian noise level (% of baseline flux)"
    )
    ax.set_ylabel("Detection rate (%)")
    ax.set_title(
        "RogueLens injection-recovery detection rate"
    )
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(
        plot_dir / "detection_rate_vs_noise.png",
        dpi=180,
    )
    plt.close(fig)

    recovered = events[events["detected"]].copy()

    t_e_error = (
        recovered.groupby(
            ["preset", "noise_percent"],
            as_index=False,
        )["t_e_relative_error"]
        .median()
        .sort_values("noise_percent")
    )

    fig, ax = plt.subplots(figsize=(7.5, 4.8))

    for preset_key in PRESET_KEYS:
        subset = t_e_error[
            t_e_error["preset"] == preset_key
        ]

        ax.plot(
            subset["noise_percent"],
            100.0 * subset["t_e_relative_error"],
            marker="o",
            label=PRESETS[preset_key].label,
        )

    ax.set_xlabel(
        "Gaussian noise level (% of baseline flux)"
    )
    ax.set_ylabel(
        "Median relative error in tE (%)"
    )
    ax.set_title(
        "Recovered Einstein-timescale accuracy"
    )
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(
        plot_dir / "t_e_error_vs_noise.png",
        dpi=180,
    )
    plt.close(fig)

    false_positive = (
        controls.groupby(
            "noise_percent",
            as_index=False,
        )["detected"]
        .mean()
        .sort_values("noise_percent")
    )

    fig, ax = plt.subplots(figsize=(7.5, 4.8))

    ax.plot(
        false_positive["noise_percent"],
        100.0 * false_positive["detected"],
        marker="o",
    )

    ax.set_xlabel(
        "Gaussian noise level (% of baseline flux)"
    )
    ax.set_ylabel("False-positive rate (%)")
    ax.set_title(
        "RogueLens flat-control false-positive rate"
    )
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(
        plot_dir / "false_positive_rate_vs_noise.png",
        dpi=180,
    )
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the RogueLens injection-recovery experiment."
        )
    )

    parser.add_argument(
        "--seeds",
        type=int,
        default=10,
        help=(
            "Random seeds per parameter combination. "
            "Use 100 for the full study."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.seeds <= 0:
        raise ValueError(
            "--seeds must be a positive integer"
        )

    results_dir = ROOT / "results"
    plot_dir = ROOT / "plots"

    results_dir.mkdir(exist_ok=True)
    plot_dir.mkdir(exist_ok=True)

    results = run_study(args.seeds)

    results.to_csv(
        results_dir / "injection_recovery.csv",
        index=False,
    )

    save_summaries(results, results_dir)
    save_plots(results, plot_dir)

    event_rows = results[
        results["trial_type"] == "injected_event"
    ]

    control_rows = results[
        results["trial_type"] == "flat_control"
    ]

    print()
    print("Study complete.")
    print(
        f"Injected-event trials: {len(event_rows)}"
    )
    print(
        "Overall detection rate: "
        f"{event_rows['detected'].mean():.1%}"
    )
    print(
        f"Flat-control trials: {len(control_rows)}"
    )
    print(
        "False-positive rate: "
        f"{control_rows['detected'].mean():.1%}"
    )
    print(f"Results: {results_dir}")
    print(f"Plots:   {plot_dir}")


if __name__ == "__main__":
    main()
