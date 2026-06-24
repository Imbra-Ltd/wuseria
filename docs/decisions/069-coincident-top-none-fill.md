# ADR-069: Extend coincident-top anchor to None high-freq cells

**Status:** Accepted
**Date:** 2026-06-24

## Prerequisites

This ADR extends **ADR-068 (coincident-top anchor for sister-filled
high-freq cells)**. ADR-068 overrides a sister-filled `freq{hi}{D}`
cell with the same-direction `freq{lo}{D}` value when the lower
curve sits at chart top (`lo >= 0.90`). The precondition that the
cell is **sister-filled** rules out the case where the higher-freq
skeleton is so completely buried that even sister fallback cannot
fire — the case #1277 surfaced on the 300mm reflex.

## Context

`samyang-300mm-f6-3-ed-umc-cs-reflex` publishes two MTF panels (max
and stopped) that show all four curves — 10S red, 10M pink, 30S
dark-grey, 30M light-grey — packed at MTF~1.0 across the entire
field. The dark/light grey 30 strokes are drawn coincident with the
brighter red/pink 10 strokes; visually only the 10 colours are
distinguishable, with maybe a single pixel of 30 grey showing
through at the curve edge.

The extractor produces this on the `max` panel:

```
pos  0.0mm  freq10S=0.98 freq10M=0.98 freq30S=1.00 freq30M=1.00   <- ADR-066 center
pos  1.4mm  freq10S=0.98 freq10M=0.98 freq30S=None freq30M=None
pos  2.8mm  freq10S=0.98 freq10M=0.98 freq30S=None freq30M=None
pos  4.2mm  freq10S=0.98 freq10M=0.98 freq30S=None freq30M=None
pos  5.6mm  freq10S=0.98 freq10M=0.98 freq30S=None freq30M=None
pos  7.0mm  freq10S=0.98 freq10M=0.98 freq30S=None freq30M=None
pos  8.4mm  freq10S=0.98 freq10M=0.98 freq30S=0.98 freq30M=0.98
pos  9.8mm  freq10S=0.98 freq10M=0.98 freq30S=0.98 freq30M=0.98
pos 11.2mm  freq10S=0.98 freq10M=0.98 freq30S=0.98 freq30M=0.98
pos 12.6mm  freq10S=0.98 freq10M=0.99 freq30S=0.98 freq30M=0.98
pos 14.0mm  freq10S=0.98 freq10M=0.98 freq30S=0.98 freq30M=0.98
```

The provenance SVG renders the polyline only where neither endpoint
is `None` (matches the B2 contract in `svg._polyline_segments`), so
the 30 curves visibly start at frac ~0.6 instead of the y-axis.

### Why ADR-068's anchor does not fire

ADR-068's gate is "sister-filled `freq{hi}{D}` cell + `freq{lo}{D}`
at the same frac >= 0.90". On the 300mm reflex:

- 30S skeleton: empty across frac 0.1..0.5 — no direct read.
- 30M skeleton: empty across frac 0.1..0.5 — no direct read either.
- Sister fallback cannot fill 30S from 30M (both are None) or
  vice versa.
- So the cells stay `None`, and ADR-068's pass skips them because
  it iterates over the sister-filled flag set.

