# Scoring Log

Per-lens scoring justifications traceable to source review pages.
Rubric rules are defined in [ADR-014](decisions/014-optical-quality-rubric.md).

Sorted by brand, then focal length (wide to tele).

---

## Fujifilm

### XF 8-16mm f/2.8 R LM WR

Premium ultra-wide zoom. Sources: LensTip (lab, trust 3).
Sensor: X-Trans III, max ~78 lpmm. Scored at 12mm mid-range.

| Field              | Score | Source data                                                                                                          | Rubric rule                   |
| ------------------ | ----- | -------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| centerStopped      | 2.0   | ~80 lpmm at 12-16mm. "Exceptional."                                                                                  | >= 90%                        |
| cornerStopped      | 1.5   | 62 lpmm edge at 12mm. 62/78 = 79%. "Very well even at max aperture" in 12-16mm range.                                | 75-89%                        |
| centerWideOpen     | 2.0   | ~70 lpmm at f/2.8 across range.                                                                                      | >= 90%                        |
| astigmatism        | 1.5   | 7.6%. "Moderate."                                                                                                    | 5-10%                         |
| coma               | 1.0   | "Noticeable", most at 8mm, slight at 12-16mm.                                                                        | "noticeable"                  |
| longitudinalCA     | 1.5   | "Slight", "out-of-focus images a bit tinted." Minor.                                                                 | "low"                         |
| lateralCA          | 2.0   | Summary PRO: "low lateral chromatic aberration." <0.05% at 12-16mm (mid-range). Correction described as "very high." | PRO: "low"; < 0.04% at mid-FL |
| distortion         | 1.5   | RAW: -0.56% at 12mm. (-8.41% at 8mm extreme.)                                                                        | 0.3-1.0%                      |
| vignettingWideOpen | 0.5   | RAW: -1.96 EV at 12mm f/2.8.                                                                                         | 1.5-2.5 EV                    |
| vignettingStopped  | 1.0   | RAW: -1.33 EV at 12mm f/11. Resistant to stopping down.                                                              | 1.0-1.5 EV                    |
| flareResistance    | 1.0   | "Some slip-ups", "not that bad given complexity." Average.                                                           | "average"                     |

### XF 10-24mm f/4 R OIS WR

Ultra-wide zoom for landscape/architecture.
Same optical formula as original XF 10-24mm f/4 R OIS (2013).
Sources: LensTip (lab, trust 3).
Sensor: X-Trans I (X-E1), per-review max 71 lpmm. Scored at mid-range.

| Field               | Score | Source data                                                                                   | Rubric rule                           |
| ------------------- | ----- | --------------------------------------------------------------------------------------------- | ------------------------------------- |
| centerStopped       | 2.0   | 69-70 lpmm at f/4-5.6 mid-range (99% of 71 max). "Worth of a good quality fixed-focal lens."  | >= 90%                                |
| cornerStopped       | 1.5   | 55 lpmm edge, "never exceeds 55 lpmm" across range. 55/71 = 77%.                              | 75-89%                                |
| centerWideOpen      | 1.5   | Variable across range.                                                                        | 75-89%                                |
| astigmatism         | 1.5   | Average 7.1%. Ranges 13% at 10mm to low mid-range.                                            | 5-10% (average)                       |
| coma                | 1.0   | "Influence can be felt", "highest at both ends", "almost imperceptible in the middle."        | "noticeable"                          |
| sphericalAberration | 1.5   | "Good control of spherical aberration."                                                       | "well corrected"                      |
| longitudinalCA      | 1.5   | "Not a big problem", "slightly yellow/bluish cast", decreases at f/5.6.                       | "low"                                 |
| lateralCA           | 1.5   | At 10mm: ~0.05%. Increases at longer FL.                                                      | 0.04-0.08%                            |
| distortion          | 1.0   | RAW: +1.53% at mid-range. (-4.62% at 10mm extreme.)                                           | 1.0-2.0%                              |
| vignettingWideOpen  | 0.5   | RAW: -1.93 EV at 10mm f/4. "Very high value."                                                 | 1.5-2.5 EV                            |
| vignettingStopped   | 1.5   | RAW: -0.61 EV at mid-range f/5.6.                                                             | 0.5-1.0 EV                            |
| bokeh               | 0.5   | "Moderately good", "distinct rim", "onion rings."                                             | "poor"                                |
| flareResistance     | 1.5   | "Works against bright light very well" at wide end. Super EBC coating. Increases at long end. | "very good" (wide) → conservative 1.5 |

### XF 14mm f/2.8 R

Wide prime. Sources: LensTip (lab, trust 3).
Sensor: X-Trans I (X-E1), max ~66 lpmm.

| Field               | Score | Source data                                                | Rubric rule      |
| ------------------- | ----- | ---------------------------------------------------------- | ---------------- |
| centerStopped       | 2.0   | 72 lpmm at f/4-5.6 (109% of max).                          | >= 90%           |
| cornerStopped       | 1.0   | Edge 42+ lpmm. >20 lpmm gap from center.                   | "average"        |
| centerWideOpen      | 2.0   | 69 lpmm at f/2.8 (105% of max).                            | >= 90%           |
| astigmatism         | 2.0   | 3.4%. "No correction problems."                            | < 5%             |
| coma                | 1.0   | "Clearly noticeable at max aperture." Low at f/4.          | "noticeable"     |
| sphericalAberration | 1.5   | Even light spread, noticeable rim at edge. No focus shift. | "well corrected" |
| longitudinalCA      | 2.0   | "Not a problem whatsoever."                                | "negligible"     |
| lateralCA           | 2.0   | Never exceeds 0.04%.                                       | < 0.04%          |
| distortion          | 2.0   | RAW: -0.23%. "Practically imperceptible."                  | < 0.3%           |
| vignettingWideOpen  | 0.5   | RAW: -2.09 EV at f/2.8.                                    | 1.5-2.5 EV       |
| vignettingStopped   | 0.5   | RAW: -1.52 EV at f/4. Still heavy.                         | 1.5-2.5 EV       |
| bokeh               | 1.5   | Even distribution, noticeable rim at edge only.            | "very good"      |
| flareResistance     | 1.5   | "Really difficult to catch any flares." Good.              | "very good"      |

### XF 16mm f/1.4 R WR

Fast wide prime. Sources: LensTip (lab, trust 3).
Sensor: X-Trans I (X-E1), max ~66 lpmm.

| Field               | Score | Source data                                                                                    | Rubric rule              |
| ------------------- | ----- | ---------------------------------------------------------------------------------------------- | ------------------------ |
| centerStopped       | 2.0   | ~70 lpmm at f/4 (106% of max). Summary PRO: "excellent image quality in the frame centre."     | PRO: "excellent"         |
| cornerStopped       | 1.0   | Edge "exceeds utility threshold at f/2.0." Below decency wide open.                            | "average"                |
| centerWideOpen      | 1.0   | 44 lpmm at f/1.4 (67% of max). Barely above decency.                                           | 60-74%                   |
| astigmatism         | 2.0   | 3.0%. "Very low level."                                                                        | < 5%                     |
| coma                | 0.5   | "Corrects coma in a very poor way", "really high at max aperture", only reduces at f/2.8.      | "poor"                   |
| sphericalAberration | 0.5   | "Textbook example of spherical aberration influence", "far from perfect."                      | "poor"                   |
| longitudinalCA      | 0.5   | "A lot of problems", "even at f/2.0 still quite bothersome."                                   | "poor"                   |
| lateralCA           | 1.5   | 0.07%. "Low level."                                                                            | 0.04-0.08%               |
| distortion          | 2.0   | RAW: -0.87%. Summary PRO: "low distortion — noticeably lower than rivals." "Excellent result." | PRO: "low/excellent"     |
| vignettingWideOpen  | 0.5   | RAW: -1.94 EV at f/1.4.                                                                        | 1.5-2.5 EV               |
| vignettingStopped   | 1.5   | RAW: -0.56 EV at f/4-5.6. "Further stopping down doesn't help much."                           | 0.5-1.0 EV               |
| bokeh               | 0.5   | "Lighter rim on edge and noticeable onion ring", "not exactly pleasant."                       | "poor"                   |
| flareResistance     | 1.0   | Summary: "good; it wasn't very good." Artifacts when stopped down with sun near edge.          | "good" (not "very good") |

### XF 16mm f/2.8 R LM WR

Compact wide prime. Sources: LensTip (lab, trust 3).
Sensor: X-Trans III, max ~78 lpmm.

| Field               | Score | Source data                                              | Rubric rule  |
| ------------------- | ----- | -------------------------------------------------------- | ------------ |
| centerStopped       | 2.0   | 77 lpmm at f/4 (99% of max).                             | >= 90%       |
| cornerStopped       | 1.0   | 55 lpmm at f/5.6-8. "Slightly better than average."      | "average"    |
| centerWideOpen      | 1.5   | 60 lpmm at f/2.8 (77% of max).                           | 75-89%       |
| astigmatism         | 1.0   | 10.3%. "Medium level."                                   | 10-18%       |
| coma                | 1.0   | "Corrects well from f/4", visible at max aperture.       | "noticeable" |
| sphericalAberration | 2.0   | "No significant focus shift."                            | "negligible" |
| lateralCA           | 1.5   | ~0.05%. "Borderline imperceptible and low."              | 0.04-0.08%   |
| distortion          | 0.0   | RAW: -7.73%. "Monstrous."                                | > 4.0%       |
| vignettingWideOpen  | 0.5   | RAW: -1.87 EV at f/2.8.                                  | 1.5-2.5 EV   |
| vignettingStopped   | 1.5   | RAW: -0.60 EV at f/8.                                    | 0.5-1.0 EV   |
| bokeh               | 0.5   | "Visible onion ring bokeh" from aspherical elements.     | "poor"       |
| flareResistance     | 1.5   | "Good", minimal issues wide open, degrades stopped down. | "very good"  |

### XF 16-55mm f/2.8 R LM WR

Standard zoom. Sources: LensTip (lab, trust 3).
Sensor: X-Trans I (X-E1), per-review max ~71 lpmm. Scored at 35mm mid-range.

| Field               | Score | Source data                                                                                                  | Rubric rule                   |
| ------------------- | ----- | ------------------------------------------------------------------------------------------------------------ | ----------------------------- |
| centerStopped       | 1.5   | ~58 lpmm at 35mm mid-range. 58/71 = 82%.                                                                     | 75-89%                        |
| cornerStopped       | 1.0   | 50 lpmm at edge. Conservative.                                                                               | "average"                     |
| centerWideOpen      | 1.5   | ~58 lpmm at 35mm f/2.8.                                                                                      | 75-89%                        |
| astigmatism         | 1.5   | 5.6%. "Low value."                                                                                           | 5-10%                         |
| coma                | 1.5   | Summary PRO: "no noticeable coma correction problems." Outperforms Canon, Nikkor, Sigma, Tokina competitors. | PRO: "no noticeable problems" |
| sphericalAberration | 2.0   | "Corrected in a perfect way."                                                                                | "negligible"                  |
| longitudinalCA      | 1.5   | "Slight colouring, nothing to worry about."                                                                  | "low"                         |
| lateralCA           | 1.5   | Summary PRO: "at no combination reaches high values, achievement worth praise." 0.09-0.12% at mid-range.     | PRO: never high               |
| distortion          | 0.5   | RAW: significant across range. "Relied on software."                                                         | 2.0-4.0%                      |
| vignettingWideOpen  | 1.5   | RAW: -0.89 EV at 35mm f/2.8.                                                                                 | 0.5-1.0 EV                    |
| vignettingStopped   | 2.0   | RAW: -0.38 EV at 35mm f/5.6.                                                                                 | < 0.5 EV                      |
| bokeh               | 0.5   | "Concentric lines, accentuated rim, truncations."                                                            | "poor"                        |
| flareResistance     | 1.5   | "Really difficult to catch flares", "small and not intensive."                                               | "very good"                   |

### XF 16-55mm f/2.8 R LM WR II

Standard zoom, new optical design. Sources: Dustin Abbott (field,
trust 3), official Fujifilm MTF chart (for astigmatism).
No lab review yet.

| Field               | Score | Source data                                                                              | Rubric rule                               |
| ------------------- | ----- | ---------------------------------------------------------------------------------------- | ----------------------------------------- |
| centerStopped       | 1.5   | "Uniformly pretty excellent" f/4-f/8. "Most consistently excellent APS-C standard zoom." | "very good" to "excellent" → conservative |
| cornerStopped       | 1.5   | MTF: S/M high through midframe. "Improved corner performance" vs Mk I.                   | "very good"                               |
| centerWideOpen      | 1.5   | "Give and take at f/2.8" at 35mm. Not "excellent" wide open.                             | "very good"                               |
| astigmatism         | 1.5   | Official MTF chart: S/M gap 0.10-0.15 at 45 lp/mm worst case. Low for a zoom.            | S/M low divergence                        |
| sphericalAberration | 2.0   | Aspherical + Super ED. No focus shift reported. Fallback: design + zero complaints.      | "negligible"                              |
| longitudinalCA      | 2.0   | "Extremely well controlled." "Huge advantage over Sigma."                                | "negligible"                              |
| lateralCA           | 2.0   | "Next to no fringing."                                                                   | "negligible"                              |
| bokeh               | 1.0   | "Fairly good for a standard zoom", "busier", inner outlining.                            | "average"                                 |
| flareResistance     | 1.5   | "Holds up to bright sun." Minor ghosting stopped down.                                   | "very good"                               |

### XF 18mm f/2.0 R

Pancake wide prime. Sources: LensTip (lab, trust 3).
Sensor: X-Trans I (X-Pro1), per-review max 66 lpmm.

