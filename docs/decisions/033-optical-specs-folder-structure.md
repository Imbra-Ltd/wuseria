# ADR-033: Per-Lens Optical Specs Folder Structure

**Status:** Accepted
**Date:** 2026-05-20

## Context

Each lens in `docs/optical-specs/<slug>/` has accumulated files
organically: construction diagrams, MTF charts, and a `notes.md` that
mixes MTF readings, analysis predictions, and operational notes. The
scoring log lives in a separate monolithic file (`docs/scoring-log.md`)
with 200+ entries.

This creates several problems:

- `notes.md` conflates analysis (predictions from optical data) with
  operational notes (problems, data issues, provenance)
- The monolithic scoring log produces noisy diffs when scoring one lens
  and is hard to navigate
- No clear convention for what files a lens folder should contain

## Decision

Formalize the per-lens folder structure under `docs/optical-specs/<slug>/`:

```
docs/optical-specs/<slug>/
  <slug>-construction.png       # required — optical construction diagram
  <slug>-mtf-*.png              # required — MTF chart images
  analysis.md                   # required — predictions from construction
                                #   parameters and MTF charts (readings,
                                #   astigmatism assessment, quality predictions)
  scoring-log.md                # required when scored — per-lens scoring
                                #   justification (same format as ADR-022)
  notes.md                      # optional — operational notes, problems
                                #   encountered, data provenance issues
```

### File responsibilities

- **analysis.md** — deterministic: given the construction and MTF data,
  what can we predict about optical quality? Contains MTF readings
  tables, astigmatism assessments, and construction-based predictions.
- **scoring-log.md** — justification: why was each optical field scored
  the way it was? Links sources, applies the rubric (ADR-014), records
  the trust level. Same field format as the monolithic scoring log
  defined in ADR-022.
- **notes.md** — operational: anything that doesn't fit analysis or
  scoring. Data extraction problems, URL changes, conflicting sources,
  manual verification notes. Created on demand, not required.

### Migration

Incremental. New scores go to per-lens `scoring-log.md`. Existing
entries in the monolithic `docs/scoring-log.md` are migrated when
a lens is re-scored or its folder is otherwise touched. The monolith
remains as-is until empty.

### Cross-lens comparison

Cross-lens comparison is the database's job (`src/data/lenses.ts`).
The scoring log's purpose is provenance (justifying why a score was
given), not cross-reference. No index or summary file is needed.

### Rename existing notes.md

Existing `notes.md` files that contain MTF readings and analysis are
renamed to `analysis.md`. A fresh `notes.md` is only created when
operational issues need to be recorded.

## Alternatives considered

**Keep monolithic scoring log** — rejected because it produces noisy
diffs, is hard to navigate, and separates scoring justification from
the optical data it references.

**Keep mixed notes.md** — rejected because it conflates analysis
(repeatable predictions) with operational notes (one-time issues),
making both harder to maintain.

**Generate a cross-lens summary from per-lens files** — rejected as
unnecessary; `lenses.ts` already serves this role with structured,
queryable data.

## Consequences

- Existing `notes.md` files must be renamed to `analysis.md` (can be
  done in bulk)
- New scoring work writes to per-lens `scoring-log.md` instead of the
  monolith
- Tools (`audit.py`) should be updated to check for `analysis.md`
  instead of `notes.md`
- The monolithic `docs/scoring-log.md` shrinks over time and is
  eventually deleted
