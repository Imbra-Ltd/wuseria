# Render-match scoring run (#963)

First render-match IoU run of `score_chart()` against the reference set.
Sister document to `calibration.md` — that one records the offset
distribution against eye-read ground truth (the `|d|` half of
`REFERENCE_SET.md` §"What 'calibration against the set' actually
means"); this one records the round-trip IoU half.

## Scope

Same 3 of 8 reference charts that `calibrate.py` covers — the ones with
both a declared profile in `profiles/declared.py` and a hand-measured
plot box.

| Chart                                | Style family                    | Profile used                |
| ------------------------------------ | ------------------------------- | --------------------------- |
| sigma-56mm-f1-4-dc-dn-c              | mainstream-2color-solid-dashed  | SIGMA_2COLOR_SOLID_DASHED   |
| samyang-85mm-f1-4-as-if-umc (max)    | mainstream-4color-all-solid     | SAMYANG_4COLOR_ALL_SOLID    |
| samyang-300mm-f6-3-ed-umc-cs-reflex (max) | idealized-flat              | SAMYANG_4COLOR_ALL_SOLID    |

## How to reproduce

```
cd tools
py -m mtfdigitizer.scorer
```

Runs `extract_chart()` to produce 11-point readings, then `score_chart()`
to redraw them as 1px polylines and compute per-field IoU against the
extractor's own dilated skeleton. Dilation radius is the
`DEFAULT_DILATION_RADIUS_PX = 3` symmetric on both sides — matched to the
sampling stage's bracket window.

Two numbers per field:

- **IoU** — `|raster ∩ skel| / |raster ∪ skel|`. The standard metric.
- **Precision** — `|raster ∩ skel| / |raster|`. What fraction of the
  redrawn polyline lands inside the dilated skeleton. Robust to the
  size asymmetry between an 11-point polyline and a dense skeleton
  trace; together with IoU it's a more honest pair than IoU alone.

## Run 1 (2026-05-30)

### Per-chart

```
sigma-56mm-f1-4-dc-dn-c (mainstream-2color-solid-dashed)
  contrast10S     IoU 0.451  precision 0.634  raster 19746  skel 20522  inter 12511
  contrast10M     IoU 0.039  precision 0.100  raster  1902  skel  3148  inter   191
  resolution30S   IoU 0.402  precision 0.587  raster 20987  skel 21981  inter 12326
  resolution30M   IoU 0.000  precision   -    raster     0  skel  6533  inter     0
  aggregate IoU:                0.223
  aggregate precision:          0.440

samyang-85mm-f1-4-as-if-umc (mainstream-4color-all-solid)
  contrast10S     IoU 0.376  precision 0.938  raster  3094  skel  7531  inter  2903
  contrast10M     IoU 0.270  precision 0.878  raster  3086  skel  9666  inter  2709
  resolution30S   IoU 0.174  precision 0.895  raster  3046  skel 15326  inter  2727
  resolution30M   IoU 0.074  precision 0.734  raster  3030  skel 29179  inter  2225
  aggregate IoU:                0.224
  aggregate precision:          0.861

samyang-300mm-f6-3-ed-umc-cs-reflex (idealized-flat)
  contrast10S     IoU 0.468  precision 0.988  raster  3030  skel  6371  inter  2995
  contrast10M     IoU 0.568  precision 0.990  raster  2742  skel  4752  inter  2714
  resolution30S   IoU 0.000  precision   -    raster     0  skel 10110  inter     0
  resolution30M   IoU 0.056  precision 0.996  raster  1224  skel 21618  inter  1219
  aggregate IoU:                0.273
  aggregate precision:          0.991
```

### Aggregate

```
charts scored:                3
mean IoU:                     0.240
median IoU:                   0.224
mean precision:               0.764
charts clearing IoU 0.75:     0/3
```

## Findings

### 1. The IoU 0.75 starting threshold from REFERENCE_SET.md fails 3/3

Median IoU is 0.224 — three quarters below the 0.75 proposed in
`REFERENCE_SET.md` §"Render-match threshold". The threshold doesn't
hold against actual data on the runnable subset and **must move, not
the extractor** (per the calibration discipline that document calls
out).

Root cause is geometric, not a calibration error: the rasterized
polyline is exactly `plot_box.width` pixels long (≈431 on Samyang,
≈2670 on Sigma). The extractor's skeleton, after morphological close
and skeletonization, is **2× to 8× longer per field** — branches and
fat traces inside the same plot box. After symmetric ±3 dilation the
skeleton's union dominates: even when the polyline lies entirely on it,
IoU stays ≤ ~0.5.

The probe ADR-038 §4 referenced (good extractions at IoU 0.64–0.87)
likely compared two like-for-like dense traces; we have a sparse
reconstruction vs a dense skeleton. The natural fix is one of:

1. **Use precision as the threshold metric**, not IoU. Precision
   asks the question the round-trip is actually testing: "did the
   polyline land on the skeleton?" — read on, finding 2 makes this
   look right.
2. **Densify the skeleton side to a single 1px centerline per field**
   before scoring. Closer to the probe's geometry but adds a stage
   to maintain, and the Sigma skeleton looks structurally complex
   enough that "centerline" may not be well-defined per column.
3. **Lower the IoU threshold** to e.g. 0.20. Honest to the data but
   keeps a metric that's mostly tracking pixel-count ratios.

### 2. Precision cleanly separates the runnable subset

Read down the precision column instead of IoU:

| Chart                       | Aggregate precision |
| --------------------------- | ------------------- |
| Sigma 56mm                  | **0.440** (low)     |
| Samyang 85mm                | **0.861** (high)    |
| Samyang 300mm idealized-flat | **0.991** (highest) |

That's the separation REFERENCE_SET.md hoped IoU would give. Samyang
clears 0.85 cleanly; Sigma sits below 0.50 because two of its four
fields (10M and 30M dashed) trace very sparsely (2/11 and 0/11 paired in
the offset-distribution run) — so the few polyline segments that do
draw aren't enough material for a precision argument either. Sigma 10S
and 30S individually score precision 0.63/0.59, which is real shape
agreement diluted by anti-aliasing at the chart edges.

A precision-based threshold of ≈ 0.80 would separate clean Samyang from
Sigma-with-sparse-dashed without false-confidence on the idealized-flat
chart, and would match the test `test_score_chart_polyline_mostly_lands_on_skeleton`'s
0.85 bound on per-chart Samyang data.

**Tentative recommendation**: report both IoU and precision; gate
auto-commit on precision ≥ 0.80 AND IoU ≥ 0.20. Pin this in
REFERENCE_SET.md only after the threshold conversation in the next
session — not from one run.

### 3. The flat-axis blind spot ADR-038 §4 calls out is real

Samyang 300mm reflex (all curves pinned at ~1.0) scores **precision
0.991** — the highest of the three charts — and even on IoU clears 0.27
which is the mean across the set. A horizontal polyline trivially lands
on a horizontal skeleton; there's no horizontal structure to disagree
on. Exactly the case REFERENCE_SET.md flags as needing the plausibility
prior, not render-match. This run confirms the prior is essential —
render-match alone would auto-commit this chart at full confidence.

### 4. Sigma 30M missing (0/11 polyline pixels)

Same root cause as `calibration.md` finding 6: morphological close
bridges most Sigma dashed-M gaps but not all; 30M paired only 2/11 in
calibration. After the polyline-gap-skip rule (no segment crosses a
None), 9 of 10 segments have a None endpoint and don't draw, so 30M
emits zero raster pixels. Precision is undefined, IoU is 0 (one-sided
empty). Not a fault in the scorer — the B2 contract correctly
propagates sparsity. Will resolve when the M-curve dashed bridging
stage improves.

### 5. Samyang 300mm 30S also missing — different root cause

`calibration.md` finding 3 already noted: the Samyang 300mm chart's
grey 30S curve renders at V ≈ 190, outside the declared
`30S-dark-grey` HSV band `V ∈ [85, 115]` (measured on the 85mm chart).
Result: zero skeleton pixels for 30S on the 300mm chart, zero raster
pixels (because the extractor returned all-None for it), `IoU = None`
(both-empty), which the scorer reports as 0.000 in aggregate output.

This is a chart-rendering-varies-by-brand-page issue, not a render-match
issue. Out of scope for the threshold conversation; in scope for the
HSV-calibration follow-up the calibration document flagged.

### 6. Skeleton sizes vary unexpectedly across fields

Skeleton pixel counts on Samyang 85mm: 7531 (10S), 9666 (10M), 15326
(30S), 29179 (30M). The 30M skeleton is **4× larger** than 10S despite
both being one curve per field. Sigma's skeletons run 2× to 3× longer
than Samyang's despite a similar plot-box geometry. Suggests
skeletonization is not always producing a single 1px centerline — it
may be branching or thickening on certain curve shapes.

This is information for a future skeleton-quality task; doesn't change
the threshold conversation but is worth flagging since render-match's
denominator depends on it.

## Threshold recommendation

**Hold the 0.75 IoU threshold conversation in REFERENCE_SET.md open**
until at least one more session, ideally informed by:

- The precision-vs-IoU question (finding 1): if precision becomes the
  primary metric, the document's "Render-match threshold" section needs
  a rewrite, not a number tweak.
- A second run after the Sigma dashed-bridging improves (lifts 10M/30M
  from sparse to dense), to confirm Sigma also clears precision ≥ 0.80
  once its dashed curves have material to compare.
- Calibration coverage on the other 5 reference charts as their
  profiles land — needed to confirm the threshold generalizes beyond
  the 2 mainstream dialects we have today.

In the meantime, the scorer produces stable numbers and the test suite
guards them; the threshold can be revised without touching code.
