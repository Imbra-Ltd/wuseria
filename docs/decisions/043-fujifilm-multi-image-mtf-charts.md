# ADR-043: Fujifilm multi-image-per-lens MTF charts

**Status:** Accepted
**Date:** 2026-06-06

## Context

The MTF digitizer (ADR-038) operates on the assumption that one chart
image is one chart: a single PNG carries every curve the lens
publishes, the extractor reads it once, and the result is one
`ExtractedChart` per source image. Every declared profile to date
(Sigma, Samyang, 7Artisans, Tokina, Viltrox) honors that assumption —
a single chart image contains the full {10S, 10M, 30S, 30M} set, and
the extractor returns four field skeletons from one pass over the
image.

Fujifilm breaks the assumption. Their MTF publication convention is
**one image per spatial frequency** rather than one image per lens.
A GF prime publishes three charts (15, 20, 40 lp/mm); a GF zoom
publishes six (15+20+40 × {wide, tele}, sometimes 10+20+40); an XF
prime publishes two (15, 45 lp/mm); an XF zoom publishes four
(15+45 × {wide, tele}).

Per-image content within the Fuji convention:

- Background: white, 282 × 212 pixels (consistent across all 129
  Fuji chart images sampled)
- Plot area: occupies roughly the upper-half of the image; thin black
  horizontal gridlines at MTF 0.0 / 0.2 / 0.4 / 0.6 / 0.8 / 1.0
- X-axis: image-height in mm. GF charts: 0–25 mm or 0–~27 mm
  (medium-format sensor radius). XF charts: 0–14.2 mm (APS-C sensor
  radius)
- Y-axis: MTF 0–1, with only the value "1" labeled at top-left
- Two curves: **blue solid = sagittal (S)**, **red dashed = meridional
  (M)**. Convention is rock-solid across every chart sampled (XF and
  GF, prime and zoom). The S/M letter labels float at the right edge
  near each curve's endpoint, with the curve color matching the
  letter color.
- Aperture: charts are published at maximum aperture only — there is
  no F8 panel and no aperture sweep. The aperture context lives on
  the lens product page, not in the chart itself.

The two structural mismatches with the existing digitizer architecture:

1. **No frequency carried by the image.** Existing profiles encode
   frequency in hue (Sigma: red=10, blue=30), curve identity (Samyang:
   four named hues), or y-position (Tokina). In the Fuji convention
   the image contains only one frequency, and that frequency lives in
   the filename suffix (`-15lp.png`). The extractor needs to be told
   which frequency it is reading.
2. **One lens → many images.** Producing a lens's full `MtfData` means
   reading 3 / 6 images (GF) or 2 / 4 images (XF) and merging the
   per-image readings into one per-position record. The existing
   `extract.py` orchestration runs the extractor once per `ChartView`
   and writes one set of inspection artifacts per view, which fits
   zooms (where each view is a distinct frequency-complete chart) but
   does not fit Fuji (where each view is one frequency of an
   incomplete reading).

ADR-042 generalized the schema to hold arbitrary frequencies. This
ADR generalizes the extractor's orchestration to assemble a
per-position reading from N per-frequency images.

## Decision

### A new profile: `FUJIFILM_PERMFREQ_2COLOR_SOLID_DASHED`

The Fujifilm per-frequency profile carries the same two-hue
solid/dashed convention as Sigma, but with one frequency per image:

| Field              | Value                                                              |
| ------------------ | ------------------------------------------------------------------ |
| name               | `fujifilm-permfreq-2color-solid-dashed`                            |
| hues               | blue (S, solid), red (M, dashed)                                   |
| style_axis         | `HUE_IS_CURVE`                                                     |
| hue_meaning        | `SAGITTAL_MERIDIONAL`                                              |
| frequencies_lpmm   | inferred from filename at runtime — not embedded in the profile    |
| dashed_is_sagittal | False (red dashed = M, matching the Sigma convention)              |
| auto_suggestable   | False (small B&W-and-color images on white BG match too liberally) |

Each Fuji chart image runs the existing `HUE_IS_CURVE` dispatch with
the **frequency declared by the caller** rather than by the profile.
The dispatch already supports per-hue S/M assignment; what it does
not support today is reading the frequency from somewhere other than
`profile.frequencies_lpmm`. ADR-042's digitizer generalization makes
the field set per-profile; this ADR adds a small extension to make
the _frequency_ itself a per-image runtime parameter.

The 282 × 212 image size is below the regime where pixel-noise priors
calibrated against the larger reference charts (Sigma at 2991×1964,
Tokina at 1541×1028) apply directly. The Fuji anchor's calibration
run measures whether render-match precision / IoU thresholds need
adjustment for this regime — see "Tier 1 anchor" below.

### Style family registration

A new style family slug, `fujifilm-permfreq`, joins the
`PROFILE_BY_STYLE` map in `family_profile.py`. The slug omits the
color/style suffix because the family is identified by the
publication convention (per-frequency-image), not the curve palette.

