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

| Score | maxAperture |
|-------|-------------|
| 2.0 | f/1.4 or faster |
| 1.5 | f/1.8-f/2.0 |
| 1.0 | f/2.8 |
| 0.5 | f/3.5-f/4.0 |
| 0.0 | f/4.5 or slower |

Used by: street (primary), travel (secondary).

**Weight score** (from `weight` in grams):

| Score | Weight |
|-------|--------|
| 2.0 | < 200g |
| 1.5 | 200-400g |
| 1.0 | 400-700g |
| 0.5 | 700-1000g |
| 0.0 | > 1000g |

Used by: travel (primary).

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

Sorted by focal length (wide to tele).

### XF 8-16mm f/2.8 R LM WR

Premium ultra-wide zoom. Sources: LensTip (lab, trust 3).
Sensor: X-Trans III, max ~78 lpmm. Scored at 12mm mid-range.

| Field | Score | Source data | Rubric rule |
|-------|-------|-------------|-------------|
| centerStopped | 2.0 | ~80 lpmm at 12-16mm. "Exceptional." | >= 90% |
| cornerStopped | 1.5 | 62 lpmm edge at 12mm. 62/78 = 79%. "Very well even at max aperture" in 12-16mm range. | 75-89% |
| centerWideOpen | 2.0 | ~70 lpmm at f/2.8 across range. | >= 90% |
| astigmatism | 1.5 | 7.6%. "Moderate." | 5-10% |
| coma | 1.0 | "Noticeable", most at 8mm, slight at 12-16mm. | "noticeable" |
| longitudinalCA | 1.5 | "Slight", "out-of-focus images a bit tinted." Minor. | "low" |
| lateralCA | 1.5 | <0.05% at 12-16mm, approaches medium at 8mm. | 0.04-0.08% |
| distortion | 1.5 | RAW: -0.56% at 12mm. (-8.41% at 8mm extreme.) | 0.3-1.0% |
| vignettingWideOpen | 0.5 | RAW: -1.96 EV at 12mm f/2.8. | 1.5-2.5 EV |
| vignettingStopped | 1.0 | RAW: -1.33 EV at 12mm f/11. Resistant to stopping down. | 1.0-1.5 EV |
| flareResistance | 1.0 | "Some slip-ups", "not that bad given complexity." Average. | "average" |

### XF 10-24mm f/4 R OIS WR

Ultra-wide zoom for landscape/architecture.
Same optical formula as original XF 10-24mm f/4 R OIS (2013).
Sources: LensTip (lab, trust 3).
Sensor: X-Trans I (X-E1), per-review max 71 lpmm. Scored at mid-range.

| Field | Score | Source data | Rubric rule |
|-------|-------|-------------|-------------|
| centerStopped | 2.0 | 69-70 lpmm at f/4-5.6 mid-range (99% of 71 max). "Worth of a good quality fixed-focal lens." | >= 90% |
| cornerStopped | 1.5 | 55 lpmm edge, "never exceeds 55 lpmm" across range. 55/71 = 77%. | 75-89% |
| centerWideOpen | 1.5 | Variable across range. | 75-89% |
| astigmatism | 1.5 | Average 7.1%. Ranges 13% at 10mm to low mid-range. | 5-10% (average) |
| coma | 1.0 | "Influence can be felt", "highest at both ends", "almost imperceptible in the middle." | "noticeable" |
| sphericalAberration | 1.5 | "Good control of spherical aberration." | "well corrected" |
| longitudinalCA | 1.5 | "Not a big problem", "slightly yellow/bluish cast", decreases at f/5.6. | "low" |
| lateralCA | 1.5 | At 10mm: ~0.05%. Increases at longer FL. | 0.04-0.08% |
| distortion | 1.0 | RAW: +1.53% at mid-range. (-4.62% at 10mm extreme.) | 1.0-2.0% |
| vignettingWideOpen | 0.5 | RAW: -1.93 EV at 10mm f/4. "Very high value." | 1.5-2.5 EV |
| vignettingStopped | 1.5 | RAW: -0.61 EV at mid-range f/5.6. | 0.5-1.0 EV |
| bokeh | 0.5 | "Moderately good", "distinct rim", "onion rings." | "poor" |
| flareResistance | 1.5 | "Works against bright light very well" at wide end. Super EBC coating. Increases at long end. | "very good" (wide) → conservative 1.5 |

