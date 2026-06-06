# Extractor prediction — Fujifilm GF 23mm f/4 R LM WR

**NOT GROUND TRUTH.** This file holds the digitizer's reading of
each sample position. It exists to save eye-read time for the
maintainer: scan each cell against the source PNG, accept what
looks right (no edit), overwrite what looks wrong.

Per [[feedback_agent_no_gt_eye_read]] only maintainer-validated
values may land in `_FUJI_GF_23_GT` in `referenceset/charts.py`.
After you've scanned this table, transcribe the validated values
(adjusting any that disagree with the source) into the GT tuple.

Source charts:

- `fujifilm-gf-23mm-f4-r-lm-wr-15lp.png`
- `fujifilm-gf-23mm-f4-r-lm-wr-20lp.png`
- `fujifilm-gf-23mm-f4-r-lm-wr-40lp.png`

Sample positions (mm, image_height_mm = 26.9):
0.0, 2.7, 5.4, 8.1, 10.8, 13.4, 16.1, 18.8, 21.5, 24.2, 26.9.

Read each cell against the source PNG's printed gridlines
(MTF 0.0 at the bottom dark axis, 0.2/0.4/0.6/0.8 at light grids,
1.0 at the top of the curve area).

## f/4

| Position (mm) | 15S  | 15M  | 20S  | 20M  | 40S  | 40M  |
| ------------- | ---- | ---- | ---- | ---- | ---- | ---- |
| 0.0           | 0.99 | 0.99 | 0.97 | 0.97 | 0.89 | 0.89 |
| 2.7           | 0.99 | 0.99 | 0.97 | 0.97 | 0.90 | —    |
| 5.4           | 0.99 | 0.99 | 0.97 | 0.95 | 0.88 | 0.86 |
| 8.1           | 0.99 | 0.99 | 0.95 | —    | 0.84 | 0.84 |
| 10.8          | 0.98 | 0.98 | 0.94 | 0.94 | 0.79 | 0.82 |
| 13.4          | 0.98 | 0.98 | 0.92 | 0.91 | 0.74 | 0.72 |
| 16.1          | 0.97 | 0.97 | 0.89 | —    | 0.71 | 0.73 |
| 18.8          | 0.94 | 0.96 | 0.81 | 0.89 | 0.67 | 0.71 |
| 21.5          | 0.88 | 0.96 | 0.71 | 0.89 | 0.60 | 0.74 |
| 24.2          | 0.82 | 0.94 | 0.63 | 0.86 | 0.53 | 0.70 |
| 26.9          | 0.76 | 0.92 | 0.58 | 0.79 | 0.48 | 0.56 |

## After validation

Copy each S/M column (11 values, top → bottom) into the matching
tuple in `tools/mtfdigitizer/referenceset/charts.py`:

```python
_FUJI_GF_23_GT: GroundTruthCurves = {
    "f/4": {
        "freq15S": (...11 values from the 15S column...),
        "freq15M": (...),
        "freq20S": (...),
        "freq20M": (...),
        "freq40S": (...),
        "freq40M": (...),
    },
}
```
