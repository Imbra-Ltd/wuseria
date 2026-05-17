---
title: "Scoring Methodology"
categories:
  - "Optics"
summary: "How Wuseria scores lenses for each photography genre using optical data and weighted formulas."
related:
  - "mtf-charts"
  - "coma"
---

Wuseria scores lenses for each photography genre using marks from 1 to 5 (in half-star steps). Scores are calculated from optical performance data, not marketing specs or subjective reviews. The goal is to answer: "How well does this lens perform for this specific genre?"

## Optical quality scale

Every optical field is rated on a 0–2 scale based on lab tests and detailed field reports from trusted review sources (LensTip, Optical Limits, Dustin Abbott, DPReview, and others).

| Score | Meaning                                            |
| ----- | -------------------------------------------------- |
| 0     | Poor — significant defect visible in normal use    |
| 0.5   | Below average — noticeable in demanding conditions |
| 1.0   | Average — acceptable for the lens class            |
| 1.5   | Good — better than most competing lenses           |
| 2.0   | Excellent — among the best in class                |

## The 14 optical fields

Wuseria evaluates 14 optical fields, organized into four clusters.

### Sharpness

Resolution and detail rendering across the frame and aperture range.

- **Center sharpness (wide open)** — resolution at the center of the frame at maximum aperture
- **Corner sharpness (wide open)** — resolution at the edges at maximum aperture
- **Center sharpness (stopped down)** — resolution at the center at the sweet-spot aperture (typically f/5.6–f/8)
- **Corner sharpness (stopped down)** — resolution at the edges at the sweet-spot aperture

### Aberrations

Optical defects that affect color accuracy and point-source rendering.

- **Longitudinal CA** — purple/green color fringing in front of and behind the focus plane, visible on high-contrast edges and bokeh highlights
- **Lateral CA** — color fringing toward the edges of the frame, caused by wavelength-dependent magnification
- **Coma** — point lights (stars, streetlamps) stretching into wing or seagull shapes at the corners
- **Astigmatism** — point sources rendering as lines or crosses instead of dots, most visible at corners
- **Spherical aberration** — focus shift between center and edges, reducing contrast wide open

### Rendering

Qualities that affect the aesthetic look of images beyond sharpness.

- **Bokeh** — smoothness and quality of out-of-focus areas; scored by highlight shape, transition edges, and background busyness
- **Vignetting (wide open)** — light falloff in corners at maximum aperture, measured in stops
- **Vignetting (stopped down)** — residual light falloff at f/5.6–f/8
- **Flare resistance** — ghosting and veiling flare when shooting into light sources

### Distortion

- **Distortion** — barrel or pincushion bending of straight lines; scored after considering whether the camera auto-corrects in-body

## Genre scoring

Each genre uses a weighted formula with **primary** and **secondary** fields. Primary fields carry 3x the weight of secondary fields and set a ceiling — a lens cannot score higher than its weakest primary field allows.

### Primary vs secondary fields

- **Primary fields** define what the genre demands. A lens with poor primary fields will score low regardless of secondary performance.
- **Secondary fields** refine the score. Strong secondary fields can lift an average lens, and weak ones can pull down an otherwise strong one.

### Genre formulas

| Genre        | Primary fields                             | Secondary fields                                                                                 |
| ------------ | ------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| Nightscape   | Coma, astigmatism, aperture speed          | Lateral CA, center/corner wide open, longitudinal CA, vignetting wide open, spherical aberration |
| Landscape    | Corner stopped, center stopped             | Distortion, lateral CA, longitudinal CA, vignetting stopped, flare resistance, astigmatism, coma |
| Architecture | Corner stopped, center stopped, distortion | Lateral CA, vignetting stopped, flare resistance                                                 |
| Portrait     | Bokeh, center wide open                    | Longitudinal CA, spherical aberration, vignetting wide open                                      |
| Street       | Center stopped, aperture speed             | Center wide open, flare resistance, longitudinal CA, coma                                        |
| Travel       | Center stopped, weight                     | Aperture speed, flare resistance, longitudinal CA                                                |
| Sport        | Center wide open                           | Aperture speed, longitudinal CA, lateral CA                                                      |
| Wildlife     | Center wide open, center stopped           | Aperture speed, longitudinal CA, lateral CA                                                      |
| Macro        | Center stopped, magnification              | Distortion, lateral CA, longitudinal CA, spherical aberration, bokeh                             |

Fields marked as "aperture speed", "weight", and "magnification" are derived from lens specifications rather than optical measurements. They are scored on the same 0–2 scale.

### From raw score to genre mark

1. Compute the weighted average of all available primary (weight 3) and secondary (weight 1) fields
2. Cap the result at the lowest primary field score — no lens can outscore its weakest critical factor
3. Map the capped 0–2 value to a 1–5 mark in half-star steps

A lens needs at least 7 of 14 optical fields populated before it can be scored.

## Data sources

Optical data comes from trusted review sources ranked by methodology rigor. Trust level 3 sources (lab-based, peer-verified) take priority. When sources disagree, higher-trust sources override lower ones.

Lenses without sufficient optical data are shown as "Not yet scored" rather than estimated. We only score lenses when we have data from trusted sources.

## Editorial picks

Genre scores are supplemented by editorial picks — lenses that the formula alone might not surface but that are widely recognized as exceptional for a given genre based on field experience and photographer consensus.

## Transparency

Scoring is opinionated and transparent. The weights and formulas are visible in the codebase. We acknowledge that no formula perfectly captures real-world performance, and encourage photographers to use scores as a starting point, not a final verdict.
