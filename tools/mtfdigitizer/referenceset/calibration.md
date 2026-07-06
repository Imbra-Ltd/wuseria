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
| samyang-85mm-f1-4-as-if-umc (max)         | mainstream-4color-all-solid     | SAMYANG_4COLOR_ALL_SOLID              |
| samyang-300mm-f6-3-ed-umc-cs-reflex (max) | idealized-flat                  | SAMYANG_4COLOR_ALL_SOLID              |
| 7artisans-50mm-f1-2-mark-ii               | samecolor-dashed-sm             | SEVENARTISANS_2COLOR_SAMECOLOR_DASHED |
| tokina-atx-m-23mm-f1-4-x                  | 2color-frequency                | TOKINA_2COLOR_FREQUENCY               |
| viltrox-af-75mm-f1-2-pro (f/1.2)          | bw-dashed-promo                 | VILTROX_BW_DASHED_F12                 |

The 1 remaining chart (7Artisans 35mm soft promo) is a deliberately
out-of-band fail-loud case and intentionally has no profile. The
Zeiss Touit press kit was promoted from rejection-case to an extracted
family by #791 / ADR-075 via the N-frequency RIDGE_TRACKING pipeline
(`ridge_tracks_to_fields_multifreq`); it joined the table when it
shipped eye-read ground truth (12mm via #1348; 32mm maintainer-verified
in Run 6, 50mm in Run 7 — #1332 complete).

## How to reproduce

```
cd tools
py -m mtfdigitizer.calibrate
```

Reads the in-source ground truth from `referenceset/charts.py` and runs
`extract_chart()` for each chart with both `plot_box` and `ground_truth`
populated. Output: per-chart `|d|` (absolute offset) median + p95 per
field, then an aggregate.

## Run 7 (after Touit 50mm maintainer eye-read GT — #1332 complete)

First run where `zeiss-touit-50mm-f2-8-macro` scores against
maintainer-read ground truth instead of extractor-seeded predictions:
132/132 cells eye-read at ±0.005 on the 0.01-grid readhelpers (78
corrected, 54 silently verified, 0 unknown). This completes the
396-cell Touit family GT — all three `multifreq-press-kit` anchors
are now maintainer-verified. Two behaviours the seeded GT hid are now
measured:

1. **Max-panel dotted-M coincidence cascade.** GT confirms the dotted
   T (M) curves hug solid S wide open — the 10-pair coincides within
   0.02 across the field (the macro is nearly astigmatism-free at
   k=2.8). The ridge tracker does not resolve the coincident pair, so
   every M assignment slides one band down in the inner field: EX
   freq10M rides the 20-band (med |d| 0.096, p95 0.123), EX freq20M
   rides the 40-band at 1.4–5.6 mm (|d| up to 0.169), and the 40-band
   pair goes ext-None at 1.4–4.2 mm (no track left to assign).
   Assignments recover from mid-field where the bands separate. Same
   coincidence-collapse root as the #791 stopped-panel limitation,
   surfacing on a MAX panel for the first time via the 50mm's dotted
   (lighter-ink) M rendering.
2. **Stopped-panel 40-band collapse, second chart.** The k=5.6
   10-pair coincidence is real (GT delta <= 0.01 — the collapsed pair
   at 10 is correct), but EX freq40S rides the 20-band across
   2.8–11.2 mm (med |d| 0.089, p95 0.111) and freq40M under-separates
   toward the corner where GT drops to 0.50 vs EX 0.71 (med 0.090,
   p95 0.226); 20M is also under-separated at the outer field (|d|
   0.055–0.075 from 12.6 mm). Matches the 32mm Run 6 signature — the
   #791 Path B failure mode is now quantified on two charts.

### Per-chart (Touit block; panels labelled)

```
zeiss-touit-50mm-f2-8-macro (multifreq-press-kit)  [max / k=2.8]
  freq10S         med |d| 0.003  p95 |d| 0.004  paired 11/11  ext-None  0
  freq10M         med |d| 0.096  p95 |d| 0.123  paired 11/11  ext-None  0
  freq20S         med |d| 0.013  p95 |d| 0.120  paired 10/11  ext-None  1
  freq20M         med |d| 0.065  p95 |d| 0.177  paired 10/11  ext-None  1
  freq40S         med |d| 0.004  p95 |d| 0.076  paired  8/11  ext-None  3
  freq40M         med |d| 0.011  p95 |d| 0.050  paired  8/11  ext-None  3
zeiss-touit-50mm-f2-8-macro (multifreq-press-kit)  [stopped / k=5.6]
  freq10S         med |d| 0.005  p95 |d| 0.005  paired 11/11  ext-None  0
  freq10M         med |d| 0.005  p95 |d| 0.009  paired 11/11  ext-None  0
  freq20S         med |d| 0.002  p95 |d| 0.005  paired 11/11  ext-None  0
  freq20M         med |d| 0.021  p95 |d| 0.084  paired 11/11  ext-None  0
  freq40S         med |d| 0.089  p95 |d| 0.111  paired 11/11  ext-None  0
  freq40M         med |d| 0.090  p95 |d| 0.226  paired 11/11  ext-None  0
```

Per-panel in-band (|d| <= 0.05, from
`readings/zeiss-touit-50mm-f2-8-macro.md`): max 40/66 (60.6%) — 40 of
58 paired cells in-band plus 8 GT cells the extractor returned no
reading for (counted as misses); stopped 47/66 (71.2%), all 66
paired. Both panels fail the 93%+ norm of the verified anchors —
deliberately documented, not silenced (#1332 AC).

Family reference — per-panel in-band across the three Touit anchors
(#1332 AC "in-band % per panel"; 12mm from
`readings/zeiss-touit-12mm-f2-8.md`, unchanged this run):

```
zeiss-touit-12mm-f2-8          max 53/66 (80.3%)   stopped 60/66 (90.9%)
zeiss-touit-32mm-f1-8          max 45/66 (68.2%)   stopped 48/66 (72.7%)
zeiss-touit-50mm-f2-8-macro    max 40/66 (60.6%)   stopped 47/66 (71.2%)
```

### Aggregate

```
before GT flip (seeded 50mm GT):        after (maintainer GT):
  paired comparisons:    1237             paired comparisons:    1278
  median |d|:           0.0060             median |d|:           0.0062
  p95 |d|:              0.0641             p95 |d|:              0.0831
  max |d|:              0.2538             max |d|:              0.2538
  within +/-0.05: 1152/1237 (93.1%)        within +/-0.05: 1156/1278 (90.5%)
```

The 2.6-point in-band drop is the honest cost of de-circularizing the
last Touit GT. The 50mm adds two metrics to watch alongside Run 6's:
max-panel freq10M med |d| (0.096 — the dotted-M cascade) and stopped
freq40S/freq40M med |d| (0.089/0.090 — the #791 Path B collapse).
Recovery is tracked via #1374 and the #791 Path B work.

## Run 6 (after Touit 32mm maintainer eye-read GT, #1332)

First run where `zeiss-touit-32mm-f1-8` scores against maintainer-read
ground truth instead of extractor-seeded predictions: 132/132 cells
eye-read at ±0.005 on the 0.01-grid readhelpers (86 corrected, 46
silently verified, 0 unknown). The GT flip converts two known-suspect
behaviours from invisible (circular seeded GT) to measured:

1. **Max-panel S/M label swap.** On the k=1.8 panel the dashed T (M)
   curves run ABOVE solid S from ~3 mm outward at 10 and 20 lp/mm.
   `_assign_interior_anchored_bands` assigns S to the upper track of
   each frequency band by construction, so the extractor mirrors GT
   with the labels exchanged — EX freq10S matches GT freq10M within
   read precision cell-for-cell (e.g. frac 1.0: EX 0.79 vs GT-M 0.79,
   EX-M 0.61 vs GT-S 0.61). Med |d| 0.073/0.070 on freq10S/M, ~0.02-
   0.03 at 20 (curves closer), ~0.01-0.02 at 40 (curves touch).
   Tracked as its own defect (see #1374) — distinct from the stopped
   collapse below.
2. **Stopped-panel 40-band cluster collapse (#791 known limitation,
   now quantified).** At k=4 the real 10S/10M pair genuinely coincides
   (GT delta <= 0.006 across the field — the collapsed pair at 10 is
   correct), 20M runs 0.01-0.02 below 20S, but 40S/40M separate widely
   mid-field (GT 40S dips to 0.56 at 11.2 mm, 40M to 0.47). The
   extracted 40S instead rides the 20-band: med |d| 0.164, p95 0.261,
   max 0.254; 40M absorbs part of the same collapse at med 0.080.

Also in this run: `_write_readings_log` derives grid columns from the
aperture's GT fields instead of a hardcoded `freq10/freq30` tuple —
the old grid rendered dead `freq30` columns and silently omitted the
Touit 20/40 fields (and Fuji's 15/45), which would have hidden exactly
the stopped-panel failures this run exists to record. All committed
readings regenerate with their real columns.

### Per-chart (Touit block; panels labelled)

```
zeiss-touit-32mm-f1-8 (multifreq-press-kit)  [max / k=1.8]
  freq10S         med |d| 0.073  p95 |d| 0.191  paired 11/11  ext-None  0
  freq10M         med |d| 0.070  p95 |d| 0.190  paired 11/11  ext-None  0
  freq20S         med |d| 0.030  p95 |d| 0.056  paired 11/11  ext-None  0
  freq20M         med |d| 0.020  p95 |d| 0.058  paired 11/11  ext-None  0
  freq40S         med |d| 0.009  p95 |d| 0.066  paired 11/11  ext-None  0
  freq40M         med |d| 0.021  p95 |d| 0.073  paired 11/11  ext-None  0
zeiss-touit-32mm-f1-8 (multifreq-press-kit)  [stopped / k=4]
  freq10S         med |d| 0.001  p95 |d| 0.006  paired 11/11  ext-None  0
  freq10M         med |d| 0.001  p95 |d| 0.006  paired 11/11  ext-None  0
  freq20S         med |d| 0.002  p95 |d| 0.004  paired 11/11  ext-None  0
  freq20M         med |d| 0.016  p95 |d| 0.025  paired 11/11  ext-None  0
  freq40S         med |d| 0.164  p95 |d| 0.261  paired 11/11  ext-None  0
  freq40M         med |d| 0.080  p95 |d| 0.137  paired 11/11  ext-None  0
```

Per-panel in-band (|d| <= 0.05, from
`readings/zeiss-touit-32mm-f1-8.md`): max 45/66 (68.2%), stopped
48/66 (72.7%). Both panels fail the 93%+ norm of the verified anchors
— deliberately documented, not silenced (#1332 AC).

### Aggregate

```
before GT flip (seeded 32mm GT):        after (maintainer GT):
  paired comparisons:    1197             paired comparisons:    1237
  median |d|:           0.0059             median |d|:           0.0060
  p95 |d|:              0.0448             p95 |d|:              0.0641
  max |d|:              0.1958             max |d|:              0.2538
  within +/-0.05: 1152/1197 (96.2%)        within +/-0.05: 1152/1237 (93.1%)
```

The 3.1-point in-band drop is the honest cost of de-circularizing the
32mm GT: 40 previously-None cells now pair, and the corrected cells
score the extractor against reality instead of against itself. The
aggregate recovers when #1374 (S/M swap) and the #791 Path B collapse
work land — freq10S/M max-panel and freq40S/M stopped-panel are the
metrics to watch.

## Run 5 (after Viltrox ridge-tracking dispatch, #994)

Viltrox profile switched from `CC_RANK_BY_MEAN_Y` (which on this chart
read the printed top plot-frame border as 10S — see Run 4 notes) to
`RIDGE_TRACKING`: per-column ridge centroids are clustered into tracks,
near-duplicate tracks (within 4 px of mean_y) are deduplicated, and
the top 4 by coverage are split by mean_y into upper-frequency (10) and
lower-frequency (30) pairs. Within each pair, the curve with the lower
mean_y is the sagittal (S) by lens physics — S MTF >= M MTF at every
position, so S sits above M in image coordinates.

Three changes ship together in this run:

1. `RIDGE_TRACKING` dispatch (new file `pipeline/ridge.py`).
2. Viltrox plot-box re-measured: y_top 130 → 153, y_bottom 365 → 393.
   The pre-#994 calibration placed OTF=1.0 at the printed "1" label
   instead of at the gridline 23 px below it. Run 4's "10S |d| = 0.000"
   was a coincidence: the chrome-border at y=130 mapped to MTF=1.0
   under the wrong y_top and matched ground truth 10S of 1.0 by
   accident, masking that the actual 10S curve was never read.
3. Chrome stripping: rows inside the plot box with ≥90% horizontal
   mask coverage are now zeroed before ridge extraction. This catches
   OTF gridlines and plot-frame borders without depending on CC
   connectivity (the Viltrox neutral mask fuses every gridline with
   every curve into one 2789-px CC).

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
  contrast10S     med |d| 0.012  p95 |d| 0.056  paired 11/11  ext-None  0
  contrast10M     med |d| 0.048  p95 |d| 0.088  paired  5/11  ext-None  6
  resolution30S   med |d| 0.020  p95 |d| 0.136  paired  7/11  ext-None  4
  resolution30M   med |d| 0.016  p95 |d| 0.146  paired  3/11  ext-None  8
```

### Aggregate

```
paired comparisons:    187
median |d|:           0.0167
p95 |d|:              0.0918
max |d|:              0.3146
within +/-0.05:       161/187 (86.1%)
```

### What changed since run 4

- **Viltrox 10S — now reading the real curve.** Run 4 paired 11/11 at
  median |d| 0.000 but was reading the top plot-frame border line
  (which mapped to MTF=1.0 under a wrong plot box; see #2 above).
  Run 5 paired 11/11 at median |d| 0.012 — same count, real curve,
  still well inside the calibration band.
- **Viltrox 10M — recovered.** 0/11 → 5/11 paired, med |d| 0.048.
  Meets the #994 acceptance criteria (≥5/11 reads at |d| ≤ 0.10).
  The 6 unread positions are columns where neither dash of the
  10M curve falls within the bracket window of the 11 sample
  fractions (a chart-rasterization limit, not an algorithm fault).
- **Viltrox 30S — improved.** 11/11 (fake, reading axis grid) → 7/11
  (real curve, med |d| 0.020). The new value is dramatically more
  trustworthy.
- **Viltrox 30M — minor paired-count regression.** 4/11 → 3/11 with
  med |d| 0.016. The lost position is offset by all three other
  fields now reading real data. Trade accepted.
- **Aggregate** — within-band 85.6% → 86.1% (+0.5 pts), p95 |d|
  0.0913 → 0.0918 (flat). Median |d| flat at 0.017. The
  improvement is in the *trustworthiness* of Viltrox readings,
  not in calibration-band membership — and that's the right
  axis: Run 4 reported high coverage with low |d| but the wins
  were artifacts.
- **No regression on the other 5 in-band families.** RIDGE_TRACKING
  is wired only to the Viltrox profile via its `hue_meaning`. All
  per-chart numbers for Sigma, Samyang 85mm/300mm, 7Artisans, and
  Tokina are identical to Run 4 byte-for-byte.

## Run 4 (after Viltrox CC-rank dispatch, #992)

Viltrox profile switched from `Y_BAND_IS_FREQUENCY` (fixed `y_band_split=0.30`)
to `CC_RANK_BY_MEAN_Y`: skeletonize the single neutral mask, rank connected
components by mean y-position, split at the largest y-gap into upper- (10
lp/mm) and lower- (30 lp/mm) frequency clusters, then within each cluster
the longest CC is the solid line and the rest are dashed fragments. No
other profile changes.

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
  contrast10S     med |d| 0.000  p95 |d| 0.050  paired 11/11  ext-None  0
  contrast10M     med |d|   -    p95 |d|   -    paired  0/11  ext-None 11
  resolution30S   med |d| 0.032  p95 |d| 0.396  paired 11/11  ext-None  0
  resolution30M   med |d| 0.060  p95 |d| 0.074  paired  4/11  ext-None  7
```

### Aggregate

```
paired comparisons:    187
median |d|:           0.0167
p95 |d|:              0.0913
max |d|:              0.3146
within +/-0.05:       160/187 (85.6%)
```

### What changed since run 3

- **Viltrox 30 lp/mm — fixed**. 30S median |d| moved 0.258 → 0.032 (now in
  the ±0.05 band, paired 11/11 vs 2/11 before); 30M moved 0.524 → 0.060
  (just outside the band, paired 4/11 vs 1/11). The 30 lp/mm pair is no
  longer the calibration's outlier — the largest-y-gap split between the
  upper and lower clusters lands cleanly between the 10 lp/mm pair and the
  30 lp/mm pair, where the fixed `y_band_split=0.30` could not.
- **Viltrox 10S — improved**. Median |d| 0.106 → 0.000 (paired 11/11). The
  reading is dominated by the top plot-box border line itself (the largest
  CC the skeletonizer recovers near y≈130 is the printed axis line, which
  happens to sit at MTF=1.0 ≈ the 10S ground truth). Honest about the
  mechanism: the win here is partly real (the 10S curve also reads ~1.0
  near center) and partly the axis line is doing the work.
- **Viltrox 10M — regression**. Now 0/11 paired (was 11/11 with |d|=0.107).
  The 10S and 10M curves physically share pixels at the top of the chart
  (both ~OTF 0.97 across most of the field width — Viltrox ground truth
  10S=1.00→0.95 and 10M=0.99→0.82 overlap heavily in the source
  rendering). After CC labeling there is only one upper-cluster CC; it
  becomes 10S, and 10M has no remainder to attach to. Tracked as a
  follow-up to #992 — separating two curves that share pixels needs a
  different technique (sub-pixel ridge tracking, two-pass mask
  subtraction, or a higher-resolution chart).
- **Aggregate** — within-band moved 75.8% → 85.6% (+9.8 pts), median |d|
  0.019 → 0.017, p95 0.141 → 0.091, max |d| 0.524 → 0.315. The CC-rank
  dispatch is a clear net win even with the 10M regression.

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
