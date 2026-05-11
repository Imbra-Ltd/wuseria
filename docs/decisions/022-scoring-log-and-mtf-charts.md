# ADR-022: Scoring log and MTF chart storage

**Status:** Accepted
**Date:** 2026-05-11

## Context

ADR-014 defined the optical quality rubric and originally contained all
per-lens scoring justification tables. After scoring ~20 lenses, the ADR
grew to 650+ lines — most of it scoring data, not rubric rules. The ADR
became hard to maintain and review.

Separately, some lenses lack lab reviews but have official manufacturer
MTF charts that can be used for astigmatism scoring (S/M line divergence).
The readings from these charts are approximate (visually estimated from
plotted curves) and need to be documented alongside the source image so
the scoring is reproducible.

## Decision

### Scoring log

Per-lens scoring justifications are extracted from ADR-014 into a
standalone file: `docs/scoring-log.md`.

- Organized by brand (alphabetical), then focal length (wide to tele)
- Each entry: lens name, sources, rubric table (field → score → source
  data → rubric rule)
- ADR-014 retains only the rubric rules and a pointer to the scoring log

### MTF chart storage

Official manufacturer MTF charts used for scoring are stored in
`docs/mtf-charts/` as pairs:

- `<slug>.jpg` — the original chart image
- `<slug>.md` — companion analysis containing:
  - Source URL
  - Chart legend (apertures, line styles, frequencies)
  - Approximate readings at key positions (center, 4mm, 8mm, 10mm, 14mm)
  - Astigmatism assessment (S/M divergence interpretation)
  - Final score with rubric mapping

Slug follows the lens data convention: `viltrox-af-56mm-f1-4-stm`.

### Genre mark completeness

All computed genre marks must be stored on the lens, including low scores
(e.g. macro=1). Transparency over curation — users see the full picture
and judge relevance themselves.

## Alternatives considered

| Alternative                            | Why rejected                                                                        |
| -------------------------------------- | ----------------------------------------------------------------------------------- |
| Keep scoring tables in ADR-014         | ADR became unwieldy; mixing rules with data                                         |
| Store scoring in a database/JSON       | Overkill for static site; Markdown is reviewable in PRs                             |
| Store only MTF images without analysis | Readings are approximate; without documented numbers the scoring isn't reproducible |
| Omit low genre marks                   | Hides information; users can't see why a lens scores poorly for a genre             |

## Consequences

- ADR-014 stays focused (~215 lines) on rubric methodology
- Scoring log grows with each scored lens but is organized by brand
  for quick navigation
- MTF chart analysis files create a traceable evidence chain:
  image → readings → rubric rule → score
- New scoring workflow step in PLAYBOOK (step 3 in "Write the data")
- `docs/mtf-charts/` and `docs/scoring-log.md` added to project layout
  in CLAUDE.md
