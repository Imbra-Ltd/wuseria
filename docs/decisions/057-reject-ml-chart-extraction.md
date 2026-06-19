# ADR-057: Reject ML-based chart extraction for v0.8.0, pivot to legend-swatch auto-calibration

**Status:** Accepted; partially superseded by [ADR-058](058-drop-chartparser-revisit-trigger.md)
**Date:** 2026-06-18

> **Partially superseded by ADR-058 (2026-06-18).** The ML-revisit
> trigger list in the Decision section names two upstream repos
> (LineFormer, AI-ChartParser). AI-ChartParser's upstream repo
> (`ywking/ChartParser`) was found to be archived (read-only) hours
> after this ADR landed, making that branch of the trigger structurally
> unreachable. ADR-058 drops AI-ChartParser from the trigger list;
> LineFormer remains. The core decision (reject ML for v0.8.0, pivot
> to legend-swatch auto-calibration) is unchanged.

## Context

Spike #1131 asked: should the MTF digitizer move from its current
classical-CV pipeline (per-brand HSV color profiles, contour following,
anchor-point alignment) to a different detection method? The classical
pipeline works (aggregate calibration: 717 paired, median |Δ| 0.0079, p95
0.0559, in-band 94.1% as of S158) but is brittle — hand-tuned per-brand
profiles, multi-frequency curve overlap failures (#1113–#1127), legend
variation breakage.

Three detection-method branches were on the table:

- **A. Vector-source extraction** — parse SVG / PDF MTF charts where
  manufacturers publish them in vector form. Cleanest possible output
  (exact path data) but only viable if enough brands publish vector.
- **B. ML segmentation** — adopt an OSS chart-extraction model (ChartDETR,
  DePlot, LineEX, Pix2Struct, PaddleOCR-VL, LineFormer, etc.) trained on
  the chart-understanding benchmarks.
- **C. Classical-CV refinement** — keep the current pipeline, refine the
  brittle parts (color profiles, legend mapping, anchor detection) in
  place.

Two probes were run before this decision: AC #3 (vector-source audit,
S158) and AC #5 (OSS extractor re-survey, S159). The findings are below.

### AC #3 — Vector-source MTF availability audit (S158, 2026-06-17)

