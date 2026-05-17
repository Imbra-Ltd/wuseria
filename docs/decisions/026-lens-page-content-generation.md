# ADR-026: Generate lens page prose from data at build time

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

## Consequences

- Optical score changes automatically update user-facing prose
- Phrase tables must be maintained — adding a new optical field requires new phrases
- Unscored lenses get minimal content ("Not yet scored")
- Generated text is a competitive advantage: unique per lens, no manual effort
- Content quality is bounded by data quality — garbage scores produce garbage prose
- Page word count: ~400 words (scored) / ~30 words (unscored)
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

Applied to Optical Quality, Genre Fit, and any section that depends on scored data.
Field is set during data entry. Absent `scoringStatus` on an unscored lens defaults
to `niche`.

## Implementation

- Utility function: `generateLensContent(lens) → ContentSpine`
- Phrase tables: score → natural-language string (review-style wording)
- Focal length context: equivalent mm → descriptive phrase
- Optical Quality uses 4 clusters (not 14 sub-headings) for UX scannability
  and SEO substance — individual field names appear in prose, not headings
- MTF charts from `docs/mtf-charts/` served as images within Specifications
- Spec stored in: `temp/lens-content-spine.md`
