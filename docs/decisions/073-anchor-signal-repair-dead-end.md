## ADR-073: Anchor-signal repair is not the lever for af-35 max-30-grey AA-halo drift

**Status:** Accepted
**Date:** 2026-06-26

## Context

ADR-060 shipped the plot-box border mask cleanup that closed three
quarters of the af-35 max-30-grey freq30M gap (p95 |d| 0.433 -> 0.113).
Its "Open" section deferred the remaining gap (mechanism 2: AA-halo
intermediate-band drift at col ~510) to a follow-up spike, on the
hypothesis that the y-anchor signal computed by `_compute_y_anchors`
was too noisy on permissive-HSV masks (3% two-ridge columns at the
time of probe S166) for the anchor-driven cost model to work.

Spike #1224 evaluated three candidates for repairing the anchor:

- **C1 seed_filter** — reject two-ridge column seeds whose smaller-y
  candidate sits in the top decile of all ridge y's (chart-title
  artifact proxy).
- **C2 smooth_fill** — window-median over the carry-filled anchor
  arrays (window 15 columns) to suppress single-seed outliers.
- **C3 iterative** — promote single-ridge columns within 30 px of the
  baseline anchor to seeds, then re-carry-fill.

Each candidate was measured under two af-35 anchor regimes
(production today = anchor OFF; per-lens Option 1 enable = anchor ON)
against the triplet protected by ADR-060: af-35 max freq30M (target),
ttartisan-50 + 7artisans (guards).

```
+-------------------------+----------+----------+----------+----------+
| cell                    | baseline | C1 seed  | C2 smooth| C3 iter  |
+-------------------------+----------+----------+----------+----------+
| Anchor regime: OFF (production today)                              |
|   af-35 max  freq30M    |  0.113   |  0.113   |  0.113   |  0.113   |
|   af-35 max  freq30S    |  0.005   |  0.005   |  0.005   |  0.005   |
|   ttartisan-50 max 30S  |  0.024   |  0.024   |  0.024   |  0.024   |
|   ttartisan-50 stop 30S |  0.011   |  0.026   |  0.011   |  0.012   |
|   ttartisan-50 stop 30M |  0.011   |  0.038   |  0.011   |  0.011   |
|   7artisans freq10S/M   |  0.052   |  0.052   |  0.052   |  0.052   |
| Anchor regime: ON (per-lens Option 1 override on max-30-grey)      |
|   af-35 max  freq30M    |  0.422   |  0.422   |  0.422   |  0.422   |
|   af-35 max  freq30S    |  0.344   |  0.344   |  0.344   |  0.344   |
|   (guards unchanged from OFF regime — override is af-35-scoped)    |
+-------------------------+----------+----------+----------+----------+
```

A second probe dumped the af-35 max-30-grey anchor signal under each
candidate. Two findings invert the spike's framing:

1. **The two-ridge ratio is 41.8%, not 3%.** S166's "3% two-ridge
   columns" measurement was taken before ADR-060's plot-box border
   strip landed. Stripping the col-516 contamination (180 grey px in
   a single vertical column) re-classifies most of the chart's
   permissive-HSV mask into two-ridge or three-plus-ridge columns
   (218 + 197 of 521). The anchor seeds are already plentiful.

2. **The seeds are clean.** Sampled across the chart width the
   baseline upper anchor sits at y=132-327 and the lower at y=189-419,
   matching the GT curve positions reported in S166 (M30 around
   y=290-330, S30 around y=410-420 at the right corner). All three
   candidates either match the baseline at sample columns or differ
   by <= 1 px on a single edge column.

The af-35 regression under anchor=ON is therefore **not produced by
broken seeds**. The mechanism is fundamental to the linear y-anchor
cost model on this chart: the AA-halo cluster at col ~510 sits in the
gap between the upper anchor (y~190 in midfield) and lower anchor
(y~240 in midfield). The `gamma * |y - anchor|` cost gradient pulls
each pass toward its own anchor band, and the halo cluster's y falls
closer to the upper anchor than the real M30 ridge does — so the
"closer to anchor" tie-break picks the wrong cluster, producing the
exact regression ADR-060 already documented.

A repaired anchor that points at the same band the broken anchor
already pointed at cannot fix the band-overlap problem.

## Decision

Anchor-signal repair is **not the lever** for the af-35 max-30-grey
freq30M AA-halo intermediate-band drift. The spike closes as a dead
end:

1. **The `EYE_READ_OVERRIDES[0]` hand-patch in `mtf-readings.test.ts`
   is declared permanent.** The (af-35, f/1.8, pos=12.6, freq=30M,
   expected=0.58) cell is the maintainer-eye-read M30 value at the
   chart's right-corner extrapolation region; it ships as the
   authoritative reading for that cell. The comment is updated to
   reflect that the extractor will not produce 0.58 on its own at this
   cell under any reasonable change to the anchor cost model, so this
   override stays.

2. **The remaining ~0.06 above the +/-0.05 calibration band on af-35
   max freq30M's frac=0.9 reading is accepted as the chart's
   irreducible error today.** It does not affect any committed lens
   data (the cell that shipped is the eye-read override).

3. **A future revisit is gated on a NEW failure mode**, not on this
   one resurfacing. The trigger condition for re-opening the anchor /
   ridge-DP question is "a second cohort lens surfaces an
   AA-halo-cluster failure at a measurable scale (p95 |d| > 0.10)
   AND the failure does not have a chart-edge eye-read override
   available." Until then the override carries the cell.

## Alternatives considered

| Alternative                                                                                                                        | Result                                                                                                                                                                                                                                                                                                                                           |
| ---------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Ship C1 seed_filter under anchor=OFF.**                                                                                          | No-op on af-35 (anchor isn't consulted) and a regression on ttartisan-50 stopped freq30S/30M (0.011 -> 0.026 / 0.038). C1's top-decile threshold filters legitimate stopped-aperture seeds. Net: pure loss.                                                                                                                                      |
| **Ship C2 smooth_fill or C3 iterative under anchor=OFF.**                                                                          | No-op on every cell measured. They modify a signal nothing reads in the production code path; under anchor=ON they still produce the same 0.422 regression because the band-overlap geometry is independent of seed quality.                                                                                                                     |
| **Enable anchor=ON per-lens for af-35 max-30-grey AND ship one of C1/C2/C3.**                                                      | Catastrophic regression on the target chart (0.113 -> 0.422 freq30M; 0.005 -> 0.344 freq30S). None of the candidates fixes the band-overlap problem at the cost-model level.                                                                                                                                                                     |
| **Tackle mechanism 2 by changing the cost model itself** (S166's "stay-in-band" / "penalize ridges between own and other anchor"). | Out of scope for this spike — the spike scope was anchor _signal_ repair, not cost-model redesign. Filed forward as a YAGNI deferral: the change is justifiable only when a second cohort lens surfaces a measurable failure, since today af-35 is the only lens that lands in this regime and the override already carries the shipped reading. |
| **Drop the `EYE_READ_OVERRIDES[0]` entry and emit None at the chart's faded right edge.**                                          | Rejected for the same reasons ADR-060 already weighed: the eye-read GT carries the maintainer's extrapolation of the curve's last visible value, which is the value that ships. The extractor honestly emitting None and then sister-fallback filling from S30=0.12 produces a worse reading than the override.                                  |

## Consequences

### Positive

- **Closes spike #1224 with measured data** rather than leaving the
  question open. Future sessions do not re-litigate seed-repair
  options.
- **Confirms ADR-060's framing was correct**: mechanism 2 needs a
  cost-model change, not a signal change.
- **Re-anchors the YAGNI revisit trigger** for any future anchor /
  ridge-DP work to a concrete observable event (a second cohort
  lens), preventing speculative refactors of `_compute_y_anchors`.

### Negative

- The af-35 max freq30M frac=0.9 reading remains ~0.06 above the
  +/-0.05 band. The aggregate `max |d|` from `mtfdigitizer.calibrate`
  is now driven by this cell (0.12 at time of writing). The
  underlying value is wrapped by the eye-read override at the
  position-12.6 cell, so the public site is unaffected; the
  calibration metric stays as the visible scar.

### Neutral

- `_compute_y_anchors` and its `_carry_fill` helper stay as-is.
  Future maintenance can rely on their current behaviour without
  worrying about an in-flight repair branch.
- The probe scripts used to produce these measurements
  (`probe_1224_anchor_repair.py`, `probe_1224_anchor_dump.py`) were
  throwaway and are deleted before this ADR's PR per the
  `base/core/quality.md` probe-script rule. Their findings live in
  this ADR and the spike's closing comment.