### Samyang 12mm f/2.0 NCS CS

Third-party ultra-wide prime. Popular astro lens.
Sources: LensTip (lab, trust 3).
Sensor: X-Trans I (X-E1), max ~66 lpmm.

| Field | Score | Source data | Rubric rule |
|-------|-------|-------------|-------------|
| centerStopped | 2.0 | ~74 lpmm at f/2.8-4.0 center (112% of max). | >= 90% |
| cornerStopped | 0.5 | Edge "below decency level" at f/2. No lpmm at sweet spot. | "poor" (conservative) |
| centerWideOpen | 2.0 | ~60 lpmm at f/2 center (91% of max). | >= 90% |
| astigmatism | 2.0 | 3.7%. "Corrected in a flawless way." | < 5% |
| coma | 1.0 | "Visible but not highly intense." Reduces to insignificant at f/2.8. | "noticeable" |
| sphericalAberration | 2.0 | "No focus shift, no problems with correction." | "negligible" |
| longitudinalCA | 0.5 | "didn't manage to deal with that problem well", "photo shows it clearly." | "poor" |
| lateralCA | 0.5 | ~0.15%. "Noticeable factor deteriorating edge image quality." | 0.15-0.20% |
| distortion | 1.0 | -1.88% barrel. Same RAW and JPEG (no in-camera correction). | 1.0-2.0% |
| vignettingWideOpen | 0.5 | -1.69 EV at f/2. | 1.5-2.5 EV |
| vignettingStopped | 1.5 | -0.87 EV at f/4. | 0.5-1.0 EV |
| bokeh | 1.5 | "Nice to look at, even light spread, no noticeable extremes." | "very good" |
| flareResistance | 0.5 | "A lot of problems against bright light", deteriorates stopped down. | "poor" |

### XF 14mm f/2.8 R

Wide prime. Sources: LensTip (lab, trust 3).
Sensor: X-Trans I (X-E1), max ~66 lpmm.

| Field | Score | Source data | Rubric rule |
|-------|-------|-------------|-------------|
| centerStopped | 2.0 | 72 lpmm at f/4-5.6 (109% of max). | >= 90% |
| cornerStopped | 1.0 | Edge 42+ lpmm. >20 lpmm gap from center. | "average" |
| centerWideOpen | 2.0 | 69 lpmm at f/2.8 (105% of max). | >= 90% |
| astigmatism | 2.0 | 3.4%. "No correction problems." | < 5% |
| coma | 1.0 | "Clearly noticeable at max aperture." Low at f/4. | "noticeable" |
| sphericalAberration | 1.5 | Even light spread, noticeable rim at edge. No focus shift. | "well corrected" |
| longitudinalCA | 2.0 | "Not a problem whatsoever." | "negligible" |
| lateralCA | 2.0 | Never exceeds 0.04%. | < 0.04% |
| distortion | 2.0 | RAW: -0.23%. "Practically imperceptible." | < 0.3% |
| vignettingWideOpen | 0.5 | RAW: -2.09 EV at f/2.8. | 1.5-2.5 EV |
| vignettingStopped | 0.5 | RAW: -1.52 EV at f/4. Still heavy. | 1.5-2.5 EV |
| bokeh | 1.5 | Even distribution, noticeable rim at edge only. | "very good" |
| flareResistance | 1.5 | "Really difficult to catch any flares." Good. | "very good" |

