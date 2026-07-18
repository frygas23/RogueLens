"""Demo light curves and image-injection helpers for the Streamlit app.

The microlensing curves come from the same ``light_curve`` simulator and
physical presets the CLI uses, so the app and the library always agree.
The two non-events (flat star, variable star) exist so the candidate
score has something to fail on.

``inject_event_into_image`` powers the Single Image Explorer: it takes a
real uploaded image, a detected star position, and a rogue-planet
preset, and renders what that star would look like at a few moments of
a hypothetical event. Pure simulation on top of real pixels -- clearly
labelled as such in the UI.
"""

from __future__ import annotations

import numpy as np

from .model import light_curve
from .presets import PRESETS, EventPreset


def _observed(result, noise_frac, seed):
    """Turn a clean LightCurveResult into (t, flux, err) with noise."""
    rng = np.random.default_rng(seed)
    err = noise_frac * result.baseline_flux * np.ones_like(result.flux)
    return result.time_days, result.flux + rng.normal(0, err), err


def preset_event_curve(preset_key: str, *, n_points: int = 400,
                       window_te: float = 6.0, noise_frac: float = 0.01,
                       seed: int = 42):
    """Noisy observation of one of the physical presets (earth, jupiter...)."""
    preset: EventPreset = PRESETS[preset_key]
    te = preset.t_e_days
    t = np.linspace(-window_te * te / 2, window_te * te / 2, n_points)
    result = light_curve(t, u0=preset.u0, t0=0.0, t_e=te,
                         source_flux=preset.source_flux,
                         blend_flux=preset.blend_flux)
    return _observed(result, noise_frac, seed)


def flat_star(seed: int = 42, n_points: int = 300):
    """No event at all. Should score near 0."""
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 20, n_points)
    err = 0.01 * np.ones_like(t)
    return t, 1.1 + rng.normal(0, err), err


def variable_star(seed: int = 42, n_points: int = 300):
    """Sinusoidal variable: the classic microlensing false positive."""
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 20, n_points)
    f = 1.0 + 0.15 * np.sin(2 * np.pi * t / 3.0)
    err = 0.01 * np.ones_like(t)
    return t, f + rng.normal(0, err), err


DEMO_CURVES = {
    **{f"{p.label} (t_e ≈ {p.t_e_days:.2g} d)": ("preset", key)
       for key, p in PRESETS.items()},
    "Flat star (no event)": ("flat", None),
    "Variable star (false positive)": ("variable", None),
}


def make_demo_curve(label: str, seed: int = 42):
    kind, key = DEMO_CURVES[label]
    if kind == "preset":
        return preset_event_curve(key, seed=seed)
    if kind == "flat":
        return flat_star(seed=seed)
    return variable_star(seed=seed)


# --------------------------------------------------------------- injection

def inject_event_into_image(image: np.ndarray, x: float, y: float,
                            magnification: float, psf_sigma_px: float = 2.5,
                            star_amplitude: float | None = None) -> np.ndarray:
    """Render one frame of a *hypothetical* event on a real image.

    We add a Gaussian blob at the star's position whose flux equals the
    star's own brightness times (A - 1): at A = 1 nothing changes, at
    A = 3 the star gains twice its normal light. This is a visualization
    trick, not photometry -- the PSF is assumed, not measured.
    """
    img = np.asarray(image, dtype=float)
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    r2 = (xx - x) ** 2 + (yy - y) ** 2
    psf = np.exp(-r2 / (2 * psf_sigma_px ** 2))

    if star_amplitude is None:
        # local star brightness above the surrounding background
        ap = r2 <= (3 * psf_sigma_px) ** 2
        ring = (r2 > (4 * psf_sigma_px) ** 2) & (r2 <= (8 * psf_sigma_px) ** 2)
        bg = float(np.median(img[ring])) if ring.any() else float(np.median(img))
        star_amplitude = max(float(img[ap].max()) - bg, 1.0)

    frame = img + (magnification - 1.0) * star_amplitude * psf
    return np.clip(frame, 0, 255)
