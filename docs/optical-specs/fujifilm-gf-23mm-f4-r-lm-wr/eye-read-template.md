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
`*-readhelper.png` (gridlines superimposed at the 11 image-height
positions 0, 2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20, 22.5, 25 mm).

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

Sample positions in mm: 0.0, 2.5, 5.0, 7.5, 10.0, 12.5, 15.0, 17.5,
20.0, 22.5, 25.0.

| Position (mm) | 15S | 15M | 20S | 20M | 40S | 40M |
| ------------- | --- | --- | --- | --- | --- | --- |
| 0.0           |     |     |     |     |     |     |
| 2.5           |     |     |     |     |     |     |
| 5.0           |     |     |     |     |     |     |
| 7.5           |     |     |     |     |     |     |
| 10.0          |     |     |     |     |     |     |
| 12.5          |     |     |     |     |     |     |
| 15.0          |     |     |     |     |     |     |
| 17.5          |     |     |     |     |     |     |
| 20.0          |     |     |     |     |     |     |
| 22.5          |     |     |     |     |     |     |
| 25.0          |     |     |     |     |     |     |

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
