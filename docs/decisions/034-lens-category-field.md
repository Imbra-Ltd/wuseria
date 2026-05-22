# ADR-034: Lens category field (photo vs cine)

**Status:** Accepted
**Date:** 2026-05-22

## Context

The database contains 11 cinema lenses (Fujifilm MKX, SLR Magic HyperPrime
CINE, NiSi Athena Prime) with more incoming (Irix cine line, SLR Magic).
There is no structured way to distinguish them from photo lenses. The only
signals are T-stop notation in the model name and inline comments.

Cinema lenses differ from photo lenses in meaningful ways: T-stop vs f-stop,
always-clickless aperture, long focus throw, breathing control, par-focal
zooms, and different review ecosystems (CineD vs still-photo sites). The
OQ scoring rubric (ADR-014) does not apply to cinema lenses — spike #555
identified that only ~4 of 14 optical fields are scoreable from cinema
review data.

A structured field is needed to filter, display, and score cinema lenses
differently from photo lenses.

## Decision

Add a required `category` field to the `Lens` interface with values
`"photo"` or `"cine"`. Every lens explicitly declares its category —
no implicit defaults.

```typescript
type LensCategory = "photo" | "cine";

interface Lens {
  // ...
  category: LensCategory;
  // ...
}
```

This is orthogonal to the existing `type` field (`"prime" | "zoom"`), which
describes optical design. A cinema zoom is still a zoom. Keeping the
dimensions separate follows the project's composition-over-flat principle.

## Alternatives considered

1. **Boolean `isCineLens`** — simpler, but less extensible and reads
   awkwardly in filters ("is cine lens" vs "category: cine").
2. **Expand `LensType`** to `"cine-prime" | "cine-zoom"` — mixes
   optical design with intended use in a single field. Violates SRP
   and makes filtering by either dimension harder.
3. **Add `"cinema"` to `ScoringStatus`** — conflates purpose with
   scoring status. A cinema lens that gets scored should not lose its
   category marker.

## Consequences

- All 232 photo lenses tagged with `category: "photo"`, all 11 cinema
  lenses tagged with `category: "cine"`.
- Future lenses must declare their category on entry — the field is
  required, so TypeScript catches omissions at build time.
- Enables filtering cinema lenses out of genre scoring and the main
  explorer if desired.
- Scoring methodology for cinema lenses remains a separate concern
  (spike #555).
