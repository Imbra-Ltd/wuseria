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
|-------|----------------|
| 2.0 | >= 90% |
| 1.5 | 75-89% |
| 1.0 | 60-74% |
| 0.5 | 50-59% |
| 0.0 | < 50% |

Reference: LensTip Fuji APS-C X-Trans IV sensor max ~85 lpmm,
decency level ~44 lpmm (~52%).

### Astigmatism

Measured as % difference between sagittal and tangential MTF.

| Score | astigmatism |
|-------|-------------|
| 2.0 | < 5% |
| 1.5 | 5-10% |
| 1.0 | 10-18% |
| 0.5 | 18-25% |
| 0.0 | > 25% |

### Lateral CA

LensTip's published scale (measured at 70% from center).

| Score | lateralCA |
|-------|-----------|
| 2.0 | < 0.04% (negligible) |
| 1.5 | 0.04-0.08% (small) |
| 1.0 | 0.09-0.14% (average) |
| 0.5 | 0.15-0.20% (large) |
| 0.0 | > 0.21% (very large) |

### Distortion

Absolute percentage, RAW (uncorrected).

| Score | distortion |
|-------|------------|
| 2.0 | < 0.3% |
| 1.5 | 0.3-1.0% |
| 1.0 | 1.0-2.0% |
| 0.5 | 2.0-4.0% |
| 0.0 | > 4.0% |

### Vignetting

Stored as two values: `vignettingWideOpen` (max aperture) and
`vignettingStopped` (f/5.6 or f/8). Genres that shoot wide open
(astro, portrait) use the first; genres that shoot stopped down
(landscape, architecture) use the second.

Extreme corner light loss in EV, RAW (uncorrected). When sources
report different measurement points, use the extreme corner value
(worst case).

| Score | EV loss |
|-------|---------|
| 2.0 | < 0.5 EV |
| 1.5 | 0.5-1.0 EV |
| 1.0 | 1.0-1.5 EV |
| 0.5 | 1.5-2.5 EV |
| 0.0 | > 2.5 EV |

### Qualitative fields

For fields where reviewers provide descriptions rather than numbers:
`coma`, `sphericalAberration`, `longitudinalCA`, `bokeh`,
`flareResistance`.

| Score | Reviewer language |
|-------|-------------------|
| 2.0 | "excellent", "negligible", "perfectly corrected", "none visible" |
| 1.5 | "very good", "low", "well corrected", "minor" |
| 1.0 | "average", "moderate", "noticeable", "acceptable" |
| 0.5 | "poor", "significant", "problematic", "heavy" |
| 0.0 | "very poor", "severe", "uncorrected", "unusable" |

When multiple sources disagree, use the highest-trust source per the
`reviewSourceDirectory`. When the highest-trust source uses ambiguous
language, round toward the conservative (lower) score.

### Fallback sources

Independent lab data (LensTip, OpticalLimits) is the primary source.
Field reviews (Dustin Abbott, DPReview) are secondary. When neither
exists for a field, two fallback methods are available. Both are
weaker than independent data and must be justified per lens.

**1. Optical construction inference**

The official optical construction can support a score **only in
combination with absence of complaints from multiple reviewers**.
Neither alone is sufficient.

| Element type | Reliable inference |
|---|---|
| ED / Super ED / fluorite | CA correction — yes |
| Aspherical elements | Spherical aberration — reasonable |
| No specific element | Coma, bokeh, flare — no inference |

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

Sorted by focal length (wide to tele). 17 lenses.
Scores use per-review sensor max (see rubric).
Zooms scored at mid-range FL.

### XF 8-16mm f/2.8 R LM WR

| Field | Score |
|-------|-------|
| sweetSpotAperture | f/5.6 |
| centerStopped | 2 |
| cornerStopped | 1.5 |
| centerWideOpen | 2 |
| cornerWideOpen | — |
| astigmatism | 1.5 |
| coma | 1 |
| sphericalAberration | — |
| longitudinalCA | 1.5 |
| lateralCA | 1.5 |
| distortion | 1.5 |
| vignettingWideOpen | 0.5 |
| vignettingStopped | 1 |
| bokeh | — |
| flareResistance | 1 |

Sources: lenstip

### XF 10-24mm f/4 R OIS WR

| Field | Score |
|-------|-------|
| sweetSpotAperture | f/5.6 |
| centerStopped | 2 |
| cornerStopped | 1.5 |
| centerWideOpen | 1.5 |
| cornerWideOpen | — |
| astigmatism | 1.5 |
| coma | 1 |
| sphericalAberration | 1.5 |
| longitudinalCA | 1.5 |
| lateralCA | 1.5 |
| distortion | 1 |
| vignettingWideOpen | 0.5 |
| vignettingStopped | 1.5 |
| bokeh | 0.5 |
| flareResistance | 1.5 |

Sources: lenstip

### 12mm f/2

