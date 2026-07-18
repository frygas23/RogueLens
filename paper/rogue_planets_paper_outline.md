# Rogue Planets: Formation, Detection and Microlensing

## Abstract draft

Rogue planets, also known as free-floating planets, are planetary-mass objects that are not clearly bound to a host star. Because they are faint and isolated, they are difficult to detect using direct light. One important detection method is gravitational microlensing, where the gravity of a foreground object temporarily magnifies the light of a background star. This paper introduces the idea of rogue planets, explains possible formation pathways, presents the basic point-lens microlensing model, and connects the theory to the RogueLens Python simulation.

## 1. Introduction

The search for exoplanets usually focuses on planets orbiting stars. However, not all planets are necessarily attached to a stellar system. Some may drift through the galaxy as free-floating or rogue planets. These objects are scientifically interesting because they can tell us about planet formation, gravitational scattering, and the early history of planetary systems.

## 2. What are rogue planets?

A rogue planet is a planetary-mass object that moves through space without an obvious host star. It may have formed inside a planetary system and later been ejected, or it may have formed in a star-like way from a collapsing cloud of gas and dust.

## 3. Possible formation mechanisms

Possible mechanisms include:

- gravitational scattering between planets,
- disruption by a passing star,
- instability in young planetary systems,
- direct formation from small molecular cloud fragments.

## 4. Why they are hard to detect

A planet orbiting a star can often be detected because it affects the star's light or motion. A rogue planet has no bright host star, so ordinary detection methods are much harder. If the planet is cold and far away, it may emit very little radiation.

## 5. Gravitational microlensing

Microlensing uses gravity instead of ordinary light. When a rogue planet passes close to the line of sight to a background star, its gravity bends the star's light. To an observer, the background star temporarily appears brighter.

The point-lens model uses:

```math
u(t) = \sqrt{u_0^2 + \left(\frac{t - t_0}{t_E}\right)^2}
```

and

```math
A(u) = \frac{u^2 + 2}{u\sqrt{u^2 + 4}}
```

## 6. Connection to RogueLens

RogueLens implements this simplified model in Python. It generates light curves, estimates event duration from lens mass, and compares example scenarios such as Earth-mass and Jupiter-mass free-floating planets.

## 7. Limitations

The model is educational and simplified. Real microlensing analysis may require finite-source effects, parallax, binary-lens models, telescope cadence, blending, and statistical fitting.

## 8. Conclusion

Rogue planets are difficult to observe directly, but microlensing provides a way to detect their gravitational influence. RogueLens shows how a compact mathematical model can produce a realistic-looking astronomical light curve and helps connect astrophysical theory with computational simulation.