| Field              | Score | Source data                                                                                         | Rubric rule |
| ------------------ | ----- | --------------------------------------------------------------------------------------------------- | ----------- |
| centerStopped      | 2.0   | 62 lpmm at f/4-5.6 (94% of 66 max). LensTip summary: "very good image quality in the frame centre." | >= 90%      |
| cornerStopped      | 1.0   | 43-44 lpmm (67% of 66 max). "Only slightly better than average."                                    | 60-74%      |
| centerWideOpen     | 1.0   | 48 lpmm at f/2 (73% of 66 max).                                                                     | 60-74%      |
| astigmatism        | 2.0   | 1.8%. "Excellent result."                                                                           | < 5%        |
| coma               | 0.5   | "At max aperture the coma is very high." Slight when stopped down.                                  | "poor"      |
| longitudinalCA     | 1.5   | "Not bothersome", "slight colouring."                                                               | "low"       |
| lateralCA          | 1.0   | 0.08-0.11%. "Borderline low and moderate."                                                          | 0.09-0.14%  |
| distortion         | 0.0   | RAW: -5.28%. "Huge barrel distortion."                                                              | > 4.0%      |
| vignettingWideOpen | 0.5   | RAW: -1.69 EV at f/2.                                                                               | 1.5-2.5 EV  |
| vignettingStopped  | 1.0   | RAW: -1.02 EV at f/5.6. "Diminishing returns."                                                      | 1.0-1.5 EV  |
| bokeh              | 1.5   | "Almost no reservations", even light spread, no rings.                                              | "very good" |
| flareResistance    | 1.5   | "Very difficult to catch artifacts." Good.                                                          | "very good" |

### XF 23mm f/1.4 R LM WR

Fast wide prime. Sources: LensTip (lab, trust 3),
OpticalLimits (lab, trust 3), Dustin Abbott (field, trust 3).
Sensor: X-Trans IV, max ~85 lpmm.

| Field               | Score | Source data                                             | Rubric rule      |
| ------------------- | ----- | ------------------------------------------------------- | ---------------- |
| centerStopped       | 2.0   | 82+ lpmm at f/4 (96% of max)                            | >= 90%           |
| cornerStopped       | 1.5   | ~70 lpmm at f/4 (82% of max)                            | 75-89%           |
| centerWideOpen      | 1.5   | ~70 lpmm at f/1.4 (82% of max)                          | 75-89%           |
| astigmatism         | 1.0   | 17.7% sagittal/tangential difference                    | 10-18%           |
| coma                | 1.5   | "slight deformations only at max aperture"              | "low"            |
| sphericalAberration | 1.5   | "subtle focus shift when stopping down"                 | "low"            |
| longitudinalCA      | 1.5   | "low even at the maximum relative aperture"             | "low"            |
| lateralCA           | 2.0   | 0.04% at all apertures                                  | < 0.04% boundary |
| distortion          | 0.5   | -3.49% barrel (RAW)                                     | 2.0-4.0%         |
| vignettingWideOpen  | 0.5   | -2.11 EV at f/1.4 (RAW)                                 | 1.5-2.5 EV       |
| vignettingStopped   | 2.0   | -0.13 EV at f/4 (RAW)                                   | < 0.5 EV         |
| bokeh               | 1.5   | "defocused circles look really well", trace onion rings | "very good"      |
| flareResistance     | 0.5   | "a lot of flares no matter what aperture"               | "poor"           |

### XF 27mm f/2.8 R WR

Pancake prime. Same optical formula as original XF 27mm f/2.8 (2013).
Sources: LensTip (lab, trust 3), Admiring Light (field, trust 2).
Sensor: X-Trans I (X-E1), max ~66 lpmm.

| Field               | Score | Source data                                                                                                                 | Rubric rule  |
| ------------------- | ----- | --------------------------------------------------------------------------------------------------------------------------- | ------------ |
| centerStopped       | 2.0   | Peak at f/4-5.6, "for a pancake simply brilliant." 64 lpmm at f/2.8 already 97% of max.                                     | >= 90%       |
| cornerStopped       | 1.0   | LensTip: "performance on the edge differs significantly from the centre." Admiring Light: "acceptable." Pancake compromise. | "acceptable" |
| centerWideOpen      | 2.0   | 64 lpmm at f/2.8 center (97% of max). LensTip: "excellent, very sharp at maximum aperture."                                 | >= 90%       |
| astigmatism         | 1.5   | 5%. LensTip: "well corrected", "low."                                                                                       | 5-10%        |
| coma                | 1.0   | "can be bothersome and distinct at max aperture", "gets significantly lower at f/4."                                        | "noticeable" |
| sphericalAberration | 2.0   | "no focus shift, sensational performance for a pancake." Defocused points look the same before/after focus.                 | "negligible" |
| longitudinalCA      | 1.5   | LensTip: "negligible influence only at max aperture." Admiring Light: "essentially completely free." Conservative.          | "low"        |
| lateralCA           | 2.0   | LensTip: "very low at any aperture." Admiring Light: "completely free."                                                     | negligible   |
| distortion          | 1.0   | RAW: -1.98% barrel. JPEG: -0.85%.                                                                                           | 1.0-2.0%     |
| vignettingWideOpen  | 0.5   | RAW: -1.81 EV at f/2.8.                                                                                                     | 1.5-2.5 EV   |
| vignettingStopped   | 1.5   | RAW: -0.74 EV at f/5.6.                                                                                                     | 0.5-1.0 EV   |
| bokeh               | 0.5   | Admiring Light: "mediocre", "somewhat harsh", "bright edges", "nissen bokeh."                                               | "poor"       |
| flareResistance     | 1.0   | LensTip: "intensive flare when source in corner." Admiring Light: "does fairly well", veiling flare possible. Mixed.        | "average"    |

### XF 33mm f/1.4 R LM WR

Standard prime. Sources: LensTip (lab, trust 3).
Sensor: X-Trans IV, max ~85 lpmm.

| Field               | Score | Source data                                                                                            | Rubric rule                |
| ------------------- | ----- | ------------------------------------------------------------------------------------------------------ | -------------------------- |
| centerStopped       | 2.0   | 79+ lpmm at f/4 (93% of max).                                                                          | >= 90%                     |
| cornerStopped       | 1.5   | "Much better than predecessor." No lpmm.                                                               | "very good" (conservative) |
| centerWideOpen      | 1.0   | 61.5 lpmm at f/1.4 (72% of max).                                                                       | 60-74%                     |
| astigmatism         | 2.0   | 4.7%. "Borderline between very low and low."                                                           | < 5%                       |
| coma                | 1.0   | "Coma makes itself felt at f/1.4", "stop down 1 EV and all problems disappear."                        | "noticeable"               |
| sphericalAberration | 1.0   | "Slight focus shift", "defocused circles not identical before/behind."                                 | "noticeable"               |
| longitudinalCA      | 2.0   | Summary PRO: "negligible longitudinal chromatic aberration." Ch5: "difficult to notice any colouring." | PRO: "negligible"          |
| lateralCA           | 2.0   | "Very low, you won't have any problems."                                                               | negligible                 |
| distortion          | 1.0   | RAW: +1.08% pincushion.                                                                                | 1.0-2.0%                   |
| vignettingWideOpen  | 0.5   | RAW: -1.84 EV at f/1.4. "A lot but doesn't fare weaker than rivals."                                   | 1.5-2.5 EV                 |
| vignettingStopped   | 1.5   | RAW: -0.72 EV at f/5.6. "Decreases so slowly", persists at higher apertures.                           | 0.5-1.0 EV                 |
| bokeh               | 1.5   | "Very slight trace of onion ring bokeh" from aspherical elements.                                      | "very good"                |
| flareResistance     | 1.5   | "Good performance against bright light."                                                               | "very good"                |

### XF 56mm f/1.2 R LM WR

Fast portrait prime. Sources: LensTip (lab, trust 3),
OpticalLimits (lab, trust 3), Dustin Abbott (field, trust 3),
Fuji vs Fuji (field, trust 2).
Sensor: X-Trans III (X-T2), max ~78 lpmm.

| Field               | Score | Source data                                                                                                           | Rubric rule                                |
| ------------------- | ----- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| centerStopped       | 2.0   | 92.8 lpmm at f/2.8 (119% of max, record)                                                                              | >= 90%                                     |
| cornerStopped       | 2.0   | ~80 lpmm at f/4 (103% of max)                                                                                         | >= 90%                                     |
| centerWideOpen      | 2.0   | 75.3 lpmm at f/1.2 (97% of max)                                                                                       | >= 90%                                     |
| astigmatism         | 2.0   | 4.6% sagittal/tangential difference                                                                                   | < 5%                                       |
| coma                | 2.0   | "deformations very slight even at max aperture, shouldn't worry you"                                                  | "negligible"                               |
| sphericalAberration | 2.0   | "difficult to notice any focus shift effect"                                                                          | "negligible"                               |
| longitudinalCA      | 2.0   | "doesn't have any problems... difficult to see any colouring"                                                         | "negligible"                               |
| lateralCA           | 2.0   | 0.02% at all apertures                                                                                                | < 0.04%                                    |
| distortion          | 2.0   | +0.13% pincushion (RAW), "practically distortion-free"                                                                | < 0.3%                                     |
| vignettingWideOpen  | 0.5   | OpticalLimits: ~1.8 EV at f/1.2. FujiVsFuji: "heavy". LensTip: -0.91 EV (milder measurement point). Conservative.     | 1.5-2.5 EV                                 |
| vignettingStopped   | 2.0   | LensTip: -0.24 EV at f/2.8, -0.17 EV at f/4. OpticalLimits: "irrelevant from f/2.8"                                   | < 0.5 EV                                   |
| bokeh               | 1.5   | LensTip: "look really nice", no onion rings. OpticalLimits: "slightly nervous inner zones, subtle rim." Conservative. | "very good" (conservative between sources) |
| flareResistance     | 1.5   | LensTip: "performs against bright light quite well", artifacts only in extreme conditions                             | "very good"                                |

### XF 80mm f/2.8 R LM OIS WR Macro

Macro prime. Sources: LensTip (lab, trust 3).
Sensor: X-Trans I (X-E1), max ~66 lpmm.

| Field               | Score | Source data                                                                                                                                                                     | Rubric rule  |
| ------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| centerStopped       | 2.0   | 82+ lpmm at f/4 (124% of max). "Revelation."                                                                                                                                    | >= 90%       |
| cornerStopped       | 1.0   | Summary PRO: "good image quality on the edge." Ch4: "hard to have serious reservations, sharp even at max aperture." Gap criticism is relative to near-record center (82 lpmm). | PRO: "good"  |
| centerWideOpen      | 2.0   | 76 lpmm at f/2.8 (115% of max). "Sensational."                                                                                                                                  | >= 90%       |
| cornerWideOpen      | 1.0   | Summary PRO: "good image quality on the edge of the frame." Ch4: "hard to have serious reservations."                                                                           | PRO: "good"  |
| astigmatism         | 2.0   | 2.5%. "Negligible", "very low."                                                                                                                                                 | < 5%         |
| coma                | 2.0   | "Practically ideal", "even at max aperture in the corner, diode images aren't distorted."                                                                                       | "negligible" |
| sphericalAberration | 2.0   | "Shouldn't be a big problem", 0.03-0.04%.                                                                                                                                       | "negligible" |
| longitudinalCA      | 2.0   | "Corrects very well, invisible even at max aperture."                                                                                                                           | "negligible" |
| lateralCA           | 2.0   | 0.03-0.04%. "Very low."                                                                                                                                                         | < 0.04%      |
| distortion          | 1.5   | RAW: +0.79%. "Shouldn't bother you."                                                                                                                                            | 0.3-1.0%     |
| vignettingWideOpen  | 0.5   | RAW: -1.74 EV at f/2.8. "Serious flaw."                                                                                                                                         | 1.5-2.5 EV   |
| vignettingStopped   | 2.0   | -0.33 EV at f/5.6.                                                                                                                                                              | < 0.5 EV     |
| bokeh               | 1.5   | "Nice, very even light spread, slight rim on edge." Mechanical vignetting truncates at max aperture.                                                                            | "very good"  |
| flareResistance     | 1.0   | "Doesn't perform the best", "purple coloring and bright radial beams" in some positions. "Not abysmal."                                                                         | "average"    |

### XF 90mm f/2.0 R LM WR

Tele portrait prime. Sources: LensTip (lab, trust 3),
Dustin Abbott (field, trust 3).
Sensor: X-Trans I (X-E1), max ~66 lpmm.

| Field               | Score | Source data                                                                                                                                 | Rubric rule          |
| ------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| centerStopped       | 2.0   | 78.5 lpmm at f/2.8 (119% of max, record). LensTip: "record-breaking."                                                                       | >= 90%               |
| cornerStopped       | 1.5   | LensTip: edge "excellent". Dustin Abbott: "nearly as good corners even at f/2." No lpmm. Conservative.                                      | "very good"          |
| centerWideOpen      | 2.0   | ~72 lpmm at f/2 center (109% of max).                                                                                                       | >= 90%               |
| astigmatism         | 2.0   | 3.2%. LensTip: "slight value."                                                                                                              | < 5%                 |
| coma                | 2.0   | "difficult to notice any influence, even in the corner wide open."                                                                          | "negligible"         |
| sphericalAberration | 2.0   | Summary PRO: "imperceptible spherical aberration." Ch5: no focus shift, differences "slight."                                               | PRO: "imperceptible" |
| longitudinalCA      | 1.5   | "not high", "might try to notice at max aperture", gone by f/2.8.                                                                           | "low"                |
| lateralCA           | 2.0   | 0.03%. LensTip: "negligible."                                                                                                               | < 0.04%              |
| distortion          | 2.0   | LensTip: "almost zero."                                                                                                                     | < 0.3%               |
| vignettingWideOpen  | 1.5   | RAW: -0.81 EV at f/2.                                                                                                                       | 0.5-1.0 EV           |
| vignettingStopped   | 2.0   | RAW: -0.14 EV at f/4.                                                                                                                       | < 0.5 EV             |
| bokeh               | 1.5   | LensTip: "very nice and even", slightly emphasized rim stopped down. Dustin Abbott: "very nice" but "a little busy" on complex backgrounds. | "very good"          |
| flareResistance     | 0.5   | LensTip: "doesn't look well", deteriorates stopped down. Dustin Abbott: "somewhat flare prone."                                             | "poor"               |

### XF 100-400mm f/4.5-5.6 R LM OIS WR

Super-tele zoom. Sources: LensTip (lab, trust 3),
Dustin Abbott (field, trust 3).
Sensor: X-Trans I (X-E1), per-review max 74 lpmm. Scored at 200mm mid-range.

