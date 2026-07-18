# Physics background

## The idea

Gravitational microlensing happens when a massive object passes close to the line of sight between an observer and a more distant star. The object's gravity bends the light from the background star. If the alignment is close enough, the background star appears temporarily brighter.

For a rogue planet, this is important because the planet itself may be too dim to see directly. Instead of observing the planet's light, we observe the planet's gravitational effect on another star's light.

## The simplified model

RogueLens uses the single-source, single-lens point model. The separation between the lens and the source is written as:

```math
u(t) = \sqrt{u_0^2 + \left(\frac{t - t_0}{t_E}\right)^2}
```

The magnification is:

```math
A(u) = \frac{u^2 + 2}{u\sqrt{u^2 + 4}}
```

This creates a smooth light curve with one peak. The peak occurs at `t0`, when the lens and source are closest in the sky.

## What the parameters mean

- `u0`: closest approach. Smaller `u0` gives a higher peak.
- `t0`: time of maximum magnification.
- `tE`: Einstein crossing time. Larger `tE` means a wider, longer event.
- `source_flux`: brightness of the background source star before lensing.
- `blend_flux`: extra constant light from nearby unresolved stars.

## Why mass matters

A larger lens mass produces a larger Einstein radius. If the relative speed is similar, a larger Einstein radius usually means a longer event duration. In the simplified physical helper, `tE` scales approximately with the square root of mass.

That is why a Jupiter-mass lens creates a wider event than an Earth-mass lens in the examples.

## What this project does not include yet

This version does not include:

- finite-source effects,
- binary lenses,
- parallax,
- real telescope cadence,
- real observational data,
- full parameter fitting.

Those are future improvements. The first goal is to understand the central idea clearly.
