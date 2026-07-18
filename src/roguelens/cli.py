"""Command-line interface for RogueLens."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from .io import save_event_report, save_light_curve_csv
from .model import event_summary, light_curve
from .plotting import plot_light_curve
from .presets import PRESETS, get_preset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate an educational rogue-planet microlensing light curve."
    )
    parser.add_argument(
        "--preset",
        default="earth",
        choices=sorted(PRESETS),
        help="Physical scenario to simulate.",
    )
    parser.add_argument(
        "--days",
        type=float,
        default=None,
        help="Half-width of the time window in days. Defaults to 4 Einstein times.",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=500,
        help="Number of sampled observation times.",
    )
    parser.add_argument(
        "--noise",
        type=float,
        default=0.0,
        help="Optional Gaussian noise standard deviation added to flux.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("plots/cli_event.png"),
        help="Output plot path.",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Optional CSV output path for the simulated light curve.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Optional Markdown report output path.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display the plot window after saving.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.samples < 10:
        parser.error("--samples must be at least 10")

    preset = get_preset(args.preset)
    t_e = preset.t_e_days
    half_window = args.days if args.days is not None else 4.0 * t_e
    if half_window <= 0:
        parser.error("--days must be positive")

    times = np.linspace(-half_window, half_window, args.samples)

    result = light_curve(
        times,
        u0=preset.u0,
        t0=preset.t0,
        t_e=t_e,
        source_flux=preset.source_flux,
        blend_flux=preset.blend_flux,
        noise_std=args.noise,
        random_seed=42,
    )

    plot_light_curve(
        result,
        title=f"RogueLens: {preset.label}",
        output_path=args.output,
        show=args.show,
    )

    print(f"Saved plot: {args.output}")
    print(f"Preset: {preset.label}")
    print(f"Lens mass: {preset.lens_mass_earth:.3g} Earth masses")
    print(f"Estimated Einstein time: {t_e:.3f} days")

    summary = event_summary(result)
    print(f"Peak magnification: {summary['peak_magnification']:.2f}x")
    print(f"Maximum brightening: {summary['max_brightening_magnitude']:.2f} mag")
    print(f"Estimated FWHM: {summary['estimated_fwhm_days']:.3f} days")

    if args.csv is not None:
        save_light_curve_csv(result, args.csv)
        print(f"Saved CSV: {args.csv}")

    if args.report is not None:
        save_event_report(result, args.report, title=f"RogueLens report: {preset.label}")
        print(f"Saved report: {args.report}")


if __name__ == "__main__":
    main()
