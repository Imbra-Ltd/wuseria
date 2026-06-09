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

## scaffold_ttartisan_tier2

Same shape as `scaffold_fuji_tier2` but for the TTartisan cohort.
Walks `docs/optical-specs/ttartisan-*`, detects each chart's plot
box via `ttartisan_plotbox.detect_ttartisan_plotbox`, and emits
`_ttartisan_tier2_charts.py` with one Tier 2 `ReferenceChart` per
lens (each chart packs two apertures via color encoding — see
ADR-044).

Tier 1 anchors live in `charts.py` proper with maintainer-read GT;
`_TIER1_SKIP_SLUGS` (at the top of the scaffolder) lists slugs the
scaffolder excludes so the same lens does not appear twice in
`REFERENCE_CHARTS` (the `test_no_duplicate_slugs` assertion would
fail). Add a slug there when promoting a TTartisan lens to Tier 1.

### Usage

```
cd tools

py -m mtfdigitizer.scripts.scaffold_ttartisan_tier2          # preview
py -m mtfdigitizer.scripts.scaffold_ttartisan_tier2 --write   # commit
```

## scaffold_anchor_helpers

For a given Tier 1 anchor slug, generates the three artifacts the
maintainer reads when filling in the `_<LENS>_GT` ground-truth
tuple in `charts.py`:

- **`<view-stem>-readhelper.png`** — 3x upscale of the view's base
  image with 11 green vertical sample-position lines + mm labels.
  One file per view (per spatial frequency for `fujifilm-permfreq`;
  per aperture for `ttartisan-4color-dual-aperture`).
- **`eye-read-template.md`** — fill-in tables (one per view) the
  maintainer completes by reading the source PNG against the
  printed gridlines.
- **`extractor-prediction.md`** — extractor's reading of every
  cell, as a starting point for maintainer validation. Not ground
  truth — the maintainer accepts cells that look right and
  overwrites cells that look wrong.

### Usage

```
cd tools

# Preview: list the artifacts that would be written.
py -m mtfdigitizer.scripts.scaffold_anchor_helpers <slug>

# Write: materialize the artifacts on disk.
py -m mtfdigitizer.scripts.scaffold_anchor_helpers <slug> --write

# Check: exit 1 if any artifact is missing or out of date.
py -m mtfdigitizer.scripts.scaffold_anchor_helpers <slug> --check
```

### Workflow

Run **after** promoting a lens to Tier 1 in `charts.py` (added
entry to `REFERENCE_CHARTS` with a `_<LENS>_GT` of None
placeholders) and **before** the maintainer fills in the 88 (or
44, etc.) GT values. The maintainer reads the source PNG against
the green sample lines in the readhelper, fills the eye-read
template, then transcribes column-by-column into the GT tuple in
`charts.py`. Finally:

```
py -m mtfdigitizer.calibrate
```

reports per-field median |Δ| and p95 |Δ| against the extractor's
output — median |Δ| under ~0.04 means the dispatch is calibrated
for that brand's style family.

### Supported style families

- `fujifilm-permfreq` — one PNG per spatial frequency; helper PNG
  per frequency; eye-read columns per (S, M) pair.
- `ttartisan-4color-dual-aperture` — one PNG packing both
  apertures by color encoding; helper PNG per aperture (uses the
  existing `<stem>-<aperture>-overlay.png` from
  `extract.py:_write_inspection_artifacts` as the base so the
  target aperture's traced curves are pre-marked); eye-read
  columns per (frequency, S|M) pair for the target aperture.

To add a new style family, extend `_resolve_helper_views` in
`scaffold_anchor_helpers.py` with a branch that returns one
`HelperView` per group of curves the maintainer reads together.
