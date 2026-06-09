# Extractor prediction — Fujifilm GF 23mm f/4 R LM WR

**NOT GROUND TRUTH.** This file holds the digitizer's reading of each sample position. It exists to save eye-read time for the maintainer: scan each cell against the source PNG, accept what looks right (no edit), overwrite what looks wrong.

Per [[feedback_agent_no_gt_eye_read]] only maintainer-validated values may land in `_<LENS>_GT` in `referenceset/charts.py`. After scanning this table, transcribe the validated values (adjusting any that disagree with the source) into the GT tuple.

Sample positions (mm, image_height_mm = 26.9): 0.0, 2.7, 5.4, 8.1, 10.8, 13.4, 16.1, 18.8, 21.5, 24.2, 26.9.

## 15 lp/mm

| Position (mm) | 15S  | 15M  |
| ------------- | ---- | ---- |
| 0.0           | 0.99 | 0.99 |
| 2.7           | 0.99 | 0.99 |
| 5.4           | 0.99 | 0.99 |
| 8.1           | 0.99 | 0.99 |
| 10.8          | 0.98 | 0.98 |
| 13.4          | 0.98 | 0.98 |
| 16.1          | 0.97 | 0.97 |
| 18.8          | 0.94 | 0.96 |
| 21.5          | 0.88 | 0.96 |
| 24.2          | 0.82 | 0.94 |
| 26.9          | 0.76 | 0.92 |

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

| Position (mm) | 40S  | 40M  |
| ------------- | ---- | ---- |
| 0.0           | 0.89 | 0.89 |
| 2.7           | 0.90 | 0.90 |
| 5.4           | 0.88 | 0.86 |
| 8.1           | 0.84 | 0.84 |
| 10.8          | 0.79 | 0.82 |
| 13.4          | 0.74 | 0.72 |
| 16.1          | 0.71 | 0.73 |
| 18.8          | 0.67 | 0.71 |
| 21.5          | 0.60 | 0.74 |
| 24.2          | 0.53 | 0.70 |
| 26.9          | 0.48 | 0.56 |

## After validation

Copy each column into the matching tuple in `tools/mtfdigitizer/referenceset/charts.py`:

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
