"""Generate a clean Earth-mass rogue planet microlensing event."""

from pathlib import Path

import numpy as np

from roguelens.model import light_curve
from roguelens.plotting import plot_light_curve
from roguelens.presets import get_preset

preset = get_preset("earth")
times = np.linspace(-4 * preset.t_e_days, 4 * preset.t_e_days, 700)
curve = light_curve(times, u0=preset.u0, t0=0.0, t_e=preset.t_e_days)

plot_light_curve(
    curve,
    title="RogueLens: Earth-mass rogue planet microlensing event",
    output_path=Path("plots/basic_event.png"),
)

print("Created plots/basic_event.png")
print(f"Estimated Einstein crossing time: {preset.t_e_days:.3f} days")
print(f"Peak magnification: {curve.magnification.max():.2f}x")
