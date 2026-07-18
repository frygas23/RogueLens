"""Prior probability that a rogue-planet microlensing event is happening.

This is the honest answer to "can't you give a probability from one
image?". Yes -- but the probability comes from *Galactic statistics*,
not from the pixels. The image only contributes one number: how many
stars are visible. Two different images with the same star count get
the same probability. That is exactly why a single frame can never
"detect" anything, and why real surveys stare at hundreds of millions
of stars for years.

The key quantity is the microlensing **optical depth** tau: the
probability that, at a random moment, a given background star lies
inside the Einstein radius of *some* lens along the line of sight.
Toward the Galactic bulge, surveys measure tau on the order of 1e-6
(one star in a million is measurably lensed at any instant).

Free-floating planets contribute only a tiny slice of that, because
tau scales with the total lens *mass* along the sightline
(tau ~ sum of theta_E^2 ~ sum of M), and planets are light. Using the
MOA/OGLE-style estimates of roughly "a few Earth-to-Jupiter-mass
free floaters per star", the FFP mass fraction is of order 1e-3 --
uncertain by at least an order of magnitude, which we say out loud.

All numbers here are order-of-magnitude and clearly labelled as such.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# optical depth by sightline, order-of-magnitude values
SIGHTLINES: dict[str, tuple[float, str]] = {
    "bulge": (2e-6, "toward the Galactic bulge (densest, where surveys look)"),
    "disk": (3e-7, "along the Galactic plane, away from the bulge"),
    "high_latitude": (1e-8, "away from the Galactic plane (few lenses)"),
}

# fraction of the optical depth contributed by free-floating planets.
# tau scales with lens mass; a few Earth-to-Jupiter-mass FFPs per
# ~0.3-solar-mass star gives roughly 1e-3. Uncertain by >= 1 order
# of magnitude -- current FFP abundance itself is an active research
# question (that's the whole point of the Roman mission!).
FFP_MASS_FRACTION = 1e-3

# typical Einstein crossing time of an FFP event, in days, used to turn
# an instantaneous probability into an event *rate*.
FFP_TYPICAL_TE_DAYS = 0.5

DAYS_PER_YEAR = 365.25


@dataclass(frozen=True)
class ProbabilityEstimate:
    n_stars: int
    sightline: str
    tau_any: float                 # optical depth, any lens mass
    tau_ffp: float                 # optical depth, FFP lenses only
    p_any_lensing_now: float       # P(>=1 star lensed by anything, right now)
    p_ffp_lensing_now: float       # P(>=1 star lensed by an FFP, right now)
    ffp_events_per_year: float     # expected FFP events/year in this field
    years_per_ffp_event: float     # expected wait for one FFP event


def _p_at_least_one(n: int, p_single: float) -> float:
    """P(at least one success in n independent tries) = 1 - (1-p)^n."""
    if n <= 0 or p_single <= 0:
        return 0.0
    # use expm1/log1p to stay accurate for tiny probabilities
    return -math.expm1(n * math.log1p(-min(p_single, 1.0)))


def estimate(n_stars: int, sightline: str = "bulge") -> ProbabilityEstimate:
    """Prior probability estimate for a field with ``n_stars`` stars."""
    if sightline not in SIGHTLINES:
        raise ValueError(f"unknown sightline {sightline!r}; "
                         f"choose one of {sorted(SIGHTLINES)}")
    tau_any = SIGHTLINES[sightline][0]
    tau_ffp = tau_any * FFP_MASS_FRACTION

    # event rate per star: Gamma = (2/pi) * tau / tE  (standard relation
    # between optical depth and event rate for a single tE scale)
    rate_per_star_per_day = (2.0 / math.pi) * tau_ffp / FFP_TYPICAL_TE_DAYS
    events_per_year = n_stars * rate_per_star_per_day * DAYS_PER_YEAR

    return ProbabilityEstimate(
        n_stars=n_stars,
        sightline=sightline,
        tau_any=tau_any,
        tau_ffp=tau_ffp,
        p_any_lensing_now=_p_at_least_one(n_stars, tau_any),
        p_ffp_lensing_now=_p_at_least_one(n_stars, tau_ffp),
        ffp_events_per_year=events_per_year,
        years_per_ffp_event=math.inf if events_per_year == 0
        else 1.0 / events_per_year,
    )


def one_in(p: float) -> str:
    """Format a small probability as '1 in N' for humans."""
    if p <= 0:
        return "essentially zero"
    if p >= 0.5:
        return f"{p:.0%}"
    return f"about 1 in {round(1.0 / p):,}"