### XF 16mm f/1.4 R WR

Fast wide prime. Sources: LensTip (lab, trust 3).
Sensor: X-Trans I (X-E1), max ~66 lpmm.

| Field | Score | Source data | Rubric rule |
|-------|-------|-------------|-------------|
| centerStopped | 1.5 | Stopped down performance good but "wanted 72-73, got less." | "very good" (conservative) |
| cornerStopped | 1.0 | Edge "exceeds utility threshold at f/2.0." Below decency wide open. | "average" |
| centerWideOpen | 1.0 | 44 lpmm at f/1.4 (67% of max). Barely above decency. | 60-74% |
| astigmatism | 2.0 | 3.0%. "Very low level." | < 5% |
| coma | 0.5 | "Corrects coma in a very poor way", "really high at max aperture", only reduces at f/2.8. | "poor" |
| sphericalAberration | 0.5 | "Textbook example of spherical aberration influence", "far from perfect." | "poor" |
| longitudinalCA | 0.5 | "A lot of problems", "even at f/2.0 still quite bothersome." | "poor" |
| lateralCA | 1.5 | 0.07%. "Low level." | 0.04-0.08% |
| distortion | 1.5 | RAW: -0.87%. "Excellent result." | 0.3-1.0% |
| vignettingWideOpen | 0.5 | RAW: -1.94 EV at f/1.4. | 1.5-2.5 EV |
| vignettingStopped | 1.5 | RAW: -0.56 EV at f/4-5.6. "Further stopping down doesn't help much." | 0.5-1.0 EV |
| bokeh | 0.5 | "Lighter rim on edge and noticeable onion ring", "not exactly pleasant." | "poor" |
| flareResistance | 1.5 | "Good" overall, no problems wide open, issues stopped down with sun outside frame. | "very good" → conservative 1.5 |

### XF 16mm f/2.8 R WR

Compact wide prime. Sources: LensTip (lab, trust 3).
Sensor: X-Trans III, max ~78 lpmm.

| Field | Score | Source data | Rubric rule |
|-------|-------|-------------|-------------|
| centerStopped | 2.0 | 77 lpmm at f/4 (99% of max). | >= 90% |
| cornerStopped | 1.0 | 55 lpmm at f/5.6-8. "Slightly better than average." | "average" |
| centerWideOpen | 1.5 | 60 lpmm at f/2.8 (77% of max). | 75-89% |
| astigmatism | 1.0 | 10.3%. "Medium level." | 10-18% |
| coma | 1.0 | "Corrects well from f/4", visible at max aperture. | "noticeable" |
| sphericalAberration | 2.0 | "No significant focus shift." | "negligible" |
| lateralCA | 1.5 | ~0.05%. "Borderline imperceptible and low." | 0.04-0.08% |
| distortion | 0.0 | RAW: -7.73%. "Monstrous." | > 4.0% |
| vignettingWideOpen | 0.5 | RAW: -1.87 EV at f/2.8. | 1.5-2.5 EV |
| vignettingStopped | 1.5 | RAW: -0.60 EV at f/8. | 0.5-1.0 EV |
| bokeh | 0.5 | "Visible onion ring bokeh" from aspherical elements. | "poor" |
| flareResistance | 1.5 | "Good", minimal issues wide open, degrades stopped down. | "very good" |

### XF 16-55mm f/2.8 R LM WR

Standard zoom. Sources: LensTip (lab, trust 3).
Sensor: X-Trans I (X-E1), per-review max ~71 lpmm. Scored at 35mm mid-range.