| Field               | Score | Source data                                                                                   | Rubric rule              |
| ------------------- | ----- | --------------------------------------------------------------------------------------------- | ------------------------ |
| centerStopped       | 1.5   | "Very good quality across all FL." Not record-breaking.                                       | "very good"              |
| cornerStopped       | 1.0   | Edge performance lower, typical for super-tele zoom. No lpmm.                                 | "average" (conservative) |
| centerWideOpen      | 1.0   | 54 lpmm at 200mm wide open (73% of 74 max).                                                   | 60-74%                   |
| astigmatism         | 1.0   | 12%. "Medium result." Highest at both ends of FL range.                                       | 10-18%                   |
| coma                | 2.0   | "No noticeable problems, diode images very similar center and corner regardless of FL."       | "negligible"             |
| sphericalAberration | 2.0   | "No focus shift, no visible influence in defocused circles, very similar before/after focus." | "negligible"             |
| longitudinalCA      | 2.0   | "Corrects longitudinal CA really well — influence negligible."                                | "negligible"             |
| lateralCA           | 1.5   | "Very low" at common apertures, "approaches medium" at long FL.                               | "low"                    |
| distortion          | 0.5   | RAW: +2.09% to +2.29% pincushion across range.                                                | 2.0-4.0%                 |
| vignettingWideOpen  | 1.0   | 100mm: -1.15 EV. 400mm: -1.35 EV.                                                             | 1.0-1.5 EV               |
| vignettingStopped   | 1.5   | 400mm f/8: -0.51 EV.                                                                          | 0.5-1.0 EV               |
| bokeh               | 1.0   | LensTip: "quite nice for a zoom, rim on edge." Dustin Abbott: "average."                      | "average"                |
| flareResistance     | 1.0   | "Flares, ghosting, and contrast decrease are easy to spot."                                   | "noticeable"             |

### XF 200mm f/2.0 R LM OIS WR

Flagship super-tele prime.
Sources: ePHOTOzine (lab, trust 2), Dustin Abbott (field, trust 3),
official Fujifilm MTF chart (for astigmatism).
No LensTip or OpticalLimits review exists.

| Field               | Score | Source data                                                                                                              | Rubric rule                                |
| ------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------ |
| centerStopped       | 2.0   | ePHOTOzine: "excellent" centre f/2.8-f/8. Multiple: "nothing to correct."                                                | "excellent"                                |
| cornerStopped       | 2.0   | ePHOTOzine: "excellent" edges f/2.8-f/8. "Edge to edge sharpness even wide open."                                        | "excellent"                                |
| centerWideOpen      | 2.0   | Multiple: "incredibly sharp wide open."                                                                                  | "excellent"                                |
| astigmatism         | 2.0   | Official Fujifilm MTF chart: S and M lines very close together across the field.                                         | S/M convergence = negligible               |
| coma                | —     | MTF chart cannot isolate coma from astigmatism. Only point-source tests can.                                             | data integrity rule                        |
| sphericalAberration | 2.0   | Optical design: 1 Super ED + 2 ED elements targeting spherical aberration. No reviewer reported focus shift or fringing. | "negligible" (design + field confirmation) |
| longitudinalCA      | 2.0   | "Very well controlled", no fringing mentioned by any source. Super ED elements.                                          | "negligible"                               |
| lateralCA           | 2.0   | ePHOTOzine: "very well controlled centre and edge."                                                                      | "negligible"                               |
| distortion          | 2.0   | +0.14% pincushion. ePHOTOzine: "minimal."                                                                                | < 0.3%                                     |
| vignettingWideOpen  | 1.5   | ePHOTOzine: 0.5 stops wide open. Boundary value, conservative.                                                           | 0.5-1.0 EV                                 |
| vignettingStopped   | 2.0   | Negligible stopped down.                                                                                                 | < 0.5 EV                                   |
| bokeh               | 2.0   | "Best bokeh of any XF lens", "silky smooth", "close to perfection."                                                      | "excellent"                                |
| flareResistance     | 1.0   | "A bit of veiling with sun in/out of frame." Some ghosting stopped down.                                                 | "average"                                  |

Note: astigmatism scored from official manufacturer MTF chart (S/M line
convergence). Spherical aberration scored via optical construction
inference (Super ED + aspherical) confirmed by field reports.

---

## Samyang

### 8mm f/3.5 Aspherical IF MC Fish-eye

Full-frame fisheye. Distortion intentional, scored 0.0.
Sources: LensTip (lab, trust 3, Nikon D200 APS-C).
Sensor: Nikon D200, max ~38-39 lpmm (estimated).

| Field               | Score | Source data                                                                                                     | Rubric rule     |
| ------------------- | ----- | --------------------------------------------------------------------------------------------------------------- | --------------- |
| centerStopped       | 2.0   | Peak near sensor max stopped down.                                                                              | >= 90%          |
| cornerStopped       | 1.5   | "Very good side-of-the-frame image quality."                                                                    | 75-89%          |
| centerWideOpen      | 1.5   | ~34 lpmm at f/3.5 (87-89% of max). "Very much useful."                                                          | 75-89%          |
| cornerWideOpen      | 1.5   | Edge described as "very good" for a fisheye at f/3.5.                                                           | "very good"     |
| astigmatism         | 1.5   | 6.3%. "Not bothersome."                                                                                         | 5-10%           |
| coma                | 1.0   | Visible at f/3.5, marginal at f/5.6.                                                                            | "noticeable"    |
| sphericalAberration | 1.5   | Optical construction: aspherical elements + 0 SA complaints from 2+ reviewers. ADR-014 inference. Conservative. |                 |
| longitudinalCA      | —     | undefined — not tested (only lateral CA covered in this review)                                                 |                 |
| lateralCA           | 0.5   | ~0.16% at max aperture. "High level."                                                                           | 0.15-0.20%      |
| distortion          | 0.0   | Fisheye — intentional extreme barrel distortion.                                                                | > 4.0% (design) |
| vignettingWideOpen  | 1.5   | ~-0.6 EV at f/3.5. Low for a fisheye.                                                                           | 0.5-1.0 EV      |
| vignettingStopped   | —     | undefined — not tested (180° FOV prevents chart capture)                                                        |                 |
| bokeh               | —     | undefined — not applicable (fisheye, depth of field too large)                                                  |                 |
| flareResistance     | 1.5   | "Difficult to spot any ghosting or flares." Positively surprised.                                               | "very good"     |

### 8mm f/2.8 ED AS IF UMC Fisheye

Diagonal fisheye. Distortion is intentional (by design), scored 0.0.
Sources: LensTip (lab, trust 3, Samsung NX10 APS-C).
Sensor: Samsung NX10, max ~50 lpmm.

| Field               | Score | Source data                                                                                                     | Rubric rule        |
| ------------------- | ----- | --------------------------------------------------------------------------------------------------------------- | ------------------ |
| centerStopped       | 2.0   | >52 lpmm at f/4 (>100%). "Sensational image quality in frame centre."                                           | >= 90%             |
| cornerStopped       | 1.5   | ~43 lpmm (86%). PRO: "excellent image quality on edge."                                                         | 75-89%             |
| centerWideOpen      | 2.0   | ~50 lpmm at f/2.8 (100%). "Outstandingly sharp."                                                                | >= 90%             |
| cornerWideOpen      | 1.5   | ~43 lpmm at f/2.8 (86%). Sharp across frame from wide open.                                                     | 75-89%             |
| astigmatism         | 2.0   | 1.3%. "Simply an excellent result." PRO: "negligible astigmatism."                                              | < 5%               |
| coma                | 1.0   | "Not perfect but certainly can't call its level high."                                                          | "noticeable"       |
| sphericalAberration | 1.5   | Optical construction: aspherical elements + 0 SA complaints from 2+ reviewers. ADR-014 inference. Conservative. |                    |
| longitudinalCA      | 1.0   | "Not perfectly corrected, but level is not very high."                                                          | "moderate"         |
| lateralCA           | 1.0   | "Borderline between low and medium values."                                                                     | 0.09-0.14%         |
| distortion          | 0.0   | Fisheye — extreme barrel distortion is intentional by design.                                                   | > 4.0% (by design) |
| vignettingWideOpen  | 0.5   | ~1.7 EV at f/2.8. CON: "noticeable vignetting."                                                                 | 1.5-2.5 EV         |
| vignettingStopped   | —     | undefined — not tested (fisheye, vignetting measurement impractical)                                            |                    |
| bokeh               | —     | undefined — not applicable (fisheye, depth of field too large)                                                  |                    |
| flareResistance     | 1.0   | Issues with sun in frame but "positive" given fisheye design constraints.                                       | "average"          |

### 10mm f/2.8 ED AS NCS CS

Rectilinear ultra-wide APS-C. Not a fisheye — distortion scored normally.
Sources: LensTip (lab, trust 3, Canon 50D APS-C).
Sensor: Canon 50D, max 52-55 lpmm.

| Field              | Score | Source data                                                                     | Rubric rule  |
| ------------------ | ----- | ------------------------------------------------------------------------------- | ------------ |
| centerStopped      | 2.0   | 52 lpmm (97% of max). PRO: "sensational image quality in frame centre."         | >= 90%       |
| cornerStopped      | 1.0   | 36 lpmm at f/8 (67%). CON: "weak image quality on edge."                        | 60-74%       |
| centerWideOpen     | 2.0   | 50 lpmm at f/2.8 (93%).                                                         | >= 90%       |
| cornerWideOpen     | 0.0   | "Not useful" at f/2.8 and f/4. Below decency.                                   | < 50%        |
| astigmatism        | 1.5   | 8%. "Moderate astigmatism."                                                     | 5-10%        |
| coma               | 2.0   | "We don't have any reservations concerning the coma correction."                | "negligible" |
| lateralCA          | 1.0   | 0.10-0.12%. "Average."                                                          | 0.09-0.14%   |
| distortion         | 0.0   | -4.19% barrel. CON: "too high distortion."                                      | > 4.0%       |
| vignettingWideOpen | 0.5   | -1.95 EV at f/2.8. CON: "distinct vignetting."                                  | 1.5-2.5 EV   |
| vignettingStopped  | 2.0   | -0.38 EV at f/5.6.                                                              | < 0.5 EV     |
| flareResistance    | 0.5   | "Can hardly be called good." CON: "work against bright light should be better." | "poor"       |

### 12mm f/2.8 ED AS NCS Fish-eye

Full-frame fisheye. Distortion intentional, scored 0.0.
Sources: LensTip (lab, trust 3, Canon 5D III FF).
Sensor: Canon 5D III, max 44-47 lpmm. APS-C vignetting data available.

| Field              | Score | Source data                                                        | Rubric rule     |
| ------------------ | ----- | ------------------------------------------------------------------ | --------------- |
| centerStopped      | 2.0   | ~47 lpmm at f/4 (103%, sensor limited). PRO: "sensational centre." | >= 90%          |
| cornerStopped      | 1.0   | CON: "weak image quality on edge." FF edges weak.                  | "average"       |
| centerWideOpen     | 2.0   | 43 lpmm at f/2.8 (94%).                                            | >= 90%          |
| cornerWideOpen     | 0.5   | FF edges weak at f/2.8.                                            | "poor"          |
| astigmatism        | 1.5   | 6.6%. "A moderate value."                                          | 5-10%           |
| lateralCA          | 0.5   | "High" at f/2.8. CON: "too high level of lateral CA."              | "poor"          |
| distortion         | 0.0   | Fisheye — intentional (-18% APS-C, -35% FF).                       | > 4.0% (design) |
| vignettingWideOpen | 1.5   | APS-C: -0.64 EV. PRO: "negligible vignetting on APS-C/DX."         | 0.5-1.0 EV      |
| vignettingStopped  | 2.0   | APS-C: -0.19 EV at f/5.6.                                          | < 0.5 EV        |
| flareResistance    | 1.5   | PRO: "very good work against bright light."                        | "very good"     |

### 12mm f/2.0 NCS CS

Third-party ultra-wide prime. Popular astro lens.
Sources: LensTip (lab, trust 3).
Sensor: X-Trans I (X-E1), max ~66 lpmm.

| Field               | Score | Source data                                                                                                                                                                                                            | Rubric rule            |
| ------------------- | ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| centerStopped       | 2.0   | ~74 lpmm at f/2.8-4.0 center (112% of max).                                                                                                                                                                            | >= 90%                 |
| cornerStopped       | 1.0   | Summary PRO: "acceptable image quality on the edge of the frame." Edges "good" at f/5.6. "Significant difference from centre" (CON).                                                                                   | PRO: "acceptable"      |
| centerWideOpen      | 2.0   | ~60 lpmm at f/2 center (91% of max).                                                                                                                                                                                   | >= 90%                 |
| astigmatism         | 2.0   | 3.7%. "Corrected in a flawless way."                                                                                                                                                                                   | < 5%                   |
| coma                | 1.5   | LensTip: "visible but intensity isn't high", "no serious reservations." Lonely Speck: "very low comatic aberration" at f/2. Dustin Abbott: "really well controlled." Consensus across sources: minor, well-controlled. | "minor" (multi-source) |
| sphericalAberration | 2.0   | "No focus shift, no problems with correction."                                                                                                                                                                         | "negligible"           |
| longitudinalCA      | 0.5   | "didn't manage to deal with that problem well", "photo shows it clearly."                                                                                                                                              | "poor"                 |
| lateralCA           | 0.5   | ~0.15%. "Noticeable factor deteriorating edge image quality."                                                                                                                                                          | 0.15-0.20%             |
| distortion          | 1.0   | -1.88% barrel. Same RAW and JPEG (no in-camera correction).                                                                                                                                                            | 1.0-2.0%               |
| vignettingWideOpen  | 0.5   | -1.69 EV at f/2.                                                                                                                                                                                                       | 1.5-2.5 EV             |
| vignettingStopped   | 1.5   | -0.87 EV at f/4.                                                                                                                                                                                                       | 0.5-1.0 EV             |
| bokeh               | 1.5   | "Nice to look at, even light spread, no noticeable extremes."                                                                                                                                                          | "very good"            |
| flareResistance     | 0.5   | "A lot of problems against bright light", deteriorates stopped down.                                                                                                                                                   | "poor"                 |