| Field | Score |
|-------|-------|
| sweetSpotAperture | f/4 |
| centerStopped | 2 |
| cornerStopped | 0.5 |
| centerWideOpen | 1.5 |
| cornerWideOpen | — |
| astigmatism | 2 |
| coma | 1 |
| sphericalAberration | 2 |
| longitudinalCA | 0.5 |
| lateralCA | 0.5 |
| distortion | 1 |
| vignettingWideOpen | 0.5 |
| vignettingStopped | 1.5 |
| bokeh | 1.5 |
| flareResistance | 0.5 |

Sources: lenstip

### XF 14mm f/2.8

| Field | Score |
|-------|-------|
| sweetSpotAperture | f/5.6 |
| centerStopped | 2 |
| cornerStopped | 1 |
| centerWideOpen | 2 |
| cornerWideOpen | — |
| astigmatism | 2 |
| coma | 1 |
| sphericalAberration | 1.5 |
| longitudinalCA | 2 |
| lateralCA | 2 |
| distortion | 2 |
| vignettingWideOpen | 0.5 |
| vignettingStopped | 0.5 |
| bokeh | 1.5 |
| flareResistance | 1.5 |

Sources: lenstip

### XF 16mm f/1.4

| Field | Score |
|-------|-------|
| sweetSpotAperture | f/4 |
| centerStopped | 1.5 |
| cornerStopped | 1 |
| centerWideOpen | 1 |
| cornerWideOpen | — |
| astigmatism | 2 |
| coma | 0.5 |
| sphericalAberration | 0.5 |
| longitudinalCA | 0.5 |
| lateralCA | 1.5 |
| distortion | 1.5 |
| vignettingWideOpen | 0.5 |
| vignettingStopped | 1.5 |
| bokeh | 0.5 |
| flareResistance | 1.5 |

Sources: lenstip

### XF 16-55mm f/2.8 R LM WR

| Field | Score |
|-------|-------|
| sweetSpotAperture | f/4 |
| centerStopped | 1.5 |
| cornerStopped | 1 |
| centerWideOpen | 1.5 |
| cornerWideOpen | — |
| astigmatism | 1.5 |
| coma | 1 |
| sphericalAberration | 2 |
| longitudinalCA | 1.5 |
| lateralCA | 1 |
| distortion | 0.5 |
| vignettingWideOpen | 1.5 |
| vignettingStopped | 2 |
| bokeh | 0.5 |
| flareResistance | 1.5 |

Sources: lenstip

### XF 16mm f/2.8

| Field | Score |
|-------|-------|
| sweetSpotAperture | f/4 |
| centerStopped | 2 |
| cornerStopped | 1 |
| centerWideOpen | 1.5 |
| cornerWideOpen | — |
| astigmatism | 1 |
| coma | 1 |
| sphericalAberration | 2 |
| longitudinalCA | — |
| lateralCA | 1.5 |
| distortion | 0 |
| vignettingWideOpen | 0.5 |
| vignettingStopped | 1.5 |
| bokeh | 0.5 |
| flareResistance | 1.5 |

Sources: lenstip

### XF 16-55mm f/2.8 R LM WR II

| Field | Score |
|-------|-------|
| sweetSpotAperture | f/4 |
| centerStopped | 1.5 |
| cornerStopped | 1.5 |
| centerWideOpen | 1.5 |
| cornerWideOpen | — |
| astigmatism | 1.5 |
| coma | — |
| sphericalAberration | 2 |
| longitudinalCA | 2 |
| lateralCA | 2 |
| distortion | — |
| vignettingWideOpen | — |
| vignettingStopped | — |
| bokeh | 1 |
| flareResistance | 1.5 |

Sources: dustinabbott

### XF 18mm f/2.0

| Field | Score |
|-------|-------|
| sweetSpotAperture | f/4 |
| centerStopped | 2 |
| cornerStopped | 1 |
| centerWideOpen | 1 |
| cornerWideOpen | — |
| astigmatism | 2 |
| coma | 0.5 |
| sphericalAberration | — |
| longitudinalCA | 1.5 |
| lateralCA | 1 |
| distortion | 0 |
| vignettingWideOpen | 0.5 |
| vignettingStopped | 1 |
| bokeh | 1.5 |
| flareResistance | 1.5 |

Sources: lenstip

### XF 23mm f/1.4 R LM WR

| Field | Score |
|-------|-------|
| sweetSpotAperture | f/4 |
| centerStopped | 2 |
| cornerStopped | 1.5 |
| centerWideOpen | 1.5 |
| cornerWideOpen | — |
| astigmatism | 1 |
| coma | 1.5 |
| sphericalAberration | 1.5 |
| longitudinalCA | 1.5 |
| lateralCA | 2 |
| distortion | 0.5 |
| vignettingWideOpen | 0.5 |
| vignettingStopped | 2 |
| bokeh | 1.5 |
| flareResistance | 0.5 |

