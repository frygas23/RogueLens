"""
RogueLens Demo: Microlensing Candidate Explorer
================================================

Streamlit front-end for RogueLens. Run from the project root:

    pip install -r requirements.txt
    streamlit run app.py

Pages:
  1. Data input        -- CSV, image sequence, or synthetic presets
  2. Light curve       -- raw / normalized / smoothed plots
  3. Model fit & score -- PSPL fit + honest 0-100 candidate score
  4. Single image      -- star detection + *statistical* rogue-planet
                          probability + hypothetical event simulation

The app never claims to detect or confirm a planet. The single-image
probability is a prior from Galactic statistics: the pixels of one
frame contain no microlensing information at all.
"""

import os
import sys

# make src/roguelens importable without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from roguelens import demo_data, detect, fitting, lightcurve_io, photometry, probability, scoring
from roguelens.model import light_curve
from roguelens.presets import PRESETS
from roguelens.fitting import pspl_flux

st.set_page_config(page_title="RogueLens Demo", page_icon="🔭", layout="wide")

DISCLAIMER = (
    "**This tool is for educational exploration only.** A high score does "
    "not confirm an exoplanet or rogue planet. Real microlensing detections "
    "require calibrated survey data, careful statistical analysis, and "
    "expert validation."
)

st.sidebar.title("🔭 RogueLens")
st.sidebar.caption("Microlensing Candidate Explorer")
page = st.sidebar.radio("Pages", [
    "1 · Data input", "2 · Light curve", "3 · Model fit & score",
    "4 · Single image explorer", "About"])
st.sidebar.divider()
st.sidebar.info(DISCLAIMER)


def _store_curve(t, f, e, source_label):
    st.session_state["t"] = np.asarray(t, float)
    st.session_state["f"] = np.asarray(f, float)
    st.session_state["e"] = None if e is None else np.asarray(e, float)
    st.session_state["source_label"] = source_label
    for key in ("fit", "score"):
        st.session_state.pop(key, None)


def _have_curve():
    return "t" in st.session_state


def _errorbar(ax, t, f, e):
    ax.errorbar(t, f, yerr=e, fmt="o", ms=3, color="#4a6fa5",
                ecolor="#b8c4d8", elinewidth=0.8, alpha=0.8, label="data")


# ---------------------------------------------------------------- page 1

if page == "1 · Data input":
    st.title("RogueLens Demo: Microlensing Candidate Explorer")
    st.markdown(DISCLAIMER)
    st.divider()

    tab_csv, tab_img, tab_demo = st.tabs(
        ["📄 CSV light curve", "🖼️ Image sequence (approximate)", "✨ Example data"])

    with tab_csv:
        st.markdown(
            "Upload a CSV with a **time** column and a **flux** column "
            "(a **flux_error** column is optional but recommended).")
        up = st.file_uploader("Light curve CSV", type=["csv"])
        if up is not None:
            try:
                t, f, e = lightcurve_io.load_light_curve_csv(up)
                _store_curve(t, f, e, f"CSV: {up.name}")
                st.success(f"Loaded {len(t)} points from **{up.name}**"
                           + ("" if e is not None else
                              " (no error column -- errors estimated from scatter)."))
            except lightcurve_io.LightCurveError as exc:
                st.error(str(exc))

    with tab_img:
        st.warning(
            "Image-based detection here is a **simplified educational "
            "approximation**, not real photometry: no calibration, no PSF "
            "fitting, no comparison stars. Time = frame number.")
        types = ["png", "jpg", "jpeg"]
        if photometry.HAS_FITS:
            types += ["fits", "fit", "fts"]
        imgs = st.file_uploader("Image frames (min 10, in time order by filename)",
                                type=types, accept_multiple_files=True)
        col1, col2, col3 = st.columns(3)
        use_center = col1.checkbox("Use image center", value=True)
        x = col2.number_input("x (pixels)", min_value=0.0, value=0.0, disabled=use_center)
        y = col3.number_input("y (pixels)", min_value=0.0, value=0.0, disabled=use_center)
        radius = st.slider("Aperture radius (pixels)", 2, 100, 15)
        if imgs and st.button("Extract light curve from images"):
            if len(imgs) < 10:
                st.error(f"Need at least 10 frames; got {len(imgs)}.")
            else:
                try:
                    ordered = sorted(imgs, key=lambda fp: fp.name)
                    t, f, e = photometry.extract_light_curve(
                        ordered, x=None if use_center else x,
                        y=None if use_center else y, radius=radius,
                        filenames=[fp.name for fp in ordered])
                    _store_curve(t, f, e, f"Images: {len(imgs)} frames")
                    st.success(f"Extracted brightness from {len(imgs)} frames.")
                except Exception as exc:
                    st.error(f"Photometry failed: {exc}")

    with tab_demo:
        st.markdown("Generate a synthetic light curve using the RogueLens "
                    "simulator and its physical presets:")
        choice = st.selectbox("Preset", list(demo_data.DEMO_CURVES.keys()))
        seed = st.number_input("Random seed", value=42, step=1)
        if st.button("Generate example data"):
            t, f, e = demo_data.make_demo_curve(choice, seed=int(seed))
            _store_curve(t, f, e, f"Preset: {choice}")
            st.success(f"Generated {len(t)} synthetic points.")

    if _have_curve():
        st.divider()
        st.markdown(f"**Current dataset:** {st.session_state['source_label']} "
                    f"({len(st.session_state['t'])} points). Continue to page 2.")

