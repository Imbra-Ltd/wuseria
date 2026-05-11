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

### XF 16mm f/2.8 R WR

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

### XF 18mm f/2 R

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

### XF 56mm f/1.2 R WR

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

### XF 90mm f/2 R LM WR

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

### XF 200mm f/2 R LM OIS WR

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

Note: sphericalAberration left undefined — no data. OpticalLimits tested
on Sony E-mount APS-C; same optical design as X-mount version.

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
