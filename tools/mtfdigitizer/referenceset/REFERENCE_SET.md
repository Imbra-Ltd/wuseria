# MTF reference set

Eight eye-verified MTF charts that calibrate the unified digitizer
(ADR-038). Each chart was opened, the curve shapes read by eye, and the
verified shape recorded here as the ground truth the extractor must match.

The machine-readable form is `charts.py`. This document carries the
reasoning — why these eight, what to look for in each, and where the
proposed thresholds come from.

## Why these eight

The reference set must cover every chart style the digitizer will see in
`docs/optical-specs/`. From a sweep of that directory the observed styles
collapse to eight families (one per row below); one chart per family puts
the set inside #933's 6–10-chart target with full coverage.

| # | Lens                                  | Style family                       | Why it earns its slot                              |
| - | ------------------------------------- | ---------------------------------- | -------------------------------------------------- |
| 1 | `sigma-56mm-f1-4-dc-dn-c`             | mainstream-2color-solid-dashed     | Canonical clean case; smooth slopes                |
| 2 | `samyang-85mm-f1-4-as-if-umc`         | mainstream-4color-all-solid        | Canonical Samyang 4-color, two stacked apertures   |
| 3 | `samyang-300mm-f6-3-ed-umc-cs-reflex` | idealized-flat                     | Flat-axis blind-spot probe case (ADR-038 §4)       |
| 4 | `7artisans-50mm-f1-2-mark-ii`         | samecolor-dashed-sm                | Same-color S/M split — CC-by-width is the only way |
| 5 | `7artisans-35mm-f1-2-mark-ii`         | soft-multicurve-promo              | Out-of-band: tests profile fail-loud (B1)          |
| 6 | `tokina-atx-m-23mm-f1-4-x`            | 2color-frequency                   | Colors carry frequency not S/M — different dialect |
| 7 | `viltrox-af-75mm-f1-2-pro`            | bw-dashed-promo                    | All-dashed, B&W, two apertures, tiny legend        |
| 8 | `zeiss-touit-32mm-f1-8`               | multifreq-press-kit                | Three frequencies (10/20/40) — out-of-band         |
| 9 | `ttartisan-7-5mm-f2-0-fisheye`        | ttartisan-4color-dual-aperture     | Second anchor (ADR-041); fisheye edge-crash stress |

The base set was eight; #9 was added when the TTartisan 4-color
dual-aperture family was introduced. ADR-041 allows multiple Tier 1
anchors per `(brand, style_family)`; the TTartisan 50/1.2 is the
primary anchor for `ttartisan-4color-dual-aperture` and the 7.5 fisheye
is the second, chosen to stress fisheye edge behavior (the right-edge
10S crash and the 30S dip-and-recover that #1122 traced to the vertical
y-axis chrome strip). The primary 50/1.2 entry is documented inline in
`charts.py` rather than here.

## Verified shapes

### 1. sigma-56mm-f1-4-dc-dn-c — clean Sigma 2-color

- **10 lp/mm** (red): S solid ~0.97 flat from 0 to ~10mm, then knees down to ~0.68 at 14mm; M dashed sits ~0.005 higher across the field, also dips at edge but less steeply.
- **30 lp/mm** (blue): both S and M start ~0.85–0.87 at center; S solid drops smoothly from ~0.80 at 10mm to ~0.33 at 14mm; M dashed holds higher (~0.60 at 14mm).
- Diagnostic: S < M at edge by a wide margin — astigmatism characteristic of f/1.4 wide-open.

### 2. samyang-85mm-f1-4-as-if-umc — Samyang 4-color, two apertures

- **MAX panel** (top): four solid curves; 10S (dark red) and 10M (pink) both start ~0.91, hold flat to ~14mm, then 10S knees down sharply to ~0.78 at edge while 10M stays high (~0.93). 30S (dark grey) starts ~0.70, sags to ~0.56 around 14mm, then upticks to ~0.55. 30M (light grey) drops more linearly from ~0.70 to ~0.55.
- **F8 panel** (bottom): all four curves recover to ~0.95–1.00 across most of the field; 30M still drops to ~0.55 at edge while 30S holds ~0.95 — the edge-30M characteristic.
- Diagnostic: stopping down fixes 10 but barely helps 30M at the edge.

