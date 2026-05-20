# ADR-026: Lens detail page content strategy

**Status:** Accepted
**Date:** 2026-05-17
**Issue:** #572

## Context

Lens detail pages (`/lenses/[slug]/`) contain only data tables and structured
specs. Search engines index thin pages poorly — 461 pages with no prose content
are a discovery liability. The site needs unique, keyword-rich text per page.

## Decision

Generate deterministic prose at build time using score-to-phrase mapping tables.
Each optical field score (0–2 scale) maps to a fixed natural-language phrase.

### Page structure

1. **Summary** — one-line verdict + strengths/weaknesses bullets
2. **Specifications** — lens configuration, MTF charts, specs table
3. **Optical Quality** — prose interpretation grouped into 4 clusters:
   - Sharpness (centerWideOpen, cornerWideOpen, centerStopped, cornerStopped)
   - Aberrations (longitudinalCA, lateralCA, coma, astigmatism, sphericalAberration)
   - Rendering (bokeh, vignettingWideOpen, vignettingStopped, flareResistance)
   - Distortion (distortion)
4. **Genre Fit** — 9 genre sub-sections, each explaining why the lens is
   or isn't suited (pros AND cons derived from formula primary/secondary fields)
5. **Reviews** — professional review source links (from `reviewSources`)
6. **Community** — user opinions as bullet points (from `communityNotes: string[]`,
   populated during scoring research, section hidden when empty)
7. **Alternatives** — direct competitor lenses (same FL range + mount),
   computed at build time, creates internal cross-links and "vs" keyword clusters

## Alternatives considered

| Alternative                              | Rejected because                                                              |
| ---------------------------------------- | ----------------------------------------------------------------------------- |
| Manual descriptions per lens             | Does not scale to 244 lenses; maintenance burden                              |
| LLM-generated content                    | Non-deterministic; can't be validated in CI; requires API calls at build time |
| No prose (status quo)                    | Pages remain thin; Discovery score stays at C                                 |
| Template sentences without score mapping | Produces identical text across lenses; no uniqueness                          |

## Unscored lens content

Unscored lenses lack Optical Quality and Genre Fit sections but still have
enough data for meaningful pages. Sections available without scores:

| Section        | Content source                                            | Est. words |
| -------------- | --------------------------------------------------------- | ---------- |
| Summary        | Spec-derived description (FL, aperture, weight, features) | 40–60      |
| Specifications | Full spec table (already populated)                       | (table)    |
| Reviews        | `reviewSources` links (if any)                            | 20–30      |
| Community      | `communityNotes` (if populated)                           | variable   |
| Alternatives   | Same FL range + mount, computed at build time             | 30–50      |

Additional spec-based prose:

- Focal length context (equivalent mm, descriptive phrase)
- Physical characteristics (weight class, build features, filter thread)
- Key features summary (AF type, OIS, weather sealing, aperture ring)

Estimated word count for unscored pages: **150–200 words** of unique content.
This exceeds typical thin-content thresholds and eliminates the need for
noindex on unscored pages.

## Consequences

- Optical score changes automatically update user-facing prose
- Phrase tables must be maintained — adding a new optical field requires new phrases
- Unscored lenses still get meaningful spec-based content (~150–200 words)
- Generated text is a competitive advantage: unique per lens, no manual effort
- Content quality is bounded by data quality — garbage scores produce garbage prose
- Page word count: ~400 words (scored) / ~150–200 words (unscored)
- Genre Fit alone generates ~270 words (9 genres × ~30 words each)
- 9 genre sub-headings per lens create 2,196 unique keyword-rich sections across the site
- Each genre explanation directly answers "is [lens] good for [genre]?" — featured snippet ready

## Expected outcome

Indexed page count increases from ~106 (23%) to 300+ as scored lens pages
cross Google's quality threshold for indexing. Unique prose per page provides
the content signal that pure data tables lack.

## Missing data handling

