"""Physical helpers for estimating microlensing scales.

RogueLens can be used with abstract parameters, but these helpers connect the
shape of a light curve to simple physical quantities such as lens mass,
distance, and transverse speed.
"""

from __future__ import annotations

import math

G = 6.67430e-11  # m^3 kg^-1 s^-2, CODATA value
C = 299_792_458.0  # m s^-1, exact by SI definition
KPC = 3.0856775814913673e19  # m
AU = 1.495978707e11  # m
EARTH_MASS = 5.9722e24  # kg
NEPTUNE_MASS_EARTH = 17.147
JUPITER_MASS = 1.89813e27  # kg
JUPITER_MASS_EARTH = JUPITER_MASS / EARTH_MASS
SECONDS_PER_DAY = 86_400.0
RAD_TO_MAS = 180.0 / math.pi * 3_600_000.0


def einstein_radius_m(
    *,
    lens_mass_earth: float,
    lens_distance_kpc: float = 4.0,
    source_distance_kpc: float = 8.0,
) -> float:
    """Estimate the physical Einstein radius in metres at the lens plane."""

    if lens_mass_earth <= 0:
        raise ValueError("lens_mass_earth must be positive")
    if lens_distance_kpc <= 0 or source_distance_kpc <= 0:
        raise ValueError("distances must be positive")
    if lens_distance_kpc >= source_distance_kpc:
        raise ValueError("the lens must be closer than the background source")

    mass_kg = lens_mass_earth * EARTH_MASS
    d_l = lens_distance_kpc * KPC
    d_s = source_distance_kpc * KPC
    d_ls = d_s - d_l

    return math.sqrt((4.0 * G * mass_kg / C**2) * (d_l * d_ls / d_s))


def angular_einstein_radius_mas(
    *,
    lens_mass_earth: float,
    lens_distance_kpc: float = 4.0,
    source_distance_kpc: float = 8.0,
) -> float:
    """Estimate the angular Einstein radius in milliarcseconds."""

    radius_m = einstein_radius_m(
        lens_mass_earth=lens_mass_earth,
        lens_distance_kpc=lens_distance_kpc,
        source_distance_kpc=source_distance_kpc,
    )
    d_l = lens_distance_kpc * KPC
    return radius_m / d_l * RAD_TO_MAS


def einstein_radius_au(
    *,
    lens_mass_earth: float,
    lens_distance_kpc: float = 4.0,
    source_distance_kpc: float = 8.0,
) -> float:
    """Estimate the physical Einstein radius in astronomical units."""

    return einstein_radius_m(
        lens_mass_earth=lens_mass_earth,
        lens_distance_kpc=lens_distance_kpc,
        source_distance_kpc=source_distance_kpc,
    ) / AU


def einstein_time_days(
    *,
    lens_mass_earth: float,
    lens_distance_kpc: float = 4.0,
    source_distance_kpc: float = 8.0,
    transverse_velocity_km_s: float = 200.0,
) -> float:
    """Estimate the Einstein crossing time in days."""

    if transverse_velocity_km_s <= 0:
        raise ValueError("transverse_velocity_km_s must be positive")

    radius_m = einstein_radius_m(
        lens_mass_earth=lens_mass_earth,
        lens_distance_kpc=lens_distance_kpc,
        source_distance_kpc=source_distance_kpc,
    )
    velocity_m_s = transverse_velocity_km_s * 1_000.0
    return radius_m / velocity_m_s / SECONDS_PER_DAY