`STYLE_FAMILIES` in `referenceset/charts.py` picks up the new entry
in the same PR that declares the profile.

### Per-lens orchestrator: `extract_lens_multipath()`

A new orchestrator alongside `extract_lens()` handles the
many-images-per-lens case. Signature sketch:

```python
def extract_lens_multipath(
    chart: ReferenceChart,
    *,
    accept_override: bool,
) -> int
```

Behavior:

1. Reads the per-image list from `chart.additional_views` plus
   `chart.chart_path` — every PNG the lens publishes.
2. For each image, parses the trailing `-NNlp` suffix into a
   frequency. Images without a frequency suffix (a top-level chart
   PNG that does not match the per-frequency convention) raise — this
   profile is not for them.
3. Runs `extract_chart()` per image with the parsed frequency
   threaded into the per-image profile (a per-call frequency
   override; the declared profile carries `frequencies_lpmm=()` and
   the override fills it in).
4. Merges the per-image readings into one per-position
   `MtfReading[]` keyed by image-height position. The
   `samples` record on each row gets one entry per frequency the
   lens publishes.
5. Writes one combined SVG per aperture, one overlay-glance HTML
   composite that tiles all per-frequency overlays side-by-side, and
   one `digitization-log.md` with one panel per frequency.
6. Honors the same render-match + plausibility gate the
   single-image path does, aggregated across all frequencies — a LOW
   verdict on any frequency holds the entire lens.

The orchestrator lives in `tools/mtfdigitizer/extract.py` alongside
the existing `extract_lens()`. The CLI grows a routing step that
inspects `chart.style_family` and dispatches to the right
orchestrator. No CLI surface change for the user: `py -m
mtfdigitizer.extract <slug>` works for any style family.

### Reference-set entries for Fujifilm

The Fuji anchor lens carries its per-frequency images as
`additional_views` entries with frequency-suffixed `chart_path`. The
canonical `chart_path` on the `ReferenceChart` itself uses the
**lowest-frequency** image (the "contrast" panel) so existing
single-view consumers (calibrate, scorer, plausibility, autotriage,
emit, svg, review per `extract.py:_resolve_view_image`) read a
coherent image. The multipath orchestrator walks the full `views`
tuple.

A Fuji `ReferenceChart` then looks like:

```python
ReferenceChart(
    slug="fujifilm-gf-23mm-f4-r-lm-wr",
    chart_path="docs/optical-specs/fujifilm-gf-23mm-f4-r-lm-wr/"
               "fujifilm-gf-23mm-f4-r-lm-wr-15lp.png",
    style_family="fujifilm-permfreq",
    apertures=("f/4",),
    frequencies_lpmm=(15, 20, 40),
    image_height_mm=25.0,
    plot_box=PlotBoxCoords(x_left=18, x_right=270,
                           y_top=15, y_bottom=135),
    ground_truth=_FUJI_GF_23_GT,  # maintainer eye-read
    additional_views=(
        ChartView(
            chart_path="docs/optical-specs/fujifilm-gf-23mm-f4-r-lm-wr/"
                       "fujifilm-gf-23mm-f4-r-lm-wr-20lp.png",
            plot_box=PlotBoxCoords(x_left=18, x_right=270,
                                   y_top=15, y_bottom=135),
        ),
        ChartView(
            chart_path="docs/optical-specs/fujifilm-gf-23mm-f4-r-lm-wr/"
                       "fujifilm-gf-23mm-f4-r-lm-wr-40lp.png",
            plot_box=PlotBoxCoords(x_left=18, x_right=270,
                                   y_top=15, y_bottom=135),
        ),
    ),
    notes="GF prime; 15/20/40 lp/mm per-frequency images; blue solid=S, red dashed=M",
)
```

(Plot-box coordinates above are illustrative; the maintainer measures
the real box during anchor setup.)

### Tier 1 anchor

Per ADR-041, one lens per `(brand, style_family)` carries eye-read
ground truth as the calibration anchor. For Fujifilm `fujifilm-permfreq`:

- **Anchor candidate:** `fujifilm-gf-23mm-f4-r-lm-wr` — a single
  aperture (f/4 max), three per-frequency images at 15/20/40 lp/mm,
  recently digitized specs (specs-log dated 2026-05-28). The 23mm
  field of view is the canonical "first lens to digitize" position
  for the brand.
- **Eye-read cost:** 11 sample positions × 2 fields (S, M) × 3
  frequencies = 66 numbers. Per `feedback_agent_no_gt_eye_read` the
  maintainer enters these; the agent does not.
- **Plot-box measurement:** one box for the GF 282×212 template
  (likely identical across all GF charts at this size); hand-measured
  once and reused.
- **Confidence-gate recalibration:** the render-match precision and
  IoU thresholds were tuned against larger reference charts. The
  282×212 GF charts may need adjusted thresholds — the calibration
  run measures whether the existing thresholds clear the anchor; if
  not, a Fuji-specific override lands in `triage.py` (or the
  thresholds widen globally, depending on what the data shows).