When optical scores or genre marks are absent, explain why using
`scoringStatus?: "niche" | "new" | "discontinued" | "specialty" | "pending"`
on the Lens interface.

| Status         | Generated phrase                                             |
| -------------- | ------------------------------------------------------------ |
| `niche`        | Limited professional review coverage for this lens.          |
| `new`          | Recently released — professional reviews pending.            |
| `discontinued` | Discontinued before comprehensive optical testing.           |
| `specialty`    | Standard optical bench tests do not apply to this lens type. |
| `pending`      | Scoring in progress.                                         |

Applied to Optical Quality and Genre Fit sections only — spec-based sections
(Summary, Specifications, Alternatives) render regardless of scoring status.
Field is set during data entry. Absent `scoringStatus` on an unscored lens defaults
to `niche`.

## Implementation

- Utility function: `generateLensContent(lens) → ContentSpine`
- Phrase tables: score → natural-language string (review-style wording)
- Focal length context: equivalent mm → descriptive phrase
- Optical Quality uses 4 clusters (not 14 sub-headings) for UX scannability
  and SEO substance — individual field names appear in prose, not headings
- MTF charts from `docs/mtf-charts/` served as images within Specifications

### Summary template

```
A {fl} f/{aperture} {type} for Fujifilm {mount}-mount ({equiv}mm equivalent) —
{flContext}. {weight}g, ~${price}. {status}.
```

Strengths: bullet list of fields with score >= 1.5.
Weaknesses: bullet list of fields with score <= 0.5.

### Focal length context phrases

| Equivalent | Phrase                                                           |
| ---------- | ---------------------------------------------------------------- |
| <= 18mm    | ultra-wide field of view for interiors and dramatic perspectives |
| 19-28mm    | wide-angle suited for landscapes and architecture                |
| 29-40mm    | moderate wide angle for street and environmental portraits       |
| 41-60mm    | standard field of view close to human vision                     |
| 61-90mm    | short telephoto ideal for portraits and subject isolation        |
| 91-135mm   | telephoto compression for portraits and detail shots             |
| 136-200mm  | telephoto reach for sports and candid photography                |
| 201-400mm  | super-telephoto reach for wildlife and distant subjects          |
| 401+mm     | extreme telephoto for birding and surveillance distances         |

### Optical Quality phrase tables

#### Sharpness

| Field          | Score 2                                           | Score 1.5                                    | Score 0.5                                        | Score 0                                   |
| -------------- | ------------------------------------------------- | -------------------------------------------- | ------------------------------------------------ | ----------------------------------------- |
| centerStopped  | excellent center sharpness when stopped down      | very good center sharpness when stopped down | average center sharpness even stopped down       | poor center sharpness stopped down        |
| cornerStopped  | excellent corner-to-corner sharpness stopped down | very good corner sharpness stopped down      | soft corners even stopped down                   | very weak corner performance stopped down |
| centerWideOpen | sharp in the center wide open                     | good center performance wide open            | soft center wide open, improves on stopping down | weak center sharpness wide open           |
| cornerWideOpen | impressive corner sharpness even wide open        | decent corner performance wide open          | soft corners wide open                           | very weak corner performance wide open    |

Sweet spot: append "Sharpest at f/{sweetSpotAperture}." when defined.

#### Aberrations

| Field               | Score 2                                       | Score 1.5                              | Score 0.5                                    | Score 0                                              |
| ------------------- | --------------------------------------------- | -------------------------------------- | -------------------------------------------- | ---------------------------------------------------- |
| longitudinalCA      | negligible longitudinal chromatic aberration  | well-corrected longitudinal CA         | noticeable longitudinal chromatic aberration | pronounced longitudinal CA (color fringing in bokeh) |
| lateralCA           | practically zero lateral chromatic aberration | low lateral chromatic aberration       | visible lateral chromatic aberration         | strong lateral CA on frame edges                     |
| coma                | well-controlled coma                          | moderate coma control                  | noticeable coma in corners                   | strong coma (problematic for point light sources)    |
| astigmatism         | minimal astigmatism                           | moderate astigmatism                   | noticeable astigmatism                       | strong astigmatism                                   |
| sphericalAberration | well-controlled spherical aberration          | proper spherical aberration correction | noticeable spherical aberration              | poorly controlled spherical aberration               |

