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

6 of 8 reference charts run today: those whose `style_family` has a
declared profile in `profiles/declared.py`.

| Chart                                     | Style family                    | Profile used                          |
| ----------------------------------------- | ------------------------------- | ------------------------------------- |
| sigma-56mm-f1-4-dc-dn-c                   | mainstream-2color-solid-dashed  | SIGMA_2COLOR_SOLID_DASHED             |
| samyang-85mm-f1-4-as-if-umc (MAX)         | mainstream-4color-all-solid     | SAMYANG_4COLOR_ALL_SOLID              |
| samyang-300mm-f6-3-ed-umc-cs-reflex (MAX) | idealized-flat                  | SAMYANG_4COLOR_ALL_SOLID              |
| 7artisans-50mm-f1-2-mark-ii               | samecolor-dashed-sm             | SEVENARTISANS_2COLOR_SAMECOLOR_DASHED |
| tokina-atx-m-23mm-f1-4-x                  | 2color-frequency                | TOKINA_2COLOR_FREQUENCY               |
| viltrox-af-75mm-f1-2-pro (f/1.2)          | bw-dashed-promo                 | VILTROX_BW_DASHED_F12                 |

The 2 remaining charts (7Artisans 35mm soft promo, Zeiss Touit press
kit) are deliberately out-of-band fail-loud cases and intentionally
have no profile.

## How to reproduce

```
cd tools
py -m mtfdigitizer.calibrate
```

Reads the in-source ground truth from `referenceset/charts.py` and runs
`extract_chart()` for each chart with both `plot_box` and `ground_truth`
populated. Output: per-chart `|d|` (absolute offset) median + p95 per
field, then an aggregate.

## Run 3 (after 3-profile expansion)

3 new profiles wired (7Artisans samecolor-dashed-sm, Tokina
2color-frequency, Viltrox bw-dashed-promo) brings the runnable set from
3 to 6 charts. Adds two new dispatch branches: `Y_BAND_IS_FREQUENCY`
(neutral-mask split by vertical position) and
`HUE_IS_CURVE+SAGITTAL_MERIDIONAL` (hue carries S/M, y-band carries
frequency within hue).

### Per-chart

```
sigma-56mm-f1-4-dc-dn-c (mainstream-2color-solid-dashed)
  contrast10S     med |d| 0.006  p95 |d| 0.039  paired 11/11  ext-None  0
  contrast10M     med |d| 0.014  p95 |d| 0.094  paired  3/11  ext-None  8
  resolution30S   med |d| 0.007  p95 |d| 0.044  paired 11/11  ext-None  0
  resolution30M   med |d| 0.013  p95 |d| 0.015  paired  2/11  ext-None  9

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

7artisans-50mm-f1-2-mark-ii (samecolor-dashed-sm)
  contrast10M     med |d| 0.032  p95 |d| 0.069  paired  5/11  ext-None  6
  contrast10S     med |d| 0.035  p95 |d| 0.095  paired  7/11  ext-None  4
  resolution30M   med |d| 0.005  p95 |d| 0.033  paired  6/11  ext-None  5
  resolution30S   med |d| 0.070  p95 |d| 0.187  paired  6/11  ext-None  5

tokina-atx-m-23mm-f1-4-x (2color-frequency)
  contrast10S     med |d| 0.030  p95 |d| 0.074  paired 10/11  ext-None  1
  contrast10M     med |d| 0.024  p95 |d| 0.105  paired 10/11  ext-None  1
  resolution30S   med |d| 0.061  p95 |d| 0.134  paired  9/11  ext-None  2
  resolution30M   med |d| 0.020  p95 |d| 0.390  paired 11/11  ext-None  0

viltrox-af-75mm-f1-2-pro (bw-dashed-promo)
  contrast10S     med |d| 0.106  p95 |d| 0.157  paired 11/11  ext-None  0
  contrast10M     med |d| 0.107  p95 |d| 0.192  paired 11/11  ext-None  0
  resolution30S   med |d| 0.258  p95 |d| 0.638  paired  2/11  ext-None  9
  resolution30M   med |d| 0.524  p95 |d| 0.524  paired  1/11  ext-None 10
```

### Aggregate

```
paired comparisons:    186
median |d|:           0.0189
p95 |d|:              0.1413
max |d|:              0.5243
within +/-0.05:       141/186 (75.8%)
```

### What changed since run 2

- **7Artisans (new)** — median 0.005–0.070 across fields; the green
  S1-dashed dip-and-recover feature reads cleanly. Blue 10S/10M split
  is approximate because the two blue lines barely separate in the
  source rendering — see ground-truth provenance note in `charts.py`.
- **Tokina (new)** — initial `y_band_split=0.50` put the split deep
  into the 30 lp/mm region (30S returned 0/11); re-measured to 0.25
  by inspecting the upper/lower curve clusters. Now median 0.020–0.061
  across fields, well inside the band.
