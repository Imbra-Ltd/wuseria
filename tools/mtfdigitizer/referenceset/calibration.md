# Calibration run (#953)

First calibration of `extract_chart()` against the reference set's
eye-read ground truth. Sister document to `REFERENCE_SET.md` — that one
declares the proposed thresholds; this one records what running the
extractor against ground truth actually produces.

This is the **offset distribution** half of the calibration defined in
`REFERENCE_SET.md` §"What 'calibration against the set' actually means".
The other half — render-match IoU — needs the confidence-signal
sub-task of epic #932 to land first.

## Scope

3 of 8 reference charts run today: those whose `style_family` has a
declared profile in `profiles/declared.py`.

| Chart                                | Style family                    | Profile used                |
| ------------------------------------ | ------------------------------- | --------------------------- |
| sigma-56mm-f1-4-dc-dn-c              | mainstream-2color-solid-dashed  | SIGMA_2COLOR_SOLID_DASHED   |
| samyang-85mm-f1-4-as-if-umc (MAX)    | mainstream-4color-all-solid     | SAMYANG_4COLOR_ALL_SOLID    |
| samyang-300mm-f6-3-ed-umc-cs-reflex (MAX) | idealized-flat              | SAMYANG_4COLOR_ALL_SOLID    |

The other 5 charts (chart 4 same-color-dashed, 5 soft promo, 6
2color-frequency, 7 B&W dashed, 8 multifreq) need profile declarations
that don't exist yet. ADR-038 §1 says other dialects land per-brand as
the digitizer encounters them; that is separate work.

## How to reproduce

```
cd tools
py -m mtfdigitizer.calibrate
```

Reads the in-source ground truth from `referenceset/charts.py` and runs
`extract_chart()` for each chart with both `plot_box` and `ground_truth`
populated. Output: per-chart `|d|` (absolute offset) median + p95 per
field, then an aggregate.

## Run from 2026-05-30 (commit before this write-up)

### Per-chart

```
sigma-56mm-f1-4-dc-dn-c (mainstream-2color-solid-dashed)
  contrast10S     med |d| 0.007  p95 |d| 0.044  paired  9/11  ext-None  2
  contrast10M     med |d| 0.009  p95 |d| 0.024  paired  2/11  ext-None  9
  resolution30S   med |d| 0.009  p95 |d| 0.034  paired  9/11  ext-None  2
  resolution30M   med |d| 0.009  p95 |d| 0.025  paired  2/11  ext-None  9

samyang-85mm-f1-4-as-if-umc (mainstream-4color-all-solid)
  contrast10S     med |d| 0.016  p95 |d| 0.029  paired 11/11  ext-None  0
  contrast10M     med |d| 0.015  p95 |d| 0.180  paired 11/11  ext-None  0
  resolution30S   med |d| 0.016  p95 |d| 0.056  paired 11/11  ext-None  0
  resolution30M   med |d| 0.012  p95 |d| 0.036  paired 11/11  ext-None  0

samyang-300mm-f6-3-ed-umc-cs-reflex (idealized-flat)
  contrast10S     med |d| 0.017  p95 |d| 0.017  paired 11/11  ext-None  0
  contrast10M     med |d| 0.012  p95 |d| 0.019  paired 10/11  ext-None  1
  resolution30S   med |d|   -    p95 |d|   -    paired  0/11  ext-None 11
  resolution30M   med |d| 0.021  p95 |d| 0.024  paired  5/11  ext-None  6
```

### Aggregate

```
paired comparisons:    92
median |d|:           0.0147
p95 |d|:              0.0366
max |d|:              0.1467
within +/-0.05:       89/92 (96.7%)
```

## Findings

### 1. The ±0.05 tolerance band proposed in REFERENCE_SET.md is justified by data

Aggregate median |d| = 0.015 — half the band. 96.7% of paired
comparisons land within ±0.05. The band's lower anchor (the #931 trace
noise floor at Δ ≈ 0.023) sits cleanly between this median and the p95
of 0.037. No reason to tighten or loosen.

### 2. Plot-box boundaries clip data on the Sigma chart

`extract_chart()` returns `None` for **all four fields at positions
0.00mm and 14.00mm** on the Sigma 56mm chart, but returns clean values
on the same positions for both Samyang charts. The cause is the bracket
window: at fraction 0.0 the window scans `[x_left - 3, x_left + 3]`,
which sits in the y-axis label region on the Sigma chart but in the
plot region on the Samyangs (because the Samyang plot box is measured
tighter).

This is a real defect surfaced by calibration — not a tolerance
question. It costs 8 paired comparisons today (2 positions × 4 fields)
and would cost more on any chart where the plot box doesn't include the
axis line cleanly. Worth a follow-up issue against `pipeline/sampling.py`
or `referenceset/charts.py` plot-box conventions.

### 3. The Samyang profile's dark-grey HSV band is brand-page-specific

The Samyang 300mm chart's grey 30S curve renders at V ≈ 190 — outside
the declared `30S-dark-grey` band of V ∈ [85, 115], which was measured
on the 85mm chart. Result: extractor reports `None` for 30S at all 11
positions on the 300mm chart (the 0/11 paired line above).

This is the chart-rendering-varies-by-brand-page warning from ADR-038
§4, observed in the wild for the first time. The fix isn't to widen the
band (would risk matching gridlines on the 85mm chart); it's likely
either a per-chart HSV calibration step or a more robust S/V-normalized
matcher. Not a calibration-tuning question — out of scope here.

### 4. The idealized-flat case reads cleanly, confirming the ADR-038 §4 trap

The Samyang 300mm reflex is the chart REFERENCE_SET.md flags as the
"flat-axis blind-spot probe case": all curves pinned at ~1.0, so any
extractor that traces them gets a high render-match score for the wrong
reason. The calibration confirms it: `extract_chart()` reads it at
median |d| = 0.017 (cleanest of the three charts on the fields where it
gets data), all 10S/10M comparisons within ±0.05. A render-match check
alone would auto-commit this chart at high confidence. **This is the
exact case the plausibility prior must catch.**

### 5. The known Samyang pink-edge limit shows up as the worst single divergence

Max |d| = 0.147 at Samyang 85mm 10M position 21.6mm (extractor 0.783 vs
eye-read 0.93). The pink curve genuinely fades below the saturation
threshold at the chart edge — the README's "Known limits, deferred"
section calls this out for the Samyang chart. The calibration shows
which single point dominates the p95 number and confirms the failure
mode matches the documented expectation.

### 6. Sigma dashed-M readings are sparse but honest (B2 contract)

10M and 30M paired 2/11 on Sigma — the morphological close bridges
*most* dash gaps but not all, and B2 (`None` on a missed bracket)
correctly fires at positions where the bridged skeleton has no pixel.
This is the contract working, not a fault. The README already records
this as a known limit. A future SVG emitter will interpolate or hold
None per its own policy.

## Threshold recommendation

The render-match threshold question (0.75 IoU) cannot be answered
without the render-match scorer. The offset tolerance band proposed at
±0.05 holds against the runnable subset and **should not be moved on
this data alone**.

Open items before the threshold conversation can close:

- Render-match scorer (epic #932 confidence-signal sub-task).
- Plot-box bracket-window fix or convention clarification — finding 2.
- Cross-chart HSV calibration for the Samyang grey bands — finding 3.
- Calibration coverage for the other 5 reference charts as their
  profiles are declared.