### 3. samyang-300mm-f6-3-ed-umc-cs-reflex — idealized-flat

- **Both panels**: ALL four curves pinned at ~1.0 across the entire field at both apertures.
- This is the chart ADR-038 §4 calls out as the flat-axis blind-spot probe case: a horizontal shift cannot be detected by render-match alone because the curves carry no horizontal structure.
- **Diagnostic value**: must trip the "suspiciously flat at ~1.0" plausibility prior. Any extractor that cleanly traces this and reports HIGH confidence has a broken confidence gate.

### 4. 7artisans-50mm-f1-2-mark-ii — Chinese same-color S/M

- Two hues; within each hue, solid = T (M) and dashed = S.
- **Blue** (10 lp/mm — labeled T1/T2 at right): T1 ~0.90 from 0 to 10mm, knees to ~0.80 at 14mm; T2 ~0.88 to ~0.70.
- **Green** (30 lp/mm — labeled S1/S2): S2 solid drops from ~0.80 at 0mm to ~0.45 at 14mm; S1 dashed dips to ~0.45 around 11mm then rises back to ~0.48 at 14mm.
- Diagnostic: the dip-and-recover in green S1 must NOT be smoothed out — it's an honest astigmatism feature. Also the green pair runs into the dip together near 9.8mm, the CC-by-width split must keep them separate.

### 5. 7artisans-35mm-f1-2-mark-ii — out-of-band soft promo

- Code-v.com lab plot reposted as a promo asset; **8 curves** of mixed colors (red, yellow, blue, green, purple, dark blue) at 5/10/20/30 lp/mm, T and S each.
- Low resolution (~370×170 px), JPEG-compressed, axis labeled `Y-FIELD ANGLE (Degrees)` 0–21 — out-of-band in every way.
- **Diagnostic value**: a correctly-implemented profile system must refuse this chart (B1: fail loud). If the digitizer tries to mask 2 hues and emit 11 readings here, the profile abstraction is broken. No specific shape is recorded — the test is "does it refuse?".

### 6. tokina-atx-m-23mm-f1-4-x — frequency-by-color convention

- Two colors, two line styles, but they map differently than Sigma:
- **10 lp/mm** is the upper pair near ~0.85–0.95 (red solid = S, blue dotted = M); both stay high to ~10mm then knee.
- **30 lp/mm** is the lower pair near ~0.55–0.75; the red S has a curious local maximum near 5mm (rising from 0.65 to 0.75 before dropping) — a feature that must survive extraction.
- Diagnostic: a Sigma-style profile (solid = S, dashed = M) would mis-classify these; colors here carry frequency, not S/M.

### 7. viltrox-af-75mm-f1-2-pro — B&W soft promo, two apertures

- **f/1.2 panel** (top): black solid curves bunched at ~0.95–1.00 for 10 lp/mm; greys at ~0.70–0.85 for 30 lp/mm, with M slightly below S at 10mm onward; edge drop visible.
- **F8 panel** (bottom): single light-blue curve hovers ~0.95 across the field; near-idealized-flat — borderline case to #3.
- Diagnostic: ambiguity at the boundary between styles; must declare profile rather than guess.

### 8. zeiss-touit-32mm-f1-8 — 3 frequencies press kit

- German Zeiss press kit; B&W, solid = Sagittal, dashed = Tangential, **three frequencies** (10/20/40 cycles/mm — top, middle, bottom).
- **k=1.8 panel**: 10 ~85→55%, 20 ~70→45%, 40 dips to ~30% around 11mm then recovers slightly.
- **k=4 panel**: 10 ~95→85%, 20 ~85→78%, 40 ~75 with a dip to ~50% at 11mm.
- Diagnostic: out-of-band for any profile that declares 2 frequencies. Must refuse, not silently drop the 20 lp/mm middle row.

### 9. ttartisan-7-5mm-f2-0-fisheye — second TTartisan 4-color anchor

