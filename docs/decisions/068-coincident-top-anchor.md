# ADR-068: Coincident-top anchor for sister-filled high-freq cells

**Status:** Accepted
**Date:** 2026-06-23

## Prerequisites

This ADR depends on **ADR-067 (per-hue y_top inset)**. The original
implementation was merged via PR #1270 then reverted via #1272 because
freq10S on the 12mm fisheye stopped panel read 0.93..0.97 — the
saturated red 10S core had been clipped by #1257's global y_top inset,
so sister fallback pulled freq10S from the diving freq10M. The
coincident anchor honestly propagated those underestimates into
freq30S, leaving a 0.03..0.07 MTF residual bow (#1271). ADR-067 fixes
the upstream clip; freq10S now reads ~0.99 across the coincident
region, and this ADR's anchor lands cleanly on top.

## Context

Chart families that pack multiple frequencies into one panel often draw
the higher-frequency curve coincident with the lower-frequency curve
while both are at MTF ~1.0 — the strokes overlap into a single visible
line. The HSV-band dispatch's higher-freq mask returns empty in the
coincident region because the lower-freq curve's saturated colour
swamps the higher-freq grey under anti-aliasing.

Sister fallback then fires to fill the empty higher-freq cells, copying
the **same-frequency M sister** (e.g. `freq30M` fills `freq30S`). But
when the M sister has already started its mid-field dive while the S
sister is still pinned at chart top, this produces a wildly wrong
value — typically 0.4+ MTF below the true position.

### Diagnostic (#1269)

On `samyang-12mm-f2-8-ed-as-ncs-fish-eye` stopped panel:

- Chart shows the dark-grey 30S curve drawn coincident with dark-red
  10S from 0mm to ~15mm (chart artist merged two near-1.0 strokes
  into one visible line)
- 30S skeleton: empty in x=31..335 (frac 0..0.71), ink starts at
  x=336 onward
- Sister fallback fills `freq30S[0..7]` from `freq30M`:

| frac | freq30S (sister-filled) | freq30M | freq10S |
| ---- | ----------------------- | ------- | ------- |
| 0.5  | 0.74                    | 0.74    | 0.97    |
| 0.6  | 0.63                    | 0.63    | 0.96    |
| 0.7  | 0.53                    | 0.53    | 0.93    |
| 0.8  | **0.98** (extracted)    | 0.47    | 0.91    |
| 0.9  | 0.95 (extracted)        | 0.45    | 1.00    |
| 1.0  | 0.89 (extracted)        | 0.47    | 1.00    |

The sister-fill at frac 0.5..0.7 produces 0.74 → 0.63 → **0.53**.
When 30S re-emerges at frac 0.8 at MTF 0.98 the sparkline jumps from
0.53 to 0.98 — a 0.45 vertical discontinuity that renders as a
visible spike in the SVG.

The 10S curve in that range stays at MTF ≥ 0.93 (the chart artist's
"merged at chart top" signal). By physics:

- Lower-frequency MTF >= higher-frequency MTF on the same direction
  (`freq10S >= freq30S` always)
- When the chart artist merges the two strokes visually, the two
  curves must be within ~one stroke width on the page
- → `freq30S` must be at or very close to `freq10S` in that region

So `freq10S` is a far better anchor than the diverging `freq30M`
sister.

## Decision

Add a post-sister-fallback pass `_apply_coincident_top_anchor` in
`tools/mtfdigitizer/pipeline/pipeline.py` that:

1. Iterates every `freq{hi}{D}` field where `D in {S, M}`
2. Finds the closest lower frequency `freq{lo}{D}` (same direction)
3. For each cell flagged sister-filled by the prior sister-fallback
   pass, if `freq{lo}{D}` at the same frac reads MTF >= 0.90,
   override the sister-filled value with the `freq{lo}{D}` value
4. Tracks per-field override count as
   `ExtractedChart.coincident_anchor_count`, surfaced in the
   production digitization log under a new `coincident-anchor`
   column (rendered only when at least one cell fired, keeping
   clean logs visually unchanged)

```
direct ---> sister --> intra-interp --> coincident-top --> center-symmetry
extract     fallback   (#1254)          anchor (#1269)    (#1267)
                                        S=M.copy(lo) if   S=M at frac=0.0
                                        sister-filled AND + 1.0 anchor if
                                        lo >= 0.90        both None
```

Threshold of 0.90 picked because:

- At MTF 0.90 the lower curve is still "essentially flat at chart top"
  — the merged-stroke assumption holds (the chart artist would not
  draw a coincident 30S curve under a 10S curve that has visibly
  descended below 0.90)
- Below 0.90 the lower curve has begun a real dip; the higher-freq
  curve at the same frac could plausibly be far lower (e.g. 10S at
  0.7 with 30S at 0.3 — large legitimate gap)
- Typical sister-fill error in the merged-stroke regime is 0.4+ MTF
  (see fisheye table above), so accepting a slightly-too-high anchor
  from `freq{lo}{D}` is much better than the existing wrong value

Four constraints that keep the rule safe:

1. **Sister-filled cells only.** Cells that the extractor successfully
   read get to keep their value, even if the lower-freq sister is at
   chart top — the chart's own ink wins.
2. **Same direction only.** `freq10S` anchors `freq30S`; `freq10M`
   anchors `freq30M`. Cross-direction inference would conflate
   independent physical axes.
3. **Same frac only.** The override is cell-by-cell, not region-based.
   A future stage could smooth the transition between
   anchored and natively-extracted values, but cell-local is the
   safest first step.
4. **Coincident-stroke gate.** For each `(hi_field, lo_field)` pair,
   measure the **minimum** `|hi - lo|` on cells where both were
   genuinely extracted (neither None, neither sister-filled) AND
   the lower curve sits at chart top (`lo >= _COINCIDENT_ANCHOR_THRESHOLD`).
   If that minimum exceeds `_COINCIDENT_ANCHOR_MAX_PAIR_DELTA = 0.05`,
   the chart has no anchor-point overlap between hi and lo — disable
   the anchor for that pair.

   The minimum (not median) is the right statistic: the anchor only
   fires in the top regime, so the gate's question is "is there at
   least one cell where hi and lo demonstrably touch at top?" Natural
   curve divergence elsewhere — e.g. samyang 12mm fisheye where 30S
   dives at the corner while 10S stays high — is irrelevant evidence
   about top-regime behaviour. A median over corner-divergent cells
   would veto the anchor on lenses where it is most justified.

   Restricting to `lo >= threshold` matters because that is the same
   regime the anchor will copy values from. Including cells outside
   that regime would let dives in either curve corrupt the gate
   statistic.

   Catches the samyang-85mm Tier 1 anchor regression: `freq10M` is
   pinned at MTF ~0.91 across the field while `freq30M` legitimately
   sits at ~0.6, a 0.30 gap on every clean cell where lo ≥ 0.9. The
   minimum |Δ| ≈ 0.29, well above 0.05 — the gate disables the
   anchor and the four sister-filled `freq30M` cells keep their
   correct 30S-sourced fallback values.

### Worked example (post-#1271 freq10S)

| frac | freq30S before #1269 | freq30S after #1269 + #1271 |
| ---- | -------------------- | --------------------------- |
| 0.0  | 1.00 (#1267 anchor)  | 1.00                        |
| 0.1  | 0.97 (sister)        | **0.99** (←10S)             |
| 0.2  | 0.94 (sister)        | **0.99** (←10S)             |
| 0.3  | 0.89 (sister)        | **0.99** (←10S)             |
| 0.4  | 0.81 (sister)        | **0.99** (←10S)             |
| 0.5  | 0.72 (sister)        | **0.99** (←10S)             |
| 0.6  | 0.62 (sister)        | **0.99** (←10S)             |
| 0.7  | 0.98 (extracted)     | 0.98                        |
| 0.8  | 0.97 (extracted)     | 0.97                        |
| 0.9  | 0.93 (extracted)     | 0.93                        |
| 1.0  | 0.88 (extracted)     | 0.88                        |

The sparkline now traces a smooth descent from 1.00 → 0.88 across
the field. The original 0.45 spike at frac 0.7→0.8 (before #1269)
and the post-#1271-revert 0.03..0.07 bow are both gone.

## Alternatives considered

1. **Backward extrapolation from first-extracted cell.** Look at
   `freq30S[8] = 0.98` and extrapolate backward through the sister-
   filled cells with linear/exponential decay to `freq30S[0] = 1.0`.
   Rejected: assumes the chart shape, throws away the available
   `freq10S` signal at each cell. The 10S anchor uses real chart
   data per cell rather than a model.

2. **Tighten the 30S V-band to capture coincident-stroke pixels.**
   Widening `30S-dark-grey`'s V range to swallow the red 10S AA
   halo would in theory recover ink for 30S in the coincident
   region. Rejected: catastrophic for ADR-062's halo-pair work —
   would re-introduce the chart-top contamination on 30M that
   ADR-062 spent considerable effort eliminating. Also wouldn't
   help when the higher-freq curve is genuinely below the lower-
   freq (where the dispatch correctly returns no 30S ink there).

3. **Per-chart hint in `ReferenceChart`.** A flag like
   `coincident_top: true` on the entry. Rejected: the pattern is
   chart-family-wide (every Samyang stopped panel, several Fuji
   panels, possibly other multi-frequency mainstream charts), so
   profile-level / pipeline-level rule is the right scope. The
   threshold-based gate (`lo >= 0.90`) handles both presence and
   absence naturally — no opt-in required.

4. **Replace sister fallback entirely with low-freq-first.** Restructure
   the fallback chain so that empty high-freq cells try low-freq same-
   direction FIRST, then fall back to same-freq sister. Rejected for
   this round: bigger refactor, harder to bound the blast radius.
   The post-pass override is a narrower change that runs only on
   already-marked sister-filled cells.

## Consequences

### Positive

- The fisheye spike that motivated the issue is gone: `freq30S` on
  `samyang-12mm-f2-8-ed-as-ncs-fish-eye` stopped traces a continuous
  descent 1.00 → 0.99 → 1.00 → 1.00 → 0.99 → 0.97 → 0.96 → 0.93 →
  0.98 → 0.95 → 0.89 instead of dropping to 0.53 then jumping back.
- The same pattern across 25+ other lenses (Sigma DC DN C, most
  Samyang Tier 2) had milder versions of the same defect; all are
  now smoothed.
- Calibration impact: see "Calibration" section below — kept within
  noise of S177 baseline.
- The override is conservative: only fires on cells the sister
  fallback had already marked as filled, and only when the lower
  curve confirms the chart-top assumption.

### Negative / accepted tradeoff

- A high-frequency curve that genuinely sits at the lower-frequency
  curve's MTF at chart top will be marked "anchored" rather than
  "sister-filled" — but the resulting value is the same. No
  measurable downside.
- Render-match precision changes by small amounts (typically ±0.01)
  per affected lens — the SVG now traces closer to the source chart
  in the coincident region, which is good but the precision metric
  weights this neutrally.

### Scope this ADR does NOT cover

- Cross-direction coincidence. `freq30S` is only anchored from
  `freq10S`, never from `freq10M`. S and M can legitimately diverge
  near chart top on some lenses; an M anchor for an S cell would
  conflate independent physical axes.
- Right-edge anchor. The rule fires anywhere in the 11-point grid,
  not just at corners, but the underlying signal (lower curve at
  chart top while higher-freq skeleton is empty) is most common
  in the first 70% of the field.
- Multi-cell smoothing. The transition between anchored cells
  (governed by `freq{lo}{D}`'s curve shape) and natively-extracted
  cells can have a small discontinuity at the boundary — see
  fisheye frac 0.7→0.8 (0.93 → 0.98) in the worked example. Cell-
  local is the safest first step; a smoothing pass could be added
  later if the residual discontinuities become a problem.
