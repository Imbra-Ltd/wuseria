# scripts/

One-shot maintenance scripts for the digitizer reference set. Not part
of the runtime pipeline; used to bootstrap new brand families.

## scaffold_fuji_tier2

Auto-detect plot boxes for every Fujifilm lens that publishes MTF
charts, and emit a `_fuji_tier2_charts.py` module of Tier 2
`ReferenceChart` entries that the production extractor consumes.

### Usage

```
cd tools

# 1. Preview: print the scaffolded module to stdout.
py -m mtfdigitizer.scripts.scaffold_fuji_tier2

# 2. Write: materialize the module on disk.
py -m mtfdigitizer.scripts.scaffold_fuji_tier2 --write
```

### Workflow

The scaffolder is intended to run **after** both Fujifilm Tier 1
anchors (`fujifilm-gf-23mm-f4-r-lm-wr` and
`fujifilm-xf-23mm-f1-4-r-lm-wr`) have eye-read ground truth filled in
and the calibration runner confirms the dispatch is calibrated for
both the GF and XF cohorts. Then:

1. `py -m mtfdigitizer.scripts.scaffold_fuji_tier2 --write` —
   materialize `_fuji_tier2_charts.py` (60 lenses, ~193 charts).
2. Add `from ._fuji_tier2_charts import FUJI_TIER2_CHARTS` to
   `charts.py` and concatenate into `REFERENCE_CHARTS`.
3. `py -m mtfdigitizer.extract --all` — production extractor walks
   the new entries one by one, gating each on render-match +
   plausibility priors + the maintainer overlay glance.

Tier 2 entries carry `ground_truth=None` per ADR-041; the maintainer
does not eye-read any of these. The two Tier 1 anchors do all the
calibration work.

### How detection works

See `tools/mtfdigitizer/fuji_plotbox.py`. In one sentence: read the
chart's horizontal lines and x-axis tick labels, then calibrate
`image_height_mm` from the mount default (26.9 mm for GF, 14.2 mm
for XF) which is the sensor half-diagonal Fujifilm publishes MTF
out to.

198 of 199 chart files detect on the current corpus; the one
rejection is `fujifilm-xf-16-50mm-f2-8-4-8-r-lm-wr-45lp.png`, a
legend image (S/M color key) — correctly refused.
