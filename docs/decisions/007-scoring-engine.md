# ADR-007: Code-defined scoring functions (computed, not stored)

**Status:** Superseded by [ADR-013](013-curated-genre-scoring.md)
**Date:** 2026-04-06

## Context

Genre scores rate each lens across 9 genres (astro, portrait, landscape, etc.). 240 lenses x 9 genres = 2,160 scores. Scores depend on lens optical data that may be updated as MTF reviews are sourced.

## Decision

Scoring formulas are pure TypeScript functions. Scores are computed at render time, not stored in the data files.

## Alternatives considered

| Alternative                             | Why rejected                                                                          |
| --------------------------------------- | ------------------------------------------------------------------------------------- |
| Pre-computed score arrays in data files | Two things to keep in sync — if a lens field changes, stored scores go stale silently |
| ML model                                | Scoring formulas are simple arithmetic; ML adds complexity for no accuracy gain       |
| Database-driven rules                   | No database in the architecture                                                       |

## Consequences

- Single source of truth — change a lens field and scores update automatically
- Each genre is a pure function: `Lens -> ScoreResult` — easy to test
- 2,160 scores computed at build time is trivial (sub-millisecond)
- Scoring logic is transparent and auditable in code
