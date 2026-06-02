# ADR-038: Unified MTF chart digitizer with declared profiles and shape-based verification

**Status:** Accepted; partially superseded by [ADR-041](041-production-digitization-no-per-lens-gt.md)
**Date:** 2026-05-29

> **Partially superseded by ADR-041 (2026-06-02).** This ADR's
> reference-set bootstrap was read as if every digitized lens needed
> eye-read ground truth. ADR-041 splits the workflow into two tiers:
> calibration anchors (one per `(brand, style_family)`, GT required,
> maintainer-only eye-read) and production digitizations (everything
> else, render-match + plausibility priors + overlay glance, no per-lens
> GT). The five pillars below still describe the calibration tier; the
> production tier reuses pillars 1–3 unchanged and replaces the §4 GT
> dependency with the confidence gate this ADR already specifies.

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
  -> re-render readings to a curve layer, pixel-compare against the original
     (round-trip render-match) + physical-plausibility priors -> confidence
       |
       +-- low confidence -> [optional] Real-ESRGAN super-resolution + CLAHE,
       |                      re-extract once
       v
  -> emit SVG (display + provenance) + readings + 3-panel review file
  -> append a confidence line to the run log (high / low + reason)
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

#### Confidence signal: round-trip render-match + plausibility priors

The goal is **high-confidence automation with bounded manual work**: most
charts auto-commit, and the maintainer's attention goes only to the ones the
tool is unsure about. That requires a confidence signal that catches the
_confident-wrong_ failures, not just visibly-jagged tracing.

The **primary signal is round-trip render-match**. The extracted readings are
re-rendered to a curve layer and pixel-compared against the original chart
region; high pixel agreement means the whole pipeline output (shape _and_
calibration) reproduces the original.

```
original chart --> [extract] --> readings --> [re-render curve layer]
       |                                              |
       +------------------> pixel-compare <-----------+
                                  |
                          match score (0-1)
```

This is deliberately stronger than a curve-smoothness score (the kind that
measures slope jitter or gap jumps). A smoothness score only catches
_extraction_ failures — a line that was hard to follow. It misses the two
failure classes that produce smooth, plausible, **wrong** output:

- **Calibration errors** — a wrong grid-step guess traces the curve
  perfectly but places it at the wrong image-height. Round-trip render
  catches this _when the curve has structure on the mis-scaled axis_: a wrong
  x-scale lands a sloped curve in the wrong place, so pixels disagree.
- **Soft-chart curve merges** — a single curve re-rendered where the original
  shows two distinct lines leaves the second line unmatched, dropping the
  score.

Round-trip render-match has **two blind spots**, both confirmed by a
de-risking probe on six representative charts.

1. **Legend/label semantics.** If the tool swaps "10 lp/mm S" with "30 lp/mm
   M" but traces both curves correctly, the re-rendered image is
   pixel-identical to the original while the data is internally mislabeled
   (the caption-swap case some brand pages exhibit). Pixel comparison cannot
   see this.
2. **Translation along a flat axis.** Render-match is translation-invariant
   where the curve is flat. The probe shifted a flat chart's curves 8%
   horizontally and render-match barely moved (IoU 0.86 -> 0.69), whereas a
   sloped chart collapsed (0.83 -> 0.08). So a horizontal mis-calibration on a
   horizontally-flat curve — exactly the idealized-flat charts like the
   300mm reflex — slips through. (A vertical shift still collapses it to 0.00;
   only the flat axis is blind.)

To cover both blind spots, **physical-plausibility priors** run as a cheap
semantic guard (no external data needed). A chart fails the guard if it
violates hard optical facts:

- center MTF is not >= edge MTF;
- 10 lp/mm is not >= 30 lp/mm at every point (swapping the bands inverts
  this — a reliable tell);
