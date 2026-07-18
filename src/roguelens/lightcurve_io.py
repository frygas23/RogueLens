"""
io.py -- loading and cleaning light curve data.

Handles the CSV upload. The rules are deliberately forgiving: column
names are matched case-insensitively and a few common aliases are
accepted, because everyone names these columns differently.
"""

import numpy as np
import pandas as pd

# accepted column names, lowercased
TIME_ALIASES = ["time", "time_days", "t", "hjd", "bjd", "jd", "mjd", "date"]
FLUX_ALIASES = ["flux", "f", "brightness", "counts", "signal"]
ERROR_ALIASES = ["flux_error", "flux_err", "error", "err", "sigma",
                 "uncertainty", "e_flux"]


class LightCurveError(ValueError):
    """Raised when a CSV can't be interpreted as a light curve."""


def _find_column(df, aliases):
    lower_map = {c.lower().strip(): c for c in df.columns}
    for alias in aliases:
        if alias in lower_map:
            return lower_map[alias]
    return None


def load_light_curve_csv(file_or_path):
    """Read a CSV and return (time, flux, flux_error or None).

    flux_error is optional in the file; if it's missing we return None
    and let the fitting code estimate a constant error from the scatter.
    """
    try:
        df = pd.read_csv(file_or_path)
    except Exception as exc:
        raise LightCurveError(f"Could not parse the CSV file: {exc}") from exc

    t_col = _find_column(df, TIME_ALIASES)
    f_col = _find_column(df, FLUX_ALIASES)
    e_col = _find_column(df, ERROR_ALIASES)

    if t_col is None or f_col is None:
        raise LightCurveError(
            "The CSV needs a time column (e.g. 'time') and a flux column "
            f"(e.g. 'flux'). Found columns: {list(df.columns)}"
        )

    t = pd.to_numeric(df[t_col], errors="coerce").to_numpy(dtype=float)
    f = pd.to_numeric(df[f_col], errors="coerce").to_numpy(dtype=float)
    e = None
    if e_col is not None:
        e = pd.to_numeric(df[e_col], errors="coerce").to_numpy(dtype=float)

    # drop rows with NaNs and sort by time
    mask = np.isfinite(t) & np.isfinite(f)
    if e is not None:
        mask &= np.isfinite(e) & (e > 0)
    t, f = t[mask], f[mask]
    if e is not None:
        e = e[mask]

    if len(t) < 10:
        raise LightCurveError(
            f"Only {len(t)} valid data points after cleaning -- need at "
            "least 10 for a meaningful fit."
        )

    order = np.argsort(t)
    t, f = t[order], f[order]
    if e is not None:
        e = e[order]
    return t, f, e


def estimate_errors(flux):
    """Fallback error estimate when the CSV has no error column.

    Uses the median absolute deviation of point-to-point differences,
    which mostly ignores the slow event shape and captures the noise.
    """
    diffs = np.diff(flux)
    mad = np.median(np.abs(diffs - np.median(diffs)))
    sigma = 1.4826 * mad / np.sqrt(2)  # MAD -> std, diff doubles variance
    sigma = max(sigma, 1e-6 * max(np.median(np.abs(flux)), 1.0))
    return np.full_like(flux, sigma)


def basic_stats(t, f):
    """Baseline flux, peak flux/time, and a smoothed curve for display."""
    baseline = np.median(f)
    # moving-median smooth, window ~ 2% of the points (at least 3)
    win = max(3, len(f) // 50)
    if win % 2 == 0:
        win += 1
    padded = np.pad(f, win // 2, mode="edge")
    smooth = np.array([np.median(padded[i:i + win]) for i in range(len(f))])
    i_peak = int(np.argmax(smooth))
    return {
        "baseline": baseline,
        "peak_time": t[i_peak],
        "peak_flux": smooth[i_peak],
        "smooth": smooth,
    }
