# ADR-038: Unified MTF chart digitizer with declared profiles and shape-based verification

**Status:** Accepted
**Date:** 2026-05-29

## Context

Digitizing MTF charts into structured readings (`src/data/mtf-readings.ts`)
is the precondition for cross-lens optical comparison and any MTF-derived
scoring (epic #790).

Today this is done by one flat script, `tools/mtf-extract-skeleton.py`,
hardcoded to exactly two chart families:

- **Sigma** — red/blue lines, solid sagittal + dashed meridional.
- **Samyang** — four distinct colors.

The #726 audit and verify pass (PR #931) exposed two structural problems.

**1. The tool only knows two brands.** It used to default any unrecognized
chart to the Samyang path and silently mis-trace it. PR #931 fixed that to
fail loud (B1), but the tool still can't handle anything beyond Sigma and
Samyang — and epic #790 spans ~24 brands.

**2. Chart styles vary far more than two families.** Mainstream brands
(Fujifilm, Sigma, Sony-style) use well-defined colors and a consistent
solid-S / dashed-M convention. Chinese brands (7Artisans, TTArtisan, Meike)
are inconsistent:

- sometimes S and M share one color, told apart only by dash pattern;
- sometimes they use different colors;
- sometimes the line style changes from chart to chart within one brand.

Many of these charts also come from promotional material and are soft
(JPEG-compressed).

Writing a separate scraper per brand (task #563) would just multiply the
two-brand problem into ~24 bespoke scripts. We need **one tool** that adapts
to chart style, refuses what it doesn't understand, and produces uniform,
verifiable output.

Two further facts, established in conversation, shape the decision:

- **Verification is per-lens and conversational** — not a built editor. When
  a trace is wrong the maintainer describes the problem in chat ("the 30M
  line misses the dip at 12mm"); the correction surface is feedback, not
  coordinate editing.
- **The correctness bar is shape, not absolute position.** At each sample
  point the traced curve's slope must match the original's. A small uniform
  vertical offset is tolerable jitter. MTF _shape_ — where curves dip, how S
  and M diverge — carries the optical meaning, and the readings are
  approximate by nature (ADR-022). Demanding absolute accuracy would be false
  precision.

## Decision

Build one unified MTF digitizer that supersedes
`tools/mtf-extract-skeleton.py` and the per-brand-scraper task (#563). It
rests on five pillars.

### 1. Declared chart profiles, with advisory auto-suggest

A **profile** describes a chart's visual dialect along two independent axes:

- **Color axis** — how many distinct hues carry curves (1, 2, or 4), and the
  HSV range of each.
- **Style axis** — within a hue, are S and M split by dash pattern (solid vs
  dashed), or are they separate hues?

Each brand **declares** its profile, mirroring the existing `BrandConfig`
pattern in `tools/brandkit/`. The declaration is the authority.

An **auto-suggest** routine inspects an image and proposes a profile, but is
**advisory only**:

- it suggests a profile when none is declared;
- when a declared profile disagrees with the image, that is a flag for
  review — never a silent switch.

This keeps the fail-loud property from PR #931 (B1): an unrecognized or
mismatched chart is refused, not guessed.

### 2. Adaptive extraction pipeline

```
chart PNG (docs/optical-specs/<slug>/)
  -> profile (declared; auto-suggest advisory)   [unknown/mismatch -> FAIL LOUD]
  -> HSV mask per declared hue
  -> morphological close (horizontally-biased kernel) to bridge dashed lines
  -> skeletonize (Zhang-Suen)
  -> connected-components split S/M by fragment width (the same-color case)
  -> read curve value at the 11 fixed sample points (interpolated)
  -> confidence score (slope jitter, gap jumps, missing points)
       |
       +-- low confidence -> [optional] Real-ESRGAN super-resolution + CLAHE,
       |                      re-extract once
       v
  -> emit SVG (display + provenance) + readings + 3-panel review file
```

Three sound parts of the current tool are kept:

- **Skeleton + connected-components S/M split** — the only thing that
  separates two same-colored curves (the Chinese-brand case). K-means color
  clustering cannot do this.
- **Axis and grid detection.**
- **`interpolate_at`** — returns `None` across large gaps rather than
  fabricating a value (per the B2 fix).

### 3. Fixed 11-point sampling, by percent of image height

Every curve is read at **0, 10, 20, ..., 100% of image height** (11 points).

This grid is uniform across all brands and formats — APS-C (~14mm),
full-frame (~20mm+), and GFX — which makes readings cross-comparable and
gives a clean SVG and DB schema.

- Reads between detected curve points use interpolation.
- Positions where the curve has no usable data read as missing, not
  fabricated.

The 11 points are mapped to real image-height mm per chart (e.g. 0-14mm for
APS-C), so the existing `MtfReading.position` semantics still hold.

### 4. Shape-based, conversational verification

Per lens, the pipeline emits one review file with three panels:

- **Left** — the original chart image.
- **Right** — the SVG regenerated from the extracted readings.
- **Bottom** — the regenerated curves overlaid on the original.

```
+---------------------+---------------------+
|   original chart    |    regenerated SVG  |
|      (raster)       |   (from readings)   |
+---------------------+---------------------+
|        overlay: regen curves on original  |
|        (aligned to detected anchors)      |
+-------------------------------------------+
```

The overlay is registered using the same axis/grid anchors the extraction
detected, so it is deterministic — no hand-tuned calibration, unlike the old
`mtf-overlay.html`.

A computed **slope-value correlation** per curve (numeric derivative of
traced vs. original at the 11 points) scores shape agreement and drives
auto-triage: low correlation flags a lens for scrutiny.

The maintainer reviews lens by lens and gives feedback in conversation; the
agent adjusts the extraction (profile tuning, mask range, sample handling)
and regenerates. There is no node-dragging editor.

**The correctness bar is derivative/shape agreement at the 11 points.** A
uniform vertical offset within a tolerance band is acceptable. That band is
left as an **open parameter**: it is set once a small set of charts has been
visually confirmed correct. It cannot be derived from the existing
`mtf-readings.ts` data, because that data is itself unverified — the verify
pass _found_ two wrong entries in it.

### 5. Output artifacts

- **SVG**, committed to `docs/optical-specs/<slug>/`. It serves two roles:
  the lens-page display asset (sharp at any zoom, dark-theme recolorable)
  and the provenance record. It is generated from the numbers, never by
  raster vectorization (see alternatives).
- **Readings**, written to `src/data/mtf-readings.ts` (existing schema).

The SVG and the committed numbers carry the same readings — one source of
truth, no drift between the picture and the data.

Because the SVG is user-visible, **human verification is required before
commit**: otherwise a digitization error would show on the live site, not
just in scoring.

## Alternatives considered

| Alternative                                  | Why rejected                                                                                                                                                                                                            |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Per-brand scraper scripts (#563)             | Multiplies the two-brand problem into ~24 bespoke scripts with no shared adaptation. Superseded by this ADR.                                                                                                            |
| Auto-detect profile (no declaration)         | Mis-profiling is the exact silent-corruption failure B1 fixed. Declaration keeps the authority explicit (project value: explicit over implicit).                                                                        |
| K-means color clustering to isolate lines    | Cannot separate two same-colored curves (the Chinese-brand case). Only the connected-components-by-width split can.                                                                                                     |
| Raster-to-SVG vectorization (Potrace)        | Soft promo charts vectorize into hundreds of tiny path fragments; reconnecting them is the dash-bridging problem made harder, with color information thrown away. Generate the SVG from extracted numbers instead.      |
| Super-resolution as a mandatory first stage  | The real failure modes are occlusion and dashed-line classification, which SR doesn't fix; SR helps only soft charts. Making it a low-confidence fallback keeps PyTorch (~2GB+, GPU) out of the default install and CI. |
| Node-dragging correction UI                  | The largest build in the original sketch. The maintainer wants conversational per-lens feedback, not coordinate editing — a generated 3-panel review file plus chat feedback achieves the goal with no UI framework.    |
| Absolute max-delta correctness bar           | False precision for approximate readings: a uniform offset is optically meaningless, while a wrong slope is not. Shape (derivative) agreement is the meaningful bar.                                                    |
| Variable grid-locked sampling (keep current) | Sample counts vary by chart (5-8 points), are not cross-comparable, and complicate a uniform SVG/DB schema. Fixed 11-point percent-of-height sampling is uniform.                                                       |

## Consequences

**Tooling retired.** `tools/mtf-extract-skeleton.py` is superseded;
`tools/mtf-extract-samyang.py` and `tools/mtf-extract-sigma.py` (already
legacy) are retired with it. Task #563 is closed as superseded.

**New package.** A digitizer package under `tools/` (e.g.
`tools/mtfdigitizer/`) hosts the profile abstraction, pipeline, SVG emitter,
and review-file generator, with its own pytest suite — matching the
`pagefetch` / `brandkit` package pattern. Creating that directory is the
architectural step this ADR authorizes.

**Optional heavy dependency.** Real-ESRGAN + PyTorch are an optional extra,
never a default or CI dependency. The pipeline runs without them and flags
charts that would need them.

**Reference set comes first.** The offset tolerance band stays unspecified
until a confirmed reference set exists. Building that set (a handful of
visually-verified charts) is the first work item, ahead of the profile
abstraction.

**Lens pages improve.** Pages gain SVG MTF charts (sharper, themeable) in
place of raster PNGs, once a lens is digitized and verified.

**Position grid changes.** The fixed 11-point grid changes the `position`
values stored for newly digitized lenses, relative to the five grid variants
in the current data. Existing entries are re-digitized onto the new grid as
they are reprocessed — not migrated blindly.

**Workflow trade-off.** Per-lens conversational verification has zero UI
build cost, but correction throughput is gated by the review cadence. That is
acceptable for an agent-assisted catalog; it would not suit an independent
contributor digitizing solo.
