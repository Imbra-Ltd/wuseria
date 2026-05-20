# ADR-014: Optical quality rubric — mapping review data to 0-2 scores

**Status:** Accepted
**Date:** 2026-04-11

## Context

The Lens type carries 13 optical quality fields on a 0-2 scale. ADR-013
requires that these fields are populated only from trusted review sources.
But different reviewers express results differently — LensTip gives lpmm
numbers, OpticalLimits gives verbal assessments, Dustin Abbott describes
rendering characteristics.

Without a rubric, two people reading the same review could assign different
scores. The scoring system must be reproducible.

## Decision

Each optical quality field has a defined rubric that maps source data to
one of five discrete values: **0, 0.5, 1.0, 1.5, 2.0**. No values between
steps. Where numerical measurements exist, thresholds are defined. Where
only qualitative assessments exist, a word-to-score mapping is defined.

If a field cannot be placed on the rubric from available data, it stays
`undefined`. No interpolation between steps.

### Resolution fields

Resolution in lpmm depends on the sensor AND the RAW processing pipeline
used for testing. LensTip's stated maximum varies between reviews even on
the same sensor body (e.g. X-E1 max ranges from 70-72 to 78-80 lpmm
across different review years as dcraw X-Trans processing matured).

**Use the maximum stated by LensTip on the resolution page of the
specific lens being scored**, not a global per-sensor number.

Applies to: `centerStopped`, `cornerStopped`, `centerWideOpen`,
`cornerWideOpen`.

| Score | % of sensor max |
| ----- | --------------- |
| 2.0   | >= 90%          |
| 1.5   | 75-89%          |
| 1.0   | 60-74%          |
| 0.5   | 50-59%          |
| 0.0   | < 50%           |

Reference: LensTip Fuji APS-C X-Trans IV sensor max ~85 lpmm,
decency level ~44 lpmm (~52%).

### Astigmatism

Measured as % difference between sagittal and tangential MTF.

| Score | astigmatism |
| ----- | ----------- |
| 2.0   | < 5%        |
| 1.5   | 5-10%       |
| 1.0   | 10-18%      |
| 0.5   | 18-25%      |
| 0.0   | > 25%       |

### Lateral CA

LensTip's published scale (measured at 70% from center).

| Score | lateralCA            |
| ----- | -------------------- |
| 2.0   | < 0.04% (negligible) |
| 1.5   | 0.04-0.08% (small)   |
| 1.0   | 0.09-0.14% (average) |
| 0.5   | 0.15-0.20% (large)   |
| 0.0   | > 0.21% (very large) |

### Distortion

Absolute percentage, RAW (uncorrected).

| Score | distortion |
| ----- | ---------- |
| 2.0   | < 0.3%     |
| 1.5   | 0.3-1.0%   |
| 1.0   | 1.0-2.0%   |
| 0.5   | 2.0-4.0%   |
| 0.0   | > 4.0%     |

### Vignetting

Stored as two values: `vignettingWideOpen` (max aperture) and
`vignettingStopped` (f/5.6 or f/8). Genres that shoot wide open
(astro, portrait) use the first; genres that shoot stopped down
(landscape, architecture) use the second.

Extreme corner light loss in EV, RAW (uncorrected). When sources
report different measurement points, use the extreme corner value
(worst case).

| Score | EV loss    |
| ----- | ---------- |
| 2.0   | < 0.5 EV   |
| 1.5   | 0.5-1.0 EV |
| 1.0   | 1.0-1.5 EV |
| 0.5   | 1.5-2.5 EV |
| 0.0   | > 2.5 EV   |

### Qualitative fields

For fields where reviewers provide descriptions rather than numbers:
`coma`, `sphericalAberration`, `longitudinalCA`, `bokeh`,
`flareResistance`.

| Score | Reviewer language                                                |
| ----- | ---------------------------------------------------------------- |
| 2.0   | "excellent", "negligible", "perfectly corrected", "none visible" |
| 1.5   | "very good", "low", "well corrected", "minor"                    |
| 1.0   | "average", "moderate", "noticeable", "acceptable"                |
| 0.5   | "poor", "significant", "problematic", "heavy"                    |
| 0.0   | "very poor", "severe", "uncorrected", "unusable"                 |

When multiple sources disagree, use the highest-trust source per the
`reviewSourceDirectory`. When the highest-trust source uses ambiguous
language, round toward the conservative (lower) score.

**Summary page authority rule:** For LensTip reviews, always verify
scores against the summary page (final chapter). The summary is
LensTip's considered final opinion and may soften or strengthen
assessments from individual test pages. If the summary contradicts
a test page, the summary wins. Example: a coma test page may say
"visible but not highly intense" (sounds like 1.0), but the summary
adding "no serious reservations" shifts it to 1.5.

**Bokeh scoring rule:** Lab tests (diode/point-source imaging) are
the authority for bokeh. LensTip's diode test is the primary source.
Field reviews describing bokeh as "creamy" or "smooth" are not
sufficient — only controlled point-source tests that show disc
evenness, rim intensity, and onion ring presence count. If two lab
sources disagree, prefer LensTip (standardized diode methodology).
Bokeh cannot be inferred from lens specs (blade count, aspherical
elements, entrance pupil) — these affect disc shape, not rendering
quality.

