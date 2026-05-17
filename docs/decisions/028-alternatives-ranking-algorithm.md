# ADR-028: Alternatives Ranking Algorithm

**Status:** Accepted
**Date:** 2026-05-17

## Context

The lens detail page shows alternative lenses a user might consider. The
original algorithm used a fixed ±15mm focal length range and sorted by FL
distance (closest first). In the crowded 50-60mm range, this surfaced 10
alternatives including kit zooms, discontinued models, and budget manual
primes — too many results of varying relevance.

The alternatives section answers: "what optically similar lenses exist
nearby?" It does not answer genre-specific questions ("what's the best
portrait lens?") — genre pages serve that purpose.

## Decision

Reworked the alternatives algorithm with four changes:

1. **Proportional FL range (±20%)** — replaces the fixed ±15mm. Scales
   naturally: tight for ultra-wide (14mm → 11-17mm), wide for tele
   (200mm → 160-240mm). Matches how photographers perceive focal length
   steps.

2. **OQ-based sorting** — alternatives sorted by optical quality score
   descending, unscored lenses last. OQ is genre-neutral (weighted average
   of 14 optical fields) and answers "best glass nearby" without assuming
   the user's intent. Genre scores were considered but rejected: the
   alternatives section has no genre context, and genre scores use coarser
   0.5 steps that produce too many ties.

3. **Type grouping (5 same + 3 other)** — primes show primes first (up
   to 5), then zooms covering the FL (up to 3), and vice versa. Prevents
   kit zooms from displacing direct competitors. The 5+3 split balances
   depth within the lens type against cross-type discovery.

4. **Discontinued filter** — only currently available lenses shown.
   Discontinued models are still in the database for historical reference
   but are not actionable purchase alternatives.

The superzoom filter (>4x zoom ratio) is retained from the original
algorithm.

## Alternatives considered

- **Fixed ±5mm / ±10mm** — rejected because fixed ranges don't scale.
  ±5mm excludes the XF 50mm from the XF 56mm (6mm gap). ±10mm is too
  wide for ultra-wide lenses (14mm would match 4-24mm).

- **Genre score sorting** — rejected. The alternatives section is
  genre-neutral. Sorting by portrait score would be wrong for a 14mm
  ultra-wide. Spike #718 confirmed that adding aperture to the portrait
  formula has negligible impact (3/94 lenses change by 0.5 as secondary)
  or is destructive (25/94 change as primary, some dropping to 1/5).

- **OQ threshold filter (±0.2)** — rejected as too restrictive. With
  51% of lenses unscored, this would exclude most candidates and produce
  empty alternatives sections.

- **No cap / higher cap** — the original 10-result cap was replaced with
  the type-grouped 5+3 model. Uncapped results are impractical in
  crowded FL ranges; the type split ensures relevance without an
  arbitrary number.

## Consequences

- Alternatives are more focused: the XF 56mm f/1.2 shows 7 alternatives
  (5 primes + 2 zooms) instead of 10 mixed results.
- Macro lenses with high OQ (e.g. Laowa 65mm, OQ 1.8) appear as
  alternatives to portrait primes — this is correct because they are
  optically excellent and viable for portrait use.
- As more lenses are scored, the OQ ranking becomes more meaningful.
  Currently 49% of lenses are scored.
- Genre-specific lens comparison remains the responsibility of genre
  pages (`/genre/portrait/`, etc.), not the alternatives section.
