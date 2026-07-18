# Technical review checklist

This file documents the second pass over the project. I wanted the repository to feel like a real student-built project rather than a single generated script.

## Code quality

- The core model is separated from plotting, presets, physical constants, and input/output helpers.
- The code uses small functions with docstrings instead of one long notebook cell.
- Inputs are validated: negative timescales, invalid separations, negative fluxes, and empty arrays are rejected.
- The project can be used from examples, from `main.py`, or as an installed command-line package.

## Physics quality

- The project clearly states that it uses the point-source/point-lens approximation.
- The equations are visible in the README and methodology notes.
- The physical timescale is not invented; it is connected to lens mass, distance, and transverse velocity through the Einstein radius.
- The limitations are explicit, so the project does not overclaim.

## Portfolio quality

- The README opens with a human motivation instead of only technical language.
- The repository includes plots, docs, examples, tests, and a CV description.
- The project has a `project_log.md`, which makes the work feel personal and traceable.
- The CV entry is specific and measurable.

## Next serious extension

The strongest future extension would be a small fitting module: generate synthetic observations, then recover `u0`, `t0`, and `tE` from the noisy data. That would turn RogueLens from a simulator into a mini data-analysis project.
