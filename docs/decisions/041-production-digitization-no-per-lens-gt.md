# ADR-041: Production digitization without per-lens ground truth

**Status:** Accepted
**Date:** 2026-06-02

## Context

ADR-038 established the unified MTF digitizer. ADR-040 established the
per-lens `digitization-log.md` and gated it on the presence of both
`plot_box` and `ground_truth` in `referenceset/charts.py`. Read together
they suggest, implicitly, that every digitized lens requires an eye-read
ground-truth tuple — because the runnable subset of the reference set was
how the digitizer was bootstrapped, and `_<LENS>_GT` is currently the only
path that produces an overlay PNG and a digitization log.

Attempting to digitize the four remaining Sigma DC DN C primes (12mm,
15mm, 16mm, 23mm — issue #1018) made the gap visible. Eye-reading 44
values per lens (11 sample positions × 4 fields) is sustainable for the
~10-chart reference set but does not scale to the ~24-brand, hundreds-of-
lenses production queue (epic #790). A maintainer-only bottleneck on
ground-truth entry would either stall the campaign or be circumvented by
agent-produced GT — which would defeat the purpose of GT entirely
(calibration would become self-confirming).

The maintainer-only eye-read rule
(`feedback_agent_no_gt_eye_read`) exists for a real reason — calibration
of the extractor against eye-read truth cannot use agent-produced numbers,
because the agent would be grading its own work. But that reason applies
to the **calibration anchor**, not to every subsequent lens that rides on
the proven calibration.

The two jobs are different:

| Job                         | What GT proves                                           | Per-lens GT?        |
| --------------------------- | -------------------------------------------------------- | ------------------- |
| **Calibration anchor**      | The extractor's profile works for this `(brand, family)` | Yes — by maintainer |
| **Production digitization** | Running the proven extractor on a new chart              | No                  |

ADR-038's confidence design already specifies a per-chart signal that
does not require GT: round-trip render-match plus plausibility priors.
ADR-038 §4 calls this out explicitly: "high-confidence charts (render-
match clears its threshold AND plausibility priors hold) commit
automatically; low-confidence charts are held for the maintainer's
review before commit." That design has been latent because every chart
in the runnable subset also had GT — there was no production path
without it.

This ADR makes the two-tier separation explicit and authorizes the
production path.

## Decision

The MTF digitization workflow is split into two tiers with different
acceptance signals.

### Tier 1 — Calibration anchors

One reference chart per `(brand, style_family)` pair carries eye-read
ground truth. It is the anchor that proves the extractor's profile +
dispatch produces calibrated readings for that family of charts.

- Lives in `tools/mtfdigitizer/referenceset/charts.py` with both
  `plot_box` and `ground_truth` populated
- Drives the calibration runner (`py -m mtfdigitizer.calibrate`)
- Drives the digitization log gate per ADR-040
- Eye-reading is done **by the maintainer only**
  ([[feedback_agent_no_gt_eye_read]] remains in force at this tier)
- Granularity: **minimum one per `(brand, style_family)`**. Adding more
  anchors in the same family is allowed and useful — every additional
  anchor cross-validates the dispatch against a chart the maintainer
  has already eye-verified, which widens the band of profile quirks the
  confidence gate has been tuned against. The minimum is enforced (a
  family with zero anchors has no Tier 1 calibration); the maximum is
  not (more anchors = more confidence-gate signal, at the cost of
  maintainer time).

Current anchors at the time of writing (2026-06-02) — 11 lenses with
GT-populated entries in `referenceset/charts.py`:

| Brand     | Style family                     | Anchor lenses                                                                      |
| --------- | -------------------------------- | ---------------------------------------------------------------------------------- |
| Sigma     | `mainstream-2color-solid-dashed` | `sigma-56mm-f1-4-dc-dn-c`, `sigma-30mm-f1-4-dc-dn-c`                               |
| Samyang   | `mainstream-4color-all-solid`    | `samyang-85mm-f1-4-as-if-umc` (MAX panel)                                          |
| Samyang   | `idealized-flat`                 | `samyang-300mm-f6-3-ed-umc-cs-reflex`                                              |
| 7Artisans | `samecolor-dashed-sm`            | `7artisans-50mm-f1-2-mark-ii`                                                      |
| Tokina    | `2color-frequency`               | `tokina-atx-m-23mm-f1-4-x`, `tokina-atx-m-33mm-f1-4-x`, `tokina-atx-m-56mm-f1-4-x` |
| Tokina    | `2color-frequency-cc-rank`       | `tokina-atx-m-11-18mm-f2-8-x` at 11mm, `tokina-atx-m-11-18mm-f2-8-x` at 18mm       |
| Viltrox   | `bw-dashed-promo`                | `viltrox-af-75mm-f1-2-pro`                                                         |

(The four scaffolded Sigma DC DN C primes — 12mm, 15mm, 16mm, 23mm —
are **not** anchors; they ride the existing Sigma anchors as Tier 2
production digitizations. See #1018.)

### Tier 2 — Production digitizations

Every other lens runs the proven extractor with no per-lens GT. The
acceptance signal is the two-signal confidence gate ADR-038 already
specifies:

1. Round-trip render-match score clears its calibrated threshold
2. Plausibility priors hold (no flatness false-fire, no SM-swap, no
   frequency-swap, no off-grid samples)

Plus a final, lightweight human step:

3. Maintainer glances at the generated overlay PNG and confirms the
   extracted curves track the printed lines

The overlay glance is a sanity check, not a calibration step. The
maintainer does not enter numbers; they answer yes or no to "does this
look right?"

The per-lens workflow becomes:

```
1. py -m mtfdigitizer.extract <lens-slug>
2. open the overlay PNG, eye-check vs source chart
3. confidence gate auto-clears (or holds for review per ADR-038 §4)
4. readings emit to src/data/mtf-readings.ts
5. commit (one lens per commit)
```

No `_<LENS>_GT`, no `plot_box`/`ground_truth` on the `ReferenceChart`
entry, no calibration-runner involvement. The extractor still consults
`charts.py` for the `plot_box` it needs to crop and sample the image —
production lenses that share a template with their anchor (e.g. Sigma
DC DN C primes at 2991×1964) reuse the anchor's box transparently;
templates that differ need a measured plot box but no GT.

### ADR-040 gate narrowing

ADR-040's rule — "logs only when `plot_box` and `ground_truth` are
populated" — was a calibration-runner gate, not a production gate.
Under this ADR it narrows to:

- **Calibration log path** (existing): runs against anchors only;
  emits the EYE vs EX comparison this ADR-040 §3 specifies
- **Production log path** (new): no EYE column; emits chart metadata,
  the sample grid, sparklines, sister-fill counts, plausibility-prior
  outcomes, and the render-match score. Same file name
  (`digitization-log.md`), same banner / `--check` semantics

Both paths produce a `digitization-log.md` in the lens folder so the
discovery story stays uniform — one log per lens, regardless of tier.

### Promotion path

A production lens becomes a calibration anchor by:

1. Maintainer eye-reading the 11×4 GT
2. Adding `_<LENS>_GT` and activating `plot_box`/`ground_truth` on the
   `ReferenceChart` entry
3. The lens's `digitization-log.md` switches from production-path to
   calibration-path on next regeneration

Promotion is triggered when extraction visibly fails on a chart in an
existing family and the failure is profile-level (e.g. a new Sigma chart
in 2028 uses a redesigned palette and the existing profile mismatches).
The signal is the maintainer's overlay glance during the normal
production workflow — the same step that approves Tier 2 commits is also
the early-warning that a chart needs Tier 1 treatment.

## Alternatives considered

| Alternative                                               | Why rejected                                                                                                                                                                                                                                                                                                                     |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Eye-read GT on every digitized lens                       | Does not scale. ~10 lenses calibrated by end of session 111; epic #790 lists ~24 brands × tens of lenses each. A 44-value-per-lens hand-entry bar would either stall the campaign or be circumvented (agent fakes GT, calibration becomes self-confirming).                                                                      |
| One GT anchor per `style_family` globally (cross-brand)   | Style families fit the dispatch logic but not the visual quirks. Sigma's plot-box convention (data-edge, not axis-edge), Samyang's stacked MAX/F8 panels, Tokina's beige background each broke the extractor in different ways during calibration. Per-brand anchoring keeps each quirk anchored to a real chart of that brand.  |
| Per-template anchor (same exact image dimensions)         | More granular than per-`(brand, family)` but adds bookkeeping for diminishing return. Sigma 30mm and 56mm share a template; the 12mm has a different one but the _profile_ (`SPLIT_BY_DASH` + `GEODESIC_DP`) still applies. Template differences are absorbed by a per-lens `plot_box` measurement, not a fresh GT.              |
| Render-match + plausibility priors with no overlay glance | Fully automated commit. Rejected for the production tier today: the confidence gate has been tuned against a small reference set, and lens pages render the digitized SVG to users — a confident-wrong chart is a public regression. The overlay glance is cheap insurance until the gate has been validated across many brands. |
| Drop GT from the reference set too                        | Would remove the ability to calibrate the confidence gate itself. The gate's threshold and the offset tolerance band (ADR-038 §4) require some chart to be eye-truth, otherwise there is no signal that distinguishes "confident-wrong" from "confident-right."                                                                  |
| New top-level digitizer config to flag "production lens"  | Adds state. The same answer falls out for free from `ReferenceChart.ground_truth is None`: that lens is production-tier.                                                                                                                                                                                                         |

## Consequences

- **#1018 unblocks immediately.** The four Sigma DC DN C primes (12mm,
  15mm, 16mm, 23mm) ride the 56mm anchor; no eye-read GT required.
  Their `ReferenceChart` entries stay with `plot_box=None,
ground_truth=None`, OR get a measured `plot_box` if their template
  differs (12mm, 15mm), still with `ground_truth=None`.
- **Epic #790 unblocks at scale.** Production digitizations across all
  ~24 brands become possible at one-lens-per-commit cadence without
  bottlenecking on the maintainer.
- **ADR-038 and ADR-040 pick up cross-references in the same PR** —
  ADR-038's `Status:` line gains `; partially superseded by ADR-041`
  and a blockquote at the top points readers here; ADR-040's `Scope`
  section gets a blockquote noting that the GT-gated log path is now
  the calibration log and that production digitizations emit a parallel
  log. Both edits are atomic with this ADR so the chain stays
  internally consistent at merge time.
- **`tools/mtfdigitizer/extract.py` needs a production entry point.**
  The current pipeline assumes the calibration path
  (`mtfdigitizer.calibrate` plus `mtfdigitizer.log` against GT).
  Building the `py -m mtfdigitizer.extract <slug>` command and the
  production log writer is a follow-up implementation task; this ADR
  authorizes the shape, not the code change. Tracked in #1021.
- **The "agent does not eye-read GT" rule
  ([[feedback_agent_no_gt_eye_read]]) stands.** Its scope tightens to
  calibration anchors only — explicit, not implicit.
- **No regression for existing anchors.** Calibration logs, the
  calibration runner, and the `--check` CI gate keep working unchanged
  for the seven currently anchored entries.
- **The aborted `feat/sigma-16mm-gt-scaffold` branch** (deleted
  2026-06-02) was correct to abandon — the scaffold treated 16mm as a
  Tier 1 anchor when it should have been Tier 2.