Sources: lenstip, opticallimits, dustinabbott

### XF 27mm f/2.8 R WR

| Field | Score |
|-------|-------|
| sweetSpotAperture | f/5.6 |
| centerStopped | 1.5 |
| cornerStopped | 1 |
| centerWideOpen | 1.5 |
| cornerWideOpen | — |
| astigmatism | 1.5 |
| coma | 1 |
| sphericalAberration | 2 |
| longitudinalCA | 1.5 |
| lateralCA | 2 |
| distortion | 1 |
| vignettingWideOpen | 0.5 |
| vignettingStopped | 1.5 |
| bokeh | 0.5 |
| flareResistance | 1 |

Sources: lenstip, admiringlight

### XF 33mm f/1.4 LM WR

| Field | Score |
|-------|-------|
| sweetSpotAperture | f/4 |
| centerStopped | 2 |
| cornerStopped | 1.5 |
| centerWideOpen | 1 |
| cornerWideOpen | — |
| astigmatism | 2 |
| coma | 1 |
| sphericalAberration | 1 |
| longitudinalCA | 1.5 |
| lateralCA | 2 |
| distortion | 1 |
| vignettingWideOpen | 0.5 |
| vignettingStopped | 1.5 |
| bokeh | 1.5 |
| flareResistance | 1.5 |

Sources: lenstip

### XF 56mm f/1.2 R WR

| Field | Score |
|-------|-------|
| sweetSpotAperture | f/2.8 |
| centerStopped | 2 |
| cornerStopped | 2 |
| centerWideOpen | 2 |
| cornerWideOpen | — |
| astigmatism | 2 |
| coma | 2 |
| sphericalAberration | 2 |
| longitudinalCA | 2 |
| lateralCA | 2 |
| distortion | 2 |
| vignettingWideOpen | 0.5 |
| vignettingStopped | 2 |
| bokeh | 1.5 |
| flareResistance | 1.5 |

Sources: lenstip, opticallimits, dustinabbott, fujivsfuji

### XF 80mm f/2.8 Macro

| Field | Score |
|-------|-------|
| sweetSpotAperture | f/4 |
| centerStopped | 2 |
| cornerStopped | 0.5 |
| centerWideOpen | 2 |
| cornerWideOpen | — |
| astigmatism | 2 |
| coma | 2 |
| sphericalAberration | 2 |
| longitudinalCA | 2 |
| lateralCA | 2 |
| distortion | 1.5 |
| vignettingWideOpen | 0.5 |
| vignettingStopped | 2 |
| bokeh | 1.5 |
| flareResistance | 1 |

Sources: lenstip

### XF 90mm f/2.0

| Field | Score |
|-------|-------|
| sweetSpotAperture | f/2.8 |
| centerStopped | 2 |
| cornerStopped | 1.5 |
| centerWideOpen | 2 |
| cornerWideOpen | — |
| astigmatism | 2 |
| coma | 2 |
| sphericalAberration | 1.5 |
| longitudinalCA | 1.5 |
| lateralCA | 2 |
| distortion | 2 |
| vignettingWideOpen | 1.5 |
| vignettingStopped | 2 |
| bokeh | 1.5 |
| flareResistance | 0.5 |

Sources: lenstip, dustinabbott

### XF 100-400mm f/4.5-5.6 R LM OIS WR

| Field | Score |
|-------|-------|
| sweetSpotAperture | f/8 |
| centerStopped | 1.5 |
| cornerStopped | 1 |
| centerWideOpen | 1 |
| cornerWideOpen | — |
| astigmatism | 1 |
| coma | 2 |
| sphericalAberration | 2 |
| longitudinalCA | 2 |
| lateralCA | 1.5 |
| distortion | 0.5 |
| vignettingWideOpen | 1 |
| vignettingStopped | 1.5 |
| bokeh | 1 |
| flareResistance | 1 |

Sources: lenstip, dustinabbott

### XF 200mm f/2.0

| Field | Score |
|-------|-------|
| sweetSpotAperture | f/2.8 |
| centerStopped | 2 |
| cornerStopped | 2 |
| centerWideOpen | 2 |
| cornerWideOpen | — |
| astigmatism | 2 |
| coma | — |
| sphericalAberration | 2 |
| longitudinalCA | 2 |
| lateralCA | 2 |
| distortion | 2 |
| vignettingWideOpen | 1.5 |
| vignettingStopped | 2 |
| bokeh | 2 |
| flareResistance | 1 |

Sources: ephotozine, dustinabbott

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Continuous 0-2 scale | Not reproducible — subjective decimal placement |
| Absolute lpmm thresholds | Sensor-dependent — same lens scores differently on X-Trans IV vs V |
| 1-5 integer scale | Too coarse for quantitative fields with known thresholds |
| Per-source normalization | Too complex; sources don't use comparable scales |
| Raw measurement storage | Would need unit conversion per field; 0-2 is the common currency |

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
