"""Core point-lens microlensing model for RogueLens.

This module implements the standard point-source/point-lens educational model:

    u(t) = sqrt(u0^2 + ((t - t0) / tE)^2)
    A(u) = (u^2 + 2) / (u * sqrt(u^2 + 4))

The goal is not to replace professional microlensing tools. The goal is to make
one real astrophysical idea understandable, testable, and reproducible in a
small high-school portfolio project.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class LightCurveResult:
    """Container for one simulated microlensing event.

    Attributes:
        time_days: Observation times in days.
        separation_u: Lens-source separation in Einstein-radius units.
        magnification: Dimensionless point-lens magnification.
        flux: Observed flux in arbitrary units.
        delta_magnitude: Brightness change relative to the baseline flux.
        baseline_flux: Unmagnified baseline flux, including blended light.
        parameters: Human-readable parameters used to generate the event.
    """

    time_days: np.ndarray
    separation_u: np.ndarray
    magnification: np.ndarray
    flux: np.ndarray
    delta_magnitude: np.ndarray
    baseline_flux: float
    parameters: dict[str, float]

    @property
    def peak_index(self) -> int:
        """Index of the brightest sampled point."""

        return int(np.argmax(self.flux))

    @property
    def peak_time_days(self) -> float:
        """Time of the brightest sampled point."""

        return float(self.time_days[self.peak_index])

    @property
    def peak_magnification(self) -> float:
        """Largest magnification in the sampled light curve."""

        return float(np.max(self.magnification))

    @property
    def peak_flux(self) -> float:
        """Largest observed flux in the sampled light curve."""

        return float(np.max(self.flux))

    @property
    def max_brightening_magnitude(self) -> float:
        """Largest brightness increase, expressed as a positive magnitude change."""

        return float(-np.min(self.delta_magnitude))


def _as_float_array(values: Iterable[float] | np.ndarray) -> np.ndarray:
    """Return values as a one-dimensional finite float array."""

    array = np.asarray(values, dtype=float)
    if array.ndim != 1:
        raise ValueError("times must be a one-dimensional array")
    if array.size == 0:
        raise ValueError("times must contain at least one value")
    if not np.all(np.isfinite(array)):
        raise ValueError("times must contain only finite values")
    return array


def lens_source_separation(
    time_days: Iterable[float] | np.ndarray,
    *,
    u0: float,
    t0: float,
    t_e: float,
) -> np.ndarray:
    """Compute the lens-source separation u(t).

    Args:
        time_days: Observation times in days.
        u0: Minimum separation in Einstein-radius units. Must be positive.
        t0: Time of closest approach, in days.
        t_e: Einstein crossing time, in days. Must be positive.

    Returns:
        A NumPy array with u(t) for each time value.
    """

    if not np.isfinite(u0) or u0 <= 0:
        raise ValueError("u0 must be a positive finite number, e.g. 0.1 or 0.2")
    if not np.isfinite(t0):
        raise ValueError("t0 must be finite")
    if not np.isfinite(t_e) or t_e <= 0:
        raise ValueError("t_e must be a positive finite number")

    t = _as_float_array(time_days)
    tau = (t - float(t0)) / float(t_e)
    return np.sqrt(float(u0) ** 2 + tau**2)


def point_lens_magnification(separation_u: Iterable[float] | np.ndarray) -> np.ndarray:
    """Compute point-lens magnification A(u).

    Args:
        separation_u: Lens-source separation in Einstein-radius units.

    Returns:
        Dimensionless magnification values.
    """

    u = np.asarray(separation_u, dtype=float)
    if u.ndim == 0:
        u = u.reshape(1)
    if not np.all(np.isfinite(u)):
        raise ValueError("all separation values must be finite")
    if np.any(u <= 0):
        raise ValueError("all separation values must be positive")

    return (u**2 + 2.0) / (u * np.sqrt(u**2 + 4.0))


def flux_to_delta_magnitude(flux: Iterable[float] | np.ndarray, baseline_flux: float) -> np.ndarray:
    """Convert flux values into magnitude change relative to a baseline.

    Astronomical magnitudes run backwards: a brighter object has a smaller
    magnitude. Therefore a microlensing event appears as a negative delta
    magnitude.
    """

    if not np.isfinite(baseline_flux) or baseline_flux <= 0:
        raise ValueError("baseline_flux must be positive and finite")
    flux_array = np.asarray(flux, dtype=float)
    if not np.all(np.isfinite(flux_array)):
        raise ValueError("flux values must be finite")
    safe_flux = np.maximum(flux_array, np.finfo(float).tiny)
    return -2.5 * np.log10(safe_flux / baseline_flux)


def light_curve(
    time_days: Iterable[float] | np.ndarray,
    *,
    u0: float = 0.15,
    t0: float = 0.0,
    t_e: float = 1.0,
    source_flux: float = 1.0,
    blend_flux: float = 0.0,
    noise_std: float = 0.0,
    random_seed: int | None = None,
) -> LightCurveResult:
    """Simulate a simple microlensing light curve.

    Args:
        time_days: Observation times in days.
        u0: Minimum lens-source separation in Einstein-radius units.
        t0: Time of closest approach in days.
        t_e: Einstein crossing time in days.
        source_flux: Baseline flux of the source star in arbitrary units.
        blend_flux: Extra constant flux from nearby unresolved stars.
        noise_std: Standard deviation of optional Gaussian noise added to flux.
        random_seed: Seed for reproducible noise.

    Returns:
        LightCurveResult with time, separation, magnification, flux, magnitude
        change, baseline flux, and the input parameters.
    """

    if not np.isfinite(source_flux) or source_flux <= 0:
        raise ValueError("source_flux must be positive and finite")
    if not np.isfinite(blend_flux) or blend_flux < 0:
        raise ValueError("blend_flux cannot be negative and must be finite")
    if not np.isfinite(noise_std) or noise_std < 0:
        raise ValueError("noise_std cannot be negative and must be finite")

    t = _as_float_array(time_days)
    u = lens_source_separation(t, u0=u0, t0=t0, t_e=t_e)
    magnification = point_lens_magnification(u)
    flux = source_flux * magnification + blend_flux

    if noise_std > 0:
        rng = np.random.default_rng(random_seed)
        flux = flux + rng.normal(0.0, noise_std, size=flux.shape)

    baseline_flux = float(source_flux + blend_flux)
    delta_magnitude = flux_to_delta_magnitude(flux, baseline_flux)

    return LightCurveResult(
        time_days=t,
        separation_u=u,
        magnification=magnification,
        flux=flux,
        delta_magnitude=delta_magnitude,
        baseline_flux=baseline_flux,
        parameters={
            "u0": float(u0),
            "t0": float(t0),
            "t_e": float(t_e),
            "source_flux": float(source_flux),
            "blend_flux": float(blend_flux),
            "noise_std": float(noise_std),
        },
    )


def estimate_fwhm_days(result: LightCurveResult) -> float:
    """Estimate the full width at half maximum of the event in days.

    The measurement is made on flux above the baseline. If the sampled time
    window does not contain both half-maximum crossings, NaN is returned.
    """

    excess_flux = result.flux - result.baseline_flux
    peak_excess = float(np.max(excess_flux))
    if peak_excess <= 0:
        return float("nan")

    half_level = 0.5 * peak_excess
    above = np.flatnonzero(excess_flux >= half_level)
    if above.size < 2:
        return float("nan")
    left = above[0]
    right = above[-1]
    return float(result.time_days[right] - result.time_days[left])


def event_summary(result: LightCurveResult) -> dict[str, float]:
    """Return a compact numeric summary for a simulated event."""

    return {
        "peak_time_days": result.peak_time_days,
        "peak_magnification": result.peak_magnification,
        "peak_flux": result.peak_flux,
        "max_brightening_magnitude": result.max_brightening_magnitude,
        "estimated_fwhm_days": estimate_fwhm_days(result),
        "baseline_flux": result.baseline_flux,
    }