### 14mm f/2.8 ED AS IF UMC

Classic ultra-wide manual prime. FF design on APS-C crop.
Sources: LensTip (lab, trust 3, Nikon D3x FF), OpticalLimits (lab, trust 3, Canon 5D II FF),
Dustin Abbott (field, trust 3). Phillip Reeve partial (blocked site).
FF lens — resolution qualitative descriptions used; corners benefit from APS-C crop.

| Field               | Score | Source data                                                                                                     | Rubric rule       |
| ------------------- | ----- | --------------------------------------------------------------------------------------------------------------- | ----------------- |
| centerStopped       | 2.0   | LensTip: 46-47 lpmm = ~100% of D3x max. All 4 sources: excellent.                                               | >= 90%            |
| cornerStopped       | 1.5   | LensTip: ~40 lpmm on APS-C edges (~85%). OL/DA both 1.5.                                                        | 75-89%            |
| centerWideOpen      | 2.0   | LensTip: 44 lpmm = ~94%. DA: "resolves more detail than any wide angle."                                        | >= 90%            |
| cornerWideOpen      | 1.0   | LensTip: "decency level" on FF (0.5), APS-C crop improves. OL: 1.0.                                             | "average" (APS-C) |
| astigmatism         | 2.0   | LensTip: 1%. "A standing ovation!"                                                                              | < 5%              |
| coma                | 1.5   | LensTip: "well-corrected", "visible but far from bothersome." DA: 2.0. LensTip primary.                         | "low"             |
| sphericalAberration | 1.5   | Optical construction: aspherical elements + 0 SA complaints from 2+ reviewers. ADR-014 inference. Conservative. |                   |
| longitudinalCA      | —     | undefined — not tested (only lateral CA covered in this review)                                                 |                   |
| lateralCA           | 1.0   | LensTip: 0.08-0.13% on APS-C crop area.                                                                         | 0.09-0.14%        |
| distortion          | 0.0   | All sources: 5-7% barrel with moustache pattern. Universal 0.0.                                                 | > 4.0%            |
| vignettingWideOpen  | 0.5   | LensTip: -2.31 EV FF. OL: >3 EV. APS-C less but still heavy.                                                    | 1.5-2.5 EV        |
| vignettingStopped   | 1.5   | LensTip: ~0.8-1.0 EV at f/5.6. DA: 1.5.                                                                         | 0.5-1.0 EV        |
| bokeh               | 1.0   | OL: "very decent" (1.5). DA: "fairly decent" (1.0). Conservative.                                               | "average"         |
| flareResistance     | 1.0   | LensTip: "moderate" improvement. Contested: DA says excellent, OL says problematic. LensTip primary.            | "average"         |

### 16mm f/2.0 ED AS UMC CS

APS-C wide prime. Tested directly on Nikon D7000.
Sources: LensTip (lab, trust 3, Nikon D7000 APS-C).
Sensor: Nikon D7000, max 55-58 lpmm.

| Field               | Score | Source data                                                                   | Rubric rule      |
| ------------------- | ----- | ----------------------------------------------------------------------------- | ---------------- |
| centerStopped       | 2.0   | 58 lpmm at f/4 (100% of max). PRO: "excellent image quality in frame centre." | >= 90%           |
| cornerStopped       | 1.5   | Edge "good to very good" from f/2.8. ~50 lpmm = ~86%.                         | 75-89%           |
| centerWideOpen      | 1.5   | ~50 lpmm at f/2 (86% of max).                                                 | 75-89%           |
| cornerWideOpen      | 0.5   | Edge "approaching decency level" at f/2.                                      | "poor"           |
| astigmatism         | 2.0   | 3%. PRO: "negligible astigmatism."                                            | < 5%             |
| coma                | 1.0   | "Not corrected in a perfect way" but not severe.                              | "noticeable"     |
| sphericalAberration | 1.5   | "Corrected in a proper way." No focus shift. PRO: "good SA correction."       | "well corrected" |
| longitudinalCA      | 1.5   | PRO: "slight chromatic aberration — both lateral and longitudinal."           | "low"            |
| lateralCA           | 1.5   | 0.060-0.065%. PRO: "slight CA."                                               | 0.04-0.08%       |
| distortion          | 0.5   | -2.53% barrel.                                                                | 2.0-4.0%         |
| vignettingWideOpen  | 0.5   | -1.58 EV at f/2. CON: "distinct vignetting at maximum aperture."              | 1.5-2.5 EV       |
| vignettingStopped   | 2.0   | -0.47 EV at f/4.                                                              | < 0.5 EV         |
| flareResistance     | 0.5   | CON: "weak performance against bright light."                                 | "poor"           |

### 21mm f/1.4 ED AS UMC CS

APS-C fast wide prime. Tested directly on Fuji X-E1.
Sources: LensTip (lab, trust 3, X-E1), Dustin Abbott (field, trust 3, X-T1).
Sensor: X-Trans I (X-E1), max ~76 lpmm.

| Field               | Score | Source data                                                                               | Rubric rule  |
| ------------------- | ----- | ----------------------------------------------------------------------------------------- | ------------ |
| centerStopped       | 2.0   | ~77 lpmm at f/4 (101% of max). "Record-breaking values."                                  | >= 90%       |
| cornerStopped       | 1.5   | "From f/5.6 the performance on both sides becomes similarly high."                        | "very good"  |
| centerWideOpen      | 1.0   | "Can certainly be called decent" at f/1.4. Above decency but not impressive.              | "average"    |
| cornerWideOpen      | 0.5   | "Near maximum relative aperture the MTFs are weak." Summary CON: "too weak edge."         | "poor"       |
| astigmatism         | 1.0   | ~15% average. Escalates to 25% at f/2.0.                                                  | 10-18%       |
| coma                | 1.5   | "Not bad at all... visible both by f/1.4 and f/2.0 but deformations not very pronounced." | "low"        |
| sphericalAberration | 2.0   | "Imperceptible spherical aberration." No focus shift.                                     | "negligible" |
| longitudinalCA      | 1.0   | "At maximum aperture seems to be a bit bothersome, level can be described as medium."     | "moderate"   |
| lateralCA           | 1.5   | 0.05-0.06%. "Low lateral chromatic aberration."                                           | 0.04-0.08%   |
| distortion          | 1.5   | -0.57% barrel. "Low and completely praiseworthy."                                         | 0.3-1.0%     |
| vignettingWideOpen  | 0.5   | -2.00 EV RAW at f/1.4. "Significantly high."                                              | 1.5-2.5 EV   |
| vignettingStopped   | 1.5   | -0.87 EV at f/2.8, -0.83 EV at f/4-5.6.                                                   | 0.5-1.0 EV   |
| bokeh               | 1.0   | "Defocused light circles look sensibly well" BUT "distinct onion ring bokeh."             | "average"    |
| flareResistance     | 2.0   | "Excellent performance against bright light." "Mastered to perfection."                   | "excellent"  |

### Tilt/Shift 24mm f/3.5 ED AS UMC

Budget tilt-shift. FF design. Scored in normal (non-shifted) mode.
Sources: LensTip (lab, trust 3, Canon 1Ds III FF), Dustin Abbott (field, trust 3).
Sensor: Canon 1Ds III, max 44-46 lpmm.

| Field               | Score | Source data                                                                                                         | Rubric rule  |
| ------------------- | ----- | ------------------------------------------------------------------------------------------------------------------- | ------------ |
| centerStopped       | 2.0   | "Beyond reproach" at f/5.6-8. PRO: "very good image quality in frame centre."                                       | "excellent"  |
| cornerStopped       | 1.5   | PRO: "good image quality on edge." APS-C: "very good and fully useful."                                             | "very good"  |
| centerWideOpen      | 1.5   | "Fully useful" at f/3.5. PRO: "very good centre."                                                                   | "very good"  |
| cornerWideOpen      | 1.5   | APS-C edge "very good and fully useful across all apertures."                                                       | "very good"  |
| astigmatism         | 1.5   | <8%. "Borderline between low and medium levels."                                                                    | 5-10%        |
| coma                | 1.5   | PRO: "slight coma." "Almost exactly the same as centre" on APS-C.                                                   | "low"        |
| sphericalAberration | 1.5   | Optical construction: 2 aspherical elements + 0 SA complaints from LensTip and DA. ADR-014 inference. Conservative. |              |
| longitudinalCA      | 2.0   | "Difficult to notice even the slightest colouring." PRO: "excellent CA control."                                    | "negligible" |
| lateralCA           | 2.0   | PRO: "excellent control of CA." "Practically imperceptible" in normal mode.                                         | < 0.04%      |
| distortion          | 1.5   | APS-C: -0.59%. (FF: -1.98%). Using APS-C value.                                                                     | 0.3-1.0%     |
| vignettingWideOpen  | 1.5   | -0.83 EV at f/3.5 (normal mode). PRO: "low vignetting in normal working mode."                                      | 0.5-1.0 EV   |
| vignettingStopped   | 2.0   | -0.40 EV at f/8.                                                                                                    | < 0.5 EV     |
| flareResistance     | 0.5   | CON: "weak work against bright light."                                                                              | "poor"       |

### 35mm f/1.2 ED AS UMC CS

Fast APS-C prime. Tested directly on Fujifilm X-T2.
Sources: LensTip (lab, trust 3, X-T2).
Sensor: X-Trans III (X-T2), max ~80 lpmm.

| Field               | Score | Source data                                                                    | Rubric rule  |
| ------------------- | ----- | ------------------------------------------------------------------------------ | ------------ |
| centerStopped       | 2.0   | ~75+ lpmm at f/4 (94% of max). PRO: "excellent image quality in frame centre." | >= 90%       |
| cornerStopped       | 1.5   | PRO: "good image quality on edge from f/2.0 aperture."                         | "very good"  |
| centerWideOpen      | 1.0   | SA softens center at f/1.2. Center peaks at f/4, wide open estimated 60-74%.   | 60-74%       |
| cornerWideOpen      | 0.5   | CON: "weak image quality on edge near maximum aperture."                       | "poor"       |
| astigmatism         | 1.0   | 17.6%. CON: "distinct astigmatism."                                            | 10-18%       |
| coma                | 1.0   | "Medium" level deformations. Stars "deformed in frame corners."                | "noticeable" |
| sphericalAberration | 0.5   | "Distinct differences." Focus shifts when stopping down. CON: "noticeable SA." | "poor"       |
| longitudinalCA      | 1.5   | "Slight tint, completely acceptable." PRO: "low longitudinal CA."              | "low"        |
| lateralCA           | 2.0   | ~0.02%. PRO: "negligible lateral CA." "Corrected in a perfect way."            | < 0.04%      |
| distortion          | 2.0   | -0.21% RAW. PRO: "practically zero distortion."                                | < 0.3%       |
| vignettingWideOpen  | 0.5   | -1.86 EV at f/1.2. CON: "huge vignetting."                                     | 1.5-2.5 EV   |
| vignettingStopped   | 1.5   | -0.67 EV at f/2.8.                                                             | 0.5-1.0 EV   |
| bokeh               | 1.0   | "Distinct concentric circles" (onion rings). "Hardly perfect."                 | "average"    |
| flareResistance     | 2.0   | "Praised for performance against bright light." Artifacts "small and few."     | "excellent"  |

### 35mm f/1.4 AS UMC

Fast standard prime. FF design on APS-C crop.
Sources: LensTip (lab, trust 3, Nikon D3x FF), OpticalLimits (lab, trust 3, Canon 5D II FF).
FF lens — qualitative descriptions used for resolution.

| Field               | Score | Source data                                                                                                     | Rubric rule       |
| ------------------- | ----- | --------------------------------------------------------------------------------------------------------------- | ----------------- |
| centerStopped       | 2.0   | LensTip: "very good, even splendid quality" at f/4-5.6. OL: "outstanding" at f/4-8.                             | "excellent"       |
| cornerStopped       | 1.5   | LensTip: "sharp images even on FF edge" from f/2.2. OL: "excellent outer zones." APS-C better.                  | "very good"       |
| centerWideOpen      | 1.0   | LensTip: ~57% of D3x max. OL: "very good at f/1.4" with "slightly reduced contrast."                            | "average"         |
| cornerWideOpen      | 1.0   | LensTip: "good or even very good" on FF edges. APS-C crop uses mid-field.                                       | "average" (APS-C) |
| astigmatism         | 2.0   | LensTip: 2.5%. "A splendid result."                                                                             | < 5%              |
| coma                | 1.0   | LensTip: "visible, although not very distinct" on APS-C, "pronounced" on FF corners.                            | "noticeable"      |
| sphericalAberration | 1.5   | Optical construction: aspherical elements + 0 SA complaints from 2+ reviewers. ADR-014 inference. Conservative. |                   |
| longitudinalCA      | 0.5   | LensTip: "huge problem." OL: "purple halos" persist to f/2.8. Both agree.                                       | "poor"            |
| lateralCA           | 2.0   | LensTip: "always low, never reaching medium level." OL: <0.6px.                                                 | < 0.04%           |
| distortion          | 1.0   | LensTip: -1.58% FF barrel. OL: ~1.6%.                                                                           | 1.0-2.0%          |
| vignettingWideOpen  | 0.5   | LensTip: -1.90 EV FF. OL: >2.2 EV.                                                                              | 1.5-2.5 EV        |
| vignettingStopped   | 1.5   | LensTip: ~0.6 EV by f/2.8. "Problem becomes insignificant."                                                     | 0.5-1.0 EV        |
| bokeh               | 1.0   | OL: "rather busy", "slightly nervous inner zone." Not assessed by LensTip.                                      | "average"         |
| flareResistance     | 1.5   | LensTip: "above average", "not perfect but not bad either."                                                     | "very good"       |

### 50mm f/1.2 AS UMC CS

Fast APS-C portrait prime. No trust-3 lab data exists.
Sources: Dustin Abbott (field, trust 3, Canon EOS M3), ePHOTOzine (lab, trust 2, Sony A6000),
What Digital Camera (lab, trust 2), Photography Blog (lab, trust 2, Sony A6000).
Trust-2 aggregation applied for centerStopped, cornerStopped, vignettingWideOpen.

