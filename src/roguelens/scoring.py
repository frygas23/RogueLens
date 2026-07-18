"""
scoring.py -- the "microlensing-likeness" candidate score.

IMPORTANT: this is a heuristic, educational score from 0 to 100. It is
NOT a probability and it does NOT confirm anything. Real surveys use
much more careful statistics plus human vetting. The point here is to
show, transparently, what properties make a light curve *look like*
microlensing:

  1. the PSPL model fits much better than a flat line
  2. the peak sticks out clearly above the noise (SNR)
  3. the event is symmetric around the peak (microlensing is achromatic
     and time-symmetric; many false positives aren't)
  4. there is one smooth bump, not several (periodic variables fail this)
  5. the fitted parameters are physically reasonable

Each component gives 0-20 points; we just add them up.
"""

from dataclasses import dataclass, field

import numpy as np




@dataclass
class ScoreResult:
    total: int
    components: dict = field(default_factory=dict)   # name -> (points, note)
    verdict: str = ""


def _clip20(x):
    return float(np.clip(x, 0.0, 20.0))


def _fit_improvement_points(fit):
    """How much better is PSPL than a flat line? (delta chi^2 based)

    A subtlety learned from testing on a variable star: the fit can
    "latch onto" one bump of a periodic signal and still show a huge
    delta chi^2 over the flat model, while leaving terrible residuals
    on the other bumps. So the improvement only counts if the model
    actually *describes* the data: we scale by a quality factor that
    collapses when the reduced chi^2 is much larger than 1.
    """
    if not fit.success or fit.chi2_flat <= 0:
        return 0.0, "Fit failed, no improvement measurable."
    delta = fit.chi2_flat - fit.chi2
    n = len(fit.errors_used)
    quality = 1.0 / (1.0 + max(fit.reduced_chi2 - 1.5, 0.0))
    pts = _clip20(20.0 * (delta / n) / 5.0 * quality)
    note = f"Δχ² over flat model: {delta:.1f} ({delta / n:.2f} per point)"
    if quality < 0.5:
        note += (f", but the model leaves large residuals "
                 f"(reduced χ² = {fit.reduced_chi2:.1f}), so most of these "
                 "points are withheld")
    return pts, note + "."


def _snr_points(t, f, e, smooth):
    """Peak signal-to-noise, measured from the *data* itself.

    We deliberately don't use the fitted peak here: with tiny tE and u0
    the fit can hallucinate an ultra-narrow spike between data points
    with huge magnification that no measurement actually supports.
    The smoothed data can't lie like that.
    """
    baseline = float(np.median(smooth))
    peak = float(np.max(smooth))
    noise = float(np.median(e))
    snr = (peak - baseline) / noise if noise > 0 else 0.0
    pts = _clip20(20.0 * snr / 20.0)  # saturates at SNR ~ 20
    return pts, f"Peak SNR ≈ {snr:.1f} (from smoothed data, not the model)."


def _symmetry_points(t, f, fit):
    """Compare the light curve before and after t0 (mirrored)."""
    if not fit.success:
        return 0.0, "No fit, symmetry not evaluated."
    t0 = fit.params["t0"]
    te = fit.params["t_e"]
    win = 2.0 * te
    left = (t >= t0 - win) & (t < t0)
    right = (t > t0) & (t <= t0 + win)
    if left.sum() < 5 or right.sum() < 5:
        return 0.0, ("Peak not sampled on both sides (or fitted event is "
                     "too narrow), so symmetry can't be demonstrated.")
    # interpolate the right side onto mirrored left-side times
    tl = t0 - t[left][::-1]        # distance from peak, ascending
    fl = f[left][::-1]
    fr = np.interp(tl, t[right] - t0, f[right])
    scale = max(np.std(f), 1e-9)
    asym = float(np.mean(np.abs(fl - fr)) / scale)
    pts = _clip20(20.0 * (1.0 - asym))
    return pts, f"Mean mirrored difference: {asym:.2f} (0 = perfectly symmetric)."


def _single_peak_points(t, f, smooth):
    """Count significant local maxima in the smoothed curve."""
    noise = float(np.std(f - smooth))
    base = float(np.median(smooth))
    # a "significant" peak pokes at least 3 sigma above baseline
    thresh = base + 3.0 * max(noise, 1e-9)
    above = smooth > thresh
    # count contiguous regions above threshold
    n_bumps = int(np.sum(np.diff(above.astype(int)) == 1) + (1 if above[0] else 0))
    if n_bumps == 1:
        return 20.0, "One significant bump found -- consistent with a single event."
    if n_bumps == 0:
        return 0.0, "No significant bump above the noise."
    pts = _clip20(20.0 / n_bumps)
    return pts, f"{n_bumps} separate bumps found -- looks periodic or messy."


def _plausibility_points(t, fit):
    """Are u0, tE, fluxes in a physically sensible range?"""
    if not fit.success:
        return 0.0, "No fit, parameters not evaluated."
    p = fit.params
    span = t[-1] - t[0]
    pts = 20.0
    notes = []
    if not (0.0 < p["u0"] < 1.5):
        pts -= 7
        notes.append(f"u0 = {p['u0']:.2f} is outside the typical (0, 1.5) range")
    if not (span / 200 < p["t_e"] < span * 2):
        pts -= 7
        notes.append(f"t_e = {p['t_e']:.2f} is implausible for this time span")
    if p["source_flux"] <= 0:
        pts -= 7
        notes.append("fitted source flux is not positive")
    if p["blend_flux"] < -0.5 * abs(p["source_flux"]):
        pts -= 5
        notes.append("strongly negative blend flux (usually a bad fit)")
    if not (t[0] <= p["t0"] <= t[-1]):
        pts -= 7
        notes.append("fitted peak time lies outside the observed window")
    note = "; ".join(notes) if notes else "All fitted parameters look physically reasonable."
    return _clip20(pts), note


def verdict_for(total):
    if total <= 30:
        return "Unlikely microlensing-like signal"
    if total <= 60:
        return "Weak candidate"
    if total <= 80:
        return "Possible microlensing-like candidate"
    return "Strong educational candidate -- would require real scientific validation"


def score_candidate(t, f, e, fit, smooth):
    """Combine all five heuristics into the 0-100 score.

    ``e`` may be None (CSV without an error column); we then fall back
    to the same scatter-based estimate the fitter uses.
    """
    if e is None:
        from . import lightcurve_io
        e = lightcurve_io.estimate_errors(np.asarray(f, float))
    comps = {}
    comps["Fit improvement over flat"] = _fit_improvement_points(fit)
    comps["Peak signal-to-noise"] = _snr_points(t, f, e, smooth)
    comps["Symmetry around peak"] = _symmetry_points(t, f, fit)
    comps["Single smooth peak"] = _single_peak_points(t, f, smooth)
    comps["Physically reasonable parameters"] = _plausibility_points(t, fit)

    total = int(round(sum(p for p, _ in comps.values())))
    total = int(np.clip(total, 0, 100))
    return ScoreResult(total=total, components=comps, verdict=verdict_for(total))
