# ADR-029: Optical Quality page structure — design analysis + lab tests

**Status:** Accepted
**Date:** 2026-05-19
**Supersedes:** ADR-026 section 3 (Optical Quality)

## Context

ADR-026 defined Optical Quality as a single section with 4 clusters (Sharpness,
Aberrations, Rendering, Distortion) derived from review scores. This works for
scored lenses but leaves unscored lenses — especially Chinese budget brands
(7Artisans, TTartisan, Meike, Pergear, Kamlan) — with no optical content at all.

We now have two additional data sources beyond review scores:

1. **MTF chart readings** — digitized from manufacturer charts (22 lenses
   and growing, stored in `src/data/mtf-readings.ts`)
2. **Optical construction data** — element/group count, special glass
   (stored on the Lens interface: `opticalElements`, `opticalGroups`,
   `specialElements`)

These sources are available for many unscored lenses because manufacturers
publish MTF charts and construction specs regardless of whether reviewers
have tested the lens. Separating design-side evidence from measured evidence
also makes provenance explicit (see #709).

### The budget brand problem

Budget Chinese lenses often have impressive manufacturer MTF charts but
higher unit-to-unit variation than premium brands. Users need to:

- See what the optical design promises (MTF + construction analysis)
- Understand what reviewers confirmed (lab/field test scores)
- Know when the gap between promise and delivery is uncertain

A single flat section cannot express this distinction.

## Decision

Split the Optical Quality section into three sub-sections:

### 3.1 Overview

Score pips for all 14 optical fields at a glance. One-line overall verdict
(e.g. "Strong performer with well-controlled aberrations"). Hidden when
no scores exist.

### 3.2 Optical Design Analysis

What the lens design tells us about performance. Renders when MTF readings
or optical construction data exist — does not require review scores.

**MTF contains real optical information.** Spike #730 confirmed through
authoritative sources (Nikon USA, Zeiss H.H. Nasse, LensRentals Roger
Cicala, Eckhardt Optics) that MTF charts reveal sharpness, astigmatism
(S/M divergence), bokeh tendency (S/M convergence), and field curvature.
These are established optical principles, not speculation.

The key variable is **computed vs measured MTF** — not whether the
relationships are valid:

| MTF type                              | Manufacturers                                | Content confidence                                                 |
| ------------------------------------- | -------------------------------------------- | ------------------------------------------------------------------ |
| **Measured** (from production lenses) | Zeiss, Leica, Sigma Art                      | High — real performance; can support scoring alongside reviews     |
| **Computed** (from optical design)    | Canon, Nikon, Fujifilm, Samyang, most others | Design intent — actual performance varies by manufacturing quality |

Content language adapts to the confidence tier. Measured MTF warrants
direct statements ("resolves fine detail well at the center"). Computed
MTF uses qualified language ("the optical design targets strong center
resolution").

**MTF Chart Analysis** (when `mtfReadings` exist for this lens):

- SVG chart rendered inline (already implemented)
- Center vs corner contrast (10 lp/mm S/M curves at wide open)
- Center vs corner resolution (30 lp/mm S/M curves at wide open)
- Astigmatism (S/M divergence across the field — this IS how astigmatism
  manifests in MTF; confirmed by Nikon USA, Eckhardt Optics)
- Bokeh tendency (S/M convergence — closer lines = smoother out-of-focus
  rendering; confirmed by Nikon USA, Luminous Landscape, Fstoppers)
- Field curvature (wavy mid-field dip pattern)
- Stopped-down improvement (if second aperture data available)

Phrase mapping — **measured MTF** (Sigma Art, Zeiss, Leica):

| MTF range (30 lp/mm center) | Phrase                                                           |
| --------------------------- | ---------------------------------------------------------------- |
| ≥ 0.90                      | Excellent center resolution                                      |
| 0.75–0.89                   | Good center resolution — typical for this aperture class         |
| 0.60–0.74                   | Moderate center resolution — sharpness improves on stopping down |
| < 0.60                      | Soft center wide open — stopping down recommended                |

Phrase mapping — **computed MTF** (Samyang, Nikon, Canon, Fujifilm, others):

| MTF range (30 lp/mm center) | Phrase                                                                               |
| --------------------------- | ------------------------------------------------------------------------------------ |
| ≥ 0.90                      | The optical design targets excellent center resolution                               |
| 0.75–0.89                   | The optical design targets good center resolution                                    |
| 0.60–0.74                   | The optical design trades center resolution for other priorities (speed, size, cost) |
| < 0.60                      | Limited fine-detail resolution in the design — stopping down expected                |

Similar tables for edge performance, S/M divergence (astigmatism), and
S/M convergence (bokeh). Full phrase tables defined in implementation.

Thresholds follow Luminous Landscape convention: >0.8 = excellent, >0.6 =
satisfactory (for 10 lp/mm contrast). Resolution (30 lp/mm) thresholds
are more demanding.

**Rendering Character** (derived from MTF contrast-resolution relationship):

Some lenses are deliberately designed for "pop" — punchy subject separation
with smooth micro-detail — rather than maximum clinical sharpness. This is
readable from the gap between 10 lp/mm (contrast) and 30 lp/mm (resolution)
curves. Classic examples: XF 35mm f/1.4 R, XF 56mm f/1.2 R.

| 10 lp/mm (contrast) | 30 lp/mm (resolution) | Rendering character                                                                                         |
| ------------------- | --------------------- | ----------------------------------------------------------------------------------------------------------- |
| High (≥0.90)        | High (≥0.85)          | Clinical / analytical — every detail resolved; ideal for landscape, architecture, product                   |
| High (≥0.90)        | Moderate (0.65–0.80)  | "Pop" / 3D rendering — punchy contrast with smooth micro-detail; flattering for skin, compelling for street |
| High (≥0.90)        | Low (<0.65)           | Soft-focus character — dreamy, vintage rendering                                                            |
| Moderate (<0.90)    | Moderate              | Flat rendering — neither clinical nor artistic                                                              |

Additional rendering signals from MTF:

- **Bokeh transition quality** — S/M convergence (already in MTF analysis)
  indicates how smoothly the lens transitions between in-focus and
  out-of-focus areas
- **3D rendering tendency** — high contrast + controlled resolution =
  subject separation ("the subject jumps off the background")
- **Cinema character** — cinema lenses deliberately introduce controlled
  spherical aberration for smooth focus falloff (gradual roll-off rather
  than cliff edge between center and corners); they also prioritize
  consistent cross-frame rendering (flatter curves) over peak sharpness
  (high curves)

This section is especially valuable for:

- Portrait photographers choosing between clinical vs flattering rendering
- Street photographers wanting subject "pop" in busy scenes
- Video/cinema shooters looking for organic rendering character
- Budget lens buyers — a 7Artisans 35mm f/0.95 with high contrast but
  moderate resolution has genuine artistic appeal that pure sharpness
  scores miss entirely

Genre relevance: rendering character directly informs portrait, street,
and travel genre fit explanations. A lens with "pop" rendering gets a
qualitative edge in these genres even if its raw sharpness score is
moderate.

**Stopped-Down Behavior** (when both wide-open and stopped-down MTF exist):

The delta between wide-open and stopped-down MTF answers "should I stop
down this lens?" — a question every photographer asks.

| Wide open → stopped down              | Meaning                                                      | Phrase                                                                              |
| ------------------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| Small improvement (Δ30S < 0.05)       | Well-corrected wide open — shoot confidently at max aperture | "Already sharp wide open — stopping down gains little"                              |
| Moderate improvement (Δ30S 0.05–0.15) | Aberration-limited wide open, benefits from stopping down    | "Sharpens noticeably when stopped down — best results around f/5.6–f/8"             |
| Large improvement (Δ30S > 0.15)       | Significant aberrations wide open, transforms stopped down   | "Wide-open rendering is soft — stop down to f/5.6 or beyond for critical sharpness" |

Genre relevance: landscape, architecture, and product photographers
need to know if stopping down is required. Portrait and street photographers
need to know if wide-open performance holds up.

Samyang charts provide both MAX aperture and F8 data. Sigma charts are
wide-open only (second aperture requires separate charts not yet collected).

**Cross-Frame Consistency** (center-to-edge MTF delta):

How flat the MTF curves are across the field. Two lenses with the same
average sharpness can have very different uniformity.

| Center-edge delta (30 lp/mm) | Pattern                             | Phrase                                                    |
| ---------------------------- | ----------------------------------- | --------------------------------------------------------- |
| Small (< 0.10)               | Flat — consistent across frame      | "Even performance from center to corners"                 |
| Moderate (0.10–0.25)         | Gradual falloff — typical           | "Moderate corner softening — typical for this lens class" |
| Large (> 0.25)               | Steep — strong center, weak corners | "Sharp center with significant corner falloff"            |

Genre relevance:

- Architecture, astrophotography, group portraits need high consistency
  (flat curves matter more than peak sharpness)
- Portrait, street tolerate steep falloff (center subject sharpness is
  what matters; soft corners add natural vignette-like focus)
- Landscape depends on the shot — foreground-to-infinity compositions
  need consistency; distant subjects need center sharpness

**What MTF charts cannot reveal** (every authoritative source agrees):

- Chromatic aberration (longitudinal or lateral)
- Distortion (barrel/pincushion)
- Vignetting / light falloff
- Flare resistance
- Coma (partially visible in S/M edge divergence, but not cleanly isolated
  from astigmatism)

**Optical Construction Analysis** (when `opticalElements` or `specialElements`
exist):

These are physical optical properties — the element types determine what
aberrations the design corrects. This is established optical engineering,
not inference. Validated against LensTip lab reviews for 5 Fujifilm lenses
in spike #730 preliminary research (~90% confidence).

High-confidence construction signals:

| Construction feature                        | Optical effect                                                                                            | Confidence |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------- | ---------- |
| ED/SED/UED/fluorite elements                | Control chromatic aberration (fringing)                                                                   | High       |
| Aspherical elements                         | Correct spherical aberration and reduce distortion                                                        | High       |
| Aspherical count ≥ 3 on FL ≤ 16mm           | Optical (not software) distortion correction                                                              | High       |
| ED count ≥ 5 on FL ≥ 200mm                  | Advanced fringing suppression for telephoto                                                               | High       |
| Elements − groups (cemented boundaries)     | Fewer air-glass surfaces = less internal reflection; diff ≤ 2 = high flare risk without advanced coatings | High       |
| UMC/SMC/nano/T\* coatings                   | Flare and ghosting resistance                                                                             | High       |
| High element count for a simple prime       | Modern high-resolution sensor-optimized design                                                            | Medium     |
| Symmetric layout (e.g. Double Gauss)        | Naturally cancels barrel/pincushion distortion                                                            | Medium     |
| High aspherical ratio in low-element design | Sharp center, potentially softer corners                                                                  | Medium     |

Content generation from construction:

- Element/group count in context (e.g. "13 elements in 10 groups — a
  complex design for a 56mm prime")
- Special element interpretation with direct language: "2 ED elements
  control chromatic aberration" — not "designed to control"
- Construction class relative to price point (value assessment)
- When scored: cross-reference with lab results ("2 ED elements control
  CA — reviewer testing confirms well-controlled fringing")
- When unscored: state the physical properties without a score claim
  ("2 ED elements control CA; no independent test data available yet")

What construction CANNOT predict:

| Field                  | Why                                                                                                                                                                    |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Vignetting             | Depends on physical barrel diameter vs sensor, not glass layout                                                                                                        |
| Coating-override flare | Nano-GI/T\* coatings can overcome structural flare risk; need coating data to assess (validated: XF 16mm f/1.4 has only 2 cemented boundaries but Nano-GI compensates) |
| Bokeh quality          | Blade count affects highlight shape, but rendering smoothness depends on aberration balance that construction alone cannot predict                                     |
| Sample variation       | High group count + budget assembly = alignment risk, but this is manufacturing quality, not optical design                                                             |

**Manufacturing variance disclaimer** (conditional):

Tied to whether MTF data is computed or measured — not just brand tier.
A Sigma Art lens with measured MTF (every copy tested) warrants more
confidence than a Samyang with computed MTF. Roger Cicala (LensRentals):
_"the real-life curves are never quite as good as the image suggests"_
— but they are correlated, not random.

Shown for lenses with computed MTF from manufacturers without per-copy
testing:

> _Manufacturer MTF charts represent optimal production samples. Budget
> manufacturers may show higher unit-to-unit variation — real-world
> performance can fall below these design targets._

Shown for brands where community consensus or known QC issues warrant it.
Not a blanket disclaimer on all budget brands — some (e.g. Viltrox) have
good consistency.

### 3.3 Lab & Field Tests

What reviewers actually measured. Renders only when optical scores exist.
Grouped by concern using the same 4-cluster structure from ADR-026:

**Sharpness**

- centerWideOpen, cornerWideOpen, centerStopped, cornerStopped

**Chromatic Aberration**

- longitudinalCA, lateralCA

**Aberrations**

- coma, astigmatism, sphericalAberration

**Rendering**

- bokeh, vignettingWideOpen, vignettingStopped, flareResistance

**Distortion**

- distortion

Each cluster uses score-to-phrase mapping (unchanged from ADR-026). When
both design analysis and lab test data exist for the same concern, the lab
test prose can reference the design prediction:

> "MTF charts predicted strong center sharpness — reviewer testing confirms
> excellent performance wide open (2/2)."

Or flag a discrepancy:

> "Despite promising MTF curves, reviewer testing found only moderate center
> sharpness (1/2) — possibly due to sample variation or focus calibration."

### Content availability matrix

| Data available              | 3.1 Overview | 3.2 Design Analysis | 3.3 Lab & Field        |
| --------------------------- | ------------ | ------------------- | ---------------------- |
| Scores + MTF + construction | Pips         | MTF + construction  | Full prose             |
| Scores only                 | Pips         | Hidden              | Full prose             |
| MTF + construction only     | Hidden       | MTF + construction  | `scoringStatus` phrase |
| MTF only                    | Hidden       | MTF only            | `scoringStatus` phrase |
| Construction only           | Hidden       | Construction only   | `scoringStatus` phrase |
| Nothing                     | Hidden       | Hidden              | `scoringStatus` phrase |

### Estimated word counts

| Section              | Scored lens | Unscored + MTF + construction | Unscored + nothing |
| -------------------- | ----------- | ----------------------------- | ------------------ |
| 3.1 Overview         | 10–20       | —                             | —                  |
| 3.2 Design Analysis  | 80–120      | 80–120                        | —                  |
| 3.3 Lab & Field      | 120–180     | 20–30 (status phrase)         | 20–30              |
| **Total OQ section** | **210–320** | **100–150**                   | **20–30**          |

Combined with other page sections (Summary, Specs, Genre Fit, Reviews,
Community, Alternatives), unscored lenses with MTF data reach **250–350
words** — well above thin-content thresholds.

## Alternatives considered

| Alternative                                    | Rejected because                                                      |
| ---------------------------------------------- | --------------------------------------------------------------------- |
| Keep flat 4-cluster structure (ADR-026)        | No content for unscored lenses; no provenance distinction             |
| Integrated "expected vs delivered" per cluster | Reads better for scored lenses but produces nothing for unscored ones |
| Separate Optical Quality page (not section)    | Over-fragments the lens detail page; worse for SEO                    |

## Consequences

- Unscored lenses with MTF charts get ~100–150 words of optical content
  where they previously got zero
- Chinese budget brands become genuinely useful pages instead of thin
  spec-only shells
- Manufacturing variance disclaimer builds user trust — honest about
  limitations without hiding data
- Design analysis creates natural "upgrade path" content: user sees budget
  lens MTF, then sees scored premium alternative with confirmed lab results
- Requires backfilling `opticalElements`/`specialElements` on more lenses
  (currently 1/244) — but MTF readings already cover 22 lenses
- Phrase tables grow: MTF-to-phrase and construction-to-phrase tables needed
  alongside existing score-to-phrase tables
- Provenance is now visible to the user: "the design says X" vs "testing
  confirmed Y" — aligns with #709 (OQ score provenance)
- **Measured MTF (Sigma Art, Zeiss, Leica) can support scoring** as
  evidence alongside reviews — these manufacturers test real production
  lenses. Computed MTF (most others) describes design intent only.
- **ADR-014 fallback #2 (MTF chart for astigmatism) stands** — S/M
  divergence is the established way astigmatism manifests in MTF charts
  (confirmed by Nikon USA, Eckhardt Optics). The earlier data analysis
  that questioned this was methodologically flawed (compared computed MTF
  against measured scores without accounting for the known gap).
- Spikes #707 and #708 remain viable — scoped to confidence-tiered
  content generation, with measured MTF enabling stronger claims than
  computed MTF

## Data requirements

To populate Design Analysis at scale:

1. **MTF readings** — continue digitizing with `mtf-extract-skeleton.py`
   (22 lenses done, 31 charts available)
2. **MTF source type** — track whether each lens's MTF is computed or
   measured. New field: `mtfType?: "computed" | "measured"` on the MTF
   data record. Defaults to `"computed"`. Sigma Art, Zeiss, Leica get
   `"measured"`.
3. **Optical construction** — backfill `opticalElements`, `opticalGroups`,
   `specialElements` from manufacturer spec sheets (data is readily
   available, just not yet entered)
4. **Manufacturing consistency** — the variance disclaimer is now driven
   by `mtfType` (computed vs measured) rather than a separate brand flag.
   Computed MTF automatically gets the qualified language tier.

## Implementation

- `generateOpticalContent(lens, mtfReadings?) → OpticalContentSpine`
- Three sub-generators: `generateOverview`, `generateDesignAnalysis`,
  `generateLabTests`
- MTF phrase tables: value ranges → natural-language descriptions
- Construction phrase tables: special element types → optical implications
- Variance disclaimer: driven by brand-level flag (TBD: field name and
  location)
- ADR-026 page structure updated: section 3 now references this ADR
