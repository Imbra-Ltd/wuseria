# ADR-084: Unified plot-box detection dispatch

**Status:** Accepted
**Date:** 2026-07-18

## Context

The digitizer ships four per-family plot-box detectors: Sigma
(`pipeline.plotbox.detect_sigma_plot_box`, #950), Samyang, TTartisan,
and Fuji (the top-level `*_plotbox.py` modules). ADR-064 formalized how
each detector is _named_ but deliberately left them per-brand, with
divergent signatures (a BGR array for Sigma, a path for the rest),
return types (a bare `PlotBox` vs a `<Brand>BoxResult`), and failure
modes (`ValueError`, a `<Brand>PlotBoxError`, or a None / sentinel
result). Every caller that wants a box must therefore know which brand
it is holding — the per-brand scaffolders each hard-code their own
detector.

Two gaps follow from having detectors but no router:

1. No single entry point tries detection and falls back to the
   hand-measured box. #1413's fidelity-neutral setup-automation goal
   (ADR-081 §3) wants one: a new brand whose chart shares an existing
   vendor's style should get detection for free (ADR-081 §5), and a
   family with no detector should still resolve its committed box
   through the same call.
2. The four detectors' own regression tests (added in #950) already pin
   detected-vs-committed accuracy per family; what is missing is the
   routing, fallback, and fail-loud behaviour as a tested surface.

Of the 11 style families in the reference set, five are covered by one
of the four detectors (Sigma; Samyang, which also covers the
`idealized-flat` template; TTartisan; Fuji), five carry a hand-measured
box but no detector (Tokina ×2, Viltrox, Zeiss, 7Artisans), and one —
`soft-multicurve-promo`, the deliberate out-of-band anchor — has
neither. A router must do the right thing for all three cases.

## Decision

Add `plotbox_detect.detect_plot_box(chart)`, a thin routing adapter over
the unchanged detectors, mirroring `family_profile.PROFILE_BY_STYLE`:

```
                chart.style_family
                        |
             _DETECTOR_BY_STYLE.get(family)
                  /              \
            detector found    no detector
                |                  |
           run detector       fall back to
            /        \        chart.plot_box
        success    raises /        |
           |       None     +------+------+
           |        |       |             |
      "detected"    +---> hand box?    no box
         box              (fallback)  (raise
                                       PlotBoxUnavailable)
```

1. `_DETECTOR_BY_STYLE` maps a style family to a detector adapter. It
   lists only validated mappings — Sigma, Samyang (plus `idealized-flat`,
   the Samyang 4-color template under a distinct family name, mirroring
   `PROFILE_BY_STYLE`), TTartisan, Fuji. An unproven mapping would let a
   wrong-but-non-raising box silently override the hand-measured one.
2. Each adapter normalizes its detector's result into a frozen
   `DetectedPlotBox` — the primary `PlotBox`, `source`
   (`"detected"` / `"fallback"`), the `detector` that ran, an optional
   `secondary_box` (Samyang's stopped panel), an optional
   `image_height_mm` (TTartisan, Fuji), and `notes`. Fuji's
   None / sentinel failure is normalized to a raised error inside its
   adapter, so a single except clause covers every detector.
3. On a detector failure or an unmapped family, fall back to
   `chart.plot_box` and record the reason in `notes`. When there is no
   hand-measured box either, raise `PlotBoxUnavailable` — never return a
   guessed box (ADR-081 §4, ADR-038 §4 B1).

The four detector modules and their ADR-064 surfaces are untouched. The
dispatch is read-only over the reference set, so routing a caller
through it changes zero committed output.

## Alternatives considered

| Alternative                                                           | Why rejected                                                                                                                                                                                                                               |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Force the four detectors into one common return type and signature    | Fights ADR-064, which deliberately keeps brand-specific extras (scheme, `image_height_mm`, secondary box); a rewrite risks the tested detectors for zero output gain. A normalizing adapter gets the shared surface without touching them. |
| A single generic detector across all families                         | Rejected by ADR-081's fidelity-first stance — a generic axis / gridline heuristic guesses where a per-family detector is exact, and the reproduction is the signature feature.                                                             |
| Leave detection per-brand in each scaffolder                          | Keeps the #1413 gap: no fallback path, no reuse-by-style for new brands, and the routing stays untested.                                                                                                                                   |
| Map only the four native families, leave `idealized-flat` on fallback | Under-routes a chart the Samyang detector reproduces exactly; `PROFILE_BY_STYLE` already treats it as Samyang, so the detector map should agree.                                                                                           |

## Consequences

| Consequence                    | Detail                                                                                                                                                                                                                    |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Output-neutral                 | New module plus one test file; no committed box changes. The four detector suites and the calibrate zero-delta gate remain the regression oracle.                                                                         |
| Single entry point             | `detect_plot_box(chart)` resolves a box for all 11 reference families — detect, fall back, or fail loud — the reuse layer ADR-081 §5 calls for.                                                                           |
| Fail-loud preserved            | A silent wrong box stays impossible: a detection failure with no hand-measured box raises rather than guessing.                                                                                                           |
| Detectors unchanged            | ADR-064 surfaces intact; this extends ADR-064's naming convention with a routing convention rather than superseding it.                                                                                                   |
| Not yet wired into scaffolders | The per-brand scaffolders still call their detector directly; routing them through the dispatch — and reusing it for the next brand that shares a style — is a follow-up, deliberately out of this output-neutral change. |
