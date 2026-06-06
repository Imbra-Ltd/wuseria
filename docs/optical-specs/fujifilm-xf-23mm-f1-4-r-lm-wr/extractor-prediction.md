# Extractor prediction — Fujifilm XF 23mm f/1.4 R LM WR

**NOT GROUND TRUTH.** Digitizer output for maintainer validation.
Scan each cell against the source PNG, accept what looks right,
overwrite what looks wrong.

Per [[feedback_agent_no_gt_eye_read]] only maintainer-validated
values may land in `_FUJI_XF_23_GT` in `referenceset/charts.py`.

Source charts:

- `fujifilm-xf-23mm-f1-4-r-lm-wr-15lp.png`
- `fujifilm-xf-23mm-f1-4-r-lm-wr-45lp.png`

Sample positions (mm, image_height_mm = 14.2):
0.0, 1.4, 2.8, 4.3, 5.7, 7.1, 8.5, 9.9, 11.4, 12.8, 14.2.

Read each cell against the source PNG's printed gridlines
(MTF 0.0 at the bottom dark axis, 0.2/0.4/0.6/0.8 at light grids,
1.0 at the top of the curve area).

## f/1.4

| Position (mm) | 15S  | 15M  | 45S  | 45M  |
| ------------- | ---- | ---- | ---- | ---- |
| 0.0           | 0.96 | 0.96 | 0.80 | 0.80 |
| 1.4           | —    | —    | 0.79 | 0.75 |
| 2.8           | 0.95 | 0.95 | 0.76 | 0.72 |
| 4.3           | 0.95 | 0.96 | 0.73 | 0.72 |
| 5.7           | 0.93 | 0.96 | 0.66 | 0.72 |
| 7.1           | 0.91 | 0.96 | 0.58 | 0.72 |
| 8.5           | 0.88 | 0.95 | 0.53 | 0.69 |
| 9.9           | 0.85 | 0.94 | 0.51 | 0.68 |
| 11.4          | 0.83 | 0.94 | 0.53 | 0.67 |
| 12.8          | 0.82 | 0.92 | 0.56 | 0.60 |
| 14.2          | 0.81 | 0.86 | 0.58 | 0.48 |

## After validation

```python
_FUJI_XF_23_GT: GroundTruthCurves = {
    "f/1.4": {
        "freq15S": (...11 values...),
        "freq15M": (...),
        "freq45S": (...),
        "freq45M": (...),
    },
}
```
