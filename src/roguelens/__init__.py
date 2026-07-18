"""RogueLens: educational microlensing simulator and candidate explorer.

Core simulator (model, physical, presets) plus analysis modules used by
the Streamlit app: lightcurve_io, fitting, scoring, photometry, detect,
probability, demo_data. The analysis modules are imported lazily by the
app so that the core simulator keeps its minimal numpy/matplotlib
dependencies.
"""

from .model import (
    LightCurveResult,
    estimate_fwhm_days,
    event_summary,
    flux_to_delta_magnitude,
    lens_source_separation,
    light_curve,
    point_lens_magnification,
)
from .physical import angular_einstein_radius_mas, einstein_radius_au, einstein_radius_m, einstein_time_days

__all__ = [
    "LightCurveResult",
    "lens_source_separation",
    "light_curve",
    "point_lens_magnification",
    "flux_to_delta_magnitude",
    "estimate_fwhm_days",
    "event_summary",
    "einstein_radius_m",
    "einstein_radius_au",
    "angular_einstein_radius_mas",
    "einstein_time_days",
]
