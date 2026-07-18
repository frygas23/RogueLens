import csv
import math

import numpy as np
import pytest

from roguelens.io import save_light_curve_csv
from roguelens.model import (
    estimate_fwhm_days,
    event_summary,
    flux_to_delta_magnitude,
    lens_source_separation,
    light_curve,
    point_lens_magnification,
)
from roguelens.physical import angular_einstein_radius_mas, einstein_radius_au, einstein_time_days


def test_separation_reaches_u0_at_t0():
    times = np.array([-1.0, 0.0, 1.0])
    u = lens_source_separation(times, u0=0.2, t0=0.0, t_e=1.0)
    assert math.isclose(u[1], 0.2)
    assert u[0] > u[1]
    assert u[2] > u[1]


def test_magnification_is_large_for_small_u_and_near_one_for_large_u():
    small = point_lens_magnification(np.array([0.1]))[0]
    large = point_lens_magnification(np.array([100.0]))[0]
    assert small > 5.0
    assert large == pytest.approx(1.0, rel=1e-4)


def test_light_curve_peak_occurs_near_t0():
    times = np.linspace(-2.0, 2.0, 401)
    result = light_curve(times, u0=0.1, t0=0.0, t_e=0.5)
    peak_time = result.time_days[result.flux.argmax()]
    assert abs(peak_time) < 0.02


def test_delta_magnitude_is_negative_when_flux_increases():
    dm = flux_to_delta_magnitude(np.array([1.0, 2.0]), baseline_flux=1.0)
    assert dm[0] == pytest.approx(0.0)
    assert dm[1] < 0.0


def test_event_summary_contains_reasonable_values():
    times = np.linspace(-3.0, 3.0, 601)
    result = light_curve(times, u0=0.2, t0=0.0, t_e=1.0)
    summary = event_summary(result)
    assert summary["peak_magnification"] > 1.0
    assert summary["max_brightening_magnitude"] > 0.0
    assert summary["estimated_fwhm_days"] > 0.0
    assert estimate_fwhm_days(result) == pytest.approx(summary["estimated_fwhm_days"])


def test_einstein_time_scales_with_square_root_of_mass():
    t1 = einstein_time_days(lens_mass_earth=1.0)
    t4 = einstein_time_days(lens_mass_earth=4.0)
    assert t4 == pytest.approx(2.0 * t1, rel=1e-6)


def test_physical_scales_are_positive():
    assert einstein_radius_au(lens_mass_earth=1.0) > 0.0
    assert angular_einstein_radius_mas(lens_mass_earth=1.0) > 0.0


def test_csv_export_writes_expected_columns(tmp_path):
    times = np.linspace(-1.0, 1.0, 11)
    result = light_curve(times, u0=0.2, t0=0.0, t_e=1.0)
    output = save_light_curve_csv(result, tmp_path / "curve.csv")
    with output.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == ["time_days", "separation_u", "magnification", "flux", "delta_magnitude"]
    assert len(rows) == 12


def test_invalid_inputs_are_rejected():
    with pytest.raises(ValueError):
        lens_source_separation([0, 1], u0=0.0, t0=0.0, t_e=1.0)
    with pytest.raises(ValueError):
        lens_source_separation([0, float("nan")], u0=0.1, t0=0.0, t_e=1.0)
    with pytest.raises(ValueError):
        point_lens_magnification(np.array([0.0]))
    with pytest.raises(ValueError):
        light_curve([0, 1], source_flux=-1.0)
    with pytest.raises(ValueError):
        flux_to_delta_magnitude([1.0], baseline_flux=0.0)