| Field               | Score | Source data                                                                                                                                                                                                                                                                | Rubric rule                  |
| ------------------- | ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| centerStopped       | 2.0   | ePHOTOzine: "excellent f/2.8-f/8." Photography Blog: "outstanding f/2-f/8." (2x trust-2 aggregate)                                                                                                                                                                         | "excellent" (agg)            |
| cornerStopped       | 1.5   | ePHOTOzine: "edges impressively close to central." Photography Blog: "best f/4-f/8." (2x trust-2)                                                                                                                                                                          | "very good" (agg)            |
| centerWideOpen      | 1.0   | DA: "surprisingly strong at f/1.2" but "not sky-high", "bit more haze due to CA."                                                                                                                                                                                          | "average"                    |
| cornerWideOpen      | 1.0   | AP: "at f/1.2 corner sharpness virtually identical to centre" (both soft). WDC agrees. (2x trust-2)                                                                                                                                                                        | "average" (agg)              |
| astigmatism         | 2.0   | Official MTF chart: S/M lines nearly overlapping throughout frame. Gap < 0.03 everywhere.                                                                                                                                                                                  | MTF fallback                 |
| coma                | 1.0   | Community consensus (3 sources, all CS version): Alik Griffin "very well controlled", DPReview tradesmith45 "slight coma in corners" (tracked astro on Fuji X), DPReview user 2 chose Samyang over XF56 for less coma (Cygnus field on X-T100). Capped at 1.0 per ADR-014. | "noticeable" (consensus cap) |
| sphericalAberration | 1.0   | DA: "haze at f/1.2, improves by f/2." AP: "improves considerably f/2-f/2.8." No focus shift reported. Conservative.                                                                                                                                                        | "noticeable" (conservative)  |
| longitudinalCA      | 1.0   | DA: "isn't too bad, bit of purple/green fringing." "Marked improvement by f/2."                                                                                                                                                                                            | "moderate"                   |
| lateralCA           | 1.5   | DA: "well controlled", "pixel width quite small." ePHOTOzine: "controlled very well." Consistent.                                                                                                                                                                          | "low"                        |
| distortion          | 2.0   | DA: "minor pincushion, minimal." ePHOTOzine Imatest: -0.156%. WDC: SMIA TV = -0.0%.                                                                                                                                                                                        | < 0.3%                       |
| vignettingWideOpen  | 1.5   | WDC: ~0.7 EV at f/1.2. Photography Blog: "very noticeable" but clears by f/5.6. (2x trust-2)                                                                                                                                                                               | 0.5-1.0 EV (agg)             |
| vignettingStopped   | 2.0   | AP: 0.3 EV at f/2, "no issue f/2.8-f/16." WDC: same. (2x trust-2 aggregate)                                                                                                                                                                                                | < 0.5 EV (agg)               |
| bokeh               | 1.0   | DA: "onion bokeh" in highlights, "nice real-world bokeh." Conservative per lab-authority rule.                                                                                                                                                                             | "average"                    |
| flareResistance     | 0.5   | DA: "fairly pronounced ghosting", "strongly colored", "difficult to remove in post."                                                                                                                                                                                       | "poor"                       |

### 50mm f/1.4 AS UMC

Budget fast normal prime. FF design on APS-C crop.
Sources: LensTip (lab, trust 3, Canon 5D III FF + Canon 50D APS-C).
APS-C distortion and coma values used where available.

| Field               | Score | Source data                                                                              | Rubric rule      |
| ------------------- | ----- | ---------------------------------------------------------------------------------------- | ---------------- |
| centerStopped       | 2.0   | ~44 lpmm at f/4 (94% of max). PRO: "very good image quality in frame centre."            | >= 90%           |
| cornerStopped       | 1.0   | "Edge becomes completely useful around f/2.8." Qualitative.                              | "average"        |
| centerWideOpen      | 0.5   | "Notably under the decency level" at f/1.4 (<30 lpmm). CON: "could be better."           | 50-59%           |
| cornerWideOpen      | 0.5   | "Full-frame edges are poor until f/2.8." APS-C slightly better.                          | "poor"           |
| astigmatism         | 2.0   | 3.8%. "A low value." PRO: "low astigmatism."                                             | < 5%             |
| coma                | 1.5   | APS-C: "corrects coma very well." PRO: "slight coma in corners of APS-C/DX."             | "low" (APS-C)    |
| sphericalAberration | 0.5   | "A very distinct ring — darker in front, lighter behind." Stops being bothersome at f/2. | "poor"           |
| lateralCA           | 2.0   | "Almost no problems whatsoever." PRO: "sensibly corrected chromatic aberration."         | < 0.04%          |
| distortion          | 1.5   | APS-C: -0.87% pincushion. (FF: -2.11%). Using APS-C value.                               | 0.3-1.0% (APS-C) |
| vignettingWideOpen  | 0.5   | FF: -1.94 EV at f/1.4. CON: "noticeable vignetting."                                     | 1.5-2.5 EV       |
| vignettingStopped   | 1.5   | FF: -0.69 EV at f/2.8. Improves to -0.33 EV at f/4.                                      | 0.5-1.0 EV       |
| bokeh               | 0.5   | "Onion ring bokeh." Does not look "very well."                                           | "poor"           |
| flareResistance     | 0.0   | "Flares clearly visible." CON: "unacceptable performance against bright light."          | "very poor"      |

### 85mm f/1.4 AS IF UMC

Portrait prime. FF design on APS-C crop.
Sources: LensTip (lab, trust 3, Nikon D3x + D200), OpticalLimits (lab, trust 3, Canon 5D II).
FF lens — qualitative descriptions used for resolution.

| Field               | Score | Source data                                                                                                     | Rubric rule  |
| ------------------- | ----- | --------------------------------------------------------------------------------------------------------------- | ------------ |
| centerStopped       | 1.5   | LensTip: "under 40 lpmm" (~85% D3x). "Rather low maximum." OL: "excellent (just)" at f/5.6.                     | "very good"  |
| cornerStopped       | 1.0   | LensTip: "30 lpmm at FF edges" (64%). APS-C mid-field better. OL: "very good" at f/5.6.                         | "average"    |
| centerWideOpen      | 1.0   | LensTip: "slightly exceeds 30 lpmm" (64%). OL: "only very good (just)."                                         | "average"    |
| cornerWideOpen      | 0.5   | Both sources: "soft" at f/1.4 corners.                                                                          | "poor"       |
| astigmatism         | 1.0   | LensTip: 10.4%.                                                                                                 | 10-18%       |
| coma                | 1.0   | LensTip: "doesn't cause problems on DX" but noticeable on FF.                                                   | "noticeable" |
| sphericalAberration | 1.5   | Optical construction: aspherical elements + 0 SA complaints from 2+ reviewers. ADR-014 inference. Conservative. |              |
| longitudinalCA      | 0.5   | Both sources: visible purple/green fringing f/1.4-f/2.8. OL: "starts to fade from f/4."                         | "poor"       |
| lateralCA           | 2.0   | LensTip: "minimal, goes unnoticed." OL: ~0.6px, "not field relevant."                                           | < 0.04%      |
| distortion          | 1.5   | LensTip: -0.33% FF. OL: 0.4% barrel. Borderline. Conservative.                                                  | 0.3-1.0%     |
| vignettingWideOpen  | 1.0   | LensTip: -1.39 EV FF. OL: 1.8 EV. Using LensTip primary.                                                        | 1.0-1.5 EV   |
| vignettingStopped   | 2.0   | LensTip: ~0.4 EV at f/2.8. OL: "basically gone from f/2.8."                                                     | < 0.5 EV     |
| bokeh               | 1.5   | Both sources: "impressive"/"super smooth" bokeh quality.                                                        | "very good"  |
| flareResistance     | 0.5   | LensTip: "must give way to rivals." Ghosting "hard to ignore."                                                  | "poor"       |

### 100mm f/2.8 ED UMC Macro

True macro (1:1 magnification). FF design, APS-C vignetting data available.
Sources: LensTip (lab, trust 3, Canon 5D III FF + Canon 50D APS-C).
Sensor: Canon 5D III, max ~44-47 lpmm. APS-C vignetting used where available.

| Field               | Score | Source data                                                                    | Rubric rule      |
| ------------------- | ----- | ------------------------------------------------------------------------------ | ---------------- |
| centerStopped       | 2.0   | "Above 45 lpmm" (95.7% of max). PRO: "sensational resolution in frame centre." | >= 90%           |
| cornerStopped       | 1.5   | PRO: "good image quality on edge of APS-C/DX."                                 | "very good"      |
| centerWideOpen      | 1.5   | "Over 35 lpmm... very good, excellent even" at f/2.8.                          | "very good"      |
| cornerWideOpen      | 0.5   | "Hardly sharp" at f/2.8. CON: "edge near max aperture worse than rivals."      | "poor"           |
| astigmatism         | 2.0   | 4.1%. PRO: "low astigmatism."                                                  | < 5%             |
| coma                | 1.0   | "No reasons to complain but hardly perfect." PRO: "moderate coma."             | "noticeable"     |
| sphericalAberration | 2.0   | "No problems whatsoever." PRO: "lack of SA problems."                          | "negligible"     |
| longitudinalCA      | 2.0   | "No problems whatsoever." PRO: "imperceptible longitudinal CA."                | "negligible"     |
| lateralCA           | 1.5   | ~0.05%. "Slight." PRO: "low lateral CA."                                       | 0.04-0.08%       |
| distortion          | 2.0   | APS-C: +0.22%. "Negligible." PRO: "practically zero distortion."               | < 0.3%           |
| vignettingWideOpen  | 2.0   | APS-C: -0.48 EV at f/2.8. PRO: "low vignetting on APS-C/DX."                   | < 0.5 EV (APS-C) |
| vignettingStopped   | 2.0   | APS-C: -0.12 EV at f/4. Negligible.                                            | < 0.5 EV (APS-C) |
| bokeh               | 1.5   | "Pleasing to the eye." PRO: "nice appearance of blurry areas."                 | "very good"      |
| flareResistance     | 1.0   | "Averagely good. Far from perfection."                                         | "average"        |

### 135mm f/2 ED UMC

Legendary fast tele prime. FF design on APS-C crop. APO-quality CA correction.
Sources: Dustin Abbott (field, trust 3, Canon 6D), Phillip Reeve (field, trust 3, Sony A7II).
Both sources confirm exceptional optical quality.

| Field               | Score | Source data                                                                                                                                                                                                                                                                                                                   | Rubric rule       |
| ------------------- | ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| centerStopped       | 2.0   | DA: "stunningly good resolution." PR: "ridiculously sharp from f/2."                                                                                                                                                                                                                                                          | "excellent"       |
| cornerStopped       | 2.0   | PR: "ridiculously sharp across the frame from f/2 on." No difference center/corner.                                                                                                                                                                                                                                           | "excellent"       |
| centerWideOpen      | 2.0   | DA: "incredibly sharp and full of rich contrast wide open." PR: sharp from f/2, no improvement.                                                                                                                                                                                                                               | "excellent"       |
| cornerWideOpen      | 1.5   | DA: "texture detail from corner to corner is very good." PR: "corners very sharp wide open."                                                                                                                                                                                                                                  | "very good"       |
| astigmatism         | 2.0   | Official MTF chart: S/M lines nearly overlapping at all positions. Max divergence ~4% at edge.                                                                                                                                                                                                                                | MTF fallback      |
| coma                | 1.5   | Community consensus (5+ with measured data): Cloudy Nights "tightest stars in any astro optic" (FWHM 2.1px), AstroBackyard "pinpoint stars at f/2", CameraLabs "almost no coma, matched Zeiss APO", Galactic Hunter "coma hard to find", Astrojolo "almost invisible elongation." Per ADR-014 tiered cap: 5+ with data = 1.5. | "low" (consensus) |
| sphericalAberration | 2.0   | PR: "I didn't notice any focus shift." DA: "I didn't really notice any optical flaws."                                                                                                                                                                                                                                        | "negligible"      |
| lateralCA           | 2.0   | PR: "no lateral CA." "True APO-qualities." DA: "less CA than Canon 135L."                                                                                                                                                                                                                                                     | "negligible"      |
| longitudinalCA      | 2.0   | PR: "only negligible hint of longitudinal CA." "APO qualities."                                                                                                                                                                                                                                                               | "negligible"      |
| distortion          | 2.0   | PR: "virtually distortion-free", 0 to -1 in Lightroom.                                                                                                                                                                                                                                                                        | < 0.3%            |
| vignettingWideOpen  | 0.5   | PR: 1.67 EV at f/2. "Worth noting although typical for a fast FF lens."                                                                                                                                                                                                                                                       | 1.5-2.5 EV        |
| vignettingStopped   | 2.0   | PR: "virtually gone at f/8."                                                                                                                                                                                                                                                                                                  | < 0.5 EV          |
| bokeh               | 1.5   | DA: "beautifully creamy" (2.0). PR: "very good" close but "harsh at long distance" (1.0). Avg.                                                                                                                                                                                                                                | "very good"       |
| flareResistance     | 1.0   | DA: "better controlled than many" (1.5). PR: ghosting "can be disturbing", contrast OK. Avg 1.0.                                                                                                                                                                                                                              | "average"         |

### AF 12mm f/2.0

Modern AF ultra-wide. APS-C native (same optics across E/X mount).
Sources: OpticalLimits (lab, trust 3, Sony APS-C), Dustin Abbott (field, trust 3, Sony APS-C).
No astigmatism or spherical aberration data — nightscape not scorable.