The chart-top assumption ADR-068 codified ("when `lo >= 0.90`,
`hi` is essentially pinned at `lo`") holds identically here. The
only difference is the upstream extractor state — sister-filled vs
None — which is incidental to the physics.

### Cell-state matrix

The four states a `freq{hi}{D}` cell can land in after sister
fallback, against the state of the same-direction `freq{lo}{D}`:

```
                            freq{lo}{D} >= 0.90      freq{lo}{D} < 0.90
                            (chart top)              (curve diving)
                            ----------------------   ---------------------
hi: extracted               keep extracted value     keep extracted value
hi: sister-filled           ADR-068 override         keep sister value
hi: None                    *** this ADR ***         keep None
                                                     (curves diverge — no
                                                      safe inference)
```

ADR-069 fills the missing cell in the top-left quadrant.

## Decision

Extend `_apply_coincident_top_anchor` in
`tools/mtfdigitizer/pipeline/pipeline.py` to also fire on cells where
the current value is `None`, using the same lower-frequency anchor
mechanism. The override applies when:

1. The cell's current value is `None` (the new case) OR the cell was
   marked sister-filled by the prior pass (ADR-068's case).
2. The same-direction lower frequency `freq{lo}{D}` at the same frac
   reads `>= _COINCIDENT_ANCHOR_THRESHOLD` (0.90, unchanged).
3. The `(hi_field, lo_field)` pair passes the existing
   coincident-stroke gate: the minimum `|hi - lo|` across cells where
   both were genuinely extracted (neither None, neither sister-filled)
   AND `lo >= 0.90` is at or below `_COINCIDENT_ANCHOR_MAX_PAIR_DELTA`
   (0.05, unchanged).

```
direct ---> sister --> intra-interp --> coincident-top --> center-symmetry
extract     fallback   (#1254)          anchor (ADR-068   (ADR-066)
                                        +ADR-069)         S=M at frac=0.0
                                                          + 1.0 if both None
                                        fires when cell is
                                          sister-filled OR None
                                        AND lo >= 0.90
                                        AND pair gate passes
```

### Per-cell decision

For each `freq{hi}{D}` cell at frac `f`:

```
prev = samples[hi][f]
lo   = samples[lo][f]
if (prev is None or sister_filled[hi][f]) \
   and lo is not None and lo >= 0.90      \
   and pair_gate_passes(hi, lo):
    samples[hi][f] = lo
    coincident_anchor_count[hi] += 1
```

frac=0.0 is **NOT** skipped. The first draft of this ADR proposed
deferring to ADR-066 (S=M=1.0 at the optical axis) at the center
cell, on the theory that a physical guarantee beats an extrapolation.
That was wrong for two reasons:

1. **Physical invariant violation.** `freq{lo}{D}` on the 300mm
   reflex extracts at ~0.985 at center due to raster snap to the
   nearest pixel row. If ADR-066 fires for the high-freq curve
   while the low-freq sits at 0.985, then `freq30S = 1.0 >
freq10S = 0.985` — physically impossible (MTF is monotonically
   non-increasing in frequency).
2. **Visible polyline kink.** The rendered SVG draws a polyline
   between the cell at frac=0.0 and the cell at frac=0.1. If
   center reads 1.0 (ADR-066) and frac=0.1 reads 0.985 (ADR-069's
   anchor from lo), the polyline has a visible upward spike at the
   leftmost vertex — exactly the "missing segments" shape #1277
   set out to fix, just relocated. Continuity across the field is
   the user-visible deliverable.

Copying `lo` into `hi` at center keeps `hi <= lo` true and reads
continuously through frac=0.1. ADR-066's 1.0 anchor still fires for
center cells the pair gate or threshold rules out — it is not a
no-op, just no longer the winner here.

Tracking continues to use the existing
`ExtractedChart.coincident_anchor_count` field — no new accounting
column. The two cases (sister-filled override, None fill) share the
same counter because they share the same physical mechanism and
threshold.

### Why the pair gate still safely rules out wrong cases

The coincident-stroke gate measures the **minimum** `|hi - lo|` on
cells where both were genuinely extracted (neither None, neither
sister-filled) AND `lo >= 0.90`. When the gate passes, the chart has
at least one cell demonstrating that hi and lo touch at chart top
within 0.05 MTF — that is the chart artist's signal that the curves
are physically coincident in the top regime.

- **300mm reflex max:** hi and lo both extracted at frac 0.6..1.0
  with `|Δ| ≈ 0.00` across that range. Min |Δ| ≈ 0.00, well below
  0.05 — gate passes, anchor fires on None cells 0.1..0.5.
- **300mm reflex stopped:** same story.
- **samyang-85mm Tier 1 anchor:** the chart that motivated the
  pair gate in ADR-068. 10M pinned at 0.91, 30M legitimately at
  0.6, min |Δ| ≈ 0.29 across every clean cell. Gate vetoes the
  pair — neither sister-filled cells (ADR-068's case) nor any
  hypothetical None cells get anchored. Preserved behaviour.
- **samyang-12mm fisheye stopped (ADR-068's main case):** 10S and
  30S touch at top in the coincident region with min |Δ| ≈ 0.006.
  Gate passes, anchor fires on the sister-filled 30S cells in the
  middle of the field (unchanged).

The gate's logic does not need adjusting for None cells because it
already isolates the chart-top regime correctly. The decision rule
above just extends the per-cell precondition from "sister-filled"
to "sister-filled or None".

### Worked example — 300mm reflex max panel

| frac | freq10S | freq30S before   | freq30S after   |
| ---- | ------- | ---------------- | --------------- |
| 0.0  | 0.98    | 1.00 (ADR-066)   | **0.98** (←10S) |
| 0.1  | 0.98    | None             | **0.98** (←10S) |
| 0.2  | 0.98    | None             | **0.98** (←10S) |
| 0.3  | 0.98    | None             | **0.98** (←10S) |
| 0.4  | 0.98    | None             | **0.98** (←10S) |
| 0.5  | 0.98    | None             | **0.98** (←10S) |
| 0.6  | 0.98    | None             | **0.98** (←10S) |
| 0.7  | 0.98    | 0.98 (extracted) | 0.98            |
| 0.8  | 0.98    | 0.98 (extracted) | 0.98            |
| 0.9  | 0.98    | 0.98 (extracted) | 0.98            |
| 1.0  | 0.98    | 0.98 (extracted) | 0.98            |

The polyline now renders end-to-end across both panels. Identical
shape for freq30M (anchored from freq10M).

## Alternatives considered

1. **Lift the sister-filled requirement entirely; anchor any cell
   when `lo >= 0.90` and the pair gate passes.** Considered the
   simplest restatement of the rule. Rejected for a narrow safety
   margin: a cell the extractor _did_ successfully read carries
   ink-level evidence that overrides theoretical chart-top
   inference. The current "extracted wins" rule (ADR-068) is the
   right default — a cell read at 0.93 when lo reads 0.99 is a
   real, mild divergence the extractor saw, not noise to be
   smoothed over by the anchor. Restricting to None and
   sister-filled keeps the override scope narrow while still
   handling the 300mm-reflex shape.

2. **Synthesise a sister-filled state for None cells, then let
   ADR-068 fire unchanged.** Pre-fill `freq30S[f] = freq30M[f]`
   when 30M is also None... but it isn't, in this case. There is
   no value to pre-fill from. Equivalent in machinery to running
   the new fill directly; just a longer path with no benefit.

3. **Pre-fill missing high-freq cells from low-freq before sister
   fallback runs.** Move the coincident-top fill earlier in the
   pipeline so it feeds sister fallback. Rejected for ordering
   risk: sister fallback's logic assumes the high-freq skeleton
   either has ink or does not. Inserting synthesised values
   upstream could mask genuine extraction gaps that other
   pipeline stages currently surface.

4. **Loosen 30-mask V band to swallow coincident-stroke pixels.**
   Considered and rejected previously for ADR-068. Same problem
   here: any HSV adjustment that recovers ink in the coincident
   region also catches halo contamination elsewhere. The 300mm
   reflex Tier 1 anchor specifically depends on the current narrow
   30 bands surviving — over-broadening would crash the calibration
   aggregate.

5. **Per-chart hint flagging "coincident at top across full field".**
   A `coincident_full_field: true` flag on the `ReferenceChart`
   entry. Rejected for the same reason ADR-068 rejected per-chart
   hints: the pattern is chart-family-wide. The pair-gate +
   threshold already handles presence and absence naturally.

## Consequences

### Positive

- 300mm reflex max and stopped panels both render continuous 30S
  and 30M polylines from frac 0.0 → 1.0 in the provenance SVG.
  Review HTMLs (`*-mtf-max-review.html`, `*-mtf-stopped-review.html`)
  now show what the chart actually publishes instead of dropped
  segments.
- Other charts with the same shape (full-field coincident curves
  at chart top — typically high-quality long-tele primes / reflex
  designs) gain the same treatment automatically.
- Anchor count is observable: `coincident_anchor_count` includes
  the None-fill cells alongside the sister-fill overrides, so the
  production digitization log shows the full footprint of the
  anchor for any chart.
- Calibration aggregate stable: the 300mm reflex is itself the
  Tier 1 anchor for the coincident-stroke gate; the new fill on
  the same chart cannot regress that anchor by construction.
  Other Tier 1 / Tier 2 charts either have non-None 30 cells in
  the affected region (anchor change is no-op) or have lo < 0.90
  (anchor cannot fire).

### Negative / accepted tradeoff

- A chart where the high-freq curve genuinely sits below the
  low-freq curve at chart top BUT the extractor failed to capture
  it (returning None) will now be filled with the low-freq value,
  slightly overestimating. The pair gate is the safety: such a
  chart cannot have any cell where extractor-extracted `hi` and
  `lo` sit within 0.05 MTF of each other across the top regime,
  so the gate vetoes the pair. The risk is non-zero only on
  charts where (a) the gate-passing cells happen to coincide and
  (b) other cells genuinely diverge — but in that combination the
  anchor is anyway only filling the cells where the chart artist
  drew the two curves on top of each other, so the value is right
  for the right reason.
- One extra branch per cell in the anchor pass, no measurable
  overhead.

### Scope this ADR does NOT cover

- Cross-direction coincidence (anchoring `freq30S` from `freq10M`
  or `freq30M` from `freq10S`). S and M can legitimately diverge
  near chart top on some lenses; the same-direction restriction
  remains.
- Multi-cell smoothing across the boundary between anchored cells
  and natively-extracted cells. The 300mm reflex case has no
  measurable discontinuity (anchor value 0.98 ≈ first extracted
  value 0.98), but the general issue noted in ADR-068's scope
  section remains future work.
- Charts where the 30 skeleton is empty AND the 10 skeleton is
  also empty in the same region. No anchor available; cells stay
  None. The B4 center-axis physics anchor (ADR-066) handles only
  the single cell at frac=0.0.
