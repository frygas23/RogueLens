"""Generate a synthetic noisy observation of a rogue planet microlensing event."""

from pathlib import Path

import numpy as np

from roguelens.model import light_curve
from roguelens.plotting import plot_light_curve
from roguelens.presets import get_preset

preset = get_preset("earth")
times = np.linspace(-4 * preset.t_e_days, 4 * preset.t_e_days, 150)
curve = light_curve(
    times,
    u0=preset.u0,
    t0=0.0,
    t_e=preset.t_e_days,
    noise_std=0.015,
    random_seed=17,
)

plot_light_curve(
    curve,
    title="RogueLens: synthetic noisy observation",
    output_path=Path("plots/noisy_observation.png"),
)

print("Created plots/noisy_observation.png")
