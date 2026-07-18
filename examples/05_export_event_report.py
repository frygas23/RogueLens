"""Export a CSV table and a small Markdown report for one event."""

from pathlib import Path

import numpy as np

from roguelens.io import save_event_report, save_light_curve_csv
from roguelens.model import event_summary, light_curve
from roguelens.presets import get_preset

preset = get_preset("earth")
times = np.linspace(-4 * preset.t_e_days, 4 * preset.t_e_days, 350)
curve = light_curve(times, u0=preset.u0, t0=0.0, t_e=preset.t_e_days)

csv_path = save_light_curve_csv(curve, Path("outputs/earth_event_light_curve.csv"))
report_path = save_event_report(curve, Path("outputs/earth_event_report.md"), title="Earth-mass rogue planet event")
summary = event_summary(curve)

print(f"Created {csv_path}")
print(f"Created {report_path}")
print("Event summary:")
for key, value in summary.items():
    print(f"  {key}: {value:.4g}")
