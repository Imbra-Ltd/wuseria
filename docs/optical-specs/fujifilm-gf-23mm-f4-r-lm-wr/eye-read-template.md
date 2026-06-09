# Eye-read template — Fujifilm GF 23mm f/4 R LM WR

Tier 1 anchor for the `fujifilm-permfreq` style family. Maintainer fills in the MTF values below by reading the source PNG(s) against the printed gridlines, then copies the tuples into `_<LENS>_GT` in `tools/mtfdigitizer/referenceset/charts.py`.

Per [[feedback_agent_no_gt_eye_read]] the agent does NOT fill these in.

## Reading procedure

A helper rendering for each view with the 11 sample-position lines overlaid:

- `fujifilm-gf-23mm-f4-r-lm-wr-15lp-readhelper.png` — 15 lp/mm
- `fujifilm-gf-23mm-f4-r-lm-wr-20lp-readhelper.png` — 20 lp/mm
- `fujifilm-gf-23mm-f4-r-lm-wr-40lp-readhelper.png` — 40 lp/mm

The green vertical lines are spaced by image-height fraction, not by the chart's printed x-tick labels. Each line is labelled with its image-height mm value (image_height_mm = 26.9).

**Important:** the green vertical lines do NOT match the printed black tick labels (5/10/15/20/25). The chart's plot area spans 0..26.9 mm (the right gridline edge corresponds to ~26.9 mm — past Fujifilm's '25 mm' tick label by ~17 px); each green vertical line in the helper PNG is labelled with its mm value.

Sample positions (mm, image_height_mm = 26.9): 0.0, 2.7, 5.4, 8.1, 10.8, 13.4, 16.1, 18.8, 21.5, 24.2, 26.9.

Read each cell at the intersection of the green vertical sample line and the curve, against the printed horizontal gridlines. Eye precision is ±0.02 (half a gridline tick). Read to two decimals. Use `None` only when the curve genuinely does not extend to that x position.

- Top of plot area → MTF 1.0
- Each printed gridline below it → 0.8, 0.6, 0.4, 0.2
- Bottom gridline → MTF 0.0
- Orange dashed lines fill in every 0.05 between the printed gridlines

## Fill-in tables

### 15 lp/mm

| Position (mm) | 15S | 15M |
| ------------- | --- | --- |
| 0.0           |     |     |
| 2.7           |     |     |
| 5.4           |     |     |
| 8.1           |     |     |
| 10.8          |     |     |
| 13.4          |     |     |
| 16.1          |     |     |
| 18.8          |     |     |
| 21.5          |     |     |
| 24.2          |     |     |
| 26.9          |     |     |

### 20 lp/mm

| Position (mm) | 20S | 20M |
| ------------- | --- | --- |
| 0.0           |     |     |
| 2.7           |     |     |
| 5.4           |     |     |
| 8.1           |     |     |
| 10.8          |     |     |
| 13.4          |     |     |
| 16.1          |     |     |
| 18.8          |     |     |
| 21.5          |     |     |
| 24.2          |     |     |
| 26.9          |     |     |

### 40 lp/mm

| Position (mm) | 40S | 40M |
| ------------- | --- | --- |
| 0.0           |     |     |
| 2.7           |     |     |
| 5.4           |     |     |
| 8.1           |     |     |
| 10.8          |     |     |
| 13.4          |     |     |
| 16.1          |     |     |
| 18.8          |     |     |
| 21.5          |     |     |
| 24.2          |     |     |
| 26.9          |     |     |

## After filling in

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

Then run from `tools/`:

```
py -m mtfdigitizer.calibrate
```

The runner reports per-field median |Δ| and p95 |Δ| against the extractor's output. Median |Δ| under ~0.04 means the dispatch is calibrated; higher means an adjustment is needed.
