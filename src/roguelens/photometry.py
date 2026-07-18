"""
image_photometry.py -- extracting a rough light curve from images.

This is the most "educational approximation" part of the whole project.
Real photometry needs calibration frames (bias/dark/flat), a real point
spread function, background subtraction done properly, and comparison
stars. We do none of that. We just:

  1. load each image (PNG/JPG always; FITS only if astropy is installed)
  2. convert to grayscale brightness
  3. sum the pixels inside a circular aperture around a chosen (x, y)
  4. subtract a background estimated from an annulus around the aperture
  5. treat the image order as the time axis (t = 0, 1, 2, ...)

So the output is a *relative*, uncalibrated light curve. It can show
"this spot got brighter in frame 12", nothing more. That's clearly
stated in the app UI too.
"""

import numpy as np
from PIL import Image

try:
    from astropy.io import fits as _fits
    HAS_FITS = True
except ImportError:
    HAS_FITS = False


def load_image_gray(file_obj, filename=""):
    """Return a 2D float array of brightness from PNG/JPG/FITS."""
    name = (filename or getattr(file_obj, "name", "")).lower()
    if name.endswith((".fits", ".fit", ".fts")):
        if not HAS_FITS:
            raise RuntimeError(
                "FITS support needs astropy. Install it with "
                "'pip install astropy' or upload PNG/JPG instead.")
        with _fits.open(file_obj) as hdul:
            for hdu in hdul:
                if hdu.data is not None and hdu.data.ndim >= 2:
                    data = np.asarray(hdu.data, dtype=float)
                    if data.ndim > 2:      # take the first plane of a cube
                        data = data[0]
                    return data
        raise ValueError(f"No 2D image data found in FITS file {name}.")
    img = Image.open(file_obj).convert("L")  # grayscale
    return np.asarray(img, dtype=float)


def aperture_photometry(data, x, y, radius, annulus_scale=(1.5, 2.5)):
    """Background-subtracted brightness in a circular aperture.

    x, y are pixel coordinates (x = column, y = row). Background is the
    median pixel value in an annulus between annulus_scale[0]*radius and
    annulus_scale[1]*radius.
    """
    h, w = data.shape
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt((xx - x) ** 2 + (yy - y) ** 2)

    ap_mask = r <= radius
    an_mask = (r >= annulus_scale[0] * radius) & (r <= annulus_scale[1] * radius)

    if ap_mask.sum() == 0:
        raise ValueError("Aperture falls completely outside the image.")

    background = float(np.median(data[an_mask])) if an_mask.sum() > 0 else 0.0
    total = float(np.sum(data[ap_mask] - background))
    # crude error: sqrt(N_pixels) * background scatter
    scatter = float(np.std(data[an_mask])) if an_mask.sum() > 5 else float(np.std(data))
    err = max(scatter * np.sqrt(ap_mask.sum()), 1e-9)
    return total, err


def extract_light_curve(files, x=None, y=None, radius=None, filenames=None):
    """Run aperture photometry on a sequence of images.

    If x/y are None we use the image center. If radius is None we use 5%
    of the smaller image dimension. Returns (time, flux, flux_error)
    where time is just the frame index.
    """
    fluxes, errors = [], []
    filenames = filenames or [getattr(fp, "name", f"frame_{i}")
                              for i, fp in enumerate(files)]
    for fp, name in zip(files, filenames):
        data = load_image_gray(fp, name)
        h, w = data.shape
        cx = w / 2 if x is None else x
        cy = h / 2 if y is None else y
        rad = min(h, w) * 0.05 if radius is None else radius
        flux, err = aperture_photometry(data, cx, cy, rad)
        fluxes.append(flux)
        errors.append(err)

    t = np.arange(len(fluxes), dtype=float)
    return t, np.asarray(fluxes), np.asarray(errors)
