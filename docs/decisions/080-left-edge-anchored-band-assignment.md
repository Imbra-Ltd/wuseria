# ADR-080: Left-edge anchored band assignment for multifreq ridge tracking

**Status:** Accepted
**Date:** 2026-07-08

## Context

The N-frequency ridge pipeline (ADR-075) assigned kept tracks to
frequency bands by slicing them, sorted by global mean y, into N
equal-count groups with the last group absorbing the remainder. That
rule assumes every frequency band kept the same number of tracks. The
Tier 1 maintainer ground truth (#1332) refuted the assumption on three
Zeiss Touit panels, quantified as #1385: on the 32mm k=4 and 50mm k=5.6
stopped panels the 10 lp/mm pair prints genuinely coincident (GT delta
<= 0.01), so five tracks carry six curves and the true band populations
are 1/2/2 — the equal split slices 1/1/3, files the dashed 20M under
freq40S (med |Delta| up to 0.164) and drops the real 40M entirely. On
the 50mm k=2.8 max panel the populations are 1/2/3 (coincident 10-pair
plus a fragmented 40-band) even though a full 2N tracks are kept, so a
kept-count trigger cannot detect the problem; every dotted-M assignment
slid one band down (freq10M med 0.096) and the 40-pair went ext-None
across the inner field.

An S209 probe dumped the kept-track composition on all six Touit
panels: the tracker itself recovers every resolvable curve correctly —
only the track-to-band assignment misfiles them. Two prior mechanisms
could not close the gap:

1. The #1347 interior k-means (`_assign_interior_anchored_bands`)
   clustered interior mean y unconditionally into N groups. Its
   min-SSE objective picks the wrong partition whenever a band's S/M
   spread exceeds the gap between adjacent bands — on the 50mm stopped
   panel it groups {10, 20S, 20M} together (SSE 326 vs 344.5 for the
   true split). Its `_interior_order_differs` guard encoded the
   equal split as safe for "true 1/1/3" stopped panels — a claim
   calibrated against the pre-#1332 extractor-seeded (circular) GT
   that maintainer GT now refutes.
2. The #1374 coverage-dashedness discriminator deliberately scopes to
   S/M labels within an already-correct band and leaves band identity
   untouched.

## Decision

Replace both the equal split and the #1347 interior k-means for
`interior_anchored_bands` profiles with `_assign_left_anchored_bands`
(`pipeline/ridge.py`), driven by two chart-physics invariants:

1. At u' = 0 sagittal and meridional MTF coincide, so the left plot
   edge shows exactly one curve anchor per frequency, and every
   continuous (solid) curve reaches it.
2. Frequency bands never cross — a lower-frequency curve stays above a
   higher-frequency one at every field position.

```
  tracks entering the left window     tracks entering mid-field
  (first 15% of plot width)           (dashes, dotted M, fragments)
            |                                   |
            v                                   v
  1-D k-means on left-window y        join the band whose nearest
  into k = N seed bands               member point at the entry
  (one anchor per frequency)          column is closest in y,
            |                         in entry-x order
            +-----------------+-----------------+
                              v
              bands map top->bottom to frequencies;
              within a band: _order_band_sm (#1374);
              >2 tracks -> keep 2 by coverage;
              1 track -> S only (coincident pair,
              sister-fill supplies M per B2)
```

Concrete rules:

1. Applies whenever `interior_anchored_bands` is set and at least N
   tracks are kept — unconditionally, not only when kept < 2N (the
   50mm max panel keeps 6 tracks yet needs 1/2/3).
2. Falls back to the equal split when fewer than N tracks reach the
   left window (no anchor per band).
3. The 2-frequency ridge families (Viltrox) do not set the flag and
   keep the equal split byte-identical.
4. `_interior_mean_y`, `_interior_order_differs`, and
   `_assign_interior_anchored_bands` are deleted; the left-anchor path
   subsumes the #1347 case (12mm max improves 53/66 -> 56/66 in-band).

## Alternatives considered

| Alternative                                                                               | Why rejected                                                                                                                                                                                                               |
| ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Keep the equal split, widen the ADR-079 emit gate                                         | Ships honest absence instead of recovered values; the extractor has the correct tracks — this is an assignment defect, not a data gap.                                                                                     |
| Unconditional interior k-means (#1347 mechanism)                                          | Min-SSE on interior mean y picks the wrong partition when a band's S/M spread exceeds the band gap (50mm stopped: SSE 326 vs 344.5).                                                                                       |
| Fused-track detection via solid-count anchoring (N full-coverage tracks = N solid curves) | Works on stopped panels but fails on the 50mm max panel, where the fragmented 40S solid has no full-coverage track.                                                                                                        |
| Per-column S/M discriminator (#1175) or DP-level curve-identity prior (#1174)             | Crossing-territory machinery, parked with probe-refuted signals on their original cohort; band identity is solvable from geometry alone without per-column ink analysis.                                                   |
| Within-band fragment merging (compose 40S from x-disjoint fragments)                      | Adds a second mechanism for marginal gain — the remaining 50mm max corner residuals are crossing cells (#1174/#1175 territory), not fragment losses. Revisit if a future chart loses whole in-band cells to fragmentation. |

## Consequences

- The six #1385 fields recover to med |Delta| 0.002–0.006 (from
  0.065–0.164); both stopped panels reach 66/66 in-band — the family's
  first 100% panels. Aggregate: 91.8% -> 96.3% in-band, p95 0.0755 ->
  0.0448 (calibration Run 9).
- The ADR-079 emit gate withholds 13 cells family-wide (was 69), all
  crossing/corner residuals documented in REFERENCE_SET.md §8/§11/§12.
- Coincident pairs are represented as a single-track band (S only) and
  reach the site through the existing sister-fill path — no new
  fabrication surface; the B2 honesty contract is unchanged.
- Any future N-frequency chart with coincident or fragmented curves
  inherits the assignment by setting `interior_anchored_bands`; the
  flag's name now denotes left-edge anchoring.
- The left window (15% of plot width) and entry probe (10 columns) are
  sized from the S209 probe across the six Touit panels (constants'
  comments in `pipeline/ridge.py` record the tolerance envelope).
