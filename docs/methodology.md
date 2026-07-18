# Methodology

RogueLens is built around one educational question:

> How can an object that emits almost no light still reveal itself through gravity?

The answer explored here is gravitational microlensing. When a compact lens, such as a free-floating planet, passes close to the line of sight between Earth and a background star, the lens bends the star's light. To an observer, the star can briefly appear brighter.

## Model used

This project uses the point-source/point-lens approximation. It assumes:

- the background star is treated as a point source,
- the rogue planet is treated as a point-mass lens,
- the lens moves in a straight line at constant transverse velocity,
- there is only one lens and one source,
- the observed flux may include optional constant blended light,
- optional Gaussian noise can be added for a simple observational feel.

The lens-source separation is modeled as:

```math
u(t)=\sqrt{u_0^2+\left(\frac{t-t_0}{t_E}\right)^2}
```

The point-lens magnification is:

```math
A(u)=\frac{u^2+2}{u\sqrt{u^2+4}}
```

## Physical scale

The Einstein crossing time is estimated from the Einstein radius and the transverse velocity:

```math
t_E = \frac{R_E}{v_\perp}
```

The physical Einstein radius at the lens plane is approximated by:

```math
R_E = \sqrt{\frac{4GM}{c^2}\frac{D_L(D_S-D_L)}{D_S}}
```

This allows the examples to compare Mars-, Earth-, Neptune-, and Jupiter-mass rogue planet scenarios.

## What the project can show well

RogueLens is useful for showing that:

1. Smaller impact parameter means a taller brightness spike.
2. Larger lens mass usually means a longer event timescale.
3. Noise and blending make the clean theoretical curve harder to interpret.
4. Short planetary microlensing events can be difficult to catch observationally.

## What the project does not claim

This is not a discovery pipeline and does not analyze real survey data. It does not include finite-source effects, parallax, binary lenses, telescope cadence, detector systematics, Bayesian inference, or real event fitting. Those would be natural extensions after the educational model is understood.
