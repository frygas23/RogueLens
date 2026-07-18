"""Compare light curves for different rogue planet masses.

The key lesson is that the shape is similar, but the duration changes. In this
simple model, more massive lenses have larger Einstein radii and therefore
longer Einstein crossing times.
"""

from pathlib import Path

import numpy as np

from roguelens.model import light_curve
from roguelens.plotting import plot_comparison
from roguelens.presets import get_preset

curves = {}
for name in ["mars", "earth", "neptune", "jupiter"]:
    preset = get_preset(name)
    times = np.linspace(-4 * preset.t_e_days, 4 * preset.t_e_days, 700)
    curve = light_curve(times, u0=preset.u0, t0=0.0, t_e=preset.t_e_days)
    curves[f"{preset.label} (tE={preset.t_e_days:.2f} d)"] = curve

plot_comparison(
    curves,
    title="RogueLens: comparing rogue planet microlensing timescales",
    output_path=Path("plots/mass_comparison.png"),
)

print("Created plots/mass_comparison.png")
