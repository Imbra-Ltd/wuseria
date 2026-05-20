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

Per-lens scoring justifications live in `docs/optical-specs/<slug>/scoring-log.md`,
one file per lens (migrated from monolithic file per ADR-033).

- Each entry: lens name, sources, rubric table (field → score → source
  data → rubric rule)
- ADR-014 retains only the rubric rules and a pointer to the scoring log

### MTF chart storage

Official manufacturer MTF charts used for scoring are stored in
`docs/mtf-charts/` as pairs:

- `<slug>.jpg` — the original chart image
- `<slug>.md` — companion analysis in the following canonical format:

```markdown
# [Lens model] — MTF Chart Analysis

Source: [link to official product page]
Image: [slug.png](slug.png)

## Chart legend

- At [focal length] (or "APS-C lens" for fixed FL)
- Solid = Sagittal (S), Dashed = Meridional (M)
- Red lines = 10 lp/mm (contrast), Blue lines = 30 lp/mm (resolution)
- X-axis: image height (mm), Y-axis: contrast (0-1)

## Readings

| Position | 10 lp/mm S | 10 lp/mm M | 30 lp/mm S | 30 lp/mm M |
| -------- | ---------- | ---------- | ---------- | ---------- |
| Center   | ~0.XX      | ~0.XX      | ~0.XX      | ~0.XX      |
| ...      | ...        | ...        | ...        | ...        |

## Astigmatism assessment

S/M divergence at 30 lp/mm:

- [Position-by-position analysis of S vs M gap]

**Scoring:** [Summary] → **[score]**

Note: [Lab precedence note if applicable]
```

Sections are mandatory in this order: title, source/image, chart
legend, readings table, astigmatism assessment with scoring line.
Zoom lenses with multiple charts use separate "## Readings — [FL]"
sections per focal length. When multiple aperture charts exist, use
separate "## Readings — [aperture]" sections.

Slug follows the lens data convention: `viltrox-af-56mm-f1-4-stm`.

### Field completeness

Every scoring log entry MUST list all 14 optical fields. Fields without
data use one of three explicit markers instead of being omitted:

| Marker                       | Meaning                                             |
| ---------------------------- | --------------------------------------------------- |
| `undefined — not tested`     | Source reviewed the lens but didn't test this field |
| `undefined — no data`        | No trusted source has data for this field           |
| `undefined — not applicable` | Field doesn't apply (e.g. bokeh for fisheye)        |

This turns the scoring log into a complete audit — every field is
accounted for. Agents can identify gaps, target searches for missing
fields when new sources become available, and avoid re-searching
fields confirmed as untestable.

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
- `docs/mtf-charts/` added to project layout in CLAUDE.md; scoring log
  now lives in per-lens `docs/optical-specs/<slug>/scoring-log.md`
