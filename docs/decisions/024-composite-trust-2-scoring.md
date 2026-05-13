# ADR-024: Composite trust-2 field scoring

**Status:** Accepted
**Date:** 2026-05-13

## Context

120 of 244 lenses are scored. The remaining 124 are predominantly niche
manual-focus brands (TTartisan, 7Artisans, Meike, Laowa, Mitakon) that
rarely receive trust-3 lab reviews. Trust-2 field sources (Fujiya Camera,
KASYAPA, Admiring Light, Christopher Frost) provide useful data, but
individual reviewers don't cover all 14 optical fields.

ADR-014 allows trust-2 aggregation: two trust-2 sources agreeing on the
**same field** count as trust-3. But field reviewers test different things —
reviewer A covers CA and flare, reviewer B covers sharpness and bokeh. The
union of their coverage could make a lens scorable, but current rules
require both to cover each field independently.

## Decision

When 2+ trust-2 sources independently review the same lens (same
mount/optical design), their field coverage may be combined into a
composite score. The following tiers determine the maximum score per field:

### Tier 1 — Dual trust-2 agreement (existing ADR-014 rule)

Both trust-2 sources cover the same field with non-contradictory data
(within 0.5 on the 0-2 scale). Use the conservative (lower) value.

**Cap: none** — equivalent to one trust-3 source.

### Tier 2 — Single trust-2 with trust-1 corroboration

One trust-2 source covers the field. Two or more trust-1 sources
independently provide non-contradictory assessments for the same field.

**Cap: none** — the trust-1 corroboration compensates for the missing
second trust-2 source.

### Tier 3 — Single trust-2 alone

One trust-2 source covers the field. No corroboration available.

**Cap: 1.5** — single-source evidence without cross-check cannot receive
the maximum score.

### Trust-1 sources

Trust-1 sources are defined in ADR-023: user forums, YouTube reviews,
social media, single-lens reviews without comparative context, and
sources with narrow coverage or limited track record.

Trust-1 corroboration requirements:

- 2+ independent sources (different authors, not cross-referencing)
- Non-contradictory with the trust-2 assessment (within 0.5)
- Each source documented in the scoring log with URL and quote

### Composite scoring constraints

- Overlapping fields (covered by both trust-2 sources) MUST agree within
  0.5 — any contradiction fails the composite for that field
- The composite MUST yield at least 7 scored optical fields
  (MIN_OPTICAL_FIELDS) — below this threshold the lens remains unscored
- Bokeh still requires a lab/diode test per ADR-014 — field impressions
  of "creamy bokeh" do not qualify
- Every field MUST document its source(s) and tier in the scoring log
- Physical property scores (aperture, weight) are unaffected — they are
  computed from lens specs, not review data

### Scoring log format

Each composite-scored field must indicate its tier:

```
| field | score | source data | rubric rule |
| lateralCA | 1.5 | Source A (trust-2): "well controlled." Tier 3, capped. | "low" (capped 1.5) |
| distortion | 2.0 | Source A (trust-2): "negligible." YT reviewer X, forum user Y agree. Tier 2. | < 0.3% (corroborated) |
| centerWideOpen | 2.0 | Source A + Source B (trust-2): both "excellent." Tier 1. | "excellent" (agg) |
```

### Precedence

From strongest to weakest evidence:

1. Trust-3 source (single source sufficient)
2. Trust-2 dual agreement (ADR-014 existing rule = Tier 1)
3. Trust-2 + trust-1 corroboration (Tier 2)
4. Trust-2 alone, capped at 1.5 (Tier 3)
5. Optical construction inference (ADR-014 existing rule)
6. Community consensus fallback (ADR-014 existing rule)

## Alternatives considered

| Alternative                             | Why rejected                                                                                                        |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| No cap on single trust-2 fields         | No cross-check means no error detection; a reviewer could be wrong about one field with no safety net               |
| Cap at 1.0 for single trust-2           | Too conservative — trust-2 sources are vetted and reliable; 1.0 undervalues their data                              |
| Require 3 trust-1 for corroboration     | Too strict — finding 3 independent sources for niche lenses is often impractical; 2 provides sufficient cross-check |
| Trust-1 sources can score independently | Trust-1 alone is unreliable; they work as corroboration, not primary evidence                                       |
| Lower MIN_OPTICAL_FIELDS to 5           | Would allow lenses with too many gaps to appear scored; 7 is the minimum for meaningful genre scores                |

## Consequences

- Unlocks scoring for niche manual-focus lenses that have trust-2 field
  coverage but no trust-3 lab data
- Estimated impact: 30-50 of the 124 unscored lenses may become scorable
  (those with 2+ trust-2 reviews covering 7+ fields in union)
- Scores from composite trust-2 may be revised when trust-3 data becomes
  available — the composite score is explicitly provisional
- Scoring log entries clearly indicate the evidence tier per field,
  making it easy to audit and upgrade when better data arrives
- Does not change any existing scores — applies only to lenses that are
  currently unscored
