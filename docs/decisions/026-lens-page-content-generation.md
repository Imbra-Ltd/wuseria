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
The content spine has 5 sections: Summary, Strengths, Weaknesses, Genre Fit,
Build (includes sweet spot aperture).

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
- Page word count: ~100 words (scored) / ~30 words (unscored)

## Expected outcome

Indexed page count increases from ~106 (23%) to 300+ as scored lens pages
cross Google's quality threshold for indexing. Unique prose per page provides
the content signal that pure data tables lack.

## Implementation

- Utility function: `generateLensContent(lens) → ContentSpine`
- Phrase tables: score → natural-language string (LensTip-inspired wording)
- Focal length context: equivalent mm → descriptive phrase
- Rendered as semantic HTML sections above spec tables
- Spec stored in: #572 comments / `temp/lens-content-spine.md`