| Field | Score | Source data | Rubric rule |
|-------|-------|-------------|-------------|
| centerStopped | 1.5 | ~58 lpmm at 35mm mid-range. 58/71 = 82%. | 75-89% |
| cornerStopped | 1.0 | 50 lpmm at edge. Conservative. | "average" |
| centerWideOpen | 1.5 | ~58 lpmm at 35mm f/2.8. | 75-89% |
| astigmatism | 1.5 | 5.6%. "Low value." | 5-10% |
| coma | 1.0 | "Moderate coma." | "noticeable" |
| sphericalAberration | 2.0 | "Corrected in a perfect way." | "negligible" |
| longitudinalCA | 1.5 | "Slight colouring, nothing to worry about." | "low" |
| lateralCA | 1.0 | 0.11-0.12% at 55mm. "Medium" at long end. | 0.09-0.14% |
| distortion | 0.5 | RAW: significant across range. "Relied on software." | 2.0-4.0% |
| vignettingWideOpen | 1.5 | RAW: -0.89 EV at 35mm f/2.8. | 0.5-1.0 EV |
| vignettingStopped | 2.0 | RAW: -0.38 EV at 35mm f/5.6. | < 0.5 EV |
| bokeh | 0.5 | "Concentric lines, accentuated rim, truncations." | "poor" |
| flareResistance | 1.5 | "Really difficult to catch flares", "small and not intensive." | "very good" |

### XF 16-55mm f/2.8 R LM WR II

Standard zoom, new optical design. Sources: Dustin Abbott (field,
trust 3), official Fujifilm MTF chart (for astigmatism).
No lab review yet.

| Field | Score | Source data | Rubric rule |
|-------|-------|-------------|-------------|
| centerStopped | 1.5 | "Uniformly pretty excellent" f/4-f/8. "Most consistently excellent APS-C standard zoom." | "very good" to "excellent" → conservative |
| cornerStopped | 1.5 | MTF: S/M high through midframe. "Improved corner performance" vs Mk I. | "very good" |
| centerWideOpen | 1.5 | "Give and take at f/2.8" at 35mm. Not "excellent" wide open. | "very good" |
| astigmatism | 1.5 | Official MTF chart: S/M gap 0.10-0.15 at 45 lp/mm worst case. Low for a zoom. | S/M low divergence |
| sphericalAberration | 2.0 | Aspherical + Super ED. No focus shift reported. Fallback: design + zero complaints. | "negligible" |
| longitudinalCA | 2.0 | "Extremely well controlled." "Huge advantage over Sigma." | "negligible" |
| lateralCA | 2.0 | "Next to no fringing." | "negligible" |
| bokeh | 1.0 | "Fairly good for a standard zoom", "busier", inner outlining. | "average" |
| flareResistance | 1.5 | "Holds up to bright sun." Minor ghosting stopped down. | "very good" |

### XF 18mm f/2 R

Pancake wide prime. Sources: LensTip (lab, trust 3).
Sensor: X-Trans I (X-Pro1), per-review max 66 lpmm.

| Field | Score | Source data | Rubric rule |
|-------|-------|-------------|-------------|
| centerStopped | 2.0 | 62 lpmm at f/4-5.6 (94% of 66 max). LensTip summary: "very good image quality in the frame centre." | >= 90% |
| cornerStopped | 1.0 | 43-44 lpmm (67% of 66 max). "Only slightly better than average." | 60-74% |
| centerWideOpen | 1.0 | 48 lpmm at f/2 (73% of 66 max). | 60-74% |
| astigmatism | 2.0 | 1.8%. "Excellent result." | < 5% |
| coma | 0.5 | "At max aperture the coma is very high." Slight when stopped down. | "poor" |
| longitudinalCA | 1.5 | "Not bothersome", "slight colouring." | "low" |
| lateralCA | 1.0 | 0.08-0.11%. "Borderline low and moderate." | 0.09-0.14% |
| distortion | 0.0 | RAW: -5.28%. "Huge barrel distortion." | > 4.0% |
| vignettingWideOpen | 0.5 | RAW: -1.69 EV at f/2. | 1.5-2.5 EV |
| vignettingStopped | 1.0 | RAW: -1.02 EV at f/5.6. "Diminishing returns." | 1.0-1.5 EV |
| bokeh | 1.5 | "Almost no reservations", even light spread, no rings. | "very good" |
| flareResistance | 1.5 | "Very difficult to catch artifacts." Good. | "very good" |

