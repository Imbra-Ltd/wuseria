# mtfdigitizer

Unified MTF chart digitizer for the wuseria optical database. Implements
[ADR-038](../../docs/decisions/038-unified-mtf-digitizer.md).

One adaptive pipeline replaces the retired per-brand scrapers: declared
chart profile → HSV mask → skeletonize → connected-components S/M split
→ 11 fixed sample points → confidence score (render-match + plausibility
priors) → SVG + readings.

## Status

Foundation complete; remaining epic work is independent (additional profiles,
lens-page SVG swap, optional Real-ESRGAN fallback).

- [x] [#933](https://github.com/Imbra-Ltd/wuseria/issues/933) — reference set
- [x] [#934](https://github.com/Imbra-Ltd/wuseria/issues/934) — profile abstraction + advisory auto-suggest
- [x] [#935](https://github.com/Imbra-Ltd/wuseria/issues/935) — adaptive extraction pipeline with 11-point sampling
- [x] [#953](https://github.com/Imbra-Ltd/wuseria/issues/953) — ground truth + plot boxes; offset distribution measured (see `referenceset/calibration.md`)
- [x] [#963](https://github.com/Imbra-Ltd/wuseria/issues/963) — `dispatch.py` shared `(style_axis, hue_meaning)` table; `rendermatch.py` round-trip IoU scorer + precision side metric (see `referenceset/scoring.md`)
- [x] [#966](https://github.com/Imbra-Ltd/wuseria/issues/966) — `priors.py` four physical-plausibility priors + `plausibility.py` runner (see `referenceset/plausibility.md`); closes the second confidence signal required by ADR-038 §"Confidence signal"
- [x] [#968](https://github.com/Imbra-Ltd/wuseria/issues/968) — `triage.py` auto-triage gate combining both signals (`precision ≥ 0.80 AND IoU ≥ 0.20 AND priors_pass` ⇒ HIGH, else LOW); `precision_of()` lives in triage and `scorer.py` imports it (see `referenceset/triage.md`)
- [x] [#971](https://github.com/Imbra-Ltd/wuseria/issues/971) — `svg.py` provenance SVG emitter; viewBox 320×218 (data area matches `MtfChart.astro` 320×200, extra 18px legend strip)
- [x] [#973](https://github.com/Imbra-Ltd/wuseria/issues/973) — `review.py` 3-panel HTML composite (original PNG + SVG + overlay); only LOW-verdict review files are committed per ADR-038 §"Workflow"
- [x] Profiles for the 3 remaining in-band families (7Artisans samecolor-dashed-sm, Tokina 2color-frequency, Viltrox bw-dashed-promo); adds `Y_BAND_IS_FREQUENCY` hue meaning, `y_band_split` profile field, and `auto_suggestable` opt-out for profiles whose hue range is too broad to participate in disambiguation
- [ ] Remaining tasks under epic [#932](https://github.com/Imbra-Ltd/wuseria/issues/932): lens-page SVG swap, optional Real-ESRGAN fallback, Viltrox 30 lp/mm tracking (y-band heuristic fails on tightly-clustered B&W charts — calibration documents the limit at 50%+ |d|)

The 0.75 IoU threshold proposed in `referenceset/REFERENCE_SET.md` fails 3/3
runnable charts due to sparse-polyline vs dense-skeleton geometric asymmetry
(precision separates them cleanly: 0.44 / 0.86 / 0.99). Threshold revision is
deferred — the discipline is "the threshold moves, not the extractor."

`extract_chart(image_path, profile, plot_box, image_height_mm)` is the
end-to-end entry point. CLI not yet exposed; the pipeline is callable
from Python now.

## Layout

```
mtfdigitizer/
  README.md           # this file
  __init__.py         # package marker + module map
  loader.py           # alpha-aware image loader (shared)
  calibrate.py        # reference-set calibration runner (#953)
  referenceset/       # eye-verified ground-truth charts (#933)
    REFERENCE_SET.md  # what's in the set, why, verified-shape notes
    calibration.md    # latest calibration run + findings (#953)
    charts.py         # machine-readable manifest (chart + plot box + ground truth)
  profiles/           # declared chart profiles + auto-suggest (#934)
    types.py          # MtfProfile, HueRange, ProfileMatch, ProfileMismatch
    declared.py       # SIGMA_2COLOR_SOLID_DASHED, SAMYANG_4COLOR_ALL_SOLID
    suggest.py        # suggest_profile() advisory + resolve() B1 entry point
  pipeline/           # adaptive extraction pipeline (#935)
    types.py          # PlotBox, SampledReading, ExtractedChart
    plotbox.py        # pixel ↔ MTF / mm conversions
    masks.py          # HueRange → binary mask, OR by name
    skeleton.py       # close + skeletonize
    split.py          # S/M split via connected-components-by-width
    sampling.py       # 11-point sampling with B2 None-on-gap
    pipeline.py       # extract_chart() orchestrator
  tests/              # pytest suite (matches brandkit/pagefetch pattern)
```

## Pipeline

```
chart PNG
  -> alpha composite onto white     (loader.py)
  -> HSV mask per declared hue      (pipeline/masks.py)
  -> morphological close + skel     (pipeline/skeleton.py)
  -> S/M split (SPLIT_BY_DASH only) (pipeline/split.py)
  -> 11-point sampling + interp     (pipeline/sampling.py)
  -> ExtractedChart with 11 SampledReading rows
```

Per-profile dispatch in `dispatch.py`:

- `(SPLIT_BY_DASH, FREQUENCY)` → Sigma + 7Artisans dialects: each hue is
  a frequency, CC-split gives S/M (7Artisans flips the convention via
  `dashed_is_sagittal=True`)
- `(HUE_IS_CURVE, CURVE_IDENTITY)` → Samyang dialect: hue name encodes
  both frequency and S/M (e.g. `10S-red`)
- `(HUE_IS_CURVE, SAGITTAL_MERIDIONAL)` → legacy Tokina prime dialect:
  hue carries S/M, `y_band_split` separates frequencies within each hue
  (superseded by `GEODESIC_DP` for the current Tokina charts)
- `(HUE_IS_CURVE, PER_COLUMN_RIDGE)` → Tokina wide-zoom variant: hue
  carries S/M, per-column ridge tracking separates frequencies (topmost
  run per column = upper freq, bottommost = lower freq). Used when the
  y-bands intersect or dashed fragments interleave in y so neither
  `y_band_split` nor CC-rank can group them. See `pipeline/ridge.py`
- `(HUE_IS_CURVE, GEODESIC_DP)` → Tokina default dialect (5 charts):
  per-hue Viterbi shortest path through the dilated mask finds two
  curves per color. The smoothness prior bridges dashed-line gaps
  without skeletonization staircase artefacts and refuses to hop to a
  parallel curve at near-touching regions. See `pipeline/dp_extract.py`
- `(SPLIT_BY_DASH, Y_BAND_IS_FREQUENCY)` → Viltrox B&W dialect: single
  neutral mask split by `y_band_split` for frequency, then CC-split
  within each band for S/M
- `(SPLIT_BY_DASH, CC_RANK_BY_MEAN_Y)` → Viltrox B&W tightly-clustered
  variant: same single neutral mask, but components ranked by mean-y
  and split at the largest y-gap instead of a fixed band
- `(SPLIT_BY_DASH, RIDGE_TRACKING)` → Viltrox AF 75mm f/1.2 variant:
  per-column ridge centroids clustered into 4 tracks for charts where
  even raw masks fuse all four curves into one CC. See `pipeline/ridge.py`

Other combinations raise `NotImplementedError` (fail loud, per B1).

### Known limits, deferred

- **Plot box is caller-supplied.** Auto-detection across the chart-style
  zoo (multi-panel stacks, mixed backgrounds, transparency) is genuinely
  hard and out of scope for #935. Test fixtures hardcode the reference
  charts' boxes; production callers will need a detector or per-chart
  hand entry until that task lands.
- **Plot-box convention is data-edge, not axis-line.** Corners are the
  first/last column with skeleton pixels, not the printed y-axis or
  legend lines. On many charts these coincide (Samyang); on others the
  printed axis sits 100+ pixels left of the first data column (Sigma).
  Measuring to the axis line causes fraction-0.0 samples to return
  `None` because the ±3 bracket window misses the first data column.
  See #954 for the diagnosis and `referenceset/calibration.md` for the
  measurement procedure.
- **Samyang pink 10M reads low at the edge** — anti-aliased pink fades
  below the saturation threshold near the chart edge, dropping curve
  pixels. The 0.10-0.20 divergence at the edge is within the band PR
  #931 deemed legitimate; future refinement.
- **Sigma dashed M is partial** — the morphological close bridges
  *most* dash gaps but not all; positions with no bridged-skeleton
  pixel correctly return `None` under the legacy strict-B2 dispatch.
  The Tokina family addresses the same shape of failure via
  `GEODESIC_DP` (per-curve support interval + intra-interval
  interpolation); Sigma still uses the older `SPLIT_BY_DASH +
  FREQUENCY` dispatch and inherits the gap behaviour. A future
  refactor may migrate Sigma to the support-interval model too.

## B-rule contracts (B1–B4)

The codebase refers to four named contracts ("B1", "B2", "B3", "B4")
in docstrings, comments, and ADR-038. They originate in the PR #931
on-paper audit of the predecessor `mtf-extract-skeleton.py` tool,
which found four bugs of the same shape — quietly fabricating data
when the honest answer was "no data here." Each contract names the
fix; subsequent code that touches the same surface must uphold it.

| Contract | Concern | Rule |
| --- | --- | --- |
| **B1** | Profile mismatch | An unknown or mismatched chart profile MUST be refused (fail loud), not silently defaulted to the most common path. Implementation: `profiles/suggest.py::resolve()` raises `ProfileMismatch`; `pipeline/dispatch.py` raises `NotImplementedError` for `(style_axis, hue_meaning)` combinations without a wired branch. |
| **B2** | Missing samples | Under the legacy dispatches (`continuous_pick.py`, `ridge.py`, `SPLIT_BY_DASH + FREQUENCY`), the sampler MUST return `None` at any sample column where no skeleton pixel exists in the bracket window — never extrapolate, never interpolate across, never copy from a neighbour. Under the DP dispatch (`GEODESIC_DP`), the DP smoothness prior IS the interpolation: each path is a single continuous curve, and its y at every column is that curve's value. Two curves of the same hue can converge to one ink stripe and both still report the shared value — which is the optical reality. `None` only ever appears when a curve has no DP path at all (e.g. hue mask is empty). `pipeline/types.py::SampledReading` and `src/types/mtf.ts::MtfReading` keep every per-field value nullable; `pipeline/rendermatch.py`, `svg.py`, `review.py` break polylines at `None`; `emit.py` passes `None` through as TypeScript `null`. |
| **B3** | Curve aggregation | Per-column aggregation MUST be order-independent and lossless. The legacy running-average + 5px cap is replaced by an unweighted per-column mean. Implementation: `pipeline/sampling.py` and `pipeline/ridge.py` aggregate by mean / median over column runs, not running averages. |
| **B4** | Center astigmatism | At the optical axis (position 0), sagittal and meridional MTF are equal by physics. The extractor MUST NOT fabricate divergence at center. Implementation: no caller manufactures an S/M gap at position 0; readings come from the chart pixels at the center column or are `None`. |

The "B2 contract" is the most-referenced of the four because
nullable readings flow through every downstream stage — the mask
extractor, the sampler, the rendermatch scorer, the SVG emitter,
the 3-panel review file, the TypeScript schema, the lens-page
table renderer. Each stage has its own way of honoring it
(`None` → broken polyline, em-dash cell, skipped IoU
contribution); a new stage that consumes `SampledReading` or
`MtfReading` MUST do the same.

Origin: see the Session 80 dev-journal entry for PR #931 — the
on-paper audit of `mtf-extract-skeleton.py` that named all four
contracts. ADR-038 references B1 (§1, §2) and B2 (§2). The
contracts predate the unified digitizer but apply to it in full.

## Profile system

A *profile* declares a chart's visual dialect along three axes (ADR-038 §1):

- **Color axis** — one HSV band per curve color (with S and V bounds, so
  pink-vs-red and dark-grey-vs-light-grey are distinguishable)
- **Style axis** — `SPLIT_BY_DASH` for one-hue-per-frequency dialects
  (Sigma); `HUE_IS_CURVE` for one-hue-per-curve dialects (Samyang)
- **Frequency count** — declaring 2 frequencies refuses 3-frequency charts

`resolve(image, declared)` is the entry point: it returns the declared
profile when the image agrees, raises `ProfileMismatch` when they
disagree, and falls back to the advisory auto-suggest only when
nothing is declared. **A declared profile is never silently switched** —
that's the B1 fail-loud gate from PR #931 generalized.

Five profiles ship today (Sigma, Samyang, 7Artisans, Tokina, Viltrox)
— one per in-band reference chart family. Two more reference charts
(7Artisans 35mm soft promo, Zeiss Touit press kit) are deliberately
out-of-band fail-loud cases and do not have profiles.

Profiles with broad hue ranges that cannot disambiguate themselves
from other profiles (Viltrox's neutral mask matches every chart's
gridlines; Tokina's red+blue overlaps Sigma) opt out of auto-suggest
via `auto_suggestable=False`. They are still callable through
`resolve(image, declared=...)` — the caller takes responsibility for
the chart/profile match.

## Reference set

Eight charts span the chart-style families we encountered in
`docs/optical-specs/`:

| # | Lens                                 | Style family                      |
| - | ------------------------------------ | --------------------------------- |
| 1 | sigma-56mm-f1-4-dc-dn-c              | 2-color solid-S/dashed-M (Sigma)  |
| 2 | samyang-85mm-f1-4-as-if-umc          | 4-color all-solid (Samyang)       |
| 3 | samyang-300mm-f6-3-ed-umc-cs-reflex  | 4-color, idealized-flat at ~1.0   |
| 4 | 7artisans-50mm-f1-2-mark-ii          | 2-color same-color dashed S/M     |
| 5 | 7artisans-35mm-f1-2-mark-ii          | Soft promo, 8+ frequencies        |
| 6 | tokina-atx-m-23mm-f1-4-x             | 2-color, colors carry frequency   |
| 7 | viltrox-af-75mm-f1-2-pro             | B&W soft promo, dashed-only       |
| 8 | zeiss-touit-32mm-f1-8                | German press kit, 3 frequencies   |

Eye-verified curve shapes (key inflection points, S/M divergence, edge
falloff) live alongside each entry in `referenceset/REFERENCE_SET.md`.
The machine-readable form is `referenceset/charts.py` — a list of
`ReferenceChart` records keyed by lens slug.

The two open ADR-038 parameters proposed against this set:

- **Render-match threshold** — `0.75` IoU initial value
- **Offset tolerance band** — `±0.05` MTF units (uniform vertical offset)

Reasoning in `referenceset/REFERENCE_SET.md` §Proposed thresholds. The
offset band side of the calibration ran in #953 against the 3 charts whose
profile is declared today; see `referenceset/calibration.md` for the
measurement and findings. Render-match calibration is still blocked on the
confidence-signal sub-task of #932.

## Calibration

```bash
cd tools
py -m mtfdigitizer.calibrate
py -m mtfdigitizer.calibrate --write-readings
```

Runs `extract_chart()` for every reference chart with both `plot_box` and
`ground_truth` populated and reports the |d| (absolute offset) distribution
per field. With `--write-readings`, additionally writes one markdown grid
per chart under `referenceset/readings/<slug>.md` for diffing across
algorithm changes. See `referenceset/calibration.md` for the latest
run's findings.

## Per-lens digitization log

```bash
cd tools
py -m mtfdigitizer.log              # Tokina lenses (default)
py -m mtfdigitizer.log --all        # every lens with a runnable chart
```

Writes `docs/optical-specs/<lens-slug>/digitization-log.md` with the
GT-vs-extracted-vs-Δ grid, sister-fallback counters, center/edge
summary, and shape metrics (peak position, half-falloff). Multi-panel
lenses (e.g. Tokina 11-18 zoom) get one log with all panels grouped.

## Running the tests

```bash
cd tools
py -m pytest mtfdigitizer/
```
