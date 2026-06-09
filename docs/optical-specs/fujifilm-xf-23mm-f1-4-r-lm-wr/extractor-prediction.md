# Extractor prediction — Fujifilm XF 23mm f/1.4 R LM WR

**NOT GROUND TRUTH.** This file holds the digitizer's reading of each sample position. It exists to save eye-read time for the maintainer: scan each cell against the source PNG, accept what looks right (no edit), overwrite what looks wrong.

Per [[feedback_agent_no_gt_eye_read]] only maintainer-validated values may land in `_<LENS>_GT` in `referenceset/charts.py`. After scanning this table, transcribe the validated values (adjusting any that disagree with the source) into the GT tuple.

Sample positions (mm, image_height_mm = 14.2): 0.0, 1.4, 2.8, 4.3, 5.7, 7.1, 8.5, 9.9, 11.4, 12.8, 14.2.

## 15 lp/mm

| Position (mm) | 15S  | 15M  |
| ------------- | ---- | ---- |
| 0.0           | 0.96 | 0.96 |
| 1.4           | —    | —    |
| 2.8           | 0.95 | 0.95 |
| 4.3           | 0.95 | 0.96 |
| 5.7           | 0.93 | 0.96 |
| 7.1           | 0.91 | 0.96 |
| 8.5           | 0.88 | 0.95 |
| 9.9           | 0.85 | 0.94 |
| 11.4          | 0.83 | 0.94 |
| 12.8          | 0.82 | 0.92 |
| 14.2          | 0.81 | 0.86 |

## 45 lp/mm

| Position (mm) | 45S  | 45M  |
| ------------- | ---- | ---- |
| 0.0           | 0.80 | 0.80 |
| 1.4           | 0.79 | 0.75 |
| 2.8           | 0.76 | 0.72 |
| 4.3           | 0.73 | 0.72 |
| 5.7           | 0.66 | 0.72 |
| 7.1           | 0.58 | 0.72 |
| 8.5           | 0.53 | 0.69 |
| 9.9           | 0.51 | 0.68 |
| 11.4          | 0.53 | 0.67 |
| 12.8          | 0.56 | 0.60 |
| 14.2          | 0.58 | 0.48 |

## After validation

Copy each column into the matching tuple in `tools/mtfdigitizer/referenceset/charts.py`:

```python
_FUJI_XF_23_GT: GroundTruthCurves = {
    "f/1.4": {
        "freq15S": (...11 values from the 15S column...),
        "freq15M": (...11 values from the 15M column...),
        "freq45S": (...11 values from the 45S column...),
        "freq45M": (...11 values from the 45M column...),
    },
}
```