| Field               | Score | Source data                                                                                                       | Rubric rule  |
| ------------------- | ----- | ----------------------------------------------------------------------------------------------------------------- | ------------ |
| centerStopped       | 2.0   | OL: "excellent center quality" at f/4-5.6. DA: "nice sharpness" at f/5.6-8.                                       | "excellent"  |
| cornerStopped       | 1.5   | OL: "very good corners/borders." DA: "corners never quite pin-sharp." OL lab primary.                             | "very good"  |
| centerWideOpen      | 1.5   | OL: "excellent" center at f/2. DA: "fairly good, not sky-high." OL lab primary.                                   | "very good"  |
| cornerWideOpen      | 1.0   | OL: "just Okay" at f/2. DA: "significant drop-off."                                                               | "average"    |
| astigmatism         | 0.5   | Official MTF chart: heavy S/M divergence. At APS-C edge (~10mm), ~30% split at 30 lp/mm.                          | MTF fallback |
| coma                | 1.5   | DA: "quite good, star points stay crisp and precise even towards edge." OL: not tested.                           | "low"        |
| sphericalAberration | 1.5   | Optical construction: 1 H-ASP + 1 ASP elements + 0 SA complaints from OL and DA. ADR-014 inference. Conservative. |              |
| longitudinalCA      | 1.0   | DA: "isn't too bad, a bit of purple/green fringing." OL: not tested.                                              | "moderate"   |
| lateralCA           | 1.0   | OL: "1.8px at corners" (~0.10-0.14%). DA: "much less, didn't find it."                                            | 0.09-0.14%   |
| distortion          | 1.0   | OL: 1.5% barrel. DA: ~1-1.5%. Both agree.                                                                         | 1.0-2.0%     |
| vignettingWideOpen  | 0.0   | OL: ">3 EV" RAW at f/2. DA: "right over two stops" (~2.1 EV). OL lab measurement.                                 | > 2.5 EV     |
| vignettingStopped   | 1.0   | OL: ">1 EV even at f/8." Persistent.                                                                              | 1.0-1.5 EV   |
| bokeh               | 0.5   | OL: "rather rough." DA: mixed — "quite nice" but "jittery transition zone."                                       | "poor"       |
| flareResistance     | 0.5   | OL: "somewhat worse than average." DA: "mostly quite good." OL lab primary.                                       | "poor"       |

---

## Sigma

### 10-18mm f/2.8 DC DN C

Compact ultra-wide zoom. Sources: Dustin Abbott (field, trust 3).
Astigmatism from official MTF chart (fallback). Backfilled.

| Field              | Score | Source data                                                                         | Rubric rule   |
| ------------------ | ----- | ----------------------------------------------------------------------------------- | ------------- |
| centerStopped      | 2.0   | Dustin Abbott: excellent center sharpness stopped down across zoom range.           | "excellent"   |
| cornerStopped      | 1.5   | Dustin Abbott: good edge performance, solid for an ultra-wide zoom.                 | "very good"   |
| centerWideOpen     | 1.5   | Dustin Abbott: sharp center at f/2.8, slight improvement on stopping down.          | "very good"   |
| cornerWideOpen     | 1.0   | Dustin Abbott: corners softer wide open, improve stopped down.                      | "average"     |
| astigmatism        | 1.5   | Official MTF chart: moderate S/M divergence at edges, tight through mid-frame.      | MTF fallback  |
| longitudinalCA     | 1.5   | Dustin Abbott: well controlled for an f/2.8 zoom.                                   | "low"         |
| lateralCA          | 2.0   | Dustin Abbott: negligible lateral CA.                                               | "negligible"  |
| distortion         | 0.5   | Dustin Abbott: significant barrel distortion at 10mm, requires software correction. | "significant" |
| vignettingWideOpen | 0.0   | Dustin Abbott: very heavy vignetting at 10mm f/2.8, pronounced light falloff.       | "very heavy"  |
| vignettingStopped  | 0.5   | Dustin Abbott: improves but still noticeable stopped down.                          | "significant" |
| bokeh              | 1.0   | Dustin Abbott: acceptable for a wide zoom, not a primary use case.                  | "average"     |
| flareResistance    | 1.5   | Dustin Abbott: good flare control with multi-coating.                               | "very good"   |

### 12mm f/1.4 DC DN C

Ultra-wide fast prime. Sources: Dustin Abbott (field, trust 3).
Astigmatism from official MTF chart (fallback). Backfilled.

| Field              | Score | Source data                                                                  | Rubric rule   |
| ------------------ | ----- | ---------------------------------------------------------------------------- | ------------- |
| centerStopped      | 1.5   | Dustin Abbott: good center sharpness, peaks around f/2.8.                    | "very good"   |
| cornerStopped      | 1.0   | Dustin Abbott: edges lag behind center, acceptable for ultra-wide.           | "average"     |
| centerWideOpen     | 1.5   | Dustin Abbott: sharp center at f/1.4, usable wide open.                      | "very good"   |
| cornerWideOpen     | 1.0   | Dustin Abbott: corners softer wide open but reasonable for 12mm f/1.4.       | "average"     |
| astigmatism        | 1.5   | Official MTF chart: near-overlap with slight divergence at extreme edge.     | MTF fallback  |
| longitudinalCA     | 1.5   | Dustin Abbott: well controlled longitudinal CA for an f/1.4 lens.            | "low"         |
| lateralCA          | 2.0   | Dustin Abbott: negligible lateral CA.                                        | "negligible"  |
| distortion         | 0.5   | Dustin Abbott: significant barrel distortion, relies on software correction. | "significant" |
| vignettingWideOpen | 0.5   | Dustin Abbott: noticeable vignetting at f/1.4, expected for fast ultra-wide. | "significant" |
| vignettingStopped  | 1.5   | Dustin Abbott: clears up well by f/2.8.                                      | "low"         |
| bokeh              | 1.0   | Dustin Abbott: acceptable bokeh, not a primary use case for 12mm.            | "average"     |
| flareResistance    | 2.0   | Dustin Abbott: excellent flare resistance, well-controlled ghosting.         | "excellent"   |

### 15mm f/1.4 DC DN C

Fast wide prime for astro/landscape. Sources: Dustin Abbott (field, trust 3).
Astigmatism from official MTF chart (fallback). Backfilled.

| Field              | Score | Source data                                                                           | Rubric rule   |
| ------------------ | ----- | ------------------------------------------------------------------------------------- | ------------- |
| centerStopped      | 1.5   | Dustin Abbott: very good center sharpness, peaks around f/2.8-4.                      | "very good"   |
| cornerStopped      | 1.0   | Dustin Abbott: edges weaker, typical for fast wide prime.                             | "average"     |
| centerWideOpen     | 1.5   | Dustin Abbott: sharp center at f/1.4, strong for astro use.                           | "very good"   |
| cornerWideOpen     | 0.5   | Dustin Abbott: notable corner softness wide open.                                     | "poor"        |
| astigmatism        | 2.0   | Dustin Abbott: well controlled. Official MTF chart confirms: near-overlap S/M lines.  | "excellent"   |
| coma               | 1.5   | Dustin Abbott: well-controlled coma, good star rendering for astro.                   | "low"         |
| longitudinalCA     | 0.5   | Dustin Abbott: noticeable purple/green fringing on high-contrast edges at f/1.4.      | "significant" |
| lateralCA          | 2.0   | Dustin Abbott: negligible lateral CA.                                                 | "negligible"  |
| distortion         | 0.0   | Dustin Abbott: very heavy barrel distortion, requires aggressive software correction. | > 4.0%        |
| vignettingWideOpen | 0.0   | Dustin Abbott: very heavy vignetting at f/1.4.                                        | "very heavy"  |
| vignettingStopped  | 1.0   | Dustin Abbott: improves but still moderate stopped down.                              | "moderate"    |
| bokeh              | 1.0   | Dustin Abbott: acceptable, some onion ring from aspherical elements.                  | "average"     |
| flareResistance    | 1.5   | Dustin Abbott: good flare control.                                                    | "very good"   |

### 16mm f/1.4 DC DN C

Fast wide prime. Sources: LensTip (lab, trust 3).
Sensor: X-Trans III (X-T2), max ~78 lpmm. Backfilled.

| Field               | Score | Source data                                                   | Rubric rule   |
| ------------------- | ----- | ------------------------------------------------------------- | ------------- |
| centerStopped       | 2.0   | LensTip: excellent center resolution at f/2.8-4.              | >= 90%        |
| cornerStopped       | 1.0   | LensTip: edges lag significantly behind center.               | 60-74%        |
| centerWideOpen      | 1.0   | LensTip: center at f/1.4 noticeably softer than stopped down. | 60-74%        |
| cornerWideOpen      | 0.5   | LensTip: soft corners wide open.                              | 50-59%        |
| astigmatism         | 1.0   | LensTip: moderate astigmatism.                                | 10-18%        |
| coma                | 0.5   | LensTip: significant coma at f/1.4, star points stretched.    | "significant" |
| sphericalAberration | 1.0   | LensTip: moderate spherical aberration, some focus shift.     | "moderate"    |
| longitudinalCA      | 0.5   | LensTip: noticeable longitudinal CA at f/1.4.                 | "significant" |
| lateralCA           | 1.5   | LensTip: low lateral CA.                                      | 0.04-0.08%    |
| distortion          | 0.5   | LensTip: significant barrel distortion.                       | 2.0-4.0%      |
| vignettingWideOpen  | 0.5   | LensTip: heavy vignetting at f/1.4.                           | 1.5-2.5 EV    |
| vignettingStopped   | 2.0   | LensTip: clears up very well stopped down.                    | < 0.5 EV      |
| bokeh               | 1.5   | LensTip: good bokeh quality, smooth rendering.                | "very good"   |

### 18-50mm f/2.8 DC DN C

Compact standard zoom. Sources: Dustin Abbott (field, trust 3).
Astigmatism from official MTF chart (fallback). Scored at mid-range. Backfilled.

| Field              | Score | Source data                                                                         | Rubric rule   |
| ------------------ | ----- | ----------------------------------------------------------------------------------- | ------------- |
| centerStopped      | 1.5   | Dustin Abbott: good center sharpness stopped down, not exceptional.                 | "very good"   |
| cornerStopped      | 1.0   | Dustin Abbott: corners lag behind center across zoom range.                         | "average"     |
| centerWideOpen     | 1.5   | Dustin Abbott: good center at f/2.8 across range.                                   | "very good"   |
| cornerWideOpen     | 0.5   | Dustin Abbott: soft corners wide open, especially at wider focal lengths.           | "poor"        |
| astigmatism        | 1.0   | Dustin Abbott: moderate. Official MTF chart shows heavy S/M divergence from early.  | "moderate"    |
| coma               | 1.0   | Dustin Abbott: moderate coma, acceptable for a zoom.                                | "moderate"    |
| longitudinalCA     | 1.5   | Dustin Abbott: well controlled for an f/2.8 zoom.                                   | "low"         |
| lateralCA          | 1.0   | Dustin Abbott: some lateral CA at frame edges.                                      | "moderate"    |
| distortion         | 0.5   | Dustin Abbott: noticeable barrel at 18mm, pincushion at 50mm. Relies on correction. | "significant" |
| vignettingWideOpen | 0.0   | Dustin Abbott: very heavy vignetting at f/2.8, especially at 18mm.                  | "very heavy"  |
| vignettingStopped  | 1.0   | Dustin Abbott: improves but still moderate.                                         | "moderate"    |
| bokeh              | 1.0   | Dustin Abbott: acceptable for a standard zoom, some nervousness in backgrounds.     | "average"     |
| flareResistance    | 1.5   | Dustin Abbott: good multi-coating, controlled flare.                                | "very good"   |

### 23mm f/1.4 DC DN C

Fast standard prime. Sources: LensTip (lab, trust 3). Backfilled.

| Field               | Score | Source data                                               | Rubric rule  |
| ------------------- | ----- | --------------------------------------------------------- | ------------ |
| centerStopped       | 2.0   | LensTip: excellent center resolution at f/2.8.            | >= 90%       |
| cornerStopped       | 1.5   | LensTip: good edge performance.                           | 75-89%       |
| centerWideOpen      | 1.5   | LensTip: good center at f/1.4, improves on stopping down. | 75-89%       |
| cornerWideOpen      | 1.0   | LensTip: edges softer wide open but usable.               | 60-74%       |
| astigmatism         | 2.0   | LensTip: low astigmatism.                                 | < 5%         |
| coma                | 1.0   | LensTip: noticeable coma at f/1.4, improves stopped down. | "noticeable" |
| sphericalAberration | 2.0   | LensTip: well corrected, negligible focus shift.          | "negligible" |
| longitudinalCA      | 2.0   | LensTip: very well corrected longitudinal CA.             | "negligible" |
| lateralCA           | 2.0   | LensTip: negligible lateral CA.                           | < 0.04%      |
| distortion          | 0.5   | LensTip: notable barrel distortion.                       | 2.0-4.0%     |
| vignettingWideOpen  | 0.5   | LensTip: heavy vignetting at f/1.4.                       | 1.5-2.5 EV   |
| vignettingStopped   | 1.5   | LensTip: clears up well by f/2.8.                         | 0.5-1.0 EV   |
| bokeh               | 1.5   | LensTip: good bokeh, smooth rendering.                    | "very good"  |
| flareResistance     | 2.0   | LensTip: excellent flare resistance.                      | "excellent"  |

### 30mm f/1.4 DC DN C

Fast normal prime. Sources: LensTip (lab, trust 3). Backfilled.

| Field               | Score | Source data                                                           | Rubric rule  |
| ------------------- | ----- | --------------------------------------------------------------------- | ------------ |
| centerStopped       | 2.0   | LensTip: excellent center resolution at f/2.8.                        | >= 90%       |
| cornerStopped       | 1.5   | LensTip: good edge performance.                                       | 75-89%       |
| centerWideOpen      | 1.0   | LensTip: center at f/1.4 softer, improves significantly stopped down. | 60-74%       |
| cornerWideOpen      | 0.5   | LensTip: soft corners wide open.                                      | 50-59%       |
| astigmatism         | 1.0   | LensTip: moderate astigmatism.                                        | 10-18%       |
| coma                | 2.0   | LensTip: negligible coma.                                             | "negligible" |
| sphericalAberration | 1.0   | LensTip: moderate spherical aberration.                               | "moderate"   |
| longitudinalCA      | 1.0   | LensTip: moderate longitudinal CA at f/1.4.                           | "moderate"   |
| lateralCA           | 1.0   | LensTip: moderate lateral CA.                                         | 0.09-0.14%   |
| distortion          | 1.0   | LensTip: moderate barrel distortion.                                  | 1.0-2.0%     |
| bokeh               | 1.5   | LensTip: good bokeh quality.                                          | "very good"  |
| flareResistance     | 1.0   | LensTip: average flare resistance.                                    | "average"    |

### 56mm f/1.4 DC DN C

Fast portrait prime. Sources: LensTip (lab, trust 3). Backfilled.