# ---------------------------------------------------------------- page 2

elif page == "2 · Light curve":
    st.title("Light curve visualization")
    if not _have_curve():
        st.info("Load some data on page **1 · Data input** first.")
    else:
        t, f = st.session_state["t"], st.session_state["f"]
        e = st.session_state["e"]
        if e is None:
            e = lightcurve_io.estimate_errors(f)
        stats = lightcurve_io.basic_stats(t, f)

        c1, c2, c3 = st.columns(3)
        c1.metric("Baseline flux (median)", f"{stats['baseline']:.4g}")
        c2.metric("Detected peak time", f"{stats['peak_time']:.4g}")
        c3.metric("Peak / baseline", f"{stats['peak_flux'] / stats['baseline']:.3f}×")

        fig, ax = plt.subplots(figsize=(8, 4))
        _errorbar(ax, t, f, e)
        if st.checkbox("Show smoothed curve", value=True):
            ax.plot(t, stats["smooth"], color="#e67e22", lw=1.5, label="smoothed")
        ax.axhline(stats["baseline"], color="gray", ls="--", lw=1, label="baseline")
        ax.axvline(stats["peak_time"], color="#27ae60", ls=":", lw=1.5, label="peak")
        ax.set(xlabel="time", ylabel="flux", title="Light curve")
        ax.grid(alpha=0.25); ax.legend(fontsize=8); fig.tight_layout()
        st.pyplot(fig)

        fig2, ax2 = plt.subplots(figsize=(8, 3.2))
        _errorbar(ax2, t, f / stats["baseline"], e / stats["baseline"])
        ax2.axhline(1.0, color="gray", ls="--", lw=1)
        ax2.set(xlabel="time", ylabel="flux / baseline", title="Normalized")
        ax2.grid(alpha=0.25); fig2.tight_layout()
        st.pyplot(fig2)

# ---------------------------------------------------------------- page 3