Probe: fetched the canonical product (and `/spec`-family sub-page) for
one representative lens from each of the 23 brands in the project
portfolio, grepped for `<svg` + `mtf` and for `application/pdf` + `mtf`.
Findings posted at
[#1131-4729998862](https://github.com/Imbra-Ltd/wuseria/issues/1131#issuecomment-4729998862).

| Vector format                        | Brands publishing              | Lenses covered              |
| ------------------------------------ | ------------------------------ | --------------------------- |
| SVG on product `/spec.html` sub-page | Tamron only                    | ~6 / 245                    |
| PDF datasheet with vector MTF text   | Zeiss only                     | ~3 / 245                    |
| Total vector-source                  | **2 / 23 brands (~9%)**        | **~9 / 245 lenses (~3.7%)** |
| All other brands                     | raster only (PNG / WebP / JPG) | —                           |

#1131 set 30% of brands as the threshold for vector-source to win as a
portfolio strategy. The measured 9% falls well below this.

**Vector-source eliminated as portfolio strategy.** Tamron-only vector
extraction remains feasible as a micro-spike if Tamron coverage in
v0.8.0 expands, but is out of scope for the digitizer detection
method.

### AC #5 — OSS chart-extractor re-survey (S159, 2026-06-18)

Probe: re-surveyed the OSS chart-extraction landscape since #942 (~12
months ago), constrained to commercial-use-permissive licenses (MIT /
BSD / Apache-2.0), CPU/single-GPU offline, and per-curve numeric output
(not tables, not VQA). Findings table posted at
[#1131-4738467067](https://github.com/Imbra-Ltd/wuseria/issues/1131#issuecomment-4738467067).

13 candidates evaluated. Three viability buckets emerged:

| Viability bucket                             | Candidates                                                                                                                                                                                       | Why                                                                                      |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| Output-shape mismatch (no per-curve numeric) | DePlot, Pix2Struct ChartQA, PP-Chart2Table, PaddleOCR-VL 1.6, Qwen2.5-VL, InternVL3, ChartDete                                                                                                   | VLM / chart-to-table — emit tables or natural-language, not (x,y) point arrays per curve |
| License blocker                              | LineFormer (no LICENSE), AI-ChartParser (no LICENSE), Plot2Spec (GPL-3.0), WebPlotDigitizer (AGPL), ChartReader (no LICENSE), extract-line-chart-data (LLM wrapper, violates offline constraint) | Cannot adopt commercially or operationally                                               |
| License-clean and line-chart-specific        | **LineEX (Apache-2.0)** — only candidate                                                                                                                                                         | —                                                                                        |

LineEX was selected for the AC #2 prototype slot per the verdict above.

### AC #2 — LineEX viability probe (S159, 2026-06-18)

Per the user-set abort rule, the prototype was time-boxed to 30 minutes
for install/run before adopting. Inspected the LineEX repo
(`Shiva-sankaran/LineEX`, last updated 2025-07-21) via GitHub API.
**Aborted at minute ~5 of the install window** on operational viability
grounds, before any code was run. Findings:

```
+---------------------------------+-------------------------------+
| LineEX requirement              | Wuseria environment           |
+---------------------------------+-------------------------------+
| Python 3.8.12 pinned            | Python 3.13 (host)            |
| PyTorch 1.10.1 (2021)           | No Windows wheels available   |
| Linux-only conda environment    | Windows 10 host               |
| 3 model checkpoints on Google   | Manual download via gdown,    |
|   Drive (KP, CE, legend)        |   no programmatic install     |
| Hardcoded /home/vp.shivasan/    | Linux absolute paths in       |
|   and /home/md.hassan/ paths    |   pipeline.py sys.path.append |
| Coupled 3-stage pipeline.py     | "Modular" in README, tangled  |
|   despite README claim          |   imports in code             |
+---------------------------------+-------------------------------+
```

Reaching a runnable LineEX install would require either a Linux Docker
container (adopting a Docker dependency for production) or a major
dependency rescue (Python 3.8 sandbox + manual checkpoint download +
patching hardcoded paths + decoupling stage 3 from the legend-mapping
module). Even on the optimistic path, **adoption of LineEX as a
production digitizer dependency carries operational debt larger than
the marginal accuracy gain** — the classical CV baseline on the
ttartisan-50mm-f1-2 GT already runs at median |Δ| ≤ 0.005 on most
freqs and < 0.020 worst case (S158 readings table). LineEX,
synthetic-trained on generic line charts and never tuned for MTF
plots, is unlikely to match — and the operational cost is permanent.

**LineEX rejected on operational viability.**

## Decision

Reject ML-based chart extraction for v0.8.0. Keep the classical-CV
pipeline. Pivot the next refinement effort to **per-brand color-profile
auto-calibration via legend-swatch clustering** — the brittleness called
out in #942 (hand-tuned HSV thresholds per brand) is the single highest-
leverage fix on the classical side and does not require an ML
dependency.

```
+----------------------------------------+
|             Detection method           |
+----------------------------------------+
| A. Vector-source           REJECTED    |  9% brand coverage (S158)
| B. ML segmentation         REJECTED    |  output-shape /
|    (LineEX)                            |  license / ops viability
| C. Classical CV refinement KEEP        |  + legend-swatch
|    + legend-swatch auto-cal              auto-calibration as
|                                          next refinement
+----------------------------------------+
```

The next milestone-level decision (v0.9.0+) MAY revisit ML extraction
if any of the following triggers fire:

- **LineFormer or AI-ChartParser publish a permissive LICENSE.** Both
  are line-chart-specific, more recent than LineEX, and (in
  LineFormer's case) use Mask2Former instance segmentation — better
  suited to overlapping curves than LineEX's keypoint detection.
- **A new OSS extractor emerges** that emits per-curve numeric output,
  is Apache-2.0 / MIT / BSD, and runs on Windows / Python 3.10+ without
  a major dependency rescue.
- **Legend-swatch auto-calibration plateaus** at a calibration error
  meaningfully higher than the current 0.0079 median, and a remaining
  brand cohort is consistently below in-band 94.1%.

## Alternatives considered

### Try LineEX anyway via Docker / WSL2

Allocate ~1h to install LineEX in a Linux Docker container on Windows.
**Rejected** — even on success, this adopts a Docker dependency for
production digitization, requires manually downloading 3 Google Drive
checkpoints (no programmatic install), and still needs hardcoded
`/home/` paths rewritten in `pipeline.py`. The operational cost of
"runnable" exceeds the marginal accuracy benefit before any code is
written.

### Try only the KP-detection stage standalone

Skip the full pipeline, install only `modules/KP_detection/` deps (XCiT
ViT + DETR keypoint head). **Rejected** — still pins Python 3.8 +
PyTorch 1.10, still has hardcoded paths, still requires Google Drive
weights. Lighter than the full pipeline but inherits all the operational
debt for arguably the least valuable stage (curve assembly stage 3, not
keypoint detection, is what we wanted to A/B against classical CV).

### Run LineFormer or AI-ChartParser under "research use"

Both are technically more modern than LineEX (LineFormer 2025-11,
AI-ChartParser 2025-12; LineFormer uses Mask2Former instance
segmentation, which fits overlapping MTF curves well). **Rejected** on
the no-circumvent-access principle — building production tooling on a
model with no LICENSE file is process-debt on a tool we may never be
able to adopt. The correct path is the asynchronous one: open
LICENSE-clarification issues on both repos and revisit if they respond
permissively. Tracked as a follow-up below, not as a v0.8.0 dependency.

### Tamron-only vector micro-spike

Write a `tools/tamron/` SVG path-extractor against `/spec.html`.
**Deferred** — bounded cost but ~6 lenses in DB; marginal portfolio
value. Only justified if Tamron coverage in v0.8.0 expands materially.

## Consequences

- **#1131 closes** with this ADR as the decision artifact. All 5 ACs
  resolved: AC #3 vector audit (rejected), AC #5 OSS re-survey
  (LineEX best candidate), AC #2 prototype (aborted on viability), AC
  #1/#4 inputs folded into the alternatives section above.
- **Classical-CV pipeline remains the digitizer.** No code changes
  this session.
- **Next classical-CV refinement: legend-swatch auto-calibration.**
  Cluster legend swatch pixels at extraction time to derive per-chart
  HSV centers instead of per-brand hand-tuned thresholds. Tracked as
  a follow-up task / issue (created post-ADR).
- **LineFormer + AI-ChartParser LICENSE clarification.** Open one-line
  issues on both upstream repos asking for permissive licensing.
  Cheap, asynchronous; positive response would re-open the ML branch
  at v0.9.0+.
- **Vector-source re-evaluation trigger:** if Tamron coverage in
  v0.8.0 grows beyond ~10 lenses, reconsider the Tamron-only
  micro-spike.
- **Documentation:** the legend-swatch auto-calibration approach,
  when implemented, will need its own ADR (not this one) — this ADR
  closes #1131 only; it does not pre-decide the implementation
  details of the next refinement.
