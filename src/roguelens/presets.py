"""Named scenarios used by examples and the command-line interface."""

from __future__ import annotations

from dataclasses import dataclass

from .physical import JUPITER_MASS_EARTH, NEPTUNE_MASS_EARTH, einstein_time_days


@dataclass(frozen=True)
class EventPreset:
    """Readable preset for a microlensing event."""

    key: str
    label: str
    lens_mass_earth: float
    u0: float
    t0: float = 0.0
    source_flux: float = 1.0
    blend_flux: float = 0.0
    velocity_km_s: float = 200.0
    lens_distance_kpc: float = 4.0
    source_distance_kpc: float = 8.0

    @property
    def t_e_days(self) -> float:
        return einstein_time_days(
            lens_mass_earth=self.lens_mass_earth,
            lens_distance_kpc=self.lens_distance_kpc,
            source_distance_kpc=self.source_distance_kpc,
            transverse_velocity_km_s=self.velocity_km_s,
        )


PRESETS: dict[str, EventPreset] = {
    "mars": EventPreset(
        key="mars",
        label="Mars-mass rogue planet",
        lens_mass_earth=0.107,
        u0=0.10,
        velocity_km_s=200.0,
    ),
    "earth": EventPreset(
        key="earth",
        label="Earth-mass rogue planet",
        lens_mass_earth=1.0,
        u0=0.12,
        velocity_km_s=200.0,
    ),
    "neptune": EventPreset(
        key="neptune",
        label="Neptune-mass rogue planet",
        lens_mass_earth=NEPTUNE_MASS_EARTH,
        u0=0.16,
        velocity_km_s=200.0,
    ),
    "jupiter": EventPreset(
        key="jupiter",
        label="Jupiter-mass rogue planet",
        lens_mass_earth=JUPITER_MASS_EARTH,
        u0=0.20,
        velocity_km_s=200.0,
    ),
    "fast": EventPreset(
        key="fast",
        label="Fast Earth-mass rogue planet",
        lens_mass_earth=1.0,
        u0=0.12,
        velocity_km_s=350.0,
    ),
    "blended": EventPreset(
        key="blended",
        label="Blended Earth-mass rogue planet event",
        lens_mass_earth=1.0,
        u0=0.12,
        velocity_km_s=200.0,
        blend_flux=0.7,
    ),
}


def get_preset(name: str) -> EventPreset:
    """Return a preset by name."""

    try:
        return PRESETS[name.lower()]
    except KeyError as exc:
        available = ", ".join(sorted(PRESETS))
        raise ValueError(f"unknown preset {name!r}. Choose one of: {available}") from exc
