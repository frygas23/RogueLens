# Rogue Planets and Gravitational Microlensing

## Abstract

Rogue planets, also called free-floating planets, are planetary-mass objects that are not clearly bound to a host star. Because they do not shine like stars and may be extremely faint, they are difficult to detect directly. One of the most important methods for detecting them is gravitational microlensing: if a rogue planet passes close to the line of sight between an observer and a distant background star, the planet's gravity can bend and magnify the star's light. This produces a temporary brightening called a microlensing light curve. In this project, I built RogueLens, a Python simulator that models simple point-lens microlensing events. The project connects astrophysics, mathematics, and programming by showing how a few equations can generate observable signatures of otherwise invisible objects.

## 1. Introduction

When most people imagine a planet, they imagine a world orbiting a star. In that picture, the star provides light, heat, and a stable gravitational center. Rogue planets challenge that picture. They are planetary-mass objects drifting through space without a clear parent star. Some may have formed around stars and later been ejected through gravitational interactions. Others may have formed more directly from collapsing gas and dust, in a way somewhat closer to star formation but at much lower mass.

The existence of rogue planets matters because it tells us that planetary systems are not always calm or permanent. Planet formation can be violent. Young planets interact gravitationally, migrate, collide, scatter, and sometimes escape. If many rogue planets exist, they may carry information about how common unstable planetary systems are and how planets form in different environments.

The difficulty is that rogue planets are hard to see. A normal planet near a star can sometimes be detected by transits, radial velocity, direct imaging, or reflected light. A rogue planet has no bright host star and may emit very little radiation. Therefore, astronomers often need indirect methods. Gravitational microlensing is one of the strongest tools for this problem.

## 2. Basic idea of gravitational microlensing

General relativity tells us that mass curves spacetime. Light follows the geometry of spacetime, so a massive object can bend the path of light from a more distant object. In strong gravitational lensing, multiple images or arcs may be visible. In microlensing, the angular separation between the images is too small to resolve directly, but the total brightness of the background source changes over time.

For rogue planets, the lens is the planet and the source is a distant background star. If the alignment is close enough, the background star temporarily appears brighter. The event is short because the planet, Earth, and background star are all moving relative to each other. For planetary-mass lenses, the signal may last from hours to days, depending on the mass, geometry, and transverse velocity.

This is why microlensing is scientifically powerful but observationally difficult. The signal may happen only once and then disappear forever. Astronomers need repeated observations of dense star fields to catch enough events.

## 3. The point-lens model

RogueLens begins with the simplest useful model: a point source and a point lens. The angular lens-source separation is written in units of the Einstein radius:

```math
u(t)=\sqrt{u_0^2+\left(\frac{t-t_0}{t_E}\right)^2}
```

Here, `u0` is the minimum separation between the lens and the source, `t0` is the time of closest approach, and `tE` is the Einstein crossing time. The formula comes from the geometry of straight-line relative motion: the separation has one component from the closest approach and one component from motion along the trajectory.

The magnification is then:

```math
A(u)=\frac{u^2+2}{u\sqrt{u^2+4}}
```

When `u` is large, the magnification approaches 1, meaning the star appears close to its normal brightness. When `u` is small, the magnification increases. Therefore, the light curve forms a peak near `t0`.

## 4. Physical meaning of the Einstein time

The Einstein crossing time is not just a random parameter. It depends on the Einstein radius and the transverse speed:

```math
t_E=\frac{R_E}{v_\perp}
```

The physical Einstein radius at the lens plane can be estimated as:

```math
R_E=\sqrt{\frac{4GM}{c^2}\frac{D_L(D_S-D_L)}{D_S}}
```

This formula shows why mass matters. If the lens mass increases, the Einstein radius increases roughly as the square root of the mass. Therefore, more massive rogue planets usually produce longer events, assuming similar distances and speeds.

In RogueLens, this is used to compare Mars-, Earth-, Neptune-, and Jupiter-mass scenarios. The exact values should not be interpreted as predictions for a specific real event, but they help build intuition.

## 5. What the simulation shows

The first result is a clean microlensing light curve. The flux starts near a baseline level, rises to a peak near the closest alignment, and returns to baseline. The curve is symmetric because the model assumes straight-line motion and a single lens.

The second result compares different lens masses. The main visual change is the duration of the event. Larger masses create wider curves because the Einstein radius is larger. This helps explain why planetary microlensing events can be short and hard to catch.

The third result adds synthetic noise. This is important because real data are not perfectly smooth. Noise makes it harder to identify the event and estimate its parameters.

The fourth result changes the impact parameter `u0`. Smaller `u0` means closer alignment, which produces a higher magnification peak. This makes intuitive sense: better alignment means stronger lensing.

## 6. Limitations

RogueLens is intentionally simple. It does not include finite-source effects, parallax, binary lenses, real telescope cadence, detector systematics, or professional model fitting. It also does not use real observational data. These limitations are not hidden because they are part of the learning process. A good scientific model should be clear about what it includes and what it ignores.

For example, very low-mass lenses can create events where the finite size of the background star matters. Binary lenses can create complex caustic structures. Parallax can break some degeneracies by using Earth's orbital motion or observations from multiple locations. These are beyond the first version but could become future extensions.

## 7. Conclusion

Rogue planets are fascinating because they are physically real but observationally elusive. They may be common, but they are difficult to study because they are dark and isolated. Gravitational microlensing gives astronomers a way to detect them indirectly through their gravitational effect on background starlight.

Building RogueLens helped me understand that astrophysics is not only about looking at beautiful images. It is also about models, equations, assumptions, data, and interpretation. A short brightening in a light curve can contain information about an object that may otherwise be invisible. That is the main idea this project tries to capture.

## References for further reading

- NASA, *Unveiling Rogue Planets With NASA's Roman Space Telescope*.
- NASA Roman Space Telescope, *Microlensing*.
- Microlensing Source, *Point Lenses*.
- Bennett, D. P. (2009), *Detection of Extrasolar Planets by Gravitational Microlensing*.
- Johnson et al. (2020), *Predictions of the Nancy Grace Roman Space Telescope Galactic Exoplanet Survey II: Free-Floating Planet Detection Rates*.
