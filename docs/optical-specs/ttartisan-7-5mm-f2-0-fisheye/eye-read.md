# Eye-read — TTartisan 7.5mm f/2.0 Fisheye

Tier 1 anchor for the `ttartisan-4color-dual-aperture` style family. Cells below are pre-populated with the extractor's predictions. The maintainer reads each cell against the source PNG; per ADR-048 each cell has one of three states:

- bare number (`0.43`) — extractor's prediction, maintainer judged it fine (silent verification)
- number with `!` (`0.45!`) — maintainer-corrected; overrides the extractor's value
- number with `?` (`0.43?`) or bare `?` — maintainer hasn't read this cell; becomes `None` in the GT tuple

When the extractor is re-run and predictions change, this file preserves `!` and `?` marks and refreshes unmarked cells. The header text and legend are regenerated from the scaffolder.

Per [[feedback_agent_no_gt_eye_read]] the agent does NOT propose cell values of its own — the extractor predictions you see are mechanical readings, not eye-reads.

## Reading procedure

A helper rendering for each view with the 11 sample-position lines overlaid:

- `ttartisan-7-5mm-f2-0-fisheye-mtf-max-readhelper.png` — f/2 (max)
- `ttartisan-7-5mm-f2-0-fisheye-mtf-stopped-readhelper.png` — f/8 (stopped)

The green vertical lines are spaced by image-height fraction, not by the chart's printed x-tick labels. Each line is labelled with its image-height mm value (image_height_mm = 14.0).

**Important:** both apertures are packed into one chart by color encoding — black/grey curves are the max-aperture pass (f/2), red/orange curves are the stopped-aperture pass (f/8). Per ADR-046 the helper PNG shows the **clean source chart** (no extractor overlay) so the eye-read is unbiased; read each aperture's curves directly off the chart's own printed lines. The green sample lines span the full plot regardless of aperture.

Sample positions (mm, image_height_mm = 14.0): 0.0, 1.4, 2.8, 4.2, 5.6, 7.0, 8.4, 9.8, 11.2, 12.6, 14.0.

Read each cell at the intersection of the green vertical sample line and the curve, against the printed horizontal gridlines. Eye precision is ±0.02 (half a gridline tick). Read to two decimals. Use `?` only when the curve genuinely does not extend to that x position.

- Top of plot area → MTF 1.0
- Each printed gridline → 0.1 OTF spacing (every line carries a y-axis label)
- Bottom gridline → MTF 0.0
- Orange dashed lines fill in every 0.05 between the printed gridlines

## f/2 (max)

| Position (mm) | 10S   | 10M   | 30S   | 30M   |
| ------------- | ----- | ----- | ----- | ----- |
| 0.0           | 0.95! | 0.95! | 0.71  | 0.71  |
| 1.4           | 0.95  | 0.95  | 0.72  | 0.72  |
| 2.8           | 0.95  | 0.95  | 0.73  | 0.75  |
| 4.2           | 0.94! | 0.95  | 0.69  | 0.75  |
| 5.6           | 0.92! | 0.95  | 0.61  | 0.72! |
| 7.0           | 0.91  | 0.94  | 0.54  | 0.67  |
| 8.4           | 0.90! | 0.94! | 0.53  | 0.66  |
| 9.8           | 0.90  | 0.93! | 0.49  | 0.70  |
| 11.2          | 0.90  | 0.90  | 0.46  | 0.69  |
| 12.6          | 0.81  | 0.91! | 0.54! | 0.57! |
| 14.0          | 0.93! | 0.75! | 0.57! | 0.48! |

## f/8 (stopped)

| Position (mm) | 10S  | 10M  | 30S   | 30M   |
| ------------- | ---- | ---- | ----- | ----- |
| 0.0           | 0.92 | 0.92 | 0.77  | 0.77  |
| 1.4           | 0.93 | 0.93 | 0.77! | 0.78! |
| 2.8           | 0.93 | 0.93 | 0.76! | 0.79  |
| 4.2           | 0.93 | 0.93 | 0.75! | 0.80  |
| 5.6           | 0.92 | 0.93 | 0.73  | 0.80  |
| 7.0           | 0.92 | 0.93 | 0.70  | 0.79  |
| 8.4           | 0.92 | 0.93 | 0.70! | 0.77  |
| 9.8           | 0.92 | 0.93 | 0.70! | 0.76  |
| 11.2          | 0.91 | 0.92 | 0.69! | 0.78! |
| 12.6          | 0.91 | 0.93 | 0.65  | 0.79  |
| 14.0          | 0.90 | 0.93 | 0.58  | 0.79  |

## Transcribing to GT

After updating the cells above, ask the agent to transcribe — or run from `tools/`:

```
py -m mtfdigitizer.eyeread ttartisan-7-5mm-f2-0-fisheye --apply
py -m mtfdigitizer.calibrate
```

The first command rewrites `_<LENS>_GT` in `tools/mtfdigitizer/referenceset/charts.py`. The second reports per-field median |Δ| and p95 |Δ| against the extractor's output. Median |Δ| under ~0.04 means the dispatch is calibrated; higher means an adjustment is needed.

The resulting GT tuple shape:

```python
_TTARTISAN_7_GT: GroundTruthCurves = {
    "max": {  # f/2
        "freq10S": (...11 values from the 10S column...),
        "freq10M": (...11 values from the 10M column...),
        "freq30S": (...11 values from the 30S column...),
        "freq30M": (...11 values from the 30M column...),
    },
    "stopped": {  # f/8
        "freq10S": (...11 values from the 10S column...),
        "freq10M": (...11 values from the 10M column...),
        "freq30S": (...11 values from the 30S column...),
        "freq30M": (...11 values from the 30M column...),
    },
}
```
