"""Show how the closest approach changes the height of the event peak."""

from pathlib import Path

import numpy as np

from roguelens.model import light_curve
from roguelens.plotting import plot_comparison
from roguelens.presets import get_preset

preset = get_preset("earth")
times = np.linspace(-4 * preset.t_e_days, 4 * preset.t_e_days, 700)

curves = {}
for u0 in [0.08, 0.15, 0.30, 0.60]:
    curve = light_curve(times, u0=u0, t0=0.0, t_e=preset.t_e_days)
    curves[f"u0 = {u0:.2f}"] = curve

plot_comparison(
    curves,
    title="RogueLens: how closest approach changes magnification",
    output_path=Path("plots/impact_parameter_comparison.png"),
)

print("Created plots/impact_parameter_comparison.png")
