# Eye-read template — Fujifilm XF 23mm f/1.4 R LM WR

Tier 1 anchor for the `fujifilm-permfreq` style family. Maintainer fills in the MTF values below by reading the source PNG(s) against the printed gridlines, then copies the tuples into `_<LENS>_GT` in `tools/mtfdigitizer/referenceset/charts.py`.

Per [[feedback_agent_no_gt_eye_read]] the agent does NOT fill these in.

## Reading procedure

A helper rendering for each view with the 11 sample-position lines overlaid:

- `fujifilm-xf-23mm-f1-4-r-lm-wr-15lp-readhelper.png` — 15 lp/mm
- `fujifilm-xf-23mm-f1-4-r-lm-wr-45lp-readhelper.png` — 45 lp/mm

The green vertical lines are spaced by image-height fraction, not by the chart's printed x-tick labels. Each line is labelled with its image-height mm value (image_height_mm = 14.2).

**Important:** the green vertical lines do NOT match the printed black tick labels (0, 5, 10, 14.2). The chart's plot area spans 0..14.2 mm (the right gridline edge corresponds to 14.2 mm, matching the APS-C 23.5x15.6 mm sensor half-diagonal); each green vertical line in the helper PNG is labelled with its mm value.

Sample positions (mm, image_height_mm = 14.2): 0.0, 1.4, 2.8, 4.3, 5.7, 7.1, 8.5, 9.9, 11.4, 12.8, 14.2.

Read each cell at the intersection of the green vertical sample line and the curve, against the printed horizontal gridlines. Eye precision is ±0.02 (half a gridline tick). Read to two decimals. Use `None` only when the curve genuinely does not extend to that x position.

- Top of plot area → MTF 1.0
- Each printed gridline below it → 0.8, 0.6, 0.4, 0.2
- Bottom gridline → MTF 0.0

## Fill-in tables

### 15 lp/mm

| Position (mm) | 15S | 15M |
| ------------- | --- | --- |
| 0.0           |     |     |
| 1.4           |     |     |
| 2.8           |     |     |
| 4.3           |     |     |
| 5.7           |     |     |
| 7.1           |     |     |
| 8.5           |     |     |
| 9.9           |     |     |
| 11.4          |     |     |
| 12.8          |     |     |
| 14.2          |     |     |

### 45 lp/mm

| Position (mm) | 45S | 45M |
| ------------- | --- | --- |
| 0.0           |     |     |
| 1.4           |     |     |
| 2.8           |     |     |
| 4.3           |     |     |
| 5.7           |     |     |
| 7.1           |     |     |
| 8.5           |     |     |
| 9.9           |     |     |
| 11.4          |     |     |
| 12.8          |     |     |
| 14.2          |     |     |

## After filling in

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

Then run from `tools/`:

```
py -m mtfdigitizer.calibrate
```

The runner reports per-field median |Δ| and p95 |Δ| against the extractor's output. Median |Δ| under ~0.04 means the dispatch is calibrated; higher means an adjustment is needed.
