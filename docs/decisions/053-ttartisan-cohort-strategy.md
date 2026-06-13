# ADR-053: TTartisan cohort strategy — ship partial coverage (A), defer anchor investment (B), defer detection rewrite (C)

**Status:** Accepted
**Date:** 2026-06-12

## Context

Spike #1130 asked: after 7 consecutive wontdo verdicts on TTartisan
root-cause framings across sessions 138–141 (#1113, #1114, #1115,
#1116, #1120, #1126, #1127), what is the cohort strategy?

Two complementary moves were on the table:

- **A. Cut losses on TTartisan** — close the cohort as partial coverage,
  ship the autotriage HIGH passes as committed data, mark LOW passes
  with a confidence badge + reason code, and move on to the next brand.
- **B. Invest in Tier 1 anchors** — scaffold 2–3 additional
  maintainer-eye-read Tier 1 anchors across the cohort spectrum so the
  autotriage gate is calibrated against ground truth, not priors.

With C (rewrite detection, #1131) and D (outsource) deferred as
explicit escalation paths if A+B's evidence shows systemic gate
misfire rather than edge-case failure.

Two probes were run before this decision (Q2 and Q5 from #1130's
investigation prompts). The Round 0 baseline on
`ttartisan-7-5mm-f2-0-fisheye` (posted at #1130, 2026-06-12) is the
third evidence input.

### Q2 — TTartisan HIGH/LOW per-chart split

Probe: `probe_ttartisan_split.py` (deleted before commit, findings
captured here). Ran `_run_pipeline` over 19 runnable TTartisan
charts, classified verdicts per (chart, aperture pass).

| classification                         | count   | %   |
| -------------------------------------- | ------- | --- |
| entirely HIGH (both passes)            | 6 / 19  | 32% |
| partially LOW (one pass HIGH, one LOW) | 13 / 19 | 68% |
| entirely LOW                           | 0 / 19  | 0%  |

Per-pass totals: 38 passes total — 25 HIGH (66%), 13 LOW (34%).

**Every TTartisan chart ships at least one HIGH-confidence aperture.**

Failure splits cleanly by aperture phase:

- `max` aperture LOW: 8 charts (`precision_below_threshold` dominant)
- `stopped` aperture LOW: 5 charts (`prior_failed_center_ge_edge`
  dominant, plus `not_suspiciously_flat` and `low_freq_ge_high`)

### Q5 — autotriage precision vs the one Tier 1 anchor

Probe: `probe_q5_autotriage_vs_gt.py` (deleted before commit,
findings here). Ran extraction + verdict on `ttartisan-50mm-f1-2`
(88 GT points), compared readings to GT per (aperture, freq), and
asked whether the GT itself satisfies the priors the gate is
checking.

| pass            | verdict | reason           | readings vs GT                                           | GT satisfies prior?                             | classification                 |
| --------------- | ------- | ---------------- | -------------------------------------------------------- | ----------------------------------------------- | ------------------------------ |
| max (f/1.2)     | HIGH    | —                | 43/44 within ±0.05, worst p95 0.072 on freq30M           | yes                                             | TN (correct)                   |
| stopped (f/5.6) | LOW     | `center_ge_edge` | 41/43 within ±0.05; freq30S p95 0.147, freq30M p95 0.151 | **freq30S violates: GT center 0.77, edge 0.84** | TP (correct against the prior) |

**The autotriage gate is correct on this anchor.** The stopped pass
on `freq30S` genuinely has edge > center (0.84 vs 0.77) in the
maintainer eye-read GT — that is real optical behavior at f/5.6 +
30 lp/mm + APS-C sensor edge, not extractor error. The `LOW`
verdict is a true positive _against the prior as written_.

But the extracted readings on the LOW pass are still
predominantly within tolerance (41/43 within ±0.05 across the
four curves). The gate is rejecting _plausibility_, not _accuracy_.

### Round 0 baseline — `ttartisan-7-5mm-f2-0-fisheye` max-aperture

Maintainer eye-pinned reference at 11 sample fractions across four
curves vs extractor output decoded from `09-emit.svg`. Acceptance
band ±0.05 per ADR-038.

| Field  | median \|Δ\| | p95 \|Δ\| | within-band | failure surface          |
| ------ | ------------ | --------- | ----------- | ------------------------ |
| S10_F2 | 0.008        | 0.166     | 9/11        | right-edge collapse      |
| T10_F2 | 0.011        | 0.057     | 9/11        | sample[1] dive (#1122)   |
| S30_F2 | 0.044        | 0.061     | 7/11        | systematic underestimate |
| T30_F2 | 0.016        | 0.258     | 9/11        | right-edge catastrophic  |

Median is inside the band on three of four fields; p95 is outside on
all four. **The right edge is the dominant failure surface, not low
field.** #1122's sample[1] dive (Δ -0.057) is real but is the
4th-largest single failure on the chart, not the dominant one.

### Synthesis across the three inputs

1. **The cohort is shippable.** Zero entirely-LOW charts. 66% of
   per-pass verdicts are HIGH. The badge story under A works
   because nothing is entirely unshippable.
2. **The gate is not buggy, it is over-strict on stopped passes.**
   Q5 shows the gate correctly flags a real prior violation, but
   the underlying readings are within tolerance. More Tier 1
   anchors (B) would not change this — they would just confirm
   the prior is unsound for stopped-down apertures on this brand.
   The actual fix shape is **per-style-family prior whitelist**, not
   anchor scaffolding.
3. **The remaining errors are right-edge convergence, not low-field
   dropout.** Round 0's worst failures are at frac 0.9–1.0 across
   three of four fields. This is a different failure mode from any
   of the 7 wontdo RCs — it's curve convergence near the legend
   box compounding with the DP's inability to follow steep falls.
   No current Tier 1 anchor exercises the fisheye's specific
   right-edge geometry, but adding one wouldn't fix the DP
   algorithm — it would only quantify how bad the failure is.

## Decision

**Adopt A. Defer B. Keep C+D as triggered escalation paths.**

A is the only move whose cost is bounded and whose value is
proven by Q2: every chart ships HIGH data on at least one
aperture. The badge surfaces honesty about confidence without
suppressing the data we have.

B is rejected as currently framed because Q5 shows the gate is
correct against the one anchor we have. Adding more anchors would
not improve gate precision — it would document that the prior
itself is wrong for stopped-down TTartisan passes. The shape of
the fix that argument points at is a **per-style-family prior
whitelist**, which is a different issue with a different cost
profile from anchor scaffolding. That work is captured separately
(see "B' replacement: per-family prior whitelist" below) and is
**not blocking** A.

C (#1131) and D stay deferred. Round 0's findings give us
something C didn't have before — a concrete acceptance bar
(median |Δ| ≤ 0.03, p95 |Δ| ≤ 0.05 across all 4 fields, no
catastrophic |Δ| > 0.10) — but A ships value first regardless of
whether C ever fires.

```
+--------------------------------+
|  Spike #1130 evidence pass     |
+--------------------------------+
   |
   v
+--------------------------------+
|  A   — ship badge + reason     |  IN: shippable per Q2
|        code on LOW passes      |  OUT: 66% HIGH committed,
|        (issue: #1134)          |       34% LOW badged
+--------------------------------+
   |
   v
+--------------------------------+
|  Monitor metric over 4 weeks   |
|  (HIGH-vs-LOW ratio across     |
|  next brand cohort: 7Artisans  |
|  or Tokina)                    |
+--------------------------------+
   |
   v   if HIGH-ratio < 50% on next brand
   |   OR if maintainer/user pushback on
   |   badged data
   v
+--------------------------------+
|  B'  — per-family prior        |
|        whitelist               |  (replaces original B scope)
|        (issue: #1135)         |
+--------------------------------+
   |
   v   if B' insufficient AND
   |   gate misfire rate > 30%
   |   across new anchors
   v
+--------------------------------+
|  C   — detection-method        |
|        rewrite (#1131)         |
+--------------------------------+
```

### B' — replacement for B's original scope

The original B was "scaffold 2–3 Tier 1 anchors." Q5 shows that
won't move the needle on the current failure mode. The replacement
is:

**B' — per-style-family prior whitelist.** Allow each `MtfProfile`
(or `style_family`) to opt out of specific priors that are
unsound for its optical population. For `ttartisan-4color-dual-aperture`
stopped passes, suppress `center_ge_edge` and
`not_suspiciously_flat`. Reasoning: stopped-down APS-C wide
primes routinely have edge > center on 30 lp/mm (corner sharpness
recovers as the aperture diffraction softens the center less),
and stopped-down 10 lp/mm curves routinely sit flat at ~0.95
(close to MTF ceiling).

This is **deferred**, not rejected. Trigger to file: when A ships
and one of two signals appears: (a) badged data accumulates
without user pushback (suggests the whitelist is unnecessary —
LOW + badge is enough), or (b) a second brand exhibits the same
"correct readings, gate flags plausibility" pattern (suggests
the per-family whitelist is the right shape).

### Q3 carry-forward — other brands at the same risk

The spike prompt asked whether 7Artisans / Tokina / Viltrox are at
the same trap. Not measured this session. Q2's approach
(per-(chart, aperture) verdict aggregation) is reusable. The
trigger for measuring is **before** committing to A on the next
brand: run the same probe on 7Artisans first, decide whether the
brand needs the same badge treatment or whether it ships full
HIGH-confidence.

### Q4 carry-forward — anchor cost envelope

Per-anchor maintainer cost from #1093: 88 GT points x 5 minutes
per eye-read = ~7 hours of focused work. Three anchors = ~21
maintainer-hours. **Not spent now** because Q5 shows the spend
wouldn't move the gate; carried as a budget envelope for if B'
proves insufficient.

### C/D escalation triggers

C (#1131) fires when **either**:

1. B' lands and the gate's misfire rate on new anchors exceeds
   30% across at least 3 anchors covering the cohort spectrum
   (clean / mid / hard) — pointing at systemic algorithm failure,
   not prior tuning.
2. Two consecutive new-brand cohorts produce <50% HIGH-pass
   ratios under A's badge treatment — suggesting the current
   pipeline can't reliably serve the broader brand portfolio.

D fires only if C runs and produces no method with median |Δ| ≤
0.03 / p95 |Δ| ≤ 0.05 against the Tier 1 anchor set after a
6-week timebox.

## Alternatives considered

### Alt 1 — A+B in parallel (the original proposal)

Rejected based on Q5. Adding 2–3 more anchors won't change what
the gate decides; the gate is correct, the prior is unsound. The
maintainer-hour spend on B (~21h) is better deferred until B'
provides a path to using new anchors against tuned priors.

### Alt 2 — B only (skip A)

Rejected. A ships value next session; B's spend takes 21
maintainer-hours and produces no shippable user-facing data on
its own. Sequence matters: A unblocks the data flow, B' (when
triggered) tunes the gate against the data A produces.

### Alt 3 — Neither (close #1112 and move on with full-LOW suppression)

Rejected. Suppressing 34% of per-pass verdicts hides shippable
HIGH passes on 13 of 19 charts. Q2 measured this directly: the
cohort is more shippable than the wontdo pattern suggested,
because the 7 wontdo RCs were all _within_ the LOW set, not
across the whole cohort.

### Alt 4 — Jump straight to C (#1131)

Rejected as too expensive given the evidence. Q5 shows the
current pipeline produces ±0.05 readings on 41/43 samples even
on the LOW pass; the gate's verdict is about plausibility, not
accuracy. A pipeline rewrite would be a sledgehammer for a prior
tuning problem.

## Consequences

### Immediate (this spike)

- Cohort epic **#1112 closes** when issue #1134 files. The
  cohort-hardening goal is replaced by A's badge framework, which
  is brand-agnostic, not TTartisan-specific. #1112's probe-first
  policy is operational and survives the epic closure.
- **#1122 stays open as P3** and is unblocked. With A in flight,
  the fisheye right-edge investigation can run on its own
  schedule, and Round 0's right-edge findings (not the
  originally-named sample[1] dive) are the actual target if
  someone picks it up.
- **#1131 stays open** as documented escalation path.

### Schema and UI

- `mtfReadings[slug]` gains a per-pass confidence field
  (`HIGH | LOW`) and a reason code (`precision_below_threshold |
prior_failed_center_ge_edge | ...`).
- Lens pages render LOW passes with a visible "confidence: LOW"
  badge linking to a wiki page explaining the digitization
  pipeline and what LOW means.
- Samples on LOW passes are **kept**, not nulled. Hiding them
  hides what we have; the badge is the user-facing honesty.
- The exact schema shape is decided in issue #1134, not here. This
  ADR commits to the _direction_, not the field name.

### Process

- New brands run Q2-style HIGH/LOW per-chart probe **before**
  committing data to `lenses.ts`. The probe is cheap (~2 min per
  brand) and reuses `_run_pipeline`.
- Probe-first remains the policy for any new RC framing. The 7-of-7
  wontdo pattern is the validation that the policy works — every
  probe ruled out a wrong fix that would have shipped buggy data.

### Risks

1. **User trust** — a "LOW confidence" badge may be read as "wrong
   data," even when the underlying readings are within ±0.05. Issue
   #1134 must include a wiki page and UI copy that explain what
   LOW means without scaring users away.
2. **Cohort-creep into new brands** — A makes it easy to ship
   partial coverage on every brand, which could mask real
   detection failures that should escalate to C. The Q2 probe
   gate (HIGH-ratio < 50% on a new brand triggers re-evaluation)
   is the control.
3. **Prior over-strictness on other brands** — Q5's finding (gate
   correct, prior unsound) may apply beyond TTartisan stopped
   passes. If 7Artisans / Tokina / Viltrox exhibit the same
   pattern, B' fires sooner than anticipated.

### Out of scope for this ADR

- Per-chart fine-tuning on TTartisan (per #1112)
- Rewriting the autotriage gate (ADR-052 stays)
- Detection method choice (deferred to #1131)
- Implementation of A — issue #1134
- Implementation of B' if/when triggered — separate issue

## Probe scripts

Both deleted before this commit per `quality.md` §Probe scripts.
Verbatim findings preserved above:

- `tools/probe_ttartisan_split.py` (Q2)
- `tools/probe_q5_autotriage_vs_gt.py` (Q5)
