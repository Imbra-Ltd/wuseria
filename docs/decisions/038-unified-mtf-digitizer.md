# ADR-038: Unified MTF chart digitizer with declared profiles and shape-based verification

**Status:** Accepted
**Date:** 2026-05-29

## Context

Digitizing MTF charts into structured readings (`src/data/mtf-readings.ts`) is
the precondition for cross-lens optical comparison and any MTF-derived scoring
(epic #790). The current tooling is a flat script, `tools/mtf-extract-skeleton.py`,
hardcoded to exactly two chart families — Sigma (red/blue, solid/dashed) and
Samyang (4 distinct colors). The #726 audit and verify pass (PR #931) confirmed
two structural problems:

1. The tool defaulted any unrecognized chart to the Samyang path, silently
   mis-tracing it. This was fixed to fail loud (B1), but the tool still only
   knows two brands. Epic #790 spans ~24 brands.
2. Chart styles vary far more widely than two families. Mainstream brands
   (Fujifilm, Sigma, Sony-style) use well-defined colors and a consistent
   solid-S / dashed-M convention. Chinese brands (7Artisans, TTArtisan, Meike,
   etc.) are inconsistent: sometimes both sagittal and meridional share one
   color distinguished only by dash pattern, sometimes they use different
   colors, sometimes line styles differ chart-to-chart within one brand. Many
   charts come from promotional material and are soft (JPEG-compressed).

A per-brand-scraper approach (task #563) would multiply the two-brand problem
into ~24 bespoke scripts. We need one tool that adapts to chart style, refuses
what it does not understand, and produces a uniform, verifiable output.

Two further facts shape the decision, established in conversation:

- The maintainer verifies **lens by lens**, conversationally — not via a built
  editor. The correction surface is feedback ("the 30M line misses the dip at
  12mm"), not coordinate editing.
- The correctness bar is **shape, not absolute position**. At each sample point
  the traced curve's derivative must match the original's; a small uniform
  vertical offset is tolerable jitter. MTF _shape_ (where curves dip, S/M
  divergence trend) carries the optical meaning; the readings are approximate
  by nature (ADR-022), so demanding absolute accuracy is false precision.

## Decision

Build a unified MTF digitizer that supersedes `tools/mtf-extract-skeleton.py`
and the per-brand-scraper task (#563). It has four pillars.

### 1. Declared chart profiles with advisory auto-suggest

A **profile** describes a chart's visual dialect as the cross-product of two
orthogonal axes:

- **Color axis** — how many distinct hues carry curves (1, 2, or 4), and the
  HSV range of each.
- **Style axis** — within a hue, whether sagittal/meridional are split by dash
  pattern (solid vs dashed) or are separate hues.

Each brand **declares** its profile (the authority), mirroring the existing
`BrandConfig` pattern in `tools/brandkit/`. An **auto-suggest** routine inspects
an image and proposes a profile, but is **advisory only**: it suggests when none
is declared, and when a declared profile disagrees with the image, that is a
**flag for review, never a silent switch**. This preserves the fail-loud
property merged in PR #931 (B1): an unrecognized or mismatched chart is refused,
not guessed.

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

The sound parts of the current tool are retained: skeleton + connected-components
S/M split (the only thing that separates two same-colored curves — K-means color
clustering cannot), axis/grid detection, and `interpolate_at` (which returns
`None` across large gaps rather than fabricating, per B2).

### 3. Fixed 11-point sampling at percent of image height

Every curve is read at **0, 10, 20, ..., 100% of image height** (11 points).
This is uniform across all brands and formats (APS-C ~14mm, full-frame ~20mm+,
GFX), making readings cross-comparable and giving a clean SVG and DB schema.
Reads between detected curve points use interpolation; positions where the
curve has no usable data read as missing (not fabricated).

Stored readings are mapped to real image-height mm per chart (e.g. 11 points
across 0-14mm for APS-C) so existing `MtfReading.position` semantics hold.

### 4. Shape-based, conversational verification

The pipeline emits, **per lens**, an aggregated review file with three panels:

- **Left** — the original chart image.
- **Right** — the regenerated SVG from the extracted readings.
- **Bottom** — the regenerated curves superimposed on the original, registered
  using the same axis/grid anchors the extraction detected (deterministic, no
  hand-tuned calibration — unlike the old `mtf-overlay.html`).

Alongside the overlay, a computed **slope-value correlation** per curve (numeric
derivative of traced vs. original at the 11 sample points) scores shape
agreement and drives auto-triage: low correlation flags a lens for scrutiny.

The maintainer reviews lens by lens and gives **feedback in conversation** about
what is wrong; the agent adjusts the extraction (profile tuning, mask range,
sample handling) and regenerates. There is no node-dragging editor.

**Correctness bar:** derivative/shape agreement at the 11 sample points. A
uniform vertical offset within a tolerance band is acceptable. The band is left
as an **open parameter**, to be set once a small reference set of charts has been
visually confirmed correct — it cannot be derived from the existing
`mtf-readings.ts` data, which is itself unverified (the verify pass _found_ two
wrong entries in it).

### Output artifacts

- **SVG** (committed to `docs/optical-specs/<slug>/`) — both the lens-page
  display asset (sharp at any zoom, dark-theme recolorable) and the provenance
  record. Generated from the numbers, not by raster vectorization (Potrace-style
  vectorization is rejected — see alternatives).
- **Readings** -> `src/data/mtf-readings.ts` (existing schema). The SVG and the
  committed numbers carry the same readings — single source of truth, no drift
  between picture and data.

Because the SVG is a user-visible display asset, **human verification is
required before commit** — a digitization error would otherwise show on the live
site, not just in scoring.

## Alternatives considered

| Alternative                                     | Why rejected                                                                                                                                                                                                                 |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Per-brand scraper scripts (#563)                | Multiplies the two-brand problem into ~24 bespoke scripts; no shared adaptation; #563 is superseded by this ADR                                                                                                              |
| Auto-detect profile (no declaration)            | Mis-profiling is the exact silent-corruption failure B1 fixed; declaration keeps the authority explicit (project value: explicit over implicit)                                                                              |
| K-means color clustering for line isolation     | Cannot separate two same-colored curves (the Chinese-brand case); only the connected-components-by-width split does                                                                                                          |
| Raster-to-SVG vectorization (Potrace, Option 3) | Soft promo charts vectorize into hundreds of tiny path fragments; reconnecting them is the dash-bridging problem made harder, with color information thrown away. Generate SVG from extracted numbers instead                |
| Super-resolution as mandatory stage 1           | The real failure modes here are occlusion and dashed-line classification, which SR does not fix; SR helps only soft charts. Making it a low-confidence fallback keeps PyTorch (~2GB+, GPU) out of the default install and CI |
| Node-dragging correction UI                     | Largest build in the original sketch; the maintainer wants conversational per-lens feedback, not coordinate editing. A generated 3-panel review file plus chat feedback achieves the goal with no UI framework               |
| Absolute max-delta correctness bar              | False precision for approximate readings; a uniform offset is optically meaningless while a wrong slope is not. Shape (derivative) agreement is the meaningful bar                                                           |
| Variable grid-locked sampling (keep current)    | Sample counts vary by chart (5-8 points), not cross-comparable, and complicate a uniform SVG/DB schema. Fixed 11-point percent-of-height sampling is uniform                                                                 |

## Consequences

- `tools/mtf-extract-skeleton.py` is superseded; `tools/mtf-extract-samyang.py`
  and `tools/mtf-extract-sigma.py` (already legacy) are retired with it. Task
  #563 is closed as superseded.
- A new digitizer package under `tools/` (e.g. `tools/mtfdigitizer/`) hosts the
  profile abstraction, pipeline, SVG emitter, and review-file generator, with
  its own pytest suite — matching the `pagefetch`/`brandkit` package pattern.
  Creating that directory is itself the architectural step this ADR authorizes.
- Real-ESRGAN + PyTorch become an **optional** extra, never a default or CI
  dependency; the pipeline runs without them and flags charts that would need
  them.
- The offset tolerance band stays unspecified until a confirmed reference set
  exists; building that reference set (a handful of visually-verified charts) is
  the first work item, ahead of the profile abstraction.
- Lens pages gain SVG MTF charts (sharper, themeable) in place of raster PNGs,
  once a lens is digitized and verified.
- The fixed 11-point grid changes the `position` values stored for newly
  digitized lenses relative to the existing five grid variants; existing entries
  are re-digitized onto the new grid as they are reprocessed, not migrated
  blindly.
- Per-lens conversational verification is the chosen workflow. Trade-off:
  zero UI build cost, but correction throughput is gated by the review cadence —
  acceptable for an agent-assisted catalog, not suited to an independent
  contributor digitizing solo.
