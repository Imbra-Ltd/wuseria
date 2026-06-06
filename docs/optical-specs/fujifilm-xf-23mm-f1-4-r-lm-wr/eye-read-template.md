# Eye-read template — Fujifilm XF 23mm f/1.4 R LM WR

Second Tier 1 anchor for the `fujifilm-permfreq` style family
(ADR-043, ADR-041). The XF (APS-C) cohort uses a different image
height (14.2 mm) and different frequencies (15 + 45 lp/mm) than
the GF (medium-format) cohort, so a dedicated anchor cross-validates
the dispatch against the XF body of charts.

Per [[feedback_agent_no_gt_eye_read]] the agent does NOT fill these
in — placeholders are in `_FUJI_XF_23_GT` in
`tools/mtfdigitizer/referenceset/charts.py` until you enter the values.

## Reading procedure

Two charts, one per spatial frequency:

- `fujifilm-xf-23mm-f1-4-r-lm-wr-15lp.png`
- `fujifilm-xf-23mm-f1-4-r-lm-wr-45lp.png`

A helper rendering with the 11 sample-position lines overlaid is in
`*-readhelper.png`. **Important:** the green vertical lines do NOT
match the printed black tick labels (0, 5, 10, 14.2). The chart's
plot area spans 0..14.2 mm (the right gridline edge corresponds to
14.2 mm, matching the APS-C 23.5×15.6 mm sensor half-diagonal), and
the digitizer samples at 11 evenly-spaced fractions: image-height
positions 0.0, 1.4, 2.8, 4.3, 5.7, 7.1, 8.5, 9.9, 11.4, 12.8, 14.2 mm.
Each green vertical line in the helper PNG is labelled with its mm
value.

Read each value at the intersection of the green vertical sample
line and the curve, against the printed horizontal gridlines:

- Top of plot area (light blue rectangle's top edge) → MTF 1.0
- Each printed light gridline below it → 0.8, 0.6, 0.4, 0.2
- Bottom dark x-axis line → MTF 0.0

Eye precision is ±0.02 (half a gridline tick is 0.10). Read to two
decimals. Use `None` only when the curve genuinely does not extend
to that x position.

## Fill-in table

Aperture: f/1.4 (single max aperture).

Sample positions in mm (image_height_mm = 14.2, fractions 0.0..1.0):
0.0, 1.4, 2.8, 4.3, 5.7, 7.1, 8.5, 9.9, 11.4, 12.8, 14.2.

| Position (mm) | 15S  | 15M  | 45S  | 45M  |
| ------------- | ---- | ---- | ---- | ---- |
| 0.0           | 0.96 | 0.96 | 0.81 | 0.81 |
| 1.4           | 0.95 | 0.95 | 0.78 | 0.75 |
| 2.8           | 0.94 | 0.94 | 0.75 | 0.71 |
| 4.3           | 0.93 | 0.95 | 0.72 | 0.72 |
| 5.7           | 0.92 | 0.96 | 0.65 | 0.73 |
| 7.1           | 0.90 | 0.96 | 0.58 | 0.72 |
| 8.5           | 0.87 | 0.95 |      |      |
| 9.9           | 0.85 | 0.95 |      |      |
| 11.4          | 0.83 | 0.95 |      |      |
| 12.8          | 0.82 | 0.91 |      |      |
| 14.2          | 0.81 | 0.85 |      |      |

## After filling in

Copy each column into the matching tuple in
`tools/mtfdigitizer/referenceset/charts.py:_FUJI_XF_23_GT`:

```python
_FUJI_XF_23_GT: GroundTruthCurves = {
    "f/1.4": {
        "freq15S": (...11 values from the 15S column...),
        "freq15M": (...11 values from the 15M column...),
        "freq45S": (...),
        "freq45M": (...),
    },
}
```

Then run from `tools/`:

```
py -m mtfdigitizer.calibrate
```

The runner reports per-field median |Δ| and p95 |Δ| against the
extractor's output. Median |Δ| under ~0.04 means the dispatch is
calibrated; higher means an adjustment is needed.
