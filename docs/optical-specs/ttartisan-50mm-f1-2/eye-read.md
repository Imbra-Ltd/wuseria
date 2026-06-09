# Eye-read — TTartisan 50mm f/1.2

Tier 1 anchor for the `ttartisan-4color-dual-aperture` style family. Cells below are pre-populated with the extractor's predictions. The maintainer reads each cell against the source PNG; per ADR-048 each cell has one of three states:

- bare number (`0.43`) — extractor's prediction, maintainer judged it fine (silent verification)
- number with `!` (`0.45!`) — maintainer-corrected; overrides the extractor's value
- number with `?` (`0.43?`) or bare `?` — maintainer hasn't read this cell; becomes `None` in the GT tuple

When the extractor is re-run and predictions change, this file preserves `!` and `?` marks and refreshes unmarked cells. The header text and legend are regenerated from the scaffolder.

Per [[feedback_agent_no_gt_eye_read]] the agent does NOT propose cell values of its own — the extractor predictions you see are mechanical readings, not eye-reads.

## Reading procedure

A helper rendering for each view with the 11 sample-position lines overlaid:

- `ttartisan-50mm-f1-2-mtf-max-readhelper.png` — f/1.2 (max)
- `ttartisan-50mm-f1-2-mtf-stopped-readhelper.png` — f/5.6 (stopped)

The green vertical lines are spaced by image-height fraction, not by the chart's printed x-tick labels. Each line is labelled with its image-height mm value (image_height_mm = 14.0).

**Important:** both apertures are packed into one chart by color encoding — black/grey curves are the max-aperture pass (f/1.2), red/orange curves are the stopped-aperture pass (f/5.6). Per ADR-046 the helper PNG shows the **clean source chart** (no extractor overlay) so the eye-read is unbiased; read each aperture's curves directly off the chart's own printed lines. The green sample lines span the full plot regardless of aperture.

Sample positions (mm, image_height_mm = 14.0): 0.0, 1.4, 2.8, 4.2, 5.6, 7.0, 8.4, 9.8, 11.2, 12.6, 14.0.

Read each cell at the intersection of the green vertical sample line and the curve, against the printed horizontal gridlines. Eye precision is ±0.02 (half a gridline tick). Read to two decimals. Use `?` only when the curve genuinely does not extend to that x position.

- Top of plot area → MTF 1.0
- Each printed gridline → 0.1 OTF spacing (every line carries a y-axis label)
- Bottom gridline → MTF 0.0
- Orange dashed lines fill in every 0.05 between the printed gridlines

## f/1.2 (max)

| Position (mm) | 10S   | 10M   | 30S   | 30M   |
| ------------- | ----- | ----- | ----- | ----- |
| 0.0           | 0.88! | 0.88! | 0.41! | 0.41! |
| 1.4           | 0.89! | 0.90! | 0.43  | 0.42! |
| 2.8           | 0.90! | 0.90! | 0.49! | 0.46! |
| 4.2           | 0.92! | 0.90! | 0.53! | 0.50! |
| 5.6           | 0.91! | 0.90! | 0.52! | 0.50! |
| 7.0           | 0.88! | 0.87! | 0.46  | 0.45! |
| 8.4           | 0.85  | 0.85  | 0.41  | 0.36! |
| 9.8           | 0.83! | 0.83  | 0.40! | 0.30  |
| 11.2          | 0.86  | 0.79  | 0.45! | 0.30  |
| 12.6          | 0.88  | 0.73! | 0.48  | 0.36  |
| 14.0          | 0.77! | 0.60! | 0.29! | 0.40! |

## f/5.6 (stopped)

| Position (mm) | 10S   | 10M   | 30S   | 30M   |
| ------------- | ----- | ----- | ----- | ----- |
| 0.0           | 0.95  | 0.95  | 0.77! | 0.77! |
| 1.4           | 0.95  | 0.95  | 0.79  | 0.79! |
| 2.8           | 0.95  | 0.95  | 0.81  | 0.81  |
| 4.2           | 0.95  | 0.95  | 0.84! | 0.83  |
| 5.6           | 0.96! | 0.95  | 0.85  | 0.82! |
| 7.0           | 0.95  | 0.95  | 0.83  | 0.79  |
| 8.4           | 0.94  | 0.94  | 0.78  | 0.74! |
| 9.8           | 0.93! | 0.93! | 0.73  | 0.70  |
| 11.2          | 0.93! | 0.93! | 0.72  | 0.72  |
| 12.6          | 0.95! | 0.94  | 0.77  | 0.76  |
| 14.0          | 0.95  | 0.93! | 0.84  | 0.69  |

## Transcribing to GT

After updating the cells above, ask the agent to transcribe — or run from `tools/`:

```
py -m mtfdigitizer.eyeread ttartisan-50mm-f1-2 --apply
py -m mtfdigitizer.calibrate
```

The first command rewrites `_<LENS>_GT` in `tools/mtfdigitizer/referenceset/charts.py`. The second reports per-field median |Δ| and p95 |Δ| against the extractor's output. Median |Δ| under ~0.04 means the dispatch is calibrated; higher means an adjustment is needed.

The resulting GT tuple shape:

```python
_TTARTISAN_50_GT: GroundTruthCurves = {
    "max": {  # f/1.2
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
