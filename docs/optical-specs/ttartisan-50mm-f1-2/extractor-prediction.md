# Extractor prediction — TTartisan 50mm f/1.2

**NOT GROUND TRUTH.** This file holds the digitizer's reading of each sample position. It exists to save eye-read time for the maintainer: scan each cell against the source PNG, accept what looks right (no edit), overwrite what looks wrong.

Per [[feedback_agent_no_gt_eye_read]] only maintainer-validated values may land in `_<LENS>_GT` in `referenceset/charts.py`. After scanning this table, transcribe the validated values (adjusting any that disagree with the source) into the GT tuple.

Sample positions (mm, image_height_mm = 14.0): 0.0, 1.4, 2.8, 4.2, 5.6, 7.0, 8.4, 9.8, 11.2, 12.6, 14.0.

## f/1.2 (max)

| Position (mm) | 10S  | 10M  | 30S  | 30M  |
| ------------- | ---- | ---- | ---- | ---- |
| 0.0           | 0.88 | 0.88 | 0.41 | 0.41 |
| 1.4           | —    | 0.90 | 0.43 | 0.44 |
| 2.8           | —    | 0.90 | 0.46 | 0.49 |
| 4.2           | 0.90 | 0.91 | 0.50 | 0.53 |
| 5.6           | 0.89 | 0.91 | 0.50 | 0.53 |
| 7.0           | 0.87 | 0.89 | 0.46 | 0.47 |
| 8.4           | 0.85 | —    | 0.41 | 0.41 |
| 9.8           | 0.84 | —    | 0.39 | —    |
| 11.2          | 0.86 | —    | 0.46 | —    |
| 12.6          | 0.88 | —    | 0.48 | —    |
| 14.0          | —    | —    | 0.40 | —    |

## f/5.6 (stopped)

| Position (mm) | 10S  | 10M  | 30S  | 30M  |
| ------------- | ---- | ---- | ---- | ---- |
| 0.0           | 0.95 | 0.95 | 0.78 | 0.78 |
| 1.4           | 0.95 | 0.95 | 0.79 | —    |
| 2.8           | 0.95 | 0.95 | 0.81 | —    |
| 4.2           | 0.95 | 0.95 | 0.84 | 0.83 |
| 5.6           | 0.95 | 0.95 | 0.85 | 0.83 |
| 7.0           | 0.95 | 0.95 | 0.83 | 0.79 |
| 8.4           | 0.94 | 0.94 | 0.78 | 0.75 |
| 9.8           | 0.94 | 0.94 | 0.73 | 0.70 |
| 11.2          | 0.94 | 0.94 | 0.72 | 0.72 |
| 12.6          | 0.94 | 0.94 | 0.77 | 0.76 |
| 14.0          | 0.95 | 0.95 | 0.84 | 0.69 |

## After validation

Copy each column into the matching tuple in `tools/mtfdigitizer/referenceset/charts.py`:

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