| Field               | Score | Source data                                                   | Rubric rule  |
| ------------------- | ----- | ------------------------------------------------------------- | ------------ |
| centerStopped       | 2.0   | LensTip: excellent center resolution at f/2.8.                | >= 90%       |
| cornerStopped       | 0.5   | LensTip: weak edge performance, significant drop from center. | 50-59%       |
| centerWideOpen      | 1.5   | LensTip: good center at f/1.4.                                | 75-89%       |
| cornerWideOpen      | 0.5   | LensTip: soft corners wide open.                              | 50-59%       |
| astigmatism         | 1.5   | LensTip: moderate-low astigmatism.                            | 5-10%        |
| coma                | 1.0   | LensTip: noticeable coma at f/1.4.                            | "noticeable" |
| sphericalAberration | 2.0   | LensTip: well corrected, no focus shift.                      | "negligible" |
| longitudinalCA      | 2.0   | LensTip: very well corrected.                                 | "negligible" |
| lateralCA           | 1.5   | LensTip: low lateral CA.                                      | 0.04-0.08%   |
| distortion          | 0.5   | LensTip: notable pincushion distortion.                       | 2.0-4.0%     |
| vignettingWideOpen  | 0.5   | LensTip: heavy vignetting at f/1.4.                           | 1.5-2.5 EV   |
| vignettingStopped   | 1.5   | LensTip: clears up well by f/2.8.                             | 0.5-1.0 EV   |
| bokeh               | 1.0   | LensTip: average bokeh, some outlining.                       | "average"    |

### 100-400mm f/5-6.3 DG DN OS C

Super-telephoto zoom. Sources: Dustin Abbott (field, trust 3).
Astigmatism from official MTF chart (fallback). Scored at mid-range. Backfilled.

| Field              | Score | Source data                                                               | Rubric rule  |
| ------------------ | ----- | ------------------------------------------------------------------------- | ------------ |
| centerStopped      | 1.5   | Dustin Abbott: good center sharpness, solid for a super-tele zoom.        | "very good"  |
| cornerStopped      | 1.5   | Dustin Abbott: surprisingly good edge performance for the class.          | "very good"  |
| centerWideOpen     | 1.5   | Dustin Abbott: good center at f/5-6.3, usable wide open.                  | "very good"  |
| cornerWideOpen     | 1.0   | Dustin Abbott: edges acceptable wide open.                                | "average"    |
| astigmatism        | 1.0   | Official MTF chart: moderate-to-heavy S/M divergence at edges.            | MTF fallback |
| longitudinalCA     | 2.0   | Dustin Abbott: very well corrected longitudinal CA.                       | "negligible" |
| lateralCA          | 2.0   | Dustin Abbott: negligible lateral CA.                                     | "negligible" |
| distortion         | 1.5   | Dustin Abbott: low distortion across zoom range.                          | 0.3-1.0%     |
| vignettingWideOpen | 1.0   | Dustin Abbott: moderate vignetting at max aperture.                       | 1.0-1.5 EV   |
| vignettingStopped  | 1.5   | Dustin Abbott: clears up well stopped down.                               | 0.5-1.0 EV   |
| bokeh              | 1.5   | Dustin Abbott: good bokeh for a tele zoom, smooth rendering.              | "very good"  |
| flareResistance    | 1.0   | Dustin Abbott: average flare resistance, some ghosting with sun in frame. | "average"    |

### 17-40mm f/1.8 DC Art

Fast standard zoom. Sources: LensTip (lab, trust 3), Dustin Abbott (field, trust 3).
Tested on Sony A7R II (42.4 MP). Scored at 28mm mid-range.

| Field               | Score | Source data                                                                                                             | Rubric rule          |
| ------------------- | ----- | ----------------------------------------------------------------------------------------------------------------------- | -------------------- |
| centerStopped       | 2.0   | LensTip: 89.6 lpmm at 28mm f/2.8. Summary PRO: "sensational image quality in the frame centre."                         | >= 90%               |
| cornerStopped       | 1.5   | LensTip: ~60 lpmm edges. Summary PRO: "very good image quality on the edge of the frame."                               | 75-89%               |
| centerWideOpen      | 2.0   | LensTip: "Sharpness at f/1.8 is excellent, no matter what focal length." Stopping down causes no improvement at center. | >= 90%               |
| cornerWideOpen      | 1.0   | Dustin Abbott: "fairly steep drop-off in the corners." LensTip: edges weaker at extremes but decent at 28mm.            | "average"            |
| astigmatism         | 2.0   | LensTip: 5.4%. "Borderline between low and very low values."                                                            | < 5% (borderline)    |
| coma                | 1.0   | LensTip: significant at 17mm with "wings", "very well" corrected at 28-40mm. Doesn't fully disappear at f/3.5.          | "noticeable" at wide |
| sphericalAberration | 1.5   | LensTip: no focus shift. Slight undercorrection visible in bokeh disc rim shift. Deliberate for bokeh aesthetics.       | "well corrected"     |
| longitudinalCA      | 1.0   | LensTip summary PRO: "moderate longitudinal chromatic aberration." Dustin Abbott: "surprised by how much fringing."     | "moderate"           |
| lateralCA           | 2.0   | LensTip: 0.02% at 28mm. Summary PRO: "sensible correction of lateral chromatic aberration."                             | < 0.04%              |
| distortion          | 1.0   | LensTip RAW: +1.52% pincushion at 28mm. (-5.82% barrel at 17mm, +3.03% pincushion at 40mm.) Summary CON.                | 1.0-2.0%             |
| vignettingWideOpen  | 0.5   | LensTip summary CON: "significant vignetting." Dustin Abbott: +38 correction at 17mm f/1.8. f/1.8 zoom = heavy falloff. | "significant"        |
| vignettingStopped   | 1.0   | Summary still flags vignetting as CON even stopped down. Improves but doesn't clear fully.                              | "moderate"           |
| bokeh               | 1.0   | LensTip: "look well for a zoom", "slight onion ring bokeh" (4 aspherical elements). Summary PRO: "sensible appearance." | "average"            |
| flareResistance     | 1.5   | LensTip summary PRO: "sensible performance against bright light." "Quite well" despite complex 17-element design.       | "very good"          |

---

## Venus Laowa

### Argus 33mm f/0.95 CF APO

Ultra-fast APS-C prime with APO designation. Sources: LensTip (lab, trust 3, Nikon Z7 DX crop),
OpticalLimits (lab, trust 3, Sony APS-C), Phillip Reeve (field, trust 3, Sony APS-C).
Sensor: Nikon Z7 DX crop, max ~85 lpmm, decency ~41-43 lpmm.

| Field               | Score | Source data                                                                                    | Rubric rule   |
| ------------------- | ----- | ---------------------------------------------------------------------------------------------- | ------------- |
| centerStopped       | 2.0   | LensTip: 85.6 lpmm at f/2.8 (record). 85.6/85 = ~100%.                                         | >= 90%        |
| cornerStopped       | 1.0   | LensTip: >60 lpmm at f/5.6. 60/85 = ~70%.                                                      | 60-74%        |
| centerWideOpen      | 1.0   | LensTip: "not the best" at f/0.95. OL: "pretty impressive." Conservative.                      | conservative  |
| cornerWideOpen      | 0.5   | LensTip: "weak quality" at f/0.95. OL: "not terrible."                                         | ~50%          |
| astigmatism         | 0.5   | LensTip: 22.5%. Summary: "noticeable astigmatism."                                             | 18-25%        |
| lateralCA           | 2.0   | LensTip: 0.03-0.04%. OL: ~0.5px. All sources agree: very low.                                  | < 0.04%       |
| longitudinalCA      | 1.0   | LensTip: "acceptable" correction. Summary: not listed as pro or con.                           | "acceptable"  |
| distortion          | 1.0   | LensTip: -1.25% pincushion. Summary: "moderate distortion."                                    | 1.0-2.0%      |
| vignettingWideOpen  | 0.5   | LensTip: -2.31 EV at f/0.95. OL: >2 EV. Phillipreeve: 2.6 EV.                                  | 1.5-2.5 EV    |
| vignettingStopped   | 2.0   | LensTip: -0.40 EV at f/5.6.                                                                    | < 0.5 EV      |
| coma                | 0.5   | LensTip: "too high." Summary confirms as con. Sagittal diagonal SA.                            | "significant" |
| sphericalAberration | 0.5   | LensTip: "problems with spherical aberration." Summary confirms as con.                        | "problematic" |
| bokeh               | 1.5   | LensTip: "even spread, barely accented onion-ring, no bright rims." Summary: "nice OOF areas." | "very good"   |
| flareResistance     | 0.0   | LensTip: "tragic/awful." Summary: "awful performance against bright light."                    | "severe"      |

Note: OL distortion (0.27%) conflicts with LensTip (-1.25%). LensTip summary
("moderate distortion") takes precedence per summary authority rule. Phillipreeve
reports "almost complete absence" of SA, contradicting LensTip; summary lists SA
as con, so LensTip wins.

---

## Viltrox

### AF 28mm f/4.5

Pancake prime ($99). Fixed aperture — wide open IS stopped down.
Sources: OpticalLimits (lab, trust 3, Sony FE full-frame),
Dustin Abbott (field, trust 3, Fuji X-mount),
Phillip Reeve (field, trust 3, Sony FE).

| Field              | Score | Source data                                                                     | Rubric rule     |
| ------------------ | ----- | ------------------------------------------------------------------------------- | --------------- |
| centerStopped      | 1.0   | OpticalLimits: "excellent dead center" (FF). Dustin Abbott: "decent" (Fuji).    | "average"       |
| cornerStopped      | 1.0   | OpticalLimits: "soft corners" (FF). Dustin Abbott: "holds up" on APS-C crop.    | "average"       |
| centerWideOpen     | 1.0   | Fixed f/4.5 — same as stopped.                                                  | same            |
| cornerWideOpen     | 1.0   | Fixed f/4.5 — same as stopped.                                                  | same            |
| astigmatism        | 2.0   | Official MTF chart: S/M nearly overlapping, max ~0.05 gap at midframe.          | S/M overlapping |
| coma               | 1.0   | Phillip Reeve: "decently corrected" at f/4.5.                                   | "acceptable"    |
| longitudinalCA     | 2.0   | Dustin Abbott: "neutral." Phillip Reeve: "not really an issue."                 | "negligible"    |
| lateralCA          | 1.5   | OpticalLimits: "quite high in corners" (FF). APS-C crops worst. Conservative.   | "low"           |
| distortion         | 1.5   | OpticalLimits: "slightly wavy pincushion." Phillip Reeve: "well corrected."     | conservative    |
| vignettingWideOpen | 0.5   | OpticalLimits: 2.8 EV (FF). Phillip Reeve: 2.9 EV (FF). APS-C est. ~1.8-2.0.    | 1.5-2.5 EV      |
| vignettingStopped  | 0.5   | Fixed aperture — same as wide open.                                             | same            |
| flareResistance    | 0.5   | Dustin Abbott: "pronounced sensitivity." Phillip Reeve: "severe veiling flare." | "poor"          |

MTF chart: [viltrox-af-28mm-f4-5.jpg](../mtf-charts/viltrox-af-28mm-f4-5.jpg)
([analysis](../mtf-charts/viltrox-af-28mm-f4-5.md))

Note: sphericalAberration, bokeh left undefined. All sources tested on
full-frame Sony except Dustin Abbott (Fuji X-mount). APS-C crop removes
weakest corner areas, improving effective corner performance.

### AF 56mm f/1.4 STM

Budget portrait prime. Sources: Dustin Abbott (field, trust 3),
Thom Hogan / sansmirror (field, trust 2, Nikon Z — same optics).

| Field              | Score | Source data                                                                 | Rubric rule           |
| ------------------ | ----- | --------------------------------------------------------------------------- | --------------------- |
| centerStopped      | 1.5   | Thom Hogan: "excellent" at f/2-f/2.8. Conservative without lpmm.            | "excellent"           |
| cornerStopped      | 1.0   | "Good" at f/5.6, "nipping at very good."                                    | "good"                |
| centerWideOpen     | 1.5   | "Very good" at f/1.4.                                                       | "very good"           |
| cornerWideOpen     | 0.5   | "Fair" at f/1.4.                                                            | "poor"                |
| astigmatism        | 1.0   | Official MTF chart: heavy S/M divergence wide open, overlapping at f/8.     | moderate (heavy↔good) |
| longitudinalCA     | 1.0   | "Clearly present" at f/1.4, "controlled by f/2.8."                          | "noticeable"          |
| lateralCA          | 1.5   | "Good, maybe a pixel's width wide open."                                    | "low"                 |
| distortion         | 1.0   | "Nearly 1.5%" pincushion. DCW Imatest: 1.11%.                               | 1.0-2.0%              |
| vignettingWideOpen | 1.5   | "Less than a stop at the corners wide open."                                | 0.5-1.0 EV            |
| bokeh              | 1.0   | "Bright edges with color fringing", "minimal onion skin", cats-eye corners. | "average"             |

MTF chart: [viltrox-af-56mm-f1-4-stm.jpg](../mtf-charts/viltrox-af-56mm-f1-4-stm.jpg)

Note: Thom Hogan tested Nikon Z version — same optical design as X-mount.
Dustin Abbott (trust 3) confirms "good image sharpness, quality bokeh" but
provided no detailed measurements. Astigmatism scored from official Viltrox
MTF chart (S/M line divergence). Missing: vignettingStopped, coma,
sphericalAberration, flareResistance.

### AF 9mm f/2.8 Air

Ultra-wide pancake prime. Sources: OpticalLimits (lab, trust 3, Sony E APS-C),
Phillip Reeve (field, trust 3), Dustin Abbott (field, trust 3).