### Physical property scores

Some genres use physical lens properties as scoring inputs, mapped
to the 0–2 scale. These are computed from `Lens` spec fields, not
from review data.

**Aperture score** (from `maxAperture`):

| Score | maxAperture     |
| ----- | --------------- |
| 2.0   | f/1.4 or faster |
| 1.5   | f/1.8-f/2.0     |
| 1.0   | f/2.8           |
| 0.5   | f/3.5-f/4.0     |
| 0.0   | f/4.5 or slower |

Used by: street (primary), travel (secondary).

**Weight score** (from `weight` in grams):

| Score | Weight    |
| ----- | --------- |
| 2.0   | < 200g    |
| 1.5   | 200-400g  |
| 1.0   | 400-700g  |
| 0.5   | 700-1000g |
| 0.0   | > 1000g   |

Used by: travel (primary).

### Trust-2 source aggregation

Two trust-2 sources providing non-contradictory data for the same
field are treated as equivalent to one trust-3 source for that field.
"Non-contradictory" means scores within 0.5 of each other on the
0–2 scale; use the lower (conservative) value.

This applies per-field, not per-lens — field A might qualify via
two trust-2 sources while field B does not. Each aggregated field
must document both sources in the scoring log.

### Community consensus fallback

When independent non-trust sources provide non-contradictory
assessments for a field, and no trust source contradicts, the field
may be scored using a tiered cap based on source count.
"Non-contradictory" means all sources agree within 0.5 of each other.

This is the weakest fallback — weaker than trust-2 aggregation and
optical construction inference. It applies only when no trust source
covers the field at all.

| Sources               | Cap | Confidence                             |
| --------------------- | --- | -------------------------------------- |
| 3                     | 1.0 | Minimum threshold — conservative       |
| 5+                    | 1.5 | Strong consensus — moderate confidence |
| 5+ with measured data | 2.0 | Overwhelming consensus with evidence   |

"Measured data" means quantitative results (FWHM, pixel-level crops,
controlled comparison tests), not just qualitative descriptions.

Requirements:

- 3+ independent sources (different authors, not cross-referencing)
- Non-contradictory assessments
- No trust source provides contradicting data
- Score capped per tier above
- Each source documented in the scoring log with URL and quote

### Fallback sources

Independent lab data (LensTip, OpticalLimits) is the primary source.
Field reviews (Dustin Abbott, DPReview) are secondary. When neither
exists for a field, two fallback methods are available. Both are
weaker than independent data and must be justified per lens.

**1. Optical construction inference**

The official optical construction can support a score **only in
combination with absence of complaints from multiple reviewers**.
Neither alone is sufficient.

| Element type             | Reliable inference                |
| ------------------------ | --------------------------------- |
| ED / Super ED / fluorite | CA correction — yes               |
| Aspherical elements      | Spherical aberration — reasonable |
| No specific element      | Coma, bokeh, flare — no inference |

- Design intent alone → `undefined`
- Zero complaints alone → `undefined`
- Design intent + zero complaints → 2.0, with both documented

**2. Official MTF chart for astigmatism**

Astigmatism appears as divergence between sagittal (S) and
meridional (M) lines on the manufacturer's MTF chart:

- S/M nearly overlapping → 2.0
- Moderate divergence → 1.0-1.5
- Heavy divergence → 0-0.5

Note: S/M divergence can indicate coma OR astigmatism — the
chart cannot isolate which. Coma requires point-source testing
(star test, diode test) and cannot be inferred from MTF charts.

Manufacturer MTF charts are computed from the optical design,
not measured from production samples.

## Reference scoring

Per-lens scoring justifications are maintained in
`docs/optical-specs/<slug>/scoring-log.md`, one file per lens (see ADR-033).
Each entry maps source data to rubric rules and is traceable
to the original review page.

## Alternatives considered

| Alternative              | Why rejected                                                       |
| ------------------------ | ------------------------------------------------------------------ |
| Continuous 0-2 scale     | Not reproducible — subjective decimal placement                    |
| Absolute lpmm thresholds | Sensor-dependent — same lens scores differently on X-Trans IV vs V |
| 1-5 integer scale        | Too coarse for quantitative fields with known thresholds           |
| Per-source normalization | Too complex; sources don't use comparable scales                   |
| Raw measurement storage  | Would need unit conversion per field; 0-2 is the common currency   |

## Consequences

- Every optical score is reproducible — same source data + rubric = same
  score
- Resolution thresholds are sensor-normalized (% of max) — works across
  X-Trans generations and GFX sensors without recalibration
- Adding GFX lenses requires knowing the sensor max for the test body,
  not new threshold tables
- The rubric may be refined as more lenses are scored — thresholds are
  living values, updated via a new ADR if changed
- Each scored lens should have a justification record (as above) traceable
  to source pages