- 800x600 dual-aperture template; solid = S, dashed = T (M). Black/grey = f/2.0; red/orange = f/8.
- **f/2.0 panel** (max aperture):
  - 10S (black solid) sits flat at ~0.96 through 8mm then crashes hard at the right edge — ~0.93 at 11mm, ~0.85 at 12.6mm, ~0.74 at 14mm.
  - 10M (black dashed) only mildly drops — holds ~0.92–0.94 to 13mm, edges to ~0.89 at 14mm.
  - 30S (grey solid) shows the dip-and-recover characteristic: ~0.71 center, ~0.55 at 7mm, dips to ~0.46 around 11mm, **recovers to ~0.58 at 14mm**.
  - 30M (grey dashed) holds ~0.65–0.72 through 11mm then sharp drop to ~0.49 at 14mm.
- **f/8 panel** (stopped aperture): 10S/10M (red pair) essentially flat at ~0.94 across the field. 30S (orange solid) tracks the grey 30S down to 0.58 at edge. 30M (orange dashed) is the most stable curve in the chart — 0.78–0.80 throughout.
- Diagnostic: the 30S corner uptick is the case #1122 fixed — the dispatch was picking the y-axis vertical chrome strip as part of the ridge candidate set, pulling the right-edge value up artificially. An extractor that smooths the dip-and-recover into a monotonic fall is dropping signal; one that puts the corner above 0.65 has re-introduced the chrome leak.

## Proposed thresholds

ADR-038 leaves the render-match threshold and offset tolerance band as
open parameters, calibrated against this reference set. These are
**starting points** for #935, not final values — they'll be refined once
the real extractor exists and we can measure actual scores.

### Render-match threshold: IoU ≥ 0.75 (starting value)

ADR-038's de-risking probe reported good extractions at IoU 0.64–0.87 and
mis-calibrated ones at 0.03–0.49 (with the flat-axis special case at 0.69
after an 8% horizontal shift). A threshold at **0.75** sits in the
overlap zone safely above the mis-calibrated band but inside what good
extractions clear, with these consequences against the reference set:

- Charts 1, 2 (clean mainstream) — expected to score ≥0.80, auto-commit.
- Chart 3 (idealized-flat) — expected to score ≥0.90 on render-match
  alone (curves trace perfectly), but **must be caught by the
  plausibility prior**, not render-match.
- Chart 4 (same-color dashed) — expected to score 0.70–0.80 due to
  dash-bridging artifacts; this one tests the threshold boundary.
- Charts 5, 8 (out-of-band) — must fail at the profile gate, not the
  render-match gate.
- Charts 6, 7 (boundary dialects) — expected to score 0.65–0.78
  depending on how well the profile handles their conventions.

The threshold trades false-flags against false-confidence: lowering it
auto-commits more dialects but lets calibration errors slip; raising it
flags more for review. **0.75 is the starting point.** Tune downward
only if the threshold pushes good extractions into the review tail at
unsustainable cadence (per ADR-038's "bounded manual work" target).

### Offset tolerance band: ±0.05 MTF units (starting value)

ADR-038's correctness bar is shape (slope agreement), not absolute
position; a uniform vertical offset within a tolerance band is
acceptable. Two anchors set the band:

- **Readings are approximate by nature** (ADR-022) — the source charts
  themselves quote MTF to 1 significant figure at the lower end (~0.05).
- The PR #931 verify pass found tracing-tool errors of median Δ 0.023
  and called them tolerable; the worst legitimate divergences at the
  edge were 0.10–0.25, which we deemed *not* tolerable in PR #931 (we
  re-extracted those entries).

A **±0.05** band brackets the "trace noise" floor from #931 (Δ 0.023
median) with room to absorb half the smallest legitimate readable unit,
without admitting the 0.10+ divergences PR #931 rejected. As with the
render-match threshold, this is a starting point — #935 will measure
real distributions and propose a final value.

### What "calibration against the set" actually means in #935

When #935 lands the real extractor, the calibration pass is:

1. Run the extractor on all 8 reference charts.
2. For each successful trace, compute render-match IoU and the
   point-by-point offset distribution against the verified shapes
   recorded above.
3. Confirm the threshold cleanly separates the 6 charts that should
   trace (1, 2, 3, 4, 6, 7) from the 2 that should refuse (5, 8) and
   the 1 that should pass tracing but fail plausibility (3).
4. If separation is unclean, the threshold and/or tolerance band move
   — never the extractor to "make the threshold work."
