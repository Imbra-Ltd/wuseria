# ADR-055: Crossing detector — candidate-walk, both-reverse verdict

**Status:** Accepted
**Date:** 2026-06-15

## Context

PR #1173 (S150) added `_detect_and_swap_at_crossings` as a post-DP
fix-up for #1170 — when two physical curves cross monotonically in
MTF space, the DP follows y-bands rather than curve identity, so each
output track inherits the OTHER curve's slope past the crossing.

The S150 implementation had two specific design choices:

1. **Greedy global-min** column selection — pick the single column
   where `|y_a - y_b|` is smallest across the shared range.
2. **Exactly-one-reverses** verdict — fire the swap iff exactly one
   track's y-slope reverses sign across the candidate column.

The S150 closing memory recorded that PR #1173 did not fix the in-
the-wild af-75 stopped freq30 case it targeted. The hypothesis at
session close was "DP paths stay in distinct y-bands end-to-end —
the V-detector physically cannot fire on this chart." The S151 spike
opened with two alternative paths (Path A: DP-level curve-identity
prior; Path B: per-column S/M from raw-mask continuity).

### S151 probe findings

A direct column-by-column dump of the DP output on the af-75 stopped
freq30 orange mask (`probe_1170_dp_trajectories.py`) showed the
hypothesis was wrong:

```
af-75 stopped-30-orange DP output  (cols 232–597, common range)
 col 232  t1=161.0  t2=163.5   dy= 2.5    <-- left-edge convergence
 col 357  t1=167.5  t2=194.5   dy=27.0
 col 471  t1=192.0  t2=229.5   dy=37.5
 col 503  t1=206.0  t2=223.0   dy=17.0
 col 516  t1=213.5  t2=216.5   dy= 3.0    <-- mid-plot V-crossing
 col 532  t1=206.5  t2=223.5   dy=17.0
 col 562  t1=191.5  t2=244.5   dy=53.0
 col 597  t1=204.0  t2=355.0   dy=148.5
```

There IS a clean sub-threshold convergence at col 516. The greedy
global-min detector picked col 232 first (dy=2.5) and rejected: at
col 232 track_b has no left-side history, so `_local_slope` returns
None and the detector exits.

Slope analysis at col 516 under `_CROSSING_SLOPE_WINDOW=10`:

```
                  pre      post
track_a (t1)   +0.589    -0.642   <-- reverses
track_b (t2)   -0.533    +0.600   <-- reverses
```

BOTH tracks reverse sign. Under the S150 "exactly one reverses" rule
this is also a no-fire. But geometrically, both-reverse is the
correct signature for two monotonic physical curves crossing in a
band-following DP: each output track inherits the OTHER curve's
slope past the crossing, which by definition has opposite sign on
both. The "exactly one reverses" rule modelled a single curve that
dives and comes back up — a shape that does not occur on actual MTF
chart data.

Probe also evaluated Paths A and B directly:

| Path                                   | Result                                                                                                                                                                                               |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A — slope-stability prior**          | af-75 t1=0.82 t2=0.78; tilt-50 t1=0.70 t2=0.84 — the more-stable track flips between bug case and control, so slope stability cannot serve as the curve-identity discriminator.                      |
| **B — per-column raw-mask continuity** | 40 sign flips in 248 cols (16% noise rate). Raw orange mask densities are 1–3 px hits for both tracks at almost every column — solid vs dashed are indistinguishable at the available stroke widths. |

Neither A nor B is viable on this data. The correct fix lives at the
detector level.

## Decision

Rewrite `_detect_and_swap_at_crossings` with three surgical changes:

1. **Candidate-walk over local minima.** Find every column where dy
   falls below `_CROSSING_DY_THRESHOLD`, collapse same-region runs to
   the leftmost minimum, then walk left-to-right. For each candidate,
   compute the verdict; the first candidate where the verdict is
   `True` is the crossing. Candidates where any slope fit is `None`
   (insufficient history) are skipped, not treated as a hard exit.

2. **Both-reverse verdict.** A monotonic crossing between two physical
   curves produces band tracks that BOTH reverse slope. The detector
   fires when both tracks reverse with magnitude above
   `_CROSSING_SLOPE_MIN_MAGNITUDE`. Neither-reverses (synthetic
   tilt-50 X passing-through, or real tilt-50 freq30 which never
   re-converges past the left edge) leaves the assignments untouched.

3. **Swap LEFT of the crossing, not right.** S150 swapped right-of-
   crossing assignments. The S151 cross-check against the in-the-wild
   af-75 chart AND the 50/1.2 Tier 1 anchor showed the bug is on the
   PRE-crossing side: downstream S/M labelling is coverage-based, so
   the higher-coverage track gets the "solid" (S) label, but on
   af-75 stopped freq30 the physical S curve dives heavily through
   midfield and the heavy-dive track has LOWER coverage. The label
   ends up correct post-crossing (track that becomes upper after the
   crossing IS the rebounding S curve) and inverted pre-crossing.
   Swapping left-of-crossing applies the correction where it's
   needed.

```
                        common columns
 +------------------------------------------------+
 |                                                |
 | dy  ___                       ___              |
 |    /   \____                 /   \             |
 |   /          \              /     \____        |
 |  /            \____________/                   |
 +----+-------------+--------+-------+-----------+
      ^             ^        ^       ^
      col 232       col 278  col 516 (verdict True)
      verdict None  False    fires here
      (no b_pre)    (sub-thr,
                    only one
                    reverses)
```

