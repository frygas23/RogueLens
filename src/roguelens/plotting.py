"""Plotting helpers for RogueLens."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import matplotlib.pyplot as plt

from .model import LightCurveResult


def plot_light_curve(
    result: LightCurveResult,
    *,
    title: str,
    output_path: str | Path,
    show: bool = False,
) -> Path:
    """Plot a single microlensing light curve."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.plot(result.time_days, result.flux, linewidth=2.2)
    ax.axhline(result.baseline_flux, linestyle="--", linewidth=1.0, alpha=0.65, label="baseline")
    ax.set_title(title)
    ax.set_xlabel("Time from closest approach (days)")
    ax.set_ylabel("Observed flux (arbitrary units)")
    ax.grid(True, alpha=0.25)
    ax.annotate(
        "temporary brightening",
        xy=(result.time_days[result.flux.argmax()], result.flux.max()),
        xytext=(0.05, 0.88),
        textcoords="axes fraction",
        arrowprops={"arrowstyle": "->", "lw": 1.2},
    )
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    if show:
        plt.show()
    plt.close(fig)
    return output


def plot_comparison(
    curves: Mapping[str, LightCurveResult],
    *,
    title: str,
    output_path: str | Path,
    show: bool = False,
) -> Path:
    """Plot several light curves on the same axes."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 5.2))
    for label, curve in curves.items():
        ax.plot(curve.time_days, curve.flux, linewidth=2.0, label=label)

    ax.set_title(title)
    ax.set_xlabel("Time from closest approach (days)")
    ax.set_ylabel("Observed flux (arbitrary units)")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    if show:
        plt.show()
    plt.close(fig)
    return output
