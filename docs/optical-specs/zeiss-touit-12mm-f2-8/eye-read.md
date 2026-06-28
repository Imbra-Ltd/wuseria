# Eye-read — zeiss-touit-12mm-f2-8

Tier 1 anchor for the `multifreq-press-kit` style family. Cells below are pre-populated with the extractor's predictions. The maintainer reads each cell against the source PNG; per ADR-048 each cell has one of three states:

- bare number (`0.43`) — extractor's prediction, maintainer judged it fine (silent verification)
- number with `!` (`0.45!`) — maintainer-corrected; overrides the extractor's value
- number with `?` (`0.43?`) or bare `?` — maintainer hasn't read this cell; becomes `None` in the GT tuple

When the extractor is re-run and predictions change, this file preserves `!` and `?` marks and refreshes unmarked cells. The header text and legend are regenerated from the scaffolder.

Per [[feedback_agent_no_gt_eye_read]] the agent does NOT propose cell values of its own — the extractor predictions you see are mechanical readings, not eye-reads.

## Reading procedure

A helper rendering for each view with the 11 sample-position lines overlaid:

- `zeiss-touit-12mm-f2-8-mtf-max-readhelper.png` — max (max)
- `zeiss-touit-12mm-f2-8-mtf-stopped-readhelper.png` — stopped (stopped)

The green vertical lines are spaced by image-height fraction, not by the chart's printed x-tick labels. Each line is labelled with its image-height mm value (image_height_mm = 15.0).

**Important:** both apertures are packed into one chart as two stacked panels — top panel is the max-aperture pass (max), bottom panel is the stopped-aperture pass (stopped). All curves are monochrome black; solid lines are sagittal (S), dashed (or dotted, on the 50mm macro) are tangential (M). Within each panel the three frequencies stack vertically: 10 lp/mm highest, 20 lp/mm middle, 40 lp/mm lowest at the optical centre. Per ADR-046 the helper PNG shows the **clean source chart** (no extractor overlay) so the eye-read is unbiased. The green sample lines span the full plot regardless of panel.

Sample positions (mm, image_height_mm = 15.0): 0.0, 1.5, 3.0, 4.5, 6.0, 7.5, 9.0, 10.5, 12.0, 13.5, 15.0.

Read each cell at the intersection of the green vertical sample line and the curve, against the printed horizontal gridlines. Eye precision is ±0.02 (half a gridline tick). Read to two decimals. Use `?` only when the curve genuinely does not extend to that x position.

- Top of plot area → MTF 1.0
- Each printed gridline below it → 0.8, 0.6, 0.4, 0.2
- Bottom gridline → MTF 0.0
- Orange dashed lines fill in every 0.05 between the printed gridlines

## max (max)

| Position (mm) | 10S  | 10M  | 20S  | 20M  | 40S  | 40M  |
| ------------- | ---- | ---- | ---- | ---- | ---- | ---- |
| 0.0           | 0.96 | 0.96 | 0.91 | 0.91 | 0.91 | 0.91 |
| 1.5           | 0.96 | —    | 0.90 | 0.80 | —    | —    |
| 3.0           | 0.96 | —    | 0.89 | 0.79 | —    | 0.77 |
| 4.5           | 0.96 | —    | 0.89 | 0.76 | —    | 0.74 |
| 6.0           | 0.96 | —    | 0.90 | 0.73 | —    | 0.69 |
| 7.5           | 0.95 | —    | 0.88 | 0.70 | —    | —    |
| 9.0           | 0.94 | 0.94 | 0.85 | 0.66 | 0.83 | 0.63 |
| 10.5          | 0.94 | 0.90 | 0.83 | —    | 0.76 | 0.61 |
| 12.0          | 0.91 | 0.83 | —    | —    | 0.64 | 0.53 |
| 13.5          | 0.85 | —    | —    | —    | 0.50 | —    |
| 15.0          | —    | —    | —    | —    | —    | —    |

## stopped (stopped)

| Position (mm) | 10S  | 10M  | 20S  | 20M  | 40S  | 40M  |
| ------------- | ---- | ---- | ---- | ---- | ---- | ---- |
| 0.0           | 0.95 | 0.95 | 0.91 | 0.91 | 0.84 | 0.84 |
| 1.5           | 0.95 | —    | 0.90 | —    | 0.82 | 0.81 |
| 3.0           | 0.94 | —    | 0.89 | —    | 0.80 | 0.78 |
| 4.5           | 0.94 | —    | 0.88 | —    | 0.77 | 0.74 |
| 6.0           | 0.93 | —    | 0.86 | —    | 0.73 | 0.68 |
| 7.5           | 0.93 | —    | 0.85 | —    | 0.71 | 0.64 |
| 9.0           | 0.93 | —    | 0.86 | —    | 0.72 | —    |
| 10.5          | 0.94 | 0.93 | 0.86 | 0.84 | 0.74 | 0.63 |
| 12.0          | —    | 0.92 | 0.86 | —    | 0.75 | —    |
| 13.5          | —    | 0.90 | 0.81 | —    | 0.65 | —    |
| 15.0          | —    | —    | —    | —    | —    | —    |

## Transcribing to GT

After updating the cells above, ask the agent to transcribe — or run from `tools/`:

```
py -m mtfdigitizer.eyeread zeiss-touit-12mm-f2-8 --apply
py -m mtfdigitizer.calibrate
```

The first command rewrites `_<LENS>_GT` in `tools/mtfdigitizer/referenceset/charts.py`. The second reports per-field median |Δ| and p95 |Δ| against the extractor's output. Median |Δ| under ~0.04 means the dispatch is calibrated; higher means an adjustment is needed.

The resulting GT tuple shape:

```python
_ZEISS_TOUIT_12_GT: GroundTruthCurves = {
    "max": {  # max
        "freq10S": (...11 values from the 10S column...),
        "freq10M": (...11 values from the 10M column...),
        "freq20S": (...11 values from the 20S column...),
        "freq20M": (...11 values from the 20M column...),
        "freq40S": (...11 values from the 40S column...),
        "freq40M": (...11 values from the 40M column...),
    },
    "stopped": {  # stopped
        "freq10S": (...11 values from the 10S column...),
        "freq10M": (...11 values from the 10M column...),
        "freq20S": (...11 values from the 20S column...),
        "freq20M": (...11 values from the 20M column...),
        "freq40S": (...11 values from the 40S column...),
        "freq40M": (...11 values from the 40M column...),
    },
}
```