`_CROSSING_DY_THRESHOLD`, `_CROSSING_SLOPE_WINDOW`, and
`_CROSSING_SLOPE_MIN_MAGNITUDE` retain their existing values from
#1173 — the S151 probe data is consistent with them.

### Why not Path A or Path B

Path A and Path B are documented in this ADR because the S150 close
memory framed them as the natural follow-ups. The probe data shows
both lack signal on the targeted chart:

- **Path A** would require a discriminator distinguishing "true" from
  "swapped" curve identity per track. Slope-stability across the
  field looked plausible but inverted between bug case and control.
- **Path B** would require solid-vs-dashed to be visible at each
  column in the raw mask. The orange-channel mask is too sparse for
  this — the dashed and solid strokes both yield 1–3 px of ink in a
  ±3 px window.

Either could come back in scope on a future chart where the both-
reverse + candidate-walk fix here fails. Follow-up issues capture
that contingency.

## Alternatives considered

- **Keep #1173's greedy global-min + exactly-one-reverses.** Fails
  on real af-75 data. The whole reason for this ADR.
- **Path A — DP-level curve-identity prior.** Probe shows slope
  stability is not a reliable discriminator. Deferred via follow-up
  issue.
- **Path B — per-column S/M via raw-mask continuity.** Probe shows
  raw orange-mask density is too sparse to separate solid from
  dashed. Deferred via follow-up issue.
- **Raise `_CROSSING_DY_THRESHOLD` from 8 to ~20 px.** Considered to
  catch the af-75 col-471–532 near-X plateau. Rejected: would also
  fire on charts where two parallel curves run within 10–20 px end-
  to-end without crossing, producing false swaps. The candidate-walk
  - both-reverse fix is more discriminating and doesn't need a
    threshold change.

## Benchmark

Direct probe of `_detect_and_swap_at_crossings` on the cohort:

| Slug                                        | Sub-thr candidates | Fired?  | Result                     |
| ------------------------------------------- | ------------------ | ------- | -------------------------- |
| `ttartisan-af-75mm-f2-0` (stopped freq30)   | cols 232, 278, 516 | col 516 | Real swap fires (bug case) |
| `ttartisan-tilt-50mm-f1-4` (stopped freq30) | cols 111, 162      | no      | No spurious swap (control) |

End-to-end `extract_chart` comparison against baseline production logs
and EYE truth where present:

| Slug                                            | Pass    | Field                  | Baseline                  | EYE  | New       | Delta                    |
| ----------------------------------------------- | ------- | ---------------------- | ------------------------- | ---- | --------- | ------------------------ |
| `ttartisan-af-75mm-f2-0`                        | stopped | freq30S corner         | 0.81                      | —    | 0.81      | 0                        |
| `ttartisan-af-75mm-f2-0`                        | stopped | freq30S midfield (0.5) | 0.86                      | —    | 0.78      | **fixed** (was inverted) |
| `ttartisan-af-75mm-f2-0`                        | stopped | freq30M midfield (0.5) | 0.78                      | —    | 0.85      | **fixed** (was inverted) |
| `ttartisan-af-75mm-f2-0`                        | max     | (all)                  | unchanged                 | —    | unchanged | 0 regressions            |
| `ttartisan-tilt-50mm-f1-4`                      | stopped | freq30S 0→1            | 0.74→0.27                 | —    | 0.74→0.27 | identical                |
| `ttartisan-tilt-50mm-f1-4`                      | stopped | freq30M 0→1            | 0.74→0.74                 | —    | 0.74→0.74 | identical                |
| `ttartisan-tilt-50mm-f1-4`                      | max     | (all)                  | unchanged                 | —    | unchanged | 0 regressions            |
| `ttartisan-50mm-f1-2`                           | stopped | freq30S corner         | 0.70                      | 0.84 | 0.84      | **fixed** (matches EYE)  |
| `ttartisan-50mm-f1-2`                           | stopped | freq30M corner         | 0.84                      | 0.70 | 0.70      | **fixed** (matches EYE)  |
| `ttartisan-50mm-f1-2`                           | max     | (all)                  | unchanged                 | —    | unchanged | 0 regressions            |
| `ttartisan-7-5mm-f2-0-fisheye`                  | both    | (all)                  | unchanged                 | —    | unchanged | 0 regressions            |
| `fujifilm-gf-23mm-f4` / `fujifilm-xf-23mm-f1-4` | (all)   | —                      | not on this dispatch path | —    | unchanged | not applicable           |

The 50/1.2 anchor fix was discovered during the benchmark and is a
beneficial side-effect — the same identity-inversion bug existed
there too, hidden by missing eye-reads on the corner sample.
mtfdigitizer pytest: 381 passed (was 378 at S150 close + 3 new tests).

## Consequences

- The S150 V-detector unit test (synthetic geometry with one curve
  reversing inside itself) was geometrically inconsistent with how
  real curves cross. Replaced with a test that models the actual
  both-monotonic crossing geometry.
- Three new tests cover the candidate-walk logic: left-edge cluster
  skip, multiple candidates take the first valid one, no sub-
  threshold convergence returns inputs unchanged.
- Path A and Path B remain available as future fallbacks if a chart
  surfaces where both-reverse + candidate-walk does not suffice.
  Captured as follow-up spike issues for paper trail.
- No change to `_RIDGE_DP_*` constants or to `dp_y_anchor` opt-in;
  the fix is downstream of the DP itself.
