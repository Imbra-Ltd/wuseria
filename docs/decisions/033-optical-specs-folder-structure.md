# ADR-033: Per-Lens Optical Specs Folder Structure

**Status:** Accepted
**Date:** 2026-05-20

## Context

Each lens in `docs/optical-specs/<slug>/` has accumulated files
organically: construction diagrams, MTF charts, and a `specs-log.md` that
mixes MTF readings, analysis predictions, and operational notes. The
scoring log lives in a separate monolithic file (`docs/scoring-log.md`)
with 200+ entries.

This creates several problems:

- `specs-log.md` conflates analysis (predictions from optical data) with
  operational notes (problems, data issues, provenance)
- The monolithic scoring log produces noisy diffs when scoring one lens
  and is hard to navigate
- No clear convention for what files a lens folder should contain

## Decision

Formalize the per-lens folder structure under `docs/optical-specs/<slug>/`:

```
docs/optical-specs/<slug>/
  <slug>-construction.{png,svg} # required — optical construction diagram
  <slug>-mtf-*.{png,svg}        # required — MTF chart images
  analysis.md                   # required — predictions from construction
                                #   parameters and MTF charts (readings,
                                #   astigmatism assessment, quality predictions)
  scoring-log.md                # required when scored — per-lens scoring
                                #   justification (same format as ADR-022)
  specs-log.md                      # required — technical specs provenance log
```

### Image format

Images in optical-specs folders must be **PNG or SVG**. Source images
downloaded as JPG or WebP must be converted to PNG before committing.
SVG is preferred when the source provides it — vector format preserves
chart text and diagram lines at any scale. PNG is acceptable for raster
sources. No other formats (JPG, WebP, GIF) are allowed.

### File responsibilities

- **analysis.md** — deterministic: given the construction and MTF data,
  what can we predict about optical quality? Contains MTF readings
  tables, astigmatism assessments, and construction-based predictions.
- **scoring-log.md** — justification: why was each optical field scored
  the way it was? Links sources, applies the rubric (ADR-014), records
  the trust level. Same field format as the monolithic scoring log
  defined in ADR-022.
- **specs-log.md** — technical specs provenance: auditable log of all
  research performed to find the lens's technical specifications
  (construction diagrams, MTF charts, element/group counts, coatings,
  special glass types, magnification data). Documents every source
  checked (successful or not), data extraction issues, conflicting
  sources, and lens-specific caveats. Required for every lens folder.
  Note: this is distinct from `scoring-log.md`, which covers optical
  quality field scoring justification (ADR-014 rubric application).

### specs-log.md format

```markdown
# <Model Name> — Notes

## Data provenance

| Date       | Source        | URL            | Result                   |
| ---------- | ------------- | -------------- | ------------------------ |
| 2026-05-22 | cosina.co.jp  | https://...    | No MTF chart             |
| 2026-05-22 | LensTip       | (not reviewed) | No data                  |
| 2026-05-22 | Dustin Abbott | https://...    | Full review, MTF + bokeh |

## Classification

- Character tier: Tier 1 / Tier 2 / Tier 3 (clinical) / N/A
- Design family: Double Gauss / Sonnar / Retrofocus / etc.

## Caveats

- (e.g. X-mount vs E-mount are different optical designs)
- (e.g. manual PDF checked, no MTF inside)
```

The provenance table is the core — every source checked gets a row,
whether the result was positive or negative. This prevents future
sessions from repeating the same searches and creates a traceable
audit trail for every data point.

### Migration

Incremental. New scores go to per-lens `scoring-log.md`. Existing
entries in the monolithic `docs/scoring-log.md` are migrated when
a lens is re-scored or its folder is otherwise touched. The monolith
remains as-is until empty.

### Cross-lens comparison

Cross-lens comparison is the database's job (`src/data/lenses.ts`).
The scoring log's purpose is provenance (justifying why a score was
given), not cross-reference. No index or summary file is needed.

### Rename existing specs-log.md

Existing `specs-log.md` files that contain MTF readings and analysis are
renamed to `analysis.md`. Every lens folder must have a `specs-log.md`
with at minimum a data provenance table.

## Alternatives considered

**Keep monolithic scoring log** — rejected because it produces noisy
diffs, is hard to navigate, and separates scoring justification from
the optical data it references.

**Keep mixed specs-log.md** — rejected because it conflates analysis
(repeatable predictions) with operational notes (one-time issues),
making both harder to maintain.

**Generate a cross-lens summary from per-lens files** — rejected as
unnecessary; `lenses.ts` already serves this role with structured,
queryable data.

## Consequences

- Existing `specs-log.md` files must be renamed to `analysis.md` (can be
  done in bulk)
- New scoring work writes to per-lens `scoring-log.md`
- Tools (`audit.py`) should be updated to check for `analysis.md`
  instead of `specs-log.md`
- The monolithic `docs/scoring-log.md` has been fully migrated and deleted
  (session 73)