XF charts (14.2 mm x-axis, different image-height extent) may need a
second anchor for the XF body of charts. Decision deferred to the
first XF Tier 2 run — if the GF-tuned thresholds clear the XF
charts, no second anchor; if XF systematically holds, the maintainer
eye-reads one XF anchor.

### What this ADR does NOT do

- Does NOT change the schema — that is ADR-042's scope.
- Does NOT change the field set in the digitizer's dispatch — that
  is ADR-042's scope (digitizer generalization step).
- Does NOT touch other brands. Venus Laowa, TTartisan, Handevision,
  etc., each get their own profile + ADR if their chart family
  differs from the declared five (or from Fuji's new family).

## Alternatives considered

| Alternative                                                            | Why rejected                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Treat each per-frequency image as its own `ChartView` zoom-style       | The existing zoom path uses `additional_views` for wide+tele _full_ charts (each contains all frequencies, just at a different focal length). Fitting Fuji into that mental model would require treating each Fuji image as a separate "view," but then the per-view `digitization-log.md` panels would each carry one-third of the data and the lens-level reading record would never assemble. The orchestrator break is intentional. |
| Stitch the per-frequency PNGs into a single composite image upfront    | Possible: paste 15/20/40 lp/mm into a synthetic Sigma-like multi-frequency chart, then feed it to the existing dispatch. Rejected because the composition is fake (Fuji never published it; the synthesis would invent gridline / hue conventions that the extractor's profile encodes as truth). The B1 fail-loud gate exists precisely to refuse fake/composite inputs.                                                               |
| Hardcode Fuji frequencies in the profile (`frequencies_lpmm=(15, 40)`) | Loses the 20 lp/mm panel. Equivalent to the lossy mapping rejected in ADR-042 — drops 1/3 of the published data to fit a fixed-shape extractor.                                                                                                                                                                                                                                                                                         |
| Defer Fujifilm; pick smaller brands first                              | Considered. Rejected because Fujifilm is the largest single un-anchored brand by lens count and chart count; deferring it means deferring 62 of the ~150 still-un-anchored lenses, the bulk of the remaining work.                                                                                                                                                                                                                      |
| Per-frequency S/M label rule from sniffing curve endpoint y-position   | The S/M letters at the right edge could be detected (find the small color blob next to the curve endpoint) and used to assign each curve. Rejected as unnecessary complexity: the blue-solid=S, red-dashed=M convention is rock-solid across every Fuji chart sampled; codifying it in the profile is simpler than runtime detection.                                                                                                   |

## Consequences

- **Extractor grows a multipath orchestrator.** `extract_lens()`
  stays single-image; `extract_lens_multipath()` is new. The CLI
  dispatches by `style_family`. This is the first time the
  orchestration layer reads anything off the profile/family — until
  now it was uniformly single-image.
- **Filename parsing is load-bearing.** The frequency suffix
  (`-15lp.png`, `-45lp.png`) is the only carrier of which frequency
  an image represents. A typo in the filename silently miscategorizes
  the reading. The orchestrator parses with a strict regex and
  raises on mismatch (no silent fallback). Filename convention is
  documented in this ADR and in the digitizer README.
- **GF and XF cohabit one style family.** Both publish at the same
  convention (blue solid + red dashed, per-frequency images, single
  max aperture). They differ in frequencies (GF: 15/20/40 or
  10/20/40; XF: 15/45) and in x-axis extent (GF up to 27 mm, XF
  14.2 mm). The profile is the same; the per-lens
  `frequencies_lpmm` and `image_height_mm` differ. No need for two
  profiles.
- **Inspection artifacts are per-frequency.** Each per-frequency
  image gets its own SVG and overlay PNG (named after the source
  image stem). The lens-level review HTML tiles every overlay
  side-by-side so the maintainer glances all frequencies in one
  view. The `digitization-log.md` carries one panel per frequency,
  each with its own sparkline.
- **Anchor cost: ~1 hour of maintainer time.** One GF prime + 66
  numbers. The first XF lens that holds gets a second 44-number
  anchor (or 22 if the XF prime only publishes 2 frequencies, as
  observed in the sample).
- **Closes part of #1047 (epic).** The Fuji profile + orchestrator
  is the third PR in the stack; Tier 1 + Tier 2 production runs
  follow.
- **Unblocks the largest remaining brand body.** 62 lenses, 129
  chart images. After the schema migration (ADR-042) lands, Fuji is
  the next bottleneck; this ADR removes it.
- **Future brand re-use.** Voigtländer APO-LANTHAR also publishes
  per-frequency images (when its charts get digitized). The
  multipath orchestrator + per-image-frequency-override pattern
  applies directly. Zeiss Touit publishes a single multi-frequency
  composite chart — a different family, will need its own ADR.
