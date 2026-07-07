# MTF reference set

The eye-verified MTF charts that calibrate the unified digitizer
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
| 8 | `zeiss-touit-32mm-f1-8`               | multifreq-press-kit                | Three frequencies (10/20/40) — extracted via N-freq RIDGE_TRACKING (#791, ADR-075) |
| 9 | `ttartisan-7-5mm-f2-0-fisheye`        | ttartisan-4color-dual-aperture     | Second anchor (ADR-041); fisheye edge-crash stress |
|10 | `ttartisan-af-35mm-f1-8`              | ttartisan-4color-dual-aperture     | Third anchor (ADR-041); right-edge S/M swap (#1199)|
|11 | `zeiss-touit-12mm-f2-8`               | multifreq-press-kit                | Second Touit anchor (ADR-041); corner crowding — edge cells crowd and fade |
|12 | `zeiss-touit-50mm-f2-8-macro`         | multifreq-press-kit                | Third Touit anchor (ADR-041); dotted M + max-panel 10-pair coincidence |

The base set was eight; #9 was added when the TTartisan 4-color
dual-aperture family was introduced. ADR-041 allows multiple Tier 1
anchors per `(brand, style_family)`; the TTartisan 50/1.2 is the
primary anchor for `ttartisan-4color-dual-aperture`, the 7.5 fisheye
is the second (stressing fisheye edge behavior — right-edge 10S crash
and the 30S dip-and-recover #1122 traced to the y-axis chrome strip),
and the af-35 is the third (stressing right-edge S/M crossings where
the solid curve's complex shape fragments its DP path while the
dashed curve looks "solid" by every CV metric — #1199 / S160). The
primary 50/1.2 entry is documented inline in `charts.py` rather than
here. The Zeiss Touit family (`multifreq-press-kit`) likewise carries
three anchors per ADR-041: the 32mm is the primary (#8); the 12mm
(#11) and 50mm macro (#12) completed the family's 396-cell ground
truth via #1332 — together the three cover both M-curve renderings
(dashed on 12/32mm, dotted on the 50mm) and both coincidence failure
modes (stopped-panel 40-band collapse, max-panel 10-pair cascade).

## Verified shapes

### 1. sigma-56mm-f1-4-dc-dn-c — clean Sigma 2-color

- **10 lp/mm** (red): S solid ~0.97 flat from 0 to ~10mm, then knees down to ~0.68 at 14mm; M dashed sits ~0.005 higher across the field, also dips at edge but less steeply.
- **30 lp/mm** (blue): both S and M start ~0.85–0.87 at center; S solid drops smoothly from ~0.80 at 10mm to ~0.33 at 14mm; M dashed holds higher (~0.60 at 14mm).
- Diagnostic: S < M at edge by a wide margin — astigmatism characteristic of f/1.4 wide-open.

### 2. samyang-85mm-f1-4-as-if-umc — Samyang 4-color, two apertures

- **max panel** (top): four solid curves; 10S (dark red) and 10M (pink) both start ~0.91, hold flat to ~14mm, then 10S knees down sharply to ~0.78 at edge while 10M stays high (~0.93). 30S (dark grey) starts ~0.70, sags to ~0.56 around 14mm, then upticks to ~0.55. 30M (light grey) drops more linearly from ~0.70 to ~0.55.
- **stopped panel** (bottom, f/8): all four curves recover to ~0.95–1.00 across most of the field; 30M still drops to ~0.55 at edge while 30S holds ~0.95 — the edge-30M characteristic.
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
- Diagnostic: extracted via the N-frequency RIDGE_TRACKING dispatch (#791, ADR-075). The wide-aperture k=1.8 panel resolves 6 distinct tracks cleanly into 3 y-bands (10/20/40); the stopped k=4 panel hits the ridge-tracker coincidence failure mode where the upper-band curves bundle within ~15 px and the clusterer collapses one pair (S196 probe recovered 5 of 6 tracks). Path A (#791) ships the wide-aperture extraction; stopped panels are gated by Tier 1 eye-read calibration.
- Ground truth lives in `docs/optical-specs/zeiss-touit-32mm-f1-8/eye-read.md` (ADR-048); maintainer-verified 2026-07-06 at ±0.005 on the 0.01-grid readhelpers (#1332): 132/132 cells read — 86 corrected, 46 silently verified, 0 unknown.
- **Verified shapes, k=1.8 (max) panel**: dashed T (M) runs ABOVE solid S from ~3 mm outward at 10 and 20 lp/mm (10M 0.89 vs 10S 0.85 at 2.8 mm, widening to 0.79 vs 0.61 at 14 mm); at 40 the pair nearly touches mid-field and crosses at the far edge (40M 0.30 vs 40S 0.37 at 14 mm). The y-order S/M exchange this panel exposed (#1374) is resolved by the per-band coverage-dashedness discriminator (calibration Run 8): max-panel freq10S/freq10M med |Δ| 0.002/0.004, freq20S/M 0.004/0.006 — under the ~0.01 resolution bar. The 40-band pair sits under the coverage margin (342 vs 333 ridge columns) and keeps the y-order fallback, which the GT confirms correct to mid-field; its far-edge crossing remains the residual (p95 0.066/0.073).
- **Verified shapes, k=4 (stopped) panel**: 10S/10M genuinely coincide (Δ ≤ 0.006 across the field — a collapsed pair at 10 is CORRECT, not a defect); 20M runs 0.01–0.02 below 20S from 2.8 mm; 40S/40M separate widely mid-field (40S dips to 0.56 at 11.2 mm, 40M to 0.47, both recovering toward the edge). The extracted 40S rides the 20-band cluster (med |Δ| 0.164, p95 0.261) and 40M absorbs part of the collapse (med 0.080) — the #791 Path B failure mode, now quantified. An extractor reading stopped freq40S at med |Δ| < 0.02 has resolved the collapse.
- Per-panel in-band (±0.05): max 61/66 (92.4%) since Run 8 (was 45/66 pre-#1374), stopped 48/66 (72.7%) — see `calibration.md` Runs 6 and 8.

### 9. ttartisan-7-5mm-f2-0-fisheye — second TTartisan 4-color anchor

- 800x600 dual-aperture template; solid = S, dashed = T (M). Black/grey = f/2; red/orange = f/8.
- Ground truth lives in `docs/optical-specs/ttartisan-7-5mm-f2-0-fisheye/eye-read.md` (ADR-048); currently seeded with the extractor's mechanical predictions, awaiting maintainer review. The verified-shapes summary below will be filled in once review lands.
- Diagnostic: the 30S corner is the case #1122 fixed — the dispatch was picking the y-axis vertical chrome strip as part of the ridge candidate set, pulling the right-edge value up artificially. An extractor that puts the 30S corner above 0.65 has re-introduced the chrome leak.

### 10. ttartisan-af-35mm-f1-8 — third TTartisan 4-color anchor

- 800x600 dual-aperture template (same as 50/1.2 and 7.5 fisheye); solid = S, dashed = T (M). Black/grey = f/1.8; red/orange = f/5.6.
- Ground truth lives in `docs/optical-specs/ttartisan-af-35mm-f1-8/eye-read.md` (ADR-048); seeded with the extractor's mechanical predictions with maintainer overrides on the stopped 30S/30M corners only (frac=1.0): the two cells flipped from `(0.63, 0.49)` to `(0.49, 0.63)` to record the #1199 S/M label swap as ground truth.
- **f/5.6 stopped panel — diagnostic**: the orange pair crosses at the right edge (mm 11–12) where the solid S30 dives steeply to 0.49 while the dashed M30 stays high at 0.63. The current extractor swaps these labels: per-column ridge DP tracks both physical curves correctly, but the S/M discriminator picks the wrong path as solid because (a) the solid S30 dive-recover-dive shape fragments its DP path (coverage=299, on-ridge runs=41), while (b) the dashed M30 is so smooth the DP locks every centroid (coverage=501, on-ridge runs=4). Neither `Track.coverage` nor `_path_mask_continuity` resolves this — both signals look at the post-DP track, not at the underlying mask's solid-vs-dashed character.
- An extractor that puts the stopped 30S corner at ~0.49 and 30M corner at ~0.63 has resolved #1199. The calibration metric to watch is p95 |Δ| on `ttartisan-af-35mm-f1-8` stopped freq30S and freq30M (currently 0.193 / 0.194 — driven by the single corner sample being swapped).
- The other 86 cells of this anchor extract very cleanly (median |Δ| 0.002–0.003), so this anchor is calibration-net-positive on the aggregate (median 0.0079 → 0.0061 and in-band 94.1% → 94.5% from S159 baseline).

### 11. zeiss-touit-12mm-f2-8 — second Touit anchor, corner crowding

- Same German press-kit template as the 32mm (#8): B&W, solid = Sagittal, dashed = Tangential, three frequencies (10/20/40), stacked panels k=2.8 (max) + k=5.6 (stopped). Sampled to 14 mm — the APS-C image-circle corner where the curves end (#1348); the printed axis runs to 15 mm but 14–15 mm is empty.
- Ground truth lives in `docs/optical-specs/zeiss-touit-12mm-f2-8/eye-read.md` (ADR-048); maintainer-verified (S200, #1348) at ±0.02 on the pre-#1372 read-helpers: 132/132 cells read — 94 corrected, 38 silently verified, 0 unknown.
- **Verified shapes, k=2.8 (max) panel**: 10S holds 0.96 through ~6 mm then dives to 0.62 at the corner while 10M stays at 0.82 — S falls BELOW M at the edge; 20S drops to 0.45 vs 20M 0.58; the 40 pair descends together (0.82 → 0.35/0.31, never more than 0.05 apart).
- **Verified shapes, k=5.6 (stopped) panel**: 10S/10M track together to 0.89/0.85 at the corner; 20S has a dip-and-recover (0.85 at 7 mm, back to 0.87 at 9.8–11.2 mm, then 0.79) while 20M keeps falling to 0.66; 40S dips to 0.70 at 7 mm and recovers to 0.75 at 11.2 mm before the 0.60 corner, while 40M falls monotonically to 0.42 — the corner S/M splits are the extractor stress.
- Extractor signature (calibration Runs 6–7): the crowded corner defeats the tracker — all six fields go ext-None at 14 mm on the max panel (the 10-pair also at 11.2 mm, and at 14 mm on the stopped panel), and the outer-field cells that do pair drift 0.08–0.18 (max 20S p95 0.218, 10S p95 0.168). On the stopped panel 20M/40M under-separate at the corner (EX rides the S track: 40M GT 0.42 vs EX 0.62, p95 0.215). Metric to watch: stopped freq20M/freq40M p95 |Δ| (currently 0.163/0.215) and recovery of the max-panel 14 mm ext-None cells.
- Per-panel in-band (±0.05): max 53/66 (80.3%), stopped 60/66 (90.9%) — see `calibration.md` Run 7.

### 12. zeiss-touit-50mm-f2-8-macro — third Touit anchor, dotted M

- Same press-kit template, but the T (M) curves print DOTTED in lighter ink (the 12/32mm siblings use dashes) and the canvas is larger (1786x2526 vs 1636x1770). Stacked panels k=2.8 (max) + k=5.6 (stopped); sampled to 14 mm per the family convention.
- Ground truth lives in `docs/optical-specs/zeiss-touit-50mm-f2-8-macro/eye-read.md` (ADR-048); maintainer-verified 2026-07-06 at ±0.005 on the 0.01-grid readhelpers (#1332): 132/132 cells read — 78 corrected, 54 silently verified, 0 unknown.
- **Verified shapes, k=2.8 (max) panel**: the macro is nearly astigmatism-free wide open — the 10-pair coincides within 0.02 (0.95 centre → 0.90 edge, no corner dive); 20M sits 0.01–0.04 under 20S (0.91 → 0.78/0.80), widest mid-field; 40S dips to 0.50 at 9.8 mm then recovers to 0.61 at the corner while 40M declines gently to 0.53 — the pair crosses twice (~5.6 mm and ~12 mm).
- **Verified shapes, k=5.6 (stopped) panel**: 10 and 20 S-curves go nearly flat (0.93 → 0.91, 0.89 → 0.85); 20M separates from ~8.4 mm to 0.77 at the corner; 40S holds 0.82 → 0.70 with a mild corner recovery to 0.72, while 40M falls steadily to 0.50 — at 0.22 the widest stopped-panel S/M split in the family.
- Extractor signature (calibration Run 7): the max-panel 10-pair coincidence cascades the dotted-M assignments one band down in the inner field — EX freq10M rides the 20-band (med |Δ| 0.096), 20M rides the 40-band at 1.4–5.6 mm (|Δ| up to 0.169), and the 40-pair goes ext-None at 1.4–4.2 mm; assignments recover from mid-field. The stopped panel repeats the 32mm #791 Path B collapse: 40S rides the 20-band (med 0.089) and 40M under-separates at the corner (GT 0.50 vs EX 0.71; med 0.090, p95 0.226). Metrics to watch: max freq10M med |Δ| (under ~0.01 resolves the dotted-M cascade) and stopped freq40S/freq40M med |Δ| (under ~0.02 resolves the collapse).
- Per-panel in-band (±0.05): max 40/66 (60.6%), stopped 47/66 (71.2%) — see `calibration.md` Run 7.

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
