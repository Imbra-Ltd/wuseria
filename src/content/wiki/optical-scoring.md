---
title: "Optical Scoring"
fullTitle: "How Wuseria Scores Lenses"
categories:
  - "Optics"
summary: "How marks, optical quality, and genre scores work in Wuseria."
related:
  - "scoring-methodology"
  - "mtf-charts"
---

Wuseria rates every lens with enough optical data on two scales: a per-genre **mark** (1 to 5 in half-star steps) and an overall **Optical Quality** score (0 to 10).

## Genre marks

Each genre has a formula with **primary** and **secondary** optical fields. Primary fields carry 3x the weight of secondary fields. The weighted average of all available fields produces a raw score on a 0-2 scale, which maps to marks 1 through 5.

The primary floor rule prevents a lens from earning a high mark if any single primary field is weak. The final score is capped at the lowest primary field value. A lens with excellent secondary scores but poor coma control will still score low for nightscape.

A lens must have at least 7 of 14 optical fields populated to receive any genre mark. Lenses without sufficient data show "Not yet scored" instead of a number.

## Optical Quality (OQ)

OQ is a single 0-10 number summarizing overall optical performance across all genres. It uses the same 14 optical fields but with weights derived from how often each field appears as a primary factor across all genre formulas. Fields important to many genres (like center sharpness stopped down) carry more weight than niche fields.

## Mark scale

| Mark    | Meaning                                 |
| ------- | --------------------------------------- |
| 5.0     | Exceptional — top-tier for the genre    |
| 4.0-4.5 | Very good — strong performer            |
| 3.0-3.5 | Good — competent for the genre          |
| 2.0-2.5 | Below average — usable with limitations |
| 1.0-1.5 | Poor — not recommended for this genre   |

## Editorial picks

Some lenses receive an editorial pick badge for a genre. These are lenses that real-world experience and photographer consensus recognize as exceptional, even if the formula alone does not fully capture their strengths.

## Data sources

Optical field scores come from lab tests and detailed field reports by trusted review sources: LensTip, Optical Limits, and DPReview. Each field is rated on a 0-2 scale where 0 is poor, 1 is average, and 2 is excellent. Scores are not estimated or interpolated — if a trusted source has not tested a field, it remains empty.