### XF 23mm f/1.4 R LM WR

Fast wide prime. Sources: LensTip (lab, trust 3),
OpticalLimits (lab, trust 3), Dustin Abbott (field, trust 3).
Sensor: X-Trans IV, max ~85 lpmm.

| Field | Score | Source data | Rubric rule |
|-------|-------|-------------|-------------|
| centerStopped | 2.0 | 82+ lpmm at f/4 (96% of max) | >= 90% |
| cornerStopped | 1.5 | ~70 lpmm at f/4 (82% of max) | 75-89% |
| centerWideOpen | 1.5 | ~70 lpmm at f/1.4 (82% of max) | 75-89% |
| astigmatism | 1.0 | 17.7% sagittal/tangential difference | 10-18% |
| coma | 1.5 | "slight deformations only at max aperture" | "low" |
| sphericalAberration | 1.5 | "subtle focus shift when stopping down" | "low" |
| longitudinalCA | 1.5 | "low even at the maximum relative aperture" | "low" |
| lateralCA | 2.0 | 0.04% at all apertures | < 0.04% boundary |
| distortion | 0.5 | -3.49% barrel (RAW) | 2.0-4.0% |
| vignettingWideOpen | 0.5 | -2.11 EV at f/1.4 (RAW) | 1.5-2.5 EV |
| vignettingStopped | 2.0 | -0.13 EV at f/4 (RAW) | < 0.5 EV |
| bokeh | 1.5 | "defocused circles look really well", trace onion rings | "very good" |
| flareResistance | 0.5 | "a lot of flares no matter what aperture" | "poor" |

### XF 27mm f/2.8 R WR

Pancake prime. Same optical formula as original XF 27mm f/2.8 (2013).
Sources: LensTip (lab, trust 3), Admiring Light (field, trust 2).
Sensor: X-Trans I (X-E1), max ~66 lpmm.

| Field | Score | Source data | Rubric rule |
|-------|-------|-------------|-------------|
| centerStopped | 2.0 | Peak at f/4-5.6, "for a pancake simply brilliant." 64 lpmm at f/2.8 already 97% of max. | >= 90% |
| cornerStopped | 1.0 | LensTip: "performance on the edge differs significantly from the centre." Admiring Light: "acceptable." Pancake compromise. | "acceptable" |
| centerWideOpen | 2.0 | 64 lpmm at f/2.8 center (97% of max). LensTip: "excellent, very sharp at maximum aperture." | >= 90% |
| astigmatism | 1.5 | 5%. LensTip: "well corrected", "low." | 5-10% |
| coma | 1.0 | "can be bothersome and distinct at max aperture", "gets significantly lower at f/4." | "noticeable" |
| sphericalAberration | 2.0 | "no focus shift, sensational performance for a pancake." Defocused points look the same before/after focus. | "negligible" |
| longitudinalCA | 1.5 | LensTip: "negligible influence only at max aperture." Admiring Light: "essentially completely free." Conservative. | "low" |
| lateralCA | 2.0 | LensTip: "very low at any aperture." Admiring Light: "completely free." | negligible |
| distortion | 1.0 | RAW: -1.98% barrel. JPEG: -0.85%. | 1.0-2.0% |
| vignettingWideOpen | 0.5 | RAW: -1.81 EV at f/2.8. | 1.5-2.5 EV |
| vignettingStopped | 1.5 | RAW: -0.74 EV at f/5.6. | 0.5-1.0 EV |
| bokeh | 0.5 | Admiring Light: "mediocre", "somewhat harsh", "bright edges", "nissen bokeh." | "poor" |
| flareResistance | 1.0 | LensTip: "intensive flare when source in corner." Admiring Light: "does fairly well", veiling flare possible. Mixed. | "average" |