| Field              | Score | Source data                                                                    | Rubric rule  |
| ------------------ | ----- | ------------------------------------------------------------------------------ | ------------ |
| centerStopped      | 2.0   | "Tack sharp from f/2.8", diffraction-limited beyond f/8.                       | "excellent"  |
| cornerStopped      | 1.5   | OpticalLimits: "easily very good." Phillip Reeve: "relatively weak" (lower).   | "very good"  |
| centerWideOpen     | 2.0   | "Tack sharp from f/2.8" — wide open IS f/2.8.                                  | "excellent"  |
| cornerWideOpen     | 1.0   | Phillip Reeve: "relatively weak" corners at f/2.8. Conservative.               | "average"    |
| astigmatism        | 1.5   | Dustin Abbott: "low", "sagittal and meridional planes closely aligned."        | "low"        |
| coma               | 1.5   | Phillip Reeve: "mild coma at f/2.8, fully eliminated at f/11."                 | "minor"      |
| longitudinalCA     | 2.0   | Phillip Reeve: "neither longitudinal nor lateral CA visible."                  | "negligible" |
| lateralCA          | 2.0   | OpticalLimits: ~0.3 pixels at borders. Phillip Reeve: "not visible."           | negligible   |
| distortion         | 1.5   | OpticalLimits: < 1% barrel. Phillip Reeve: "wavy, difficult to correct."       | 0.3-1.0%     |
| vignettingWideOpen | 0.0   | OpticalLimits: 3.0 EV at f/2.8 RAW.                                            | > 2.5 EV     |
| vignettingStopped  | 0.5   | Phillip Reeve: ~1.9 EV at f/5.6-f/8. Barely improves.                          | 1.5-2.5 EV   |
| bokeh              | 1.0   | Dustin Abbott: "a little busy", "more outlining than preferred."               | "average"    |
| flareResistance    | 0.5   | Phillip Reeve: "weak performance." Dustin Abbott: "fairly good." Conservative. | "poor"       |

MTF chart: [viltrox-af-9mm-f2-8-air.jpg](../mtf-charts/viltrox-af-9mm-f2-8-air.jpg)
([analysis](../mtf-charts/viltrox-af-9mm-f2-8-air.md))

Note: sphericalAberration left undefined — no data. OpticalLimits tested
on Sony E-mount APS-C; same optical design as X-mount version. Official
MTF chart confirms astigmatism score of 1.5 (moderate edge divergence).

### AF 35mm f/1.7 Air

Compact standard prime. Sources: LensTip (lab, trust 3, Editor's Choice),
OpticalLimits (lab, trust 3). Sensor: LensTip max ~90 lpmm.

| Field               | Score | Source data                                                                       | Rubric rule                  |
| ------------------- | ----- | --------------------------------------------------------------------------------- | ---------------------------- |
| centerStopped       | 2.0   | 91.8 lpmm at f/2.8 (102% of max).                                                 | >= 90%                       |
| cornerStopped       | 1.5   | 66-68 lpmm at f/2.8-5.6 (75.6% of max). Summary PRO: "very good edge resolution." | 75-89%                       |
| centerWideOpen      | 1.5   | "Over 70 lpmm" at f/1.7 (78% of max).                                             | 75-89%                       |
| cornerWideOpen      | 1.0   | "Almost 61 lpmm" at f/1.7 (68% of max).                                           | 60-74%                       |
| astigmatism         | 2.0   | 4.1%. "Very low."                                                                 | < 5%                         |
| coma                | 1.0   | Summary PRO: "moderate coma." Detail: "slight enlargement."                       | "moderate"                   |
| sphericalAberration | 1.0   | "Moderate level", "slight focus shift."                                           | "moderate"                   |
| longitudinalCA      | 1.5   | LensTip PRO: "imperceptible." OpticalLimits: "noticeable at f/1.7, gone by f/4."  | Conservative between sources |
| lateralCA           | 2.0   | 0.02-0.03% across apertures.                                                      | < 0.04%                      |
| distortion          | 1.5   | LensTip: +0.32% RAW. OpticalLimits: 0.6%. Conservative.                           | 0.3-1.0%                     |
| vignettingWideOpen  | 0.5   | RAW: -2.15 EV at f/1.7 (LensTip). OpticalLimits: ~2.3 EV.                         | 1.5-2.5 EV                   |
| vignettingStopped   | 1.5   | RAW: -0.52 EV at f/5.6.                                                           | 0.5-1.0 EV                   |
| bokeh               | 1.5   | LensTip diode: "even light spread, no distinct extremes." Minor onion ring.       | "very good" (lab diode test) |
| flareResistance     | 1.0   | "Average performance", "not very serious problems."                               | "average"                    |

### AF 85mm f/1.8 II (PFU RBMH)

Portrait tele prime. Mk II uses same optics as PFU RBMH.
Sources: LensTip (lab, trust 3, tested APS-C + FF),
OpticalLimits (lab, trust 3, Fuji X-mount).

| Field               | Score | Source data                                                                  | Rubric rule            |
| ------------------- | ----- | ---------------------------------------------------------------------------- | ---------------------- |
| centerStopped       | 1.5   | OpticalLimits: "excellent (just) levels at f/4 across frame."                | "just excellent" → 1.5 |
| cornerStopped       | 1.5   | OpticalLimits: "excellent across frame" at f/4.                              | "excellent"            |
| centerWideOpen      | 1.5   | OpticalLimits: "very good straight away" at f/1.8.                           | "very good"            |
| cornerWideOpen      | 1.0   | LensTip: APS-C edge "over 55 lpmm" at max aperture. 55/78 = 70%.             | 60-74%                 |
| astigmatism         | 1.5   | 5.0%. "Low, outperforms Sony."                                               | 5-10%                  |
| coma                | 2.0   | "Diode in APS-C corner looks practically same as centre."                    | "negligible"           |
| sphericalAberration | 1.5   | "Corrects a bit better than Sony", no focus shift.                           | "well corrected"       |
| longitudinalCA      | 1.0   | "Not corrected perfectly well", "can be bothersome."                         | "noticeable"           |
| lateralCA           | 1.5   | "Low, near max aperture even very low." OpticalLimits: 1.1px border.         | "low"                  |
| distortion          | 1.5   | LensTip: +0.88% APS-C. OpticalLimits: 0.3% (Fuji). Conservative.             | 0.3-1.0%               |
| vignettingWideOpen  | 1.5   | LensTip Fuji X-T2: -0.95 EV at f/1.8. OpticalLimits: 0.9 EV.                 | 0.5-1.0 EV             |
| vignettingStopped   | 2.0   | LensTip: -0.31 EV at f/2.8. OpticalLimits: "negligible from f/2.8."          | < 0.5 EV               |
| bokeh               | 1.5   | LensTip diode: "smooth, even light layout." Minor mechanical vignetting.     | "very good"            |
| flareResistance     | 0.5   | LensTip: "photos from X-T2 look much worse." System-dependent, poor on Fuji. | "poor" (Fuji-specific) |

Note: Mk II shares identical optical design with PFU RBMH (10 elements,
7 groups, 1 ELD). Mk II is lighter (340g vs 490g) with improved AF.

---

## Voigtlander

### Color-Skopar 18mm f/2.8

Not scored — no trust-3 reviews available. Released January 2024. LensTip has
specs page only, no lab review. No coverage from OpticalLimits, DxOMark,
LensRentals, The Digital Picture, Dustin Abbott, DPReview (editorial),
Phillip Reeve, Lloyd Chambers, or Lonely Speck.

### Nokton 23mm f/1.2

Not scored — no trust-3 reviews available. LensTip has specs page only, no lab
review. No coverage from any other trust-3 source. Community data
(DPReview forums, Digital Camera World Z-mount proxy) is qualitative only,
insufficient for rubric scoring.

### Nokton 35mm f/0.9 Aspherical

Sources: LensTip (lab, trust 3). Sensor: X-Trans III (X-T2), max ~85 lpmm.

| Field               | Score | Source data                                                                  | Rubric rule         |
| ------------------- | ----- | ---------------------------------------------------------------------------- | ------------------- |
| centerStopped       | 2.0   | 82-83 lpmm at f/2.8-f/4. "Excellent."                                        | 82/85 = 96%, >= 90% |
| cornerStopped       | 1.0   | ~55 lpmm at f/5.6. "Medium results."                                         | 55/85 = 65%, 60-74% |
| centerWideOpen      | 0.0   | ~40 lpmm at f/0.9. "Just slightly exceeding 40 lpmm."                        | 40/85 = 47%, < 50%  |
| cornerWideOpen      | 0.0   | "Weak" up to f/2.0.                                                          | < 50%               |
| astigmatism         | 0.5   | 22.5%. "A significant value."                                                | 18-25%              |
| coma                | 0.0   | "Seriously deformed", "huge wings." Summary: "very high coma."               | "severe"            |
| sphericalAberration | 0.5   | Summary: "weak correction of spherical aberration." Focus shift f/0.9-f/1.4. | "poor"              |
| longitudinalCA      | 2.0   | "Almost imperceptible." Summary: "imperceptible."                            | "negligible"        |
| lateralCA           | 1.5   | 0.08%. "Borderline between low and medium."                                  | 0.04-0.08%          |
| distortion          | 1.0   | RAW -1.27% barrel. "Lack of any serious problems."                           | 1.0-2.0%            |
| vignettingWideOpen  | 0.5   | -2.10 EV RAW at f/0.9. "Distinct vignetting."                                | 1.5-2.5 EV          |
| vignettingStopped   | 2.0   | -0.41 EV RAW at f/5.6.                                                       | < 0.5 EV            |
| bokeh               | 0.5   | Diode: "noticeable onion ring bokeh", angular polygons stopped down.         | "problematic"       |
| flareResistance     | 1.0   | "Manages to avoid serious slip-ups", "acceptable but unremarkable."          | "acceptable"        |

### Nokton 35mm f/1.2

Sources: LensTip (lab, trust 3). Sensor: X-Trans III (X-T2), max ~85 lpmm.

| Field               | Score | Source data                                                              | Rubric rule         |
| ------------------- | ----- | ------------------------------------------------------------------------ | ------------------- |
| centerStopped       | 2.0   | >80 lpmm at f/4. "Exceeds 80 lpmm."                                      | 80/85 = 94%, >= 90% |
| cornerStopped       | 0.0   | "Decent quality only at f/8-f/11." ~44 lpmm at best.                     | 44/85 = 52%, ~50%   |
| centerWideOpen      | 0.0   | "Images are of weak quality" at f/1.2-f/1.4.                             | < 50%               |
| cornerWideOpen      | 0.0   | Worse than center wide open.                                             | < 50%               |
| astigmatism         | 1.0   | 12.8%. "Borderline between medium and high level."                       | 10-18%              |
| coma                | 0.0   | "Really huge." "Long wings." Summary: con.                               | "severe"            |
| sphericalAberration | 0.0   | "Some problems", "characteristic mist", "badly corrected."               | "very poor"         |
| longitudinalCA      | 2.0   | "Rather doesn't experience any problems."                                | "negligible"        |
| lateralCA           | 1.5   | 0.05-0.07%. "Low."                                                       | 0.04-0.08%          |
| distortion          | 1.0   | RAW -1.53% barrel. "Not a serious flaw."                                 | 1.0-2.0%            |
| vignettingWideOpen  | 0.0   | -2.67 EV RAW at f/1.2. "Very high."                                      | > 2.5 EV            |
| vignettingStopped   | 1.5   | -0.56 EV at f/5.6.                                                       | 0.5-1.0 EV          |
| bokeh               | 2.0   | Diode: "very even, without any local extremes or onion ring bokeh."      | "excellent"         |
| flareResistance     | 0.5   | "Failed completely", "really hopeless", "big intensive light artifacts." | "poor"              |

### Nokton 50mm f/1.2

Not scored — X-mount version is an exclusive APS-C Sonnar design (290g, 58mm
filter), different from both the VM Aspherical (8 elem/6 groups, 347g) and the
SE E-mount (8 elem/6 groups, 434g). No trust-3 or trust-2 reviews exist for
the X-mount design. DCFever (trust-2) has a brief X-mount article in Chinese
with qualitative impressions only. Database specs corrected: 492g→290g,
filterThread 52→58, MFD 450→390mm.

### Macro APO-Ultron 35mm f/2

Not scored — no trust-3 reviews available. LensTip has specs page only.
Not reviewed by any of the 10 trust-3 sources. Only community impressions
(DPReview forum mini-review, FujiFanBoys) with no quantitative data.

### Ultron 27mm f/2

Sources: LensTip (lab, trust 3). Sensor: X-Trans III (X-T2), max ~85 lpmm.

| Field               | Score | Source data                                                                                 | Rubric rule          |
| ------------------- | ----- | ------------------------------------------------------------------------------------------- | -------------------- |
| centerStopped       | 2.0   | >80 lpmm at f/4. "Excellent."                                                               | 80/85 = 94%, >= 90%  |
| cornerStopped       | 0.5   | ~50 lpmm at f/4-f/8. "Medium results."                                                      | 50/85 = 59%, 50-59%  |
| centerWideOpen      | 1.5   | >64 lpmm at f/2. "Excellent image quality in the frame centre."                             | 64/85 = 75%, 75-89%  |
| cornerWideOpen      | 0.0   | 36.6 lpmm at f/2. "Simply blurry."                                                          | 36.6/85 = 43%, < 50% |
| astigmatism         | 1.5   | 6%. "Borderline between low and very low level." Summary: "slight."                         | 5-10%                |
| coma                | 0.0   | "Very high" at f/2. "First big slip-up." Summary: con.                                      | "severe"             |
| sphericalAberration | 1.5   | "Not a huge problem." "No noticeable focus shift." Summary: "lack of any serious problems." | "well corrected"     |
| longitudinalCA      | 2.0   | "Performed here very well, no issues." Summary: "imperceptible."                            | "negligible"         |
| lateralCA           | 2.0   | ~0.01%. "Negligible value." Summary: "slight."                                              | < 0.04%              |
| distortion          | 2.0   | +0.18% RAW. "Brushing against zero." Summary: "practically zero."                           | < 0.3%               |
| vignettingWideOpen  | 0.5   | -2.16 EV RAW at f/2. "Distinct." Summary: con.                                              | 1.5-2.5 EV           |
| vignettingStopped   | 1.5   | -0.79 EV RAW at f/4.                                                                        | 0.5-1.0 EV           |
| bokeh               | 1.5   | "Even light distribution", "no onion-ring effect." Summary: "sensibly-looking."             | "very good"          |
| flareResistance     | 1.5   | "Pretty well", "few and far between." Summary: "decent performance."                        | "very good"          |
