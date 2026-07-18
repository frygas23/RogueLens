"""Fitting the point-lens model to an observed light curve.

This is the "inverse" of model.py: instead of simulating a curve from
known parameters, we start from data and search for the parameters.

Strategy: microlensing fits are sensitive to the starting guess
(``scipy.optimize.curve_fit`` is a local optimizer), so we build a
decent initial guess from the data itself and also try a small grid of
t_e values, keeping the best chi-squared. We also fit a flat (constant)
model, because the candidate score needs to know how much better the
microlensing model is than "nothing happened".
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import curve_fit

from . import lightcurve_io
from .model import lens_source_separation, point_lens_magnification


def pspl_flux(t, u0, t0, t_e, source_flux, blend_flux):
    """Model flux built from the same functions the simulator uses."""
    u = lens_source_separation(t, u0=u0, t0=t0, t_e=t_e)
    return source_flux * point_lens_magnification(u) + blend_flux


@dataclass
class FitResult:
    success: bool
    message: str = ""
    params: dict = field(default_factory=dict)       # u0, t0, t_e, F_s, F_b
    param_errors: dict = field(default_factory=dict)
    chi2: float = np.inf
    chi2_flat: float = np.inf
    reduced_chi2: float = np.inf
    model_flux: np.ndarray | None = None
    residuals: np.ndarray | None = None
    errors_used: np.ndarray | None = None


def _initial_guesses(t, f):
    """Build starting points for the optimizer from simple data features."""
    stats = lightcurve_io.basic_stats(t, f)
    baseline = stats["baseline"]
    t0_guess = stats["peak_time"]
    amp = max(stats["peak_flux"] / max(baseline, 1e-9), 1.001)

    # invert A(u) approximately to guess u0 from the peak amplification
    a = amp
    u0_guess = float(np.sqrt(2 * a / np.sqrt(a ** 2 - 1) - 2)) if a > 1.0001 else 1.0
    u0_guess = float(np.clip(u0_guess, 0.01, 2.0))

    # width guess: time the smoothed curve spends above half the bump height
    smooth = stats["smooth"]
    half = baseline + 0.5 * (stats["peak_flux"] - baseline)
    above = t[smooth > half]
    width = (above.max() - above.min()) if len(above) > 1 else (t[-1] - t[0]) / 10
    width = max(width, (t[-1] - t[0]) / 200)

    span = t[-1] - t[0]
    te_grid = np.unique(np.clip(
        [width / 2, width, width * 2, span / 20, span / 5],
        span / 500, span * 2))
    return baseline, t0_guess, u0_guess, te_grid


def fit_flat(t, f, e):
    """Weighted-mean constant model and its chi-squared."""
    w = 1.0 / e ** 2
    mean = np.sum(w * f) / np.sum(w)
    chi2 = float(np.sum(((f - mean) / e) ** 2))
    return mean, chi2


def fit_pspl(t, f, e=None) -> FitResult:
    """Fit the point-lens model. Returns a FitResult, never raises."""
    t = np.asarray(t, float)
    f = np.asarray(f, float)
    if e is None:
        e = lightcurve_io.estimate_errors(f)
    e = np.asarray(e, float)

    _, chi2_flat = fit_flat(t, f, e)
    result = FitResult(success=False, chi2_flat=chi2_flat, errors_used=e)

    if len(t) < 10:
        result.message = "Not enough data points to fit (need at least 10)."
        return result

    baseline, t0_guess, u0_guess, te_grid = _initial_guesses(t, f)
    span = t[-1] - t[0]

    # bounds: keep parameters in a physically sensible box
    lower = [1e-4, t[0] - span, span / 1000, 1e-12, 0.0]
    upper = [3.0, t[-1] + span, span * 10, np.inf, np.inf]

    best = None
    for te0 in te_grid:
        p0 = [u0_guess, t0_guess, te0,
              max(baseline * 0.8, 1e-9), max(baseline * 0.2, 0.0)]
        try:
            popt, pcov = curve_fit(
                pspl_flux, t, f, p0=p0, sigma=e,
                absolute_sigma=True, bounds=(lower, upper), maxfev=20000)
        except (RuntimeError, ValueError):
            continue  # this starting point didn't converge; try the next
        m = pspl_flux(t, *popt)
        chi2 = float(np.sum(((f - m) / e) ** 2))
        if best is None or chi2 < best[0]:
            best = (chi2, popt, pcov, m)

    if best is None:
        result.message = (
            "The optimizer could not converge from any starting point. "
            "This usually means the data has no clear single bump for the "
            "model to latch onto (flat, periodic, or very noisy data)."
        )
        return result

    chi2, popt, pcov, m = best
    perr = np.sqrt(np.abs(np.diag(pcov)))
    names = ["u0", "t0", "t_e", "source_flux", "blend_flux"]
    dof = max(len(t) - len(popt), 1)

    result.success = True
    result.params = dict(zip(names, [float(v) for v in popt]))
    result.param_errors = dict(zip(names, [float(v) for v in perr]))
    result.chi2 = chi2
    result.reduced_chi2 = chi2 / dof
    result.model_flux = m
    result.residuals = f - m
    result.message = "Fit converged."
    return result