### XF 33mm f/1.4 R LM WR

Standard prime. Sources: LensTip (lab, trust 3).
Sensor: X-Trans IV, max ~85 lpmm.

| Field | Score | Source data | Rubric rule |
|-------|-------|-------------|-------------|
| centerStopped | 2.0 | 79+ lpmm at f/4 (93% of max). | >= 90% |
| cornerStopped | 1.5 | "Much better than predecessor." No lpmm. | "very good" (conservative) |
| centerWideOpen | 1.0 | 61.5 lpmm at f/1.4 (72% of max). | 60-74% |
| astigmatism | 2.0 | 4.7%. "Borderline between very low and low." | < 5% |
| coma | 1.0 | "Coma makes itself felt at f/1.4", "stop down 1 EV and all problems disappear." | "noticeable" |
| sphericalAberration | 1.0 | "Slight focus shift", "defocused circles not identical before/behind." | "noticeable" |
| longitudinalCA | 1.5 | "Corrects longitudinal CA properly well." | "well corrected" |
| lateralCA | 2.0 | "Very low, you won't have any problems." | negligible |
| distortion | 1.0 | RAW: +1.08% pincushion. | 1.0-2.0% |
| vignettingWideOpen | 0.5 | RAW: -1.84 EV at f/1.4. "A lot but doesn't fare weaker than rivals." | 1.5-2.5 EV |
| vignettingStopped | 1.5 | RAW: -0.72 EV at f/5.6. "Decreases so slowly", persists at higher apertures. | 0.5-1.0 EV |
| bokeh | 1.5 | "Very slight trace of onion ring bokeh" from aspherical elements. | "very good" |
| flareResistance | 1.5 | "Good performance against bright light." | "very good" |

### XF 56mm f/1.2 R WR

Fast portrait prime. Sources: LensTip (lab, trust 3),
OpticalLimits (lab, trust 3), Dustin Abbott (field, trust 3),
Fuji vs Fuji (field, trust 2).
Sensor: X-Trans III (X-T2), max ~78 lpmm.

| Field | Score | Source data | Rubric rule |
|-------|-------|-------------|-------------|
| centerStopped | 2.0 | 92.8 lpmm at f/2.8 (119% of max, record) | >= 90% |
| cornerStopped | 2.0 | ~80 lpmm at f/4 (103% of max) | >= 90% |
| centerWideOpen | 2.0 | 75.3 lpmm at f/1.2 (97% of max) | >= 90% |
| astigmatism | 2.0 | 4.6% sagittal/tangential difference | < 5% |
| coma | 2.0 | "deformations very slight even at max aperture, shouldn't worry you" | "negligible" |
| sphericalAberration | 2.0 | "difficult to notice any focus shift effect" | "negligible" |
| longitudinalCA | 2.0 | "doesn't have any problems... difficult to see any colouring" | "negligible" |
| lateralCA | 2.0 | 0.02% at all apertures | < 0.04% |
| distortion | 2.0 | +0.13% pincushion (RAW), "practically distortion-free" | < 0.3% |
| vignettingWideOpen | 0.5 | OpticalLimits: ~1.8 EV at f/1.2. FujiVsFuji: "heavy". LensTip: -0.91 EV (milder measurement point). Conservative. | 1.5-2.5 EV |
| vignettingStopped | 2.0 | LensTip: -0.24 EV at f/2.8, -0.17 EV at f/4. OpticalLimits: "irrelevant from f/2.8" | < 0.5 EV |
| bokeh | 1.5 | LensTip: "look really nice", no onion rings. OpticalLimits: "slightly nervous inner zones, subtle rim." Conservative. | "very good" (conservative between sources) |
| flareResistance | 1.5 | LensTip: "performs against bright light quite well", artifacts only in extreme conditions | "very good" |

### XF 80mm f/2.8 R LM OIS WR Macro

