# Eye-read — TTartisan AF 35mm f/1.8

Tier 1 anchor for the `ttartisan-4color-dual-aperture` style family. Cells below are pre-populated with the extractor's predictions. The maintainer reads each cell against the source PNG; per ADR-048 each cell has one of three states:

- bare number (`0.43`) — extractor's prediction, maintainer judged it fine (silent verification)
- number with `!` (`0.45!`) — maintainer-corrected; overrides the extractor's value
- number with `?` (`0.43?`) or bare `?` — maintainer hasn't read this cell; becomes `None` in the GT tuple

When the extractor is re-run and predictions change, this file preserves `!` and `?` marks and refreshes unmarked cells. The header text and legend are regenerated from the scaffolder.

Per [[feedback_agent_no_gt_eye_read]] the agent does NOT propose cell values of its own — the extractor predictions you see are mechanical readings, not eye-reads.

## Reading procedure

A helper rendering for each view with the 11 sample-position lines overlaid:

- `ttartisan-af-35mm-f1-8-mtf-max-readhelper.png` — f/1.8 (max)
- `ttartisan-af-35mm-f1-8-mtf-stopped-readhelper.png` — f/5.6 (stopped)

The green vertical lines are spaced by image-height fraction, not by the chart's printed x-tick labels. Each line is labelled with its image-height mm value (image_height_mm = 14.0).

**Important:** both apertures are packed into one chart by color encoding — black/grey curves are the max-aperture pass (f/1.8), red/orange curves are the stopped-aperture pass (f/5.6). Per ADR-046 the helper PNG shows the **clean source chart** (no extractor overlay) so the eye-read is unbiased; read each aperture's curves directly off the chart's own printed lines. The green sample lines span the full plot regardless of aperture.

Sample positions (mm, image_height_mm = 14.0): 0.0, 1.4, 2.8, 4.2, 5.6, 7.0, 8.4, 9.8, 11.2, 12.6, 14.0.

Read each cell at the intersection of the green vertical sample line and the curve, against the printed horizontal gridlines. Eye precision is ±0.02 (half a gridline tick). Read to two decimals. Use `?` only when the curve genuinely does not extend to that x position.

- Top of plot area → MTF 1.0
- Each printed gridline → 0.1 OTF spacing (every line carries a y-axis label)
- Bottom gridline → MTF 0.0
- Orange dashed lines fill in every 0.05 between the printed gridlines

## f/1.8 (max)

| Position (mm) | 10S  | 10M  | 30S  | 30M   |
| ------------- | ---- | ---- | ---- | ----- |
| 0.0           | 0.95 | 0.95 | 0.79 | 0.79  |
| 1.4           | 0.95 | 0.95 | 0.79 | 0.78  |
| 2.8           | 0.95 | 0.95 | 0.80 | 0.74  |
| 4.2           | 0.96 | 0.95 | 0.77 | 0.72  |
| 5.6           | 0.93 | 0.93 | 0.67 | 0.71  |
| 7.0           | 0.91 | 0.92 | 0.56 | 0.67  |
| 8.4           | 0.92 | 0.92 | 0.54 | 0.64  |
| 9.8           | 0.93 | 0.92 | 0.68 | 0.63  |
| 11.2          | 0.89 | 0.90 | 0.67 | 0.63  |
| 12.6          | 0.71 | 0.89 | 0.31 | 0.58! |
| 14.0          | 0.38 | 0.88 | 0.12 | 0.50! |

## f/5.6 (stopped)

| Position (mm) | 10S  | 10M  | 30S   | 30M   |
| ------------- | ---- | ---- | ----- | ----- |
| 0.0           | 0.94 | 0.94 | 0.84  | 0.84  |
| 1.4           | 0.94 | 0.94 | 0.84  | 0.84  |
| 2.8           | 0.94 | 0.94 | 0.86  | 0.84  |
| 4.2           | 0.95 | 0.94 | 0.86  | 0.82  |
| 5.6           | 0.94 | 0.94 | 0.85  | 0.80  |
| 7.0           | 0.94 | 0.94 | 0.81  | 0.81  |
| 8.4           | 0.94 | 0.94 | 0.79  | 0.78  |
| 9.8           | 0.93 | 0.93 | 0.78  | 0.78  |
| 11.2          | 0.95 | 0.93 | 0.85  | 0.73  |
| 12.6          | 0.95 | 0.91 | 0.82  | 0.67  |
| 14.0          | 0.88 | 0.88 | 0.49! | 0.63! |

## Manual artifact patches (#1201 → #1224)

The extractor still mistracks the dashed grey M30 F1.8 at the bend
column (frac 0.9 reads as 0.66 — the ridge DP slides through an
intermediate AA-halo band at col ~510 instead of staying on the
dashed M30 ridge; see #1217 / S168 for the mechanism analysis).
Deeper extractor fix tracked as #1224 (anchor-signal repair).

frac 1.0 / pos 14.0 used to read as 0.17 (border-line contamination)
but #1223 / ADR-060 stripped the plot-box border from the grey mask;
the extractor now correctly returns None there because the chart's
M30 dashed curve genuinely fades before x_right. The eye-read 0.50
is extrapolation past where data exists.

Until #1224 lands, three downstream artifacts carry hand-patched M30
right-edge values matching the eye-read above (0.58 at frac 0.9,
0.50 at frac 1.0):

- `ttartisan-af-35mm-f1-8-mtf-max.svg` — points and dots at x=277.2 and x=304.0
- `ttartisan-af-35mm-f1-8-mtf-max-overlay.png` — re-rendered with patched readings
- `src/data/mtf-readings.ts` — position 12.6 M30 cell; durability across
  `emit_ttartisan_tier2 --write` provided by the override-respecting
  splice (#1305 / S187), not just the regression test (#1202).

The auto-generated `digitization-log.md` correctly shows the extractor's
actual reading (`—` at frac 1.0, 0.66 at frac 0.9) — do not patch it;
it is the diagnostic record for #1224.

## Transcribing to GT

After updating the cells above, ask the agent to transcribe — or run from `tools/`:

```
py -m mtfdigitizer.eyeread ttartisan-af-35mm-f1-8 --apply
py -m mtfdigitizer.calibrate
```

The first command rewrites `_<LENS>_GT` in `tools/mtfdigitizer/referenceset/charts.py`. The second reports per-field median |Δ| and p95 |Δ| against the extractor's output. Median |Δ| under ~0.04 means the dispatch is calibrated; higher means an adjustment is needed.

The resulting GT tuple shape:

```python
_TTARTISAN_af_GT: GroundTruthCurves = {
    "max": {  # f/1.8
        "freq10S": (...11 values from the 10S column...),
        "freq10M": (...11 values from the 10M column...),
        "freq30S": (...11 values from the 30S column...),
        "freq30M": (...11 values from the 30M column...),
    },
    "stopped": {  # f/5.6
        "freq10S": (...11 values from the 10S column...),
        "freq10M": (...11 values from the 10M column...),
        "freq30S": (...11 values from the 30S column...),
        "freq30M": (...11 values from the 30M column...),
    },
}
```