- a curve is suspiciously flat across the whole field at ~1.0 (no real lens
  holds near-perfect MTF to the edge — this is the idealized/placeholder
  chart, and the precise case render-match's flat-axis blind spot misses);
- values fall outside a plausible range.

**A chart is high-confidence only when render-match clears its threshold AND
the plausibility priors hold.** Anything else is flagged low-confidence. The
probe confirmed this two-signal design is necessary, not redundant: neither
signal alone is sufficient, but each covers the other's blind spots.

#### Workflow: confidence log + chat summary

Every run appends a confidence line per chart to a log. The maintainer asks
for a summary in chat and works only the low-confidence entries:

```
MTF digitization run -- 31 charts
  HIGH confidence (auto-committed): 24
  LOW confidence (needs review):     7
    - samyang-300mm-reflex   : render-match 0.61  (grid-step ambiguous)
    - 7artisans-35mm-f1-2-ii : plausibility FAIL  (10<30 at edge -- bands swapped?)
    - meike-25mm-f0-95       : render-match 0.72  (dashed line merged -- soft JPEG)
    ...
```

For a flagged chart the maintainer opens its 3-panel review file, sees what is
wrong, and gives feedback in conversation; the agent adjusts the extraction
(profile tuning, mask range, sample handling) and regenerates. There is no
node-dragging editor. High-confidence charts are not shown — the point is that
the maintainer is never asked to eyeball a chart the tool already verified two
independent ways.

The render-match **threshold needs calibration**, not a blind constant: soft
JPEGs score lower even when correct, so the threshold must account for input
quality or every promo chart false-flags. It is tuned against the reference
set (the first work item), alongside the offset tolerance band.

**What "correct" means** is shape agreement: at each sample point the traced
curve's slope matches the original's, and a uniform vertical offset within a
tolerance band is acceptable (the readings are approximate by nature). That is
the optical definition of correct. Render-match is how the tool _measures_ it
automatically — a high render-match score is shape agreement observed in
pixels. The tolerance band is left as an **open parameter**, set against the
reference set; it cannot be derived from the existing `mtf-readings.ts` data,
because that data is itself unverified — the verify pass _found_ two wrong
entries in it.

### 5. Output artifacts

- **SVG**, committed to `docs/optical-specs/<slug>/`. It serves two roles:
  the lens-page display asset (sharp at any zoom, dark-theme recolorable)
  and the provenance record. It is generated from the numbers, never by
  raster vectorization (see alternatives).
- **Readings**, written to `src/data/mtf-readings.ts` (existing schema).

The SVG and the committed numbers carry the same readings — one source of
truth, no drift between the picture and the data.

Because the SVG is user-visible, a digitization error would show on the live
site, not just in scoring — so commit is **gated on confidence, not on a
manual pass for every chart**. High-confidence charts (render-match clears its
threshold AND plausibility priors hold) commit automatically; low-confidence
charts are held for the maintainer's review before commit. The confidence
signal is the gate, which is why it must catch the confident-wrong cases, not
just jagged tracing.

## Alternatives considered

| Alternative                                                  | Why rejected                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Per-brand scraper scripts (#563)                             | Multiplies the two-brand problem into ~24 bespoke scripts with no shared adaptation. Superseded by this ADR.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Auto-detect profile (no declaration)                         | Mis-profiling is the exact silent-corruption failure B1 fixed. Declaration keeps the authority explicit (project value: explicit over implicit).                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| K-means color clustering to isolate lines                    | Cannot separate two same-colored curves (the Chinese-brand case). Only the connected-components-by-width split can.                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Raster-to-SVG vectorization (Potrace)                        | Soft promo charts vectorize into hundreds of tiny path fragments; reconnecting them is the dash-bridging problem made harder, with color information thrown away. Generate the SVG from extracted numbers instead.                                                                                                                                                                                                                                                                                                                                                                                |
| Super-resolution as a mandatory first stage                  | The real failure modes are occlusion and dashed-line classification, which SR doesn't fix; SR helps only soft charts. Making it a low-confidence fallback keeps PyTorch (~2GB+, GPU) out of the default install and CI.                                                                                                                                                                                                                                                                                                                                                                           |
| Node-dragging correction UI                                  | The largest build in the original sketch. The maintainer wants conversational per-lens feedback, not coordinate editing — a generated 3-panel review file plus chat feedback achieves the goal with no UI framework.                                                                                                                                                                                                                                                                                                                                                                              |
| WebPlotDigitizer as low-confidence-tail fallback (#942)      | Evaluated as an off-the-shelf coordinate editor for the flagged tail. Unsuitable: four manual datasets per MTF chart (10/30 × S/M), no same-color dashed-vs-solid discrimination (the Fujifilm/Sigma case), no headless/batch path, CSV export via copy-paste popup, and adopting it forfeits the SVG-from-numbers single-source-of-truth property. Calibration reuse via JSON project export across one brand's series is a real win but does not overcome per-chart friction. Conversational correction remains the default; revisit only if the tail proves intolerable once #933 + #935 land. |
| Absolute max-delta correctness bar                           | False precision for approximate readings: a uniform offset is optically meaningless, while a wrong slope is not. Shape (derivative) agreement is the meaningful bar.                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Curve-smoothness confidence score (slope jitter / gap jumps) | Only catches extraction failures (hard-to-follow lines). Misses the confident-wrong cases — wrong calibration and soft-chart curve merges trace smoothly but are wrong. Round-trip render-match catches those by comparing the whole output to the original in pixels.                                                                                                                                                                                                                                                                                                                            |
| Render-match alone as the confidence signal                  | Pixel comparison cannot see legend/label semantics: a chart with swapped S/M or 10/30 labels re-renders pixel-identical. Pair render-match with physical-plausibility priors to guard the semantic blind spot.                                                                                                                                                                                                                                                                                                                                                                                    |
| Variable grid-locked sampling (keep current)                 | Sample counts vary by chart (5-8 points), are not cross-comparable, and complicate a uniform SVG/DB schema. Fixed 11-point percent-of-height sampling is uniform.                                                                                                                                                                                                                                                                                                                                                                                                                                 |

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

**Reference set comes first.** Both the render-match threshold and the offset
tolerance band stay unspecified until a confirmed reference set exists.
Building that set (a handful of visually-verified charts) is the first work
item, ahead of the profile abstraction — nothing in the confidence gate can be
calibrated without it.

**Confidence design validated by probe.** A de-risking probe on six
representative charts (clean Sigma, mid Samyang, the flat 300mm reflex, small
7Artisans) confirmed render-match separates good extractions (IoU 0.64-0.87)
from mis-calibrated ones (IoU drops to 0.03-0.49 on sloped curves), and
characterized its flat-axis blind spot — which the plausibility priors cover.
The two-signal gate is empirically necessary, not belt-and-suspenders.

**Lens pages improve.** Pages gain SVG MTF charts (sharper, themeable) in
place of raster PNGs, once a lens is digitized and verified.

**Position grid changes.** The fixed 11-point grid changes the `position`
values stored for newly digitized lenses, relative to the five grid variants
in the current data. Existing entries are re-digitized onto the new grid as
they are reprocessed — not migrated blindly.

**Bounded manual work.** High-confidence charts auto-commit; the maintainer
reviews only the low-confidence ones, surfaced as a chat summary from the run
log. This is high automation, not literally zero-touch — calibration and
legend semantics cannot be self-verified from pixels for every chart, so the
honest target is "auto-commit what two independent checks agree on, flag the
rest," never "trust a single smoothness score and commit blind."

**Workflow trade-off.** Conversational correction of flagged charts has zero
UI build cost, but throughput on the low-confidence tail is gated by the review
cadence. That is acceptable for an agent-assisted catalog; it would not suit an
independent contributor digitizing solo.
