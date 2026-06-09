# Eye-read template — TTartisan 50mm f/1.2

Tier 1 anchor for the `ttartisan-4color-dual-aperture` style family. Maintainer fills in the MTF values below by reading the source PNG(s) against the printed gridlines, then copies the tuples into `_<LENS>_GT` in `tools/mtfdigitizer/referenceset/charts.py`.

Per [[feedback_agent_no_gt_eye_read]] the agent does NOT fill these in.

## Reading procedure

A helper rendering for each view with the 11 sample-position lines overlaid:

- `ttartisan-50mm-f1-2-mtf-max-readhelper.png` — f/1.2 (max)
- `ttartisan-50mm-f1-2-mtf-stopped-readhelper.png` — f/5.6 (stopped)

The green vertical lines are spaced by image-height fraction, not by the chart's printed x-tick labels. Each line is labelled with its image-height mm value (image_height_mm = 14.0).

**Important:** both apertures are packed into one chart by color encoding — black/grey curves are the max-aperture pass (f/1.2), red/orange curves are the stopped-aperture pass (f/5.6). One helper PNG per aperture has the target aperture's traced curves marked by the extractor; read against those, not the other aperture's curves. The green sample lines span the full plot regardless of aperture.

Sample positions (mm, image_height_mm = 14.0): 0.0, 1.4, 2.8, 4.2, 5.6, 7.0, 8.4, 9.8, 11.2, 12.6, 14.0.

Read each cell at the intersection of the green vertical sample line and the curve, against the printed horizontal gridlines. Eye precision is ±0.02 (half a gridline tick). Read to two decimals. Use `None` only when the curve genuinely does not extend to that x position.

- Top of plot area → MTF 1.0
- Each printed gridline → 0.1 OTF spacing (every line carries a y-axis label)
- Bottom gridline → MTF 0.0

## Fill-in tables

### f/1.2 (max)

| Position (mm) | 10S | 10M | 30S | 30M |
| ------------- | --- | --- | --- | --- |
| 0.0           |     |     |     |     |
| 1.4           |     |     |     |     |
| 2.8           |     |     |     |     |
| 4.2           |     |     |     |     |
| 5.6           |     |     |     |     |
| 7.0           |     |     |     |     |
| 8.4           |     |     |     |     |
| 9.8           |     |     |     |     |
| 11.2          |     |     |     |     |
| 12.6          |     |     |     |     |
| 14.0          |     |     |     |     |

### f/5.6 (stopped)

| Position (mm) | 10S | 10M | 30S | 30M |
| ------------- | --- | --- | --- | --- |
| 0.0           |     |     |     |     |
| 1.4           |     |     |     |     |
| 2.8           |     |     |     |     |
| 4.2           |     |     |     |     |
| 5.6           |     |     |     |     |
| 7.0           |     |     |     |     |
| 8.4           |     |     |     |     |
| 9.8           |     |     |     |     |
| 11.2          |     |     |     |     |
| 12.6          |     |     |     |     |
| 14.0          |     |     |     |     |

## After filling in

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

Then run from `tools/`:

```
py -m mtfdigitizer.calibrate
```

The runner reports per-field median |Δ| and p95 |Δ| against the extractor's output. Median |Δ| under ~0.04 means the dispatch is calibrated; higher means an adjustment is needed.
