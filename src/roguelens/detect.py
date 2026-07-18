"""Simple star detection in a single astronomical image.

Used by the Single Image Explorer page. This is deliberately basic:

1. estimate the background (median) and the noise (MAD) of the frame,
2. smooth lightly with a Gaussian to suppress single hot pixels,
3. keep local maxima that stand more than ``k_sigma`` above the background.

It will happily "detect" galaxies, JPEG artifacts, or lens flares as
stars -- it has no idea what a point spread function is. That's fine for
its only job here: counting roughly how many star-like sources appear
in a frame, so the probability page has an N to work with.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import ndimage


@dataclass(frozen=True)
class DetectedStar:
    x: float          # pixel column
    y: float          # pixel row
    brightness: float  # smoothed peak value above background


def estimate_background(data: np.ndarray) -> tuple[float, float]:
    """Return (background level, noise sigma) using median and MAD."""
    bg = float(np.median(data))
    mad = float(np.median(np.abs(data - bg)))
    noise = max(1.4826 * mad, 1e-9)  # MAD -> Gaussian sigma
    return bg, noise


def detect_stars(
    data: np.ndarray,
    *,
    k_sigma: float = 5.0,
    min_separation_px: int = 4,
    max_stars: int = 3000,
) -> list[DetectedStar]:
    """Find star-like local maxima in a 2D brightness array."""
    data = np.asarray(data, dtype=float)
    if data.ndim != 2:
        raise ValueError("detect_stars expects a 2D grayscale array")

    bg, noise = estimate_background(data)
    smooth = ndimage.gaussian_filter(data, sigma=1.5)

    # a pixel is a peak if it equals the local maximum of its neighbourhood
    size = 2 * min_separation_px + 1
    local_max = ndimage.maximum_filter(smooth, size=size)
    peaks = (smooth == local_max) & (smooth > bg + k_sigma * noise)

    ys, xs = np.nonzero(peaks)
    if len(xs) == 0:
        return []

    values = smooth[ys, xs] - bg
    order = np.argsort(values)[::-1][:max_stars]
    return [DetectedStar(x=float(xs[i]), y=float(ys[i]),
                         brightness=float(values[i])) for i in order]
