# ADR-030: Optical construction diagram storage

**Status:** Accepted
**Date:** 2026-05-19

## Context

ADR-029 defines an Optical Design Analysis section for lens detail pages
that includes optical construction analysis — element/group interpretation,
special glass, coatings, and cemented boundaries. Manufacturer product
pages publish optical construction diagrams (cross-section schematics
showing element arrangement) that are primary reference material for this
analysis.

MTF charts already have a dedicated directory (`docs/mtf-charts/`,
per ADR-022) with a `.png` + `.md` companion pair convention. Optical
construction diagrams serve a different purpose (design analysis vs.
scoring) and mixing them into `docs/mtf-charts/` would make the directory
name misleading.

## Decision

Store optical construction diagrams in `docs/optical-construction/` as
image files. No companion `.md` analysis files — the construction data
is captured directly in lens data fields (`opticalElements`,
`opticalGroups`, `specialElements`, `coating`).

### Naming convention

`<brand>-<slug>.png` — same slug derivation as MTF charts
(lowercase, hyphens, no special characters).

Examples:

- `fujifilm-xf-14mm-f2-8-r.png`
- `fujifilm-gf-110mm-f2-r-lm-wr.png`

### Fetch workflow

When fetching manufacturer spec pages for optical data, always save:

1. MTF chart images to `docs/mtf-charts/`
2. Optical construction diagrams to `docs/optical-construction/`

Both are reference material, not served on the site (per ADR-027).

## Alternatives considered

**Co-locate in `docs/mtf-charts/` with `-construction` suffix** —
simpler (no new directory) but makes the directory name inaccurate.
Different assets serve different analysis purposes and will be
referenced by different content generators.

## Consequences

- New directory `docs/optical-construction/` for construction diagrams
- Spec fetch workflow saves both MTF charts and construction diagrams
- ADR-029 content generation can reference construction diagrams for
  visual verification during development
