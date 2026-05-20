# ADR-032: Use Diffraction MTF for Scoring and Display

**Status:** Accepted
**Date:** 2026-05-20

## Context

Sigma publishes two types of computed MTF charts for each lens:

- **Diffraction MTF** — ray tracing through the optical design plus the
  physical diffraction model of the aperture. This is what all other
  manufacturers (Fujifilm, Samyang, Tamron, etc.) publish as their
  standard MTF chart.
- **Geometrical MTF** — ray tracing only, with diffraction effects
  stripped out. Isolates lens design aberrations from the physics of
  the aperture opening.

Both are computed (simulated from the lens prescription), not measured
from a physical copy. We store both chart types in `docs/optical-specs/`
for reference, but need to decide which type to use for scoring and
display on the optical quality page.

## Decision

Use **diffraction MTF** exclusively for scoring and display.

Geometrical MTF charts are retained in `docs/optical-specs/` for
reference but are not used in `mtf-readings.ts` or any scoring logic.

## Alternatives considered

**Use geometrical MTF** — rejected because it is not comparable across
brands (no other manufacturer publishes it), and it ignores diffraction
which is a real physical constraint on resolution.

**Use both** — rejected because displaying two chart types per lens adds
complexity without actionable value for the target audience (beginners
evaluating lenses).

## Consequences

- All `mtf-readings.ts` entries use diffraction MTF values
- For Sigma primes: mtf-1 is diffraction, mtf-2 is geometrical — only
  mtf-1 is used for readings
- For Sigma zooms: mtf-1 (wide diffraction) and mtf-2 (tele diffraction)
  are used; mtf-3 and mtf-4 (geometrical) are ignored for scoring
- Cross-brand MTF comparisons are apples-to-apples since all
  manufacturers publish diffraction MTF
- Lab-measured MTF (LensTip, etc.) still takes precedence over any
  computed MTF per ADR-014