elif page == "3 · Model fit & score":
    st.title("Model fitting & candidate score")
    if not _have_curve():
        st.info("Load some data on page **1 · Data input** first.")
    else:
        t, f = st.session_state["t"], st.session_state["f"]
        e = st.session_state["e"]
        if e is None:
            e = lightcurve_io.estimate_errors(f)

        if st.button("Fit point-lens model", type="primary") or "fit" in st.session_state:
            if "fit" not in st.session_state:
                with st.spinner("Fitting..."):
                    fit = fitting.fit_pspl(t, f, e)
                    smooth = lightcurve_io.basic_stats(t, f)["smooth"]
                    st.session_state["fit"] = fit
                    st.session_state["score"] = scoring.score_candidate(
                        t, f, e, fit, smooth)
            fit = st.session_state["fit"]
            score = st.session_state["score"]

            if not fit.success:
                st.error(f"**The fit did not converge.** {fit.message}")
                st.markdown("If a simple point-lens model can't describe the "
                            "data at all, it is probably not microlensing-like.")
            else:
                st.subheader("Best-fit parameters")
                p, pe = fit.params, fit.param_errors
                st.table(pd.DataFrame(
                    [{"parameter": n, "value": f"{p[n]:.4g}",
                      "± uncertainty": f"{pe[n]:.2g}"} for n in p]))
                st.caption(f"χ² = {fit.chi2:.1f} (flat: {fit.chi2_flat:.1f}); "
                           f"reduced χ² = {fit.reduced_chi2:.2f}")

                st.subheader("Model vs. data")
                fig, ax = plt.subplots(figsize=(8, 4))
                _errorbar(ax, t, f, e)
                tt = np.linspace(t[0], t[-1], 1000)
                ax.plot(tt, pspl_flux(tt, **p), color="#c0392b", lw=2, label="PSPL model")
                ax.axvline(p["t0"], color="#27ae60", ls=":", lw=1, label="fitted t0")
                ax.set(xlabel="time", ylabel="flux"); ax.grid(alpha=0.25)
                ax.legend(fontsize=8); fig.tight_layout()
                st.pyplot(fig)

                fig2, ax2 = plt.subplots(figsize=(8, 2.8))
                _errorbar(ax2, t, fit.residuals, fit.errors_used)
                ax2.axhline(0, color="#c0392b", lw=1.5)
                ax2.set(xlabel="time", ylabel="data − model", title="Residuals")
                ax2.grid(alpha=0.25); fig2.tight_layout()
                st.pyplot(fig2)

            st.subheader("Candidate score")
            st.metric("Microlensing-likeness score", f"{score.total} / 100",
                      help="Heuristic educational score, NOT a probability.")
            st.progress(score.total / 100.0)
            st.markdown(f"**Verdict:** {score.verdict}")
            with st.expander("How the score breaks down (each part 0–20 points)"):
                for name, (pts, note) in score.components.items():
                    st.markdown(f"- **{name}: {pts:.1f} / 20** — {note}")

            st.subheader("Plain-English interpretation")
            if fit.success and score.total > 60:
                st.markdown(
                    "This light curve contains a single smooth brightening "
                    "event that is reasonably well described by a point-lens "
                    "microlensing model. **However, this demo cannot confirm "
                    "an exoplanet or rogue planet.** Real confirmation would "
                    "require survey data, calibration, comparison with "
                    "variable stars, telescope metadata, and expert validation.")
            elif fit.success and score.total > 30:
                st.markdown("The model fits to some degree, but one or more "
                            "properties are weak -- at best a low-priority "
                            "candidate in a real survey.")
            else:
                st.markdown("The data does not resemble a single point-lens "
                            "microlensing event (flat, periodic, or too noisy).")

            st.subheader("Limitations")
            st.markdown(
                "- Heuristic score, not a calibrated probability.\n"
                "- Simplest PSPL model only: no parallax, finite-source, or binary lenses.\n"
                "- Image-derived curves are uncalibrated relative brightness.\n"
                "- Many signals (novae, flares, variables, glitches) mimic a smooth bump.\n"
                "- Real surveys use years of data, statistics, and human review.")
            st.info(DISCLAIMER)
        else:
            st.markdown("Press **Fit point-lens model** to run the analysis.")

# ---------------------------------------------------------------- page 4