Macro prime. Sources: LensTip (lab, trust 3).
Sensor: X-Trans I (X-E1), max ~66 lpmm.

| Field | Score | Source data | Rubric rule |
|-------|-------|-------------|-------------|
| centerStopped | 2.0 | 82+ lpmm at f/4 (124% of max). "Revelation." | >= 90% |
| cornerStopped | 0.5 | "Huge discrepancy between centre and edge." | "poor" |
| centerWideOpen | 2.0 | 76 lpmm at f/2.8 (115% of max). | >= 90% |
| astigmatism | 2.0 | 2.5%. "Negligible", "very low." | < 5% |
| coma | 2.0 | "Practically ideal", "even at max aperture in the corner, diode images aren't distorted." | "negligible" |
| sphericalAberration | 2.0 | "Shouldn't be a big problem", 0.03-0.04%. | "negligible" |
| longitudinalCA | 2.0 | "Corrects very well, invisible even at max aperture." | "negligible" |
| lateralCA | 2.0 | 0.03-0.04%. "Very low." | < 0.04% |
| distortion | 1.5 | RAW: +0.79%. "Shouldn't bother you." | 0.3-1.0% |
| vignettingWideOpen | 0.5 | RAW: -1.74 EV at f/2.8. "Serious flaw." | 1.5-2.5 EV |
| vignettingStopped | 2.0 | -0.33 EV at f/5.6. | < 0.5 EV |
| bokeh | 1.5 | "Nice, very even light spread, slight rim on edge." Mechanical vignetting truncates at max aperture. | "very good" |
| flareResistance | 1.0 | "Doesn't perform the best", "purple coloring and bright radial beams" in some positions. "Not abysmal." | "average" |

### XF 90mm f/2 R LM WR

Tele portrait prime. Sources: LensTip (lab, trust 3),
Dustin Abbott (field, trust 3).
Sensor: X-Trans I (X-E1), max ~66 lpmm.

| Field | Score | Source data | Rubric rule |
|-------|-------|-------------|-------------|
| centerStopped | 2.0 | 78.5 lpmm at f/2.8 (119% of max, record). LensTip: "record-breaking." | >= 90% |
| cornerStopped | 1.5 | LensTip: edge "excellent". Dustin Abbott: "nearly as good corners even at f/2." No lpmm. Conservative. | "very good" |
| centerWideOpen | 2.0 | ~72 lpmm at f/2 center (109% of max). | >= 90% |
| astigmatism | 2.0 | 3.2%. LensTip: "slight value." | < 5% |
| coma | 2.0 | "difficult to notice any influence, even in the corner wide open." | "negligible" |
| sphericalAberration | 1.5 | "no focus shift, corrected at least satisfactorily, slight differences before/after focal point." | "well corrected" |
| longitudinalCA | 1.5 | "not high", "might try to notice at max aperture", gone by f/2.8. | "low" |
| lateralCA | 2.0 | 0.03%. LensTip: "negligible." | < 0.04% |
| distortion | 2.0 | LensTip: "almost zero." | < 0.3% |
| vignettingWideOpen | 1.5 | RAW: -0.81 EV at f/2. | 0.5-1.0 EV |
| vignettingStopped | 2.0 | RAW: -0.14 EV at f/4. | < 0.5 EV |
| bokeh | 1.5 | LensTip: "very nice and even", slightly emphasized rim stopped down. Dustin Abbott: "very nice" but "a little busy" on complex backgrounds. | "very good" |
| flareResistance | 0.5 | LensTip: "doesn't look well", deteriorates stopped down. Dustin Abbott: "somewhat flare prone." | "poor" |

### XF 100-400mm f/4.5-5.6 R LM OIS WR

Super-tele zoom. Sources: LensTip (lab, trust 3),
Dustin Abbott (field, trust 3).
Sensor: X-Trans I (X-E1), per-review max 74 lpmm. Scored at 200mm mid-range.

