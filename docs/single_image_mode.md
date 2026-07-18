# Single Image Explorer: what it does and what it honestly can't

## The question this page answers

"Can I upload one picture of the sky and find out if a rogue planet is
there?" -- the most natural question anyone asks about this project.
The honest answer has two parts.

## Part 1: why one image can never detect a rogue planet

- A rogue planet emits essentially no visible light. In any image, the
  number of photons coming from it is zero. There is literally nothing
  in the pixels to find.
- The only practical way to detect one is **gravitational
  microlensing**: the planet's gravity briefly magnifies a background
  star, which brightens and fades over hours to days.
- That is a change **in time**. A single frame is a single moment --
  one point of a light curve. From one point you cannot tell whether a
  star is "brightening" or simply always looks like that.
- This is not an engineering limitation that a better algorithm could
  fix. It is information theory: the signal is temporal, and one frame
  contains no temporal information.

Even professional surveys (OGLE, MOA, KMTNet, and NASA's upcoming Roman
mission) cannot detect a rogue planet from one image. They photograph
the same fields thousands of times over years.

## Part 2: the probability we CAN honestly compute

What one image *does* tell us is **how many stars** are in the field.
Combined with Galactic statistics, that gives a **prior probability**
that a microlensing event is happening among them right now:

- The microlensing **optical depth** τ is the measured probability that
  a random background star is inside some lens's Einstein radius at a
  random moment. Toward the Galactic bulge, surveys find τ of order
  10⁻⁶ -- about one star in a million is measurably lensed at any
  instant. Away from the bulge τ is far smaller.
- τ scales with the total lens **mass** along the line of sight
  (τ ∝ Σ θ_E² ∝ Σ M). Free-floating planets are light, so even with a
  few of them per star their share of τ is only of order 10⁻³ -- a
  number uncertain by at least an order of magnitude, since the FFP
  abundance itself is an open research question.
- For N detected stars:
  P(at least one lensed now) = 1 − (1 − τ)^N ≈ N·τ for small τ.
- Converting the instantaneous probability to an **event rate** with
  Γ ≈ (2/π)·τ/t_E and a typical FFP crossing time of ~0.5 days gives
  the expected waiting time for one event in this exact field.

### Worked example

A bulge image with 1,200 detected stars:

- P(some star lensed by anything right now) ≈ 1 in 400
- P(some star lensed by a rogue planet right now) ≈ 1 in 400,000
- Expected wait for one rogue-planet event, watching this field
  continuously: **on the order of a thousand years**.

That last number is the whole story of why microlensing surveys monitor
*hundreds of millions* of stars: multiply N by 100,000 and the waiting
time drops to a few events per year.

## The crucial caveat

This probability is a **prior**. It depends only on the star count and
the assumed direction -- **not on the pixels**. Two completely different
images with the same number of stars get the same answer. The page says
this explicitly, because pretending the number came from analyzing the
image content would be exactly the kind of dishonesty this project was
designed to avoid.

## The simulation panel

The page also lets you pick a detected star and renders what a
hypothetical rogue-planet event **would** look like on it: five frames
at t = −2t_E … +2t_E with the star's light scaled by the point-lens
magnification A(t), plus the corresponding light curve from the
RogueLens simulator. The injected "star" uses an assumed Gaussian PSF,
so this is a visualization, not photometry -- and the UI labels it as
fiction on top of the real image.