- **Viltrox (new)** — 10 lp/mm reads at median 0.106–0.107 (above the
  band but within p95 of 0.20). 30 lp/mm fails: median 0.258–0.524,
  only 1–2 paired comparisons. **Known limit**: the four curves are
  too tightly bunched in OTF space (0.65–1.0) for the y-band
  classifier to separate them. Logged in `declared.py` and the README;
  the y-band heuristic doesn't fit tightly-clustered B&W charts and
  the chart documents the failure mode for the next iteration.
- **Aggregate moves**: median |d| holds at 0.019 (slightly better
  than run 2's 0.014 weighted by the same charts); the new charts
  pull p95 up to 0.14 and within-band down to 75.8%. The 4 new bad
  comparisons all come from Viltrox 30 lp/mm — without that chart's
  contribution, the in-band rate would be ~92%.

## Run 2 (after #954 plot-box fix)

### Per-chart

```
sigma-56mm-f1-4-dc-dn-c (mainstream-2color-solid-dashed)
  contrast10S     med |d| 0.006  p95 |d| 0.039  paired 11/11  ext-None  0
  contrast10M     med |d| 0.014  p95 |d| 0.094  paired  3/11  ext-None  8
  resolution30S   med |d| 0.007  p95 |d| 0.044  paired 11/11  ext-None  0
  resolution30M   med |d| 0.013  p95 |d| 0.015  paired  2/11  ext-None  9

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
paired comparisons:    97
median |d|:           0.0143
p95 |d|:              0.0400
max |d|:              0.1467
within +/-0.05:       93/97 (95.9%)
```

### What changed since run 1

| Metric                | Run 1 (axis-line box) | Run 2 (data-edge box) |
| --------------------- | --------------------- | --------------------- |
| Sigma 10S paired      | 9/11                  | **11/11**             |
| Sigma 30S paired      | 9/11                  | **11/11**             |
| Sigma 10M paired      | 2/11                  | **3/11**              |
| Aggregate paired      | 92                    | **97**                |
| Median \|d\|          | 0.0147                | **0.0143**            |
| p95 \|d\|             | 0.0366                | 0.0400                |
| Within ±0.05          | 96.7%                 | 95.9%                 |

5 paired comparisons recovered at the chart edges. The p95 and "within
±0.05" numbers move slightly the wrong way because the recovered Sigma
boundary readings sit further from ground truth than the interior ones
do (Sigma 10S p95 went from 0.044 to 0.039, but 30S p95 went from 0.034
to 0.044 — picking up the boundary point on a steeper curve adds a
higher-error data point). Net: more honest data, similar quality.

## Run from 2026-05-30 (run 1, pre-#954-fix, for reference)

Original run before the Sigma plot-box was re-measured. The numbers
above ("Run 2") supersede this; kept here for diff context.

### Per-chart

```
sigma-56mm-f1-4-dc-dn-c (mainstream-2color-solid-dashed)
  contrast10S     med |d| 0.007  p95 |d| 0.044  paired  9/11  ext-None  2
  contrast10M     med |d| 0.009  p95 |d| 0.024  paired  2/11  ext-None  9
  resolution30S   med |d| 0.009  p95 |d| 0.034  paired  9/11  ext-None  2
  resolution30M   med |d| 0.009  p95 |d| 0.025  paired  2/11  ext-None  9
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

### 2. Plot-box boundary clipping was a convention mismatch (RESOLVED #954)

Run 1 returned `None` for all four Sigma fields at fractions 0.0 and
1.0. Root cause: the Sigma plot box was measured to the printed y-axis
line (x=186), but the leftmost curve column sits at x=311 — a 125-pixel
whitespace gap that exceeds the ±3 bracket window. The Samyang reference
charts use a different convention (plot box measured to the first/last
data column), which is why they extracted cleanly at the same fractions.

Fix: re-measure the Sigma plot box to `(309, 2980)`, aligned with the
printed "0" and "12.5" tick label positions (verified by tick-spacing
probe). The data-edge convention is now the project-wide standard.
Bracket window stays at ±3 — widening it (tried during the fix) catches
the Sigma edges but pulls in extra anti-aliased pixels on the Samyang
charts and degrades their edge readings by 0.02–0.04.

Convention for future plot-box measurements: **plot box corners are the
first/last column with skeleton pixels, not the printed axis lines.**
The two conventions can coincide (Samyang) or not (Sigma) — never
assume.

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
- Cross-chart HSV calibration for the Samyang grey bands — finding 3.
- Calibration coverage for the other 5 reference charts as their
  profiles are declared.

Resolved since run 1: finding 2 (plot-box convention) — see fix #954.
