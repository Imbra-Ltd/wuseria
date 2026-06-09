# Eye-read — Fujifilm GF 23mm f/4 R LM WR

Tier 1 anchor for the `fujifilm-permfreq` style family. Cells below are pre-populated with the extractor's predictions. The maintainer reads each cell against the source PNG; per ADR-048 each cell has one of three states:

- bare number (`0.43`) — extractor's prediction, maintainer judged it fine (silent verification)
- number with `!` (`0.45!`) — maintainer-corrected; overrides the extractor's value
- number with `?` (`0.43?`) or bare `?` — maintainer hasn't read this cell; becomes `None` in the GT tuple

When the extractor is re-run and predictions change, this file preserves `!` and `?` marks and refreshes unmarked cells. The header text and legend are regenerated from the scaffolder.

Per [[feedback_agent_no_gt_eye_read]] the agent does NOT propose cell values of its own — the extractor predictions you see are mechanical readings, not eye-reads.

## Reading procedure

A helper rendering for each view with the 11 sample-position lines overlaid:

- `fujifilm-gf-23mm-f4-r-lm-wr-15lp-readhelper.png` — 15 lp/mm
- `fujifilm-gf-23mm-f4-r-lm-wr-20lp-readhelper.png` — 20 lp/mm
- `fujifilm-gf-23mm-f4-r-lm-wr-40lp-readhelper.png` — 40 lp/mm

The green vertical lines are spaced by image-height fraction, not by the chart's printed x-tick labels. Each line is labelled with its image-height mm value (image_height_mm = 26.9).

**Important:** the green vertical lines do NOT match the printed black tick labels (5/10/15/20/25). The chart's plot area spans 0..26.9 mm (the right gridline edge corresponds to ~26.9 mm — past Fujifilm's '25 mm' tick label by ~17 px); each green vertical line in the helper PNG is labelled with its mm value.

Sample positions (mm, image_height_mm = 26.9): 0.0, 2.7, 5.4, 8.1, 10.8, 13.4, 16.1, 18.8, 21.5, 24.2, 26.9.

Read each cell at the intersection of the green vertical sample line and the curve, against the printed horizontal gridlines. Eye precision is ±0.02 (half a gridline tick). Read to two decimals. Use `?` only when the curve genuinely does not extend to that x position.

- Top of plot area → MTF 1.0
- Each printed gridline below it → 0.8, 0.6, 0.4, 0.2
- Bottom gridline → MTF 0.0
- Orange dashed lines fill in every 0.05 between the printed gridlines

## 15 lp/mm

| Position (mm) | 15S   | 15M  |
| ------------- | ----- | ---- |
| 0.0           | 0.99  | 0.99 |
| 2.7           | 0.99  | 0.99 |
| 5.4           | 0.99  | 0.99 |
| 8.1           | 0.99  | 0.99 |
| 10.8          | 0.98  | 0.98 |
| 13.4          | 0.98  | 0.98 |
| 16.1          | 0.97  | 0.97 |
| 18.8          | 0.94  | 0.96 |
| 21.5          | 0.88  | 0.96 |
| 24.2          | 0.82  | 0.94 |
| 26.9          | 0.75! | 0.92 |

## 20 lp/mm

| Position (mm) | 20S  | 20M  |
| ------------- | ---- | ---- |
| 0.0           | 0.97 | 0.97 |
| 2.7           | 0.97 | 0.97 |
| 5.4           | 0.97 | 0.95 |
| 8.1           | 0.95 | 0.95 |
| 10.8          | 0.94 | 0.94 |
| 13.4          | 0.92 | 0.91 |
| 16.1          | 0.89 | 0.89 |
| 18.8          | 0.81 | 0.89 |
| 21.5          | 0.71 | 0.89 |
| 24.2          | 0.63 | 0.86 |
| 26.9          | 0.58 | 0.79 |

## 40 lp/mm

| Position (mm) | 40S   | 40M   |
| ------------- | ----- | ----- |
| 0.0           | 0.89  | 0.89  |
| 2.7           | 0.90  | 0.90  |
| 5.4           | 0.88  | 0.86  |
| 8.1           | 0.84  | 0.84  |
| 10.8          | 0.79  | 0.82  |
| 13.4          | 0.74  | 0.72  |
| 16.1          | 0.71  | 0.73  |
| 18.8          | 0.67  | 0.71  |
| 21.5          | 0.60  | 0.74  |
| 24.2          | 0.53  | 0.70  |
| 26.9          | 0.46! | 0.53! |

## Transcribing to GT

After updating the cells above, ask the agent to transcribe — or run from `tools/`:

```
py -m mtfdigitizer.eyeread fujifilm-gf-23mm-f4-r-lm-wr --apply
py -m mtfdigitizer.calibrate
```

The first command rewrites `_<LENS>_GT` in `tools/mtfdigitizer/referenceset/charts.py`. The second reports per-field median |Δ| and p95 |Δ| against the extractor's output. Median |Δ| under ~0.04 means the dispatch is calibrated; higher means an adjustment is needed.

The resulting GT tuple shape:

```python
_FUJI_GF_23_GT: GroundTruthCurves = {
    "f/4": {
        "freq15S": (...11 values from the 15S column...),
        "freq15M": (...11 values from the 15M column...),
        "freq20S": (...11 values from the 20S column...),
        "freq20M": (...11 values from the 20M column...),
        "freq40S": (...11 values from the 40S column...),
        "freq40M": (...11 values from the 40M column...),
    },
}
```
