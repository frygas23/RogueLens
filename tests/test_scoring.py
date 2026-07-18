"""Tests for roguelens.scoring -- do the heuristics rank things sensibly?

We test the *ordering*, not exact values: a clean event must outscore a
flat star and a periodic variable, and everything stays in [0, 100].
"""

from roguelens import demo_data, fitting, lightcurve_io, scoring


def _score(t, f, e):
    fit = fitting.fit_pspl(t, f, e)
    smooth = lightcurve_io.basic_stats(t, f)["smooth"]
    return scoring.score_candidate(t, f, e, fit, smooth)


def test_scores_stay_in_range():
    for label in demo_data.DEMO_CURVES:
        s = _score(*demo_data.make_demo_curve(label))
        assert 0 <= s.total <= 100


def test_clean_event_scores_high():
    s = _score(*demo_data.preset_event_curve("earth"))
    assert s.total >= 61


def test_flat_star_scores_low():
    s = _score(*demo_data.flat_star())
    assert s.total <= 30


def test_variable_star_scores_below_real_event():
    s_var = _score(*demo_data.variable_star())
    s_evt = _score(*demo_data.preset_event_curve("earth"))
    assert s_var.total < s_evt.total
    # a periodic signal must never look like a strong candidate
    assert s_var.total <= 80


def test_fit_improvement_withheld_for_bad_fits():
    # the variable star tricks the fit into one bump; the improvement
    # component must be heavily penalized by the residual-quality factor
    t, f, e = demo_data.variable_star()
    fit = fitting.fit_pspl(t, f, e)
    smooth = lightcurve_io.basic_stats(t, f)["smooth"]
    s = scoring.score_candidate(t, f, e, fit, smooth)
    pts, _ = s.components["Fit improvement over flat"]
    assert pts < 5.0


def test_verdict_bands():
    assert "Unlikely" in scoring.verdict_for(10)
    assert "Weak" in scoring.verdict_for(45)
    assert "Possible" in scoring.verdict_for(70)
    assert "Strong" in scoring.verdict_for(90)