elif page == "4 · Single image explorer":
    st.title("Single image explorer")
    st.markdown(
        "Upload **one** image of the sky -- any place, any time. The app "
        "will count the star-like sources and answer the honest version of "
        "*\"is a rogue planet there?\"*")
    st.error(
        "**Why one image can never detect a rogue planet:** rogue planets "
        "emit no visible light, so an image contains zero photons from "
        "them. The only way to find one is microlensing -- a background "
        "star brightening and fading over hours or days. That is a change "
        "**in time**, and a single frame is a single moment. What we *can* "
        "compute is a **statistical prior**: given how many stars are in "
        "the frame and which direction it looks, how likely is it that "
        "some star is being lensed right now. That number comes from "
        "Galactic statistics, **not from the pixels** -- two different "
        "images with the same star count get the same answer.")

    up = st.file_uploader("Sky image (PNG/JPG"
                          + (", FITS)" if photometry.HAS_FITS else ")"),
                          type=(["png", "jpg", "jpeg"]
                                + (["fits", "fit", "fts"] if photometry.HAS_FITS else [])))
    if up is not None:
        data = photometry.load_image_gray(up, up.name)
        k = st.slider("Detection threshold (σ above background)", 3.0, 15.0, 5.0, 0.5)
        stars = detect.detect_stars(data, k_sigma=k)
        n = len(stars)

        col_img, col_prob = st.columns([3, 2])
        with col_img:
            fig, ax = plt.subplots(figsize=(6, 6 * data.shape[0] / data.shape[1]))
            ax.imshow(data, cmap="gray", origin="upper")
            if stars:
                ax.scatter([s.x for s in stars], [s.y for s in stars],
                           s=40, facecolors="none", edgecolors="#2ecc71", lw=0.8)
            ax.set_title(f"{n} star-like sources detected")
            ax.axis("off"); fig.tight_layout()
            st.pyplot(fig)
            st.caption("The detector marks local maxima above the noise. It "
                       "can't tell stars from galaxies or JPEG artifacts.")

        with col_prob:
            st.subheader("Statistical estimate")
            sight = st.selectbox(
                "Which direction does the image look?",
                list(probability.SIGHTLINES.keys()),
                format_func=lambda s: probability.SIGHTLINES[s][1])
            est = probability.estimate(n, sight)
            st.metric("P(some star lensed by *anything* right now)",
                      probability.one_in(est.p_any_lensing_now))
            st.metric("P(some star lensed by a **rogue planet** right now)",
                      probability.one_in(est.p_ffp_lensing_now))
            if np.isfinite(est.years_per_ffp_event):
                st.metric("Expected wait, watching this exact field 24/7,"
                          " for ONE rogue-planet event",
                          f"≈ {est.years_per_ffp_event:,.0f} years")
            st.caption(
                "Order-of-magnitude numbers based on measured microlensing "
                "optical depth (τ ~ 10⁻⁶ toward the bulge) and rough "
                "free-floating-planet abundances (uncertain by ≥10×). "
                "This is a prior, not a detection. It explains why surveys "
                "like OGLE monitor hundreds of millions of stars for years.")

        st.divider()
        st.subheader("What *would* it look like? (simulation)")
        st.markdown(
            "Pick a detected star and RogueLens will render a **hypothetical** "
            "rogue-planet event on it, using the project's own simulator. "
            "This is fiction on top of your real image -- a teaching tool.")
        if n == 0:
            st.info("No stars detected -- try lowering the threshold.")
        else:
            c1, c2 = st.columns(2)
            idx = c1.number_input("Star number (brightest = 0)", 0, n - 1, 0)
            preset_key = c2.selectbox(
                "Lens preset", list(PRESETS.keys()),
                format_func=lambda k_: PRESETS[k_].label)
            star = stars[int(idx)]
            preset = PRESETS[preset_key]
            te = preset.t_e_days

            times = np.array([-2.0, -1.0, 0.0, 1.0, 2.0]) * te
            result = light_curve(times, u0=preset.u0, t0=0.0, t_e=te)

            cols = st.columns(len(times))
            zoom = 40
            x0, x1 = int(max(star.x - zoom, 0)), int(min(star.x + zoom, data.shape[1]))
            y0, y1 = int(max(star.y - zoom, 0)), int(min(star.y + zoom, data.shape[0]))
            for col, t_i, a_i in zip(cols, times, result.magnification):
                frame = demo_data.inject_event_into_image(data, star.x, star.y, a_i)
                col.image(frame[y0:y1, x0:x1], clamp=True,
                          caption=f"t = {t_i:+.2g} d · A = {a_i:.2f}",
                          use_container_width=True)

            tt = np.linspace(-3 * te, 3 * te, 400)
            full = light_curve(tt, u0=preset.u0, t0=0.0, t_e=te)
            fig, ax = plt.subplots(figsize=(8, 3))
            ax.plot(tt, full.magnification, color="#c0392b", lw=2)
            ax.scatter(times, result.magnification, color="#27ae60", zorder=3)
            ax.set(xlabel="time (days)", ylabel="magnification A(t)",
                   title=f"Hypothetical {preset.label} event on star #{int(idx)} "
                         f"(t_e ≈ {te:.2g} d)")
            ax.grid(alpha=0.25); fig.tight_layout()
            st.pyplot(fig)
            st.warning("Simulated event -- nothing in the uploaded image "
                       "actually brightened. Real detection needs many "
                       "frames over time (see pages 1–3).")

# ---------------------------------------------------------------- about

else:
    st.title("About RogueLens")
    st.markdown("""
RogueLens is an educational simulator and candidate-exploration tool.
**It does not discover planets by itself.**

Gravitational microlensing happens when a massive object passes almost
exactly in front of a background star. Its gravity bends and briefly
magnifies the starlight, producing a smooth symmetric bump in the
star's light curve. Because the effect depends only on mass, it is one
of the very few ways to detect **free-floating ("rogue") planets** --
their events last only hours to a couple of days.

**What the app does:** simulates events (using physically derived
Einstein times for Mars/Earth/Neptune/Jupiter-mass lenses), fits the
point-lens model to uploaded data, computes a transparent 0–100
candidate score, and -- for a single image -- gives the *statistical*
probability that a rogue-planet event is happening among the visible
stars, while explaining why one frame can never detect one.

Made as a high-school astrophysics portfolio project.
""")
    st.info(DISCLAIMER)
