# Eye-read template — Fujifilm GF 23mm f/4 R LM WR

Tier 1 anchor for the `fujifilm-permfreq` style family (ADR-043).
Maintainer fills in the MTF values below by reading the source PNGs
against the printed gridlines, then copies the tuples into
`_FUJI_GF_23_GT` in `tools/mtfdigitizer/referenceset/charts.py`.

Per [[feedback_agent_no_gt_eye_read]] the agent does NOT fill these in.

## Reading procedure

Three charts, one per spatial frequency:

- `fujifilm-gf-23mm-f4-r-lm-wr-15lp.png`
- `fujifilm-gf-23mm-f4-r-lm-wr-20lp.png`
- `fujifilm-gf-23mm-f4-r-lm-wr-40lp.png`

A helper rendering with the 11 sample-position lines overlaid is in
`*-readhelper.png`. **Important:** the green vertical lines do NOT
match the printed black tick labels (5/10/15/20/25). The chart's
plot area spans 0..26.9 mm (the right gridline edge corresponds to
~26.9 mm — past Fujifilm's "25 mm" tick label by ~17 px), and the
digitizer samples at 11 evenly-spaced fractions: image-height
positions 0.0, 2.7, 5.4, 8.1, 10.8, 13.4, 16.1, 18.8, 21.5, 24.2,
26.9 mm. Each green vertical line in the helper PNG is labelled
with its mm value.

Read each value at the intersection of the green vertical sample line
and the curve, against the printed horizontal gridlines:

- Top of plot area → MTF 1.0
- Each printed gridline below it → 0.8, 0.6, 0.4, 0.2
- Bottom gridline → MTF 0.0

Eye precision is ±0.02 (half a gridline tick is 0.10). Read to two
decimals. Use `None` only when the curve genuinely does not extend
to that x position (the curve ends before the right edge); if the
curve is present but hard to disambiguate from the sister, read it
anyway and the calibration runner will report the Δ.

## Fill-in table

Aperture: f/4 (single max aperture, no F8 panel).

Sample positions in mm (image_height_mm = 26.9, fractions 0.0..1.0):
0.0, 2.7, 5.4, 8.1, 10.8, 13.4, 16.1, 18.8, 21.5, 24.2, 26.9.

| Position (mm) | 15S | 15M | 20S | 20M | 40S | 40M |
| ------------- | --- | --- | --- | --- | --- | --- |
| 0.0           |     |     |     |     |     |     |
| 2.7           |     |     |     |     |     |     |
| 5.4           |     |     |     |     |     |     |
| 8.1           |     |     |     |     |     |     |
| 10.8          |     |     |     |     |     |     |
| 13.4          |     |     |     |     |     |     |
| 16.1          |     |     |     |     |     |     |
| 18.8          |     |     |     |     |     |     |
| 21.5          |     |     |     |     |     |     |
| 24.2          |     |     |     |     |     |     |
| 26.9          |     |     |     |     |     |     |

## After filling in

Copy each column into the matching tuple in
`tools/mtfdigitizer/referenceset/charts.py`:

```python
_FUJI_GF_23_GT: GroundTruthCurves = {
    "f/4": {
        "freq15S": (...11 values from the 15S column...),
        "freq15M": (...11 values from the 15M column...),
        "freq20S": (...),
        "freq20M": (...),
        "freq40S": (...),
        "freq40M": (...),
    },
}
```

Then run from `tools/`:

```
py -m mtfdigitizer.calibrate
```

The runner will report per-field median |Δ| and p95 |Δ| against
the extractor's output. Median |Δ| under ~0.04 means the dispatch
is calibrated; higher means an adjustment is needed.
