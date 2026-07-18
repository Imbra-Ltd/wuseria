# ADR-081: MTF chart reproduction is a signature feature — fidelity over extraction throughput

**Status:** Proposed
**Date:** 2026-07-18

## Prerequisites

This ADR governs the acceptance target of the digitizer built under
**ADR-038** and tiered by **ADR-041**. It reconciles two consumers of
the digitized readings: the rendered lens-detail reproduction, and the
downstream optical content/scoring of **ADR-029 §3.2** and **ADR-014**
(fallback #2, astigmatism-from-MTF). It preserves the S/M identity
mechanisms of **ADR-049** and **ADR-080**, relies on **ADR-079** for
honest gaps, and sits alongside the escape hatches already rejected in
**ADR-053** and **ADR-057**.

## Context

The digitizer has been the dominant workstream for ~118 sessions and
stands at 6 of 24 brands (#790), which reads as too slow and too
complex. The tempting speedup is to lower the extractor's acceptance
target:

- coarsen calibration from per-cell fidelity to the score/phrase
  buckets that ADR-014 and ADR-029 consume, or
- retire the expensive crossing/swap sagittal-vs-meridional identity
  detector (ADR-049), on the argument that astigmatism and bokeh are
  scored on `|S - M|` _magnitude_, which is invariant to swapping the
  two labels.

That argument holds only for the scoring consumer. It ignores the
primary one. The digitized readings are not merely a scoring input:
the re-rendered SVG chart and the numeric S/M table are rendered on the
lens detail page as a first-class product feature — a genuine
reproduction (real re-drawn chart plus real numbers), not a copied
manufacturer image. Every digitized value is user-visible, and a
knowledgeable reader can cross-check it against the source chart.

So the display is the strictest consumer, and it dominates:

```
        digitized readings (curve values + S/M identity)
                          |
          +---------------+-------------------+
          v                                   v
   lens-detail reproduction           optical content / scoring
   (re-rendered chart + S/M table)    (ADR-029 buckets, ADR-014
   STRICT: correct shape AND          fallback #2)
   correct S/M label, user-visible    LOOSE: coarse buckets,
                                       |S - M| magnitude
          |                                   ^
          +-----------------------------------+
       display fidelity subsumes the coarse consumer:
       calibrate to fidelity and prediction is satisfied for free;
       the reverse is not true
```

A swapped S/M label is invisible to the astigmatism score but plainly
visible in the rendered table, and a wrong value destroys the
credibility of "real numbers." Display fidelity — correct curve shape
AND correct S/M identity — is therefore load-bearing, not cosmetic.

## Decision

1. The MTF chart-plus-table reproduction is a first-class signature
   feature of the site. The extractor's acceptance target is display
   faithfulness — correct curve shape and correct S/M identity, verified
   against eye-read ground truth. This target is NOT lowered for
   throughput.

2. The acceptance metric is NOT coarsened to score/phrase buckets, and
   the crossing/swap S/M identity machinery (ADR-049; left-edge ordering
   ADR-080) is NOT retired. Optical content and scoring (ADR-029 §3.2,
   ADR-014 fallback #2) are downstream free-riders on display fidelity —
   satisfied automatically by it, never a reason to loosen it.

3. Throughput improvements MUST be fidelity-preserving. Approved
   directions, in priority order:
   - **Setup automation** that removes per-brand hand-work without
     changing outputs — legend-swatch auto-suggest (#1198), plot-box
     auto-detection.
   - **Accidental-complexity removal** that changes zero outputs —
     delete superseded extraction dialects, add a registry for the
     scattered tuned constants, decompose the oversized `ridge.py`,
     add per-stage diagnostics, and consolidate (not delete) the
     correction passes.
   - **Process discipline** — time-box per cohort, probe-first, invest
     in per-stage debug output once a debugging loop repeats.

4. The only extractor-facing throughput lever is honest gaps: an
   irreducibly-ambiguous cell is nulled per ADR-079 — a visible gap in
   both chart and table — so one hard cell never blocks a whole lens,
   and the cell is improved later. A wrong emitted value is never
   acceptable: it is visible in the table and forfeits the signature's
   credibility.

5. Ground-truth verification is scoped per distinct chart style, not per
   brand — reuse GT across brands that share a chart vendor's style,
   rather than eye-reading a full anchor set for every brand.

## Alternatives considered

| Alternative                                                 | Why rejected                                                                                                                |
| ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Coarsen the acceptance metric to ADR-029 / ADR-014 buckets  | The buckets serve scoring; the visible table needs the exact value. Loosening corrupts the signature feature.               |
| Retire the crossing/swap S/M identity detector              | Swap-invariance holds only for the astigmatism/bokeh score; a swapped label is visible and wrong in the rendered S/M table. |
| Treat MTF as a scoring input only and drop the reproduction | The faithful reproduction is the differentiator — a copied manufacturer image is not.                                       |
| ML / vector-source extraction to cut cost                   | Already rejected in ADR-057 (no license-clean model; vector covers ~9% of brands).                                          |
| Ship a high-value subset and close the milestone short      | Out of scope — all brands are wanted; the goal is speed without dropping coverage or fidelity.                              |

## Consequences

- The core extractor complexity — curve tracing, S/M identity, crossing
  detection, dashed-gap bridging, halo subtraction, plot-box accuracy —
  is accepted as inherent to the value proposition, not flagged as
  over-engineering. Reviews and audits should stop treating it as debt
  to shed.
- Speedup effort is redirected to setup automation, refactor-for-
  maintainability, per-stage diagnostics, and honest gaps.
- Every fidelity-neutral refactor (dialect deletion, constant registry,
  `ridge.py` split, correction-pass consolidation) MUST be verified
  output-neutral by the calibrate-and-diff-golden-grids harness — zero
  GT delta is the pass condition.
- The `confidence` / `mtfType` fields are kept: computed-vs-measured
  governs downstream prose confidence (ADR-029), not the extractor bar.
  This resolves the open S210 retire-the-confidence-fields question in
  favour of keep.
- Per-brand onboarding cost drops through setup automation, so the 18
  remaining brands get cheaper without any fidelity risk.
- Some cells remain irreducibly ambiguous; an ADR-079 gap is the
  accepted outcome for those, not a defect to chase indefinitely.
- This ADR sets approach and priorities; it does not itself change code.
  It exists because lowering the fidelity bar was proposed and rejected,
  and the constraint is worth recording so it is not retread.