| Field | Score | Source data | Rubric rule |
|-------|-------|-------------|-------------|
| centerStopped | 1.5 | "Very good quality across all FL." Not record-breaking. | "very good" |
| cornerStopped | 1.0 | Edge performance lower, typical for super-tele zoom. No lpmm. | "average" (conservative) |
| centerWideOpen | 1.0 | 54 lpmm at 200mm wide open (73% of 74 max). | 60-74% |
| astigmatism | 1.0 | 12%. "Medium result." Highest at both ends of FL range. | 10-18% |
| coma | 2.0 | "No noticeable problems, diode images very similar center and corner regardless of FL." | "negligible" |
| sphericalAberration | 2.0 | "No focus shift, no visible influence in defocused circles, very similar before/after focus." | "negligible" |
| longitudinalCA | 2.0 | "Corrects longitudinal CA really well — influence negligible." | "negligible" |
| lateralCA | 1.5 | "Very low" at common apertures, "approaches medium" at long FL. | "low" |
| distortion | 0.5 | RAW: +2.09% to +2.29% pincushion across range. | 2.0-4.0% |
| vignettingWideOpen | 1.0 | 100mm: -1.15 EV. 400mm: -1.35 EV. | 1.0-1.5 EV |
| vignettingStopped | 1.5 | 400mm f/8: -0.51 EV. | 0.5-1.0 EV |
| bokeh | 1.0 | LensTip: "quite nice for a zoom, rim on edge." Dustin Abbott: "average." | "average" |
| flareResistance | 1.0 | "Flares, ghosting, and contrast decrease are easy to spot." | "noticeable" |

### XF 200mm f/2 R LM OIS WR

Flagship super-tele prime.
Sources: ePHOTOzine (lab, trust 2), Dustin Abbott (field, trust 3),
official Fujifilm MTF chart (for astigmatism).
No LensTip or OpticalLimits review exists.

| Field | Score | Source data | Rubric rule |
|-------|-------|-------------|-------------|
| centerStopped | 2.0 | ePHOTOzine: "excellent" centre f/2.8-f/8. Multiple: "nothing to correct." | "excellent" |
| cornerStopped | 2.0 | ePHOTOzine: "excellent" edges f/2.8-f/8. "Edge to edge sharpness even wide open." | "excellent" |
| centerWideOpen | 2.0 | Multiple: "incredibly sharp wide open." | "excellent" |
| astigmatism | 2.0 | Official Fujifilm MTF chart: S and M lines very close together across the field. | S/M convergence = negligible |
| coma | — | MTF chart cannot isolate coma from astigmatism. Only point-source tests can. | data integrity rule |
| sphericalAberration | 2.0 | Optical design: 1 Super ED + 2 ED elements targeting spherical aberration. No reviewer reported focus shift or fringing. | "negligible" (design + field confirmation) |
| longitudinalCA | 2.0 | "Very well controlled", no fringing mentioned by any source. Super ED elements. | "negligible" |
| lateralCA | 2.0 | ePHOTOzine: "very well controlled centre and edge." | "negligible" |
| distortion | 2.0 | +0.14% pincushion. ePHOTOzine: "minimal." | < 0.3% |
| vignettingWideOpen | 1.5 | ePHOTOzine: 0.5 stops wide open. Boundary value, conservative. | 0.5-1.0 EV |
| vignettingStopped | 2.0 | Negligible stopped down. | < 0.5 EV |
| bokeh | 2.0 | "Best bokeh of any XF lens", "silky smooth", "close to perfection." | "excellent" |
| flareResistance | 1.0 | "A bit of veiling with sun in/out of frame." Some ghosting stopped down. | "average" |

Note: astigmatism scored from official manufacturer MTF chart (S/M line
convergence). Spherical aberration scored via optical construction
inference (Super ED + aspherical) confirmed by field reports.

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