#### Rendering

| Field              | Score 2                              | Score 1.5                             | Score 0.5                                        | Score 0                                 |
| ------------------ | ------------------------------------ | ------------------------------------- | ------------------------------------------------ | --------------------------------------- |
| bokeh              | smooth, pleasing bokeh rendering     | good bokeh character                  | busy bokeh character                             | harsh, distracting bokeh                |
| vignettingWideOpen | minimal light falloff wide open      | moderate vignetting wide open         | distinct vignetting wide open                    | heavy light falloff at maximum aperture |
| vignettingStopped  | virtually no vignetting stopped down | negligible vignetting stopped down    | some vignetting persists stopped down            | notable vignetting even stopped down    |
| flareResistance    | excellent flare resistance           | good performance against bright light | performance against bright light could be better | poor flare resistance                   |

#### Distortion

| Field      | Score 2               | Score 1.5      | Score 0.5             | Score 0                                     |
| ---------- | --------------------- | -------------- | --------------------- | ------------------------------------------- |
| distortion | negligible distortion | low distortion | noticeable distortion | significant distortion requiring correction |

### Genre formula reference

| Genre        | Primary fields                           | Secondary fields                                                                                  |
| ------------ | ---------------------------------------- | ------------------------------------------------------------------------------------------------- |
| nightscape   | centerWideOpen                           | \_apertureScore, lateralCA, longitudinalCA, vignettingStopped, flareResistance, astigmatism, coma |
| landscape    | centerStopped, cornerStopped             | lateralCA, longitudinalCA, vignettingStopped, flareResistance, astigmatism, coma                  |
| architecture | cornerStopped, centerStopped, distortion | lateralCA, vignettingStopped, flareResistance                                                     |
| portrait     | bokeh, centerWideOpen                    | longitudinalCA, sphericalAberration, vignettingWideOpen                                           |
| street       | centerStopped, \_apertureScore           | centerWideOpen, flareResistance, longitudinalCA, coma                                             |
| travel       | centerStopped, \_weightScore             | \_apertureScore, flareResistance, longitudinalCA                                                  |
| sport        | centerWideOpen                           | \_apertureScore, longitudinalCA, lateralCA                                                        |
| wildlife     | centerWideOpen, centerStopped            | \_apertureScore, longitudinalCA, lateralCA                                                        |
| macro        | centerStopped, \_magnificationScore      | distortion, lateralCA, longitudinalCA, sphericalAberration, bokeh                                 |

### Derived field descriptions

| Derived field               | Natural language                           |
| --------------------------- | ------------------------------------------ |
| \_apertureScore (high)      | fast maximum aperture                      |
| \_apertureScore (low)       | slow maximum aperture limits low-light use |
| \_weightScore (high)        | lightweight and portable                   |
| \_weightScore (low)         | heavy for travel use                       |
| \_magnificationScore (high) | strong close-focus magnification           |
| \_magnificationScore (low)  | low magnification limits close-up work     |

### Genre fit template

```
**{Genre} ({mark}/5):** {pros from formula fields}. {cons from formula fields}.
```

Omit entire section when `genreMarks` is null. Show "Not yet scored." fallback.

### Alternatives matching logic

Same mount + overlapping focal length range (+/-10mm equivalent):

- For a 56mm prime: show all primes in 46-66mm range
- For a 16-55mm zoom: show zooms that overlap that range

Sort by genre similarity (highest overlap in top genres), then by price.
Max 5 alternatives. Omit section when fewer than 2 exist.

### Meta description template

```
{brand} {model}: {topGenre1}, {topGenre2} lens. Strengths: {strength1}, {strength2}. {weight}g, ~${price}.
```

Target: ~150 characters, unique per lens, keyword-rich.
