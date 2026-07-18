"""Tests for roguelens.probability and roguelens.detect."""

import math

import numpy as np
import pytest

from roguelens import detect, probability


# ------------------------------------------------------------ probability

def test_zero_stars_zero_probability():
    est = probability.estimate(0, "bulge")
    assert est.p_any_lensing_now == 0.0
    assert est.p_ffp_lensing_now == 0.0


def test_probability_grows_with_star_count():
    p_small = probability.estimate(100, "bulge").p_ffp_lensing_now
    p_big = probability.estimate(10_000, "bulge").p_ffp_lensing_now
    assert p_big > p_small > 0.0


def test_ffp_probability_below_any_lensing():
    est = probability.estimate(5000, "bulge")
    assert est.p_ffp_lensing_now < est.p_any_lensing_now


def test_bulge_denser_than_high_latitude():
    p_bulge = probability.estimate(1000, "bulge").p_any_lensing_now
    p_high = probability.estimate(1000, "high_latitude").p_any_lensing_now
    assert p_bulge > p_high


def test_small_probability_approximation():
    # for tiny p, P(>=1 of N) ~ N * p
    n, tau = 1000, probability.SIGHTLINES["bulge"][0]
    est = probability.estimate(n, "bulge")
    assert math.isclose(est.p_any_lensing_now, n * tau, rel_tol=1e-2)


def test_unknown_sightline_raises():
    with pytest.raises(ValueError):
        probability.estimate(100, "andromeda")


def test_one_in_formatting():
    assert "1 in" in probability.one_in(1e-6)
    assert probability.one_in(0.0) == "essentially zero"


# ---------------------------------------------------------------- detect

def _field_with_stars(positions, shape=(200, 200), seed=0):
    rng = np.random.default_rng(seed)
    img = rng.normal(20, 3, shape)
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    for (sx, sy) in positions:
        img += 120 * np.exp(-(((xx - sx) ** 2 + (yy - sy) ** 2) / (2 * 2.0 ** 2)))
    return np.clip(img, 0, 255)


def test_detects_planted_stars():
    truth = [(40, 60), (120, 150), (170, 30), (90, 90)]
    stars = detect.detect_stars(_field_with_stars(truth))
    assert len(stars) == len(truth)
    found = {(round(s.x), round(s.y)) for s in stars}
    assert found == set(truth)


def test_empty_field_finds_nothing():
    stars = detect.detect_stars(_field_with_stars([]))
    assert len(stars) == 0


def test_brightest_star_comes_first():
    truth = [(50, 50), (150, 150)]
    img = _field_with_stars(truth)
    yy, xx = np.mgrid[0:200, 0:200]
    img += 100 * np.exp(-(((xx - 150) ** 2 + (yy - 150) ** 2) / (2 * 2.0 ** 2)))
    stars = detect.detect_stars(np.clip(img, 0, 255))
    assert (round(stars[0].x), round(stars[0].y)) == (150, 150)


def test_rejects_non_2d_input():
    with pytest.raises(ValueError):
        detect.detect_stars(np.zeros((4, 4, 3)))
