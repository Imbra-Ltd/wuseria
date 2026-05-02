# ADR-019: Display optical quality on native 0-2 scale

**Status:** Accepted
**Date:** 2026-05-01

## Context

The `computeOpticalQuality` function computes a weighted average of optical
fields, each on a 0-2 scale. The result was multiplied by 5 to produce a
0-10 display value. This created two problems:

1. The explorer showed OQ on a 0-10 scale while genre screener field
   scores used 0-2 — users had to mentally convert between them.
2. Color-coding OQ required back-converting to 0-2 thresholds, adding
   complexity for no user benefit.

## Decision

Display OQ on the native 0-2 scale. Remove the x5 multiplier from
`computeOpticalQuality`. Apply the same traffic-light color thresholds
used by `FieldVal` for individual optical fields:

- Green: 1.5+ (good)
- Amber: 1.0-1.4 (acceptable)
- Red: < 1.0 (poor)

OQ filter ranges in the Lens Explorer updated to match (1.5+, 1.0-1.4,
0.5-0.9, 0-0.4).

## Alternatives considered

| Alternative                     | Why rejected                                                |
| ------------------------------- | ----------------------------------------------------------- |
| Keep 0-10 with color thresholds | Two scales on one site; thresholds require back-conversion  |
| Switch everything to 0-5        | Arbitrary multiplier, no alignment with source data         |
| Switch everything to 0-10       | Would require changing all optical field displays site-wide |

## Consequences

- One scale (0-2) across all pages: field scores, OQ aggregate, genre screener
- Color language is consistent — green/amber/red means the same everywhere
- If we later rescale (0-5 or 0-10), it is a single multiplier change that
  propagates to all pages
- Users familiar with the old 0-10 OQ values will see lower numbers — no
  migration path needed since the site is pre-launch
