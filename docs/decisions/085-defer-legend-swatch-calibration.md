# ADR-085: Defer legend-swatch auto-calibration — the palette is not the per-brand bottleneck

**Status:** Accepted
**Date:** 2026-07-19

## Context

ADR-057 kept the classical-CV digitizer and named its next refinement:
"per-brand color-profile auto-calibration via legend-swatch clustering
... the single highest-leverage fix on the classical side." The premise
was that hand-tuned HSV thresholds in `profiles/declared.py` are the
per-brand onboarding bottleneck — each new brand needs a fresh sampling
pass — and that a legend-swatch-derived palette would eliminate it.

Spike #1198 (the last open task of epic #1415, ADR-081 throughput) was
scoped to measure that claim before any code lands, on the two chart
families where legend-swatch calibration has both clean semantics and
the most hand-tuned bands: Samyang (`mainstream-4color-all-solid`, 6
declared `HueRange` entries) and TTartisan (`ttartisan-4color-dual-
aperture`, 6 entries). The measurements below are the spike output; a
throwaway probe drove the real extractor over the committed ground
truth and was deleted before this commit.

### What the probe measured

1. **AC1 — detection is feasible but not turnkey.** A geometric
   swatch detector using only the existing cv2/numpy stack found all
   four colour swatches on both charts. Text-anchor (OCR) detection is
   unavailable without adding a tesseract binary + `pytesseract` — a
   heavyweight new dependency — so it loses on cost before reliability
   is even weighed. The false-positive class differs by legend chrome:
   Samyang's ruled table leaks light cell separators, TTartisan's
   bordered box leaks dark box borders — no single width/colour filter
   cleans both. This reproduces the issue's own audit: one swatch-cluster
   algorithm does not fit all families.

2. **AC2 — the swatch centres already reproduce the declared bands.**
   Every real colour swatch's HSV centre falls inside exactly the
   correct declared `HueRange`, 1:1, on both charts. The hand-tuned
   bands are centred on the legend swatch colours; a derived band would
   confirm the palette, not correct it.

3. **AC3 — swapping to a legend-derived palette costs almost nothing,
   because the palette was never the expensive part.** Real extractor,
   Samyang 85mm, 88 paired positions vs committed GT:

   | Palette                               | paired | med \|Δ\| | p95 \|Δ\| |
   | ------------------------------------- | ------ | --------- | --------- |
   | DECLARED (hand-tuned)                 | 88     | 0.0077    | 0.0336    |
   | derived palette + kept dispatch       | 88     | 0.0077    | 0.0384    |
   | DECLARED palette, bare dispatch       | 88     | 0.0083    | 0.0518    |
   | derived palette, bare dispatch        | 88     | 0.0083    | 0.0601    |
   | derived palette (wide), bare dispatch | 88     | 0.0079    | 0.0877    |

   "Bare" strips the hand-tuned dispatch fields a legend swatch cannot
   produce: the AA-halo subtraction (ADR-059, ADR-062) and the below-top
   CC filter (ADR-074). Reading: the palette swap costs +0.005 p95 and
   zero median; stripping the dispatch costs +0.018 p95 — more than the
   palette. The tail accuracy comes from the non-derivable per-lens
   forensics, not from the HSV bands.

## Decision

Defer adoption of legend-swatch auto-calibration. Keep the hand-tuned
per-brand palettes and the manual swatch-sampling step. This scopes
ADR-057's "next refinement" pointer: the legend palette is auto-derivable
at near-zero accuracy cost, but it is not the per-brand bottleneck, so
automating it does not advance the ADR-081 throughput goal.

```
   per-brand onboarding cost, by step
   +-------------------------------------------------+
   | sample 4 swatch HSV centres     ~5 min   CHEAP  |  <- what #1198
   |   (legend-swatch auto-cal target)               |     would automate
   +-------------------------------------------------+
   | per-lens dispatch forensics     multi-   COSTLY |  <- the real
   |   halo_pairs (ADR-059/062),     session          |     bottleneck;
   |   CC filters (ADR-074),                          |     NOT legend-
   |   dp_y_anchor / sm_swap                          |     derivable
   +-------------------------------------------------+
   legend-swatch auto-cal automates the cheap row and
   leaves the costly row fully manual -> defer
```

The redirected effort (AC5's "different next-refinement target"): the
classical-CV bottleneck is the dispatch forensics, not the palette.
Throughput gains there come from the setup-automation and diagnostics
route ADR-081 already mandates — the plot-box dispatch (ADR-084) and the
per-stage diagnostic bundle (#1412) — not from palette derivation. No
new palette-automation work is scheduled.

ADR-057's core decision (reject ML, keep classical CV) is unaffected and
reaffirmed — the classical baseline runs at median |Δ| 0.0077 on the
anchor. Only its forward pointer naming legend-swatch as the
highest-leverage next fix is superseded here; ADR-057's status gains a
partial-supersession marker to keep that pointer discoverable, matching
the ADR-058 precedent.

## Alternatives considered

| Alternative                                                    | Why rejected                                                                                                                                                                                                                    |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Adopt legend-swatch calibration as ADR-057 recommended         | AC3 shows a zero-to-negative accuracy delta on the cleanest anchor; the step it automates (swatch sampling) is already ~5 minutes, while the costly per-lens dispatch forensics stay manual. Net throughput gain is negligible. |
| Adopt for Samyang + TTartisan only (the 2 ideal families)      | Same near-zero delta, plus a per-family detector to build and maintain (AC1: table vs box chrome need different filters). Cost exceeds the benefit even where semantics are cleanest.                                           |
| Build the per-family detector now, defer only the palette swap | The detector's only consumer is the palette swap; building it without adopting the swap is dead code. Revisit both together if the trigger fires.                                                                               |
| Draft the defer decision from AC1/AC2 alone, skip AC3          | AC2 is directional but AC4 wants a measured delta; the AC3 run is what distinguishes "argued it wouldn't help" from "measured it doesn't." The measurement also produced the sharper finding (dispatch > palette).              |

## Consequences

| Consequence                    | Detail                                                                                                                                                                                                                                |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| No code change                 | Spike output is this ADR; the throwaway probe is deleted. `declared.py` and the dispatch are untouched.                                                                                                                               |
| Epic #1415 closes              | #1198 was its last open task (#1412, #1413, #1414 done); deferring with a measured basis completes the epic's definition of done.                                                                                                     |
| Manual swatch sampling stays   | New Samyang/TTartisan lenses still get their palette sampled by hand — a cheap step the measurement shows is not worth automating.                                                                                                    |
| Revisit trigger named          | Re-open if a future family's curves sit so close in HSV that hand-sampling the palette becomes the multi-session step (i.e. the palette, not the dispatch, becomes the bottleneck) — then the cost/benefit flips.                     |
| ADR-057 forward pointer scoped | ADR-057's "legend-swatch is the highest-leverage next fix" is superseded; its core reject-ML decision stands. Reciprocal partial-supersession markers link the two.                                                                   |
| Single-anchor caveat recorded  | AC3 ran on the 85mm anchor only; the declared bands serve 19 Samyang lenses, so a one-chart-derived palette could regress harder cases not run here. The p95 figures are a lower bound on the risk, which strengthens the defer call. |
