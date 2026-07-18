"""Tests for roguelens.fitting -- can we recover known parameters?"""

import numpy as np

from roguelens import demo_data, fitting
from roguelens.fitting import pspl_flux


def test_recovers_injected_parameters():
    rng = np.random.default_rng(1)
    t = np.linspace(0, 20, 500)
    true = dict(u0=0.2, t0=10.0, t_e=2.0, source_flux=1.0, blend_flux=0.2)
    f = pspl_flux(t, **true)
    e = 0.005 * np.ones_like(f)
    f = f + rng.normal(0, e)

    fit = fitting.fit_pspl(t, f, e)
    assert fit.success
    assert np.isclose(fit.params["t0"], true["t0"], atol=0.1)
    assert np.isclose(fit.params["t_e"], true["t_e"], rtol=0.15)
    assert np.isclose(fit.params["u0"], true["u0"], rtol=0.25)


def test_pspl_beats_flat_on_preset_event():
    t, f, e = demo_data.preset_event_curve("earth", seed=7)
    fit = fitting.fit_pspl(t, f, e)
    assert fit.success
    assert fit.chi2 < fit.chi2_flat
    assert fit.reduced_chi2 < 3.0


def test_flat_data_gives_small_improvement():
    t, f, e = demo_data.flat_star(seed=7)
    fit = fitting.fit_pspl(t, f, e)
    if fit.success:
        assert (fit.chi2_flat - fit.chi2) / len(t) < 1.0


def test_works_without_error_column():
    t, f, _ = demo_data.preset_event_curve("jupiter", seed=3)
    fit = fitting.fit_pspl(t, f, e=None)
    assert fit.success


def test_too_few_points_fails_gracefully():
    fit = fitting.fit_pspl(np.arange(5.0), np.ones(5), 0.01 * np.ones(5))
    assert not fit.success
    assert "enough" in fit.message.lower()
