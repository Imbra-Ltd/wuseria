# ADR-054: Per-pass MTF confidence schema

**Status:** Accepted
**Date:** 2026-06-13

## Context

ADR-053 (TTartisan cohort strategy) decided that the autotriage LOW
verdict is honest signal that should reach the user — partial
coverage with a badge, not suppression. Implementation is issue
#1134.

The schema question the implementation forces: how does the
TypeScript type for `mtfReadings[slug]` carry per-pass confidence
without breaking the existing 100+ hand-curated entries on day one?

Three shapes were considered (full enumeration in #1134's investigation
notes); this ADR records what was chosen.

## Decision

Add two fields to the existing `MtfChart` interface:

```typescript
type MtfConfidence = "HIGH" | "LOW";

interface MtfChart {
  aperture: string;
  focalLength?: number;
  confidence: MtfConfidence; // required
  confidenceReason?: string; // set only when confidence === "LOW"
  readings: MtfReading[];
}
```

**`confidence` is required, not optional.** Every existing entry in
`src/data/mtf-readings.ts` is migrated to `confidence: "HIGH"`. The
type system catches a missing field at compile time; an optional field
would silently default to the renderer's interpretation of `undefined`
and obscure data-quality regressions.

**`confidenceReason` is a free-form string, not an enum.** The
authoritative source is `mtfdigitizer.triage.LowReason` (Python
`Enum.value` strings like `precision_below_threshold`,
`prior_failed_center_ge_edge`). Mirroring the enum in TS would
require manual sync on every ADR-052 reason-code change. The
free-form contract is enforced by:

1. The autotriage gate (ADR-052) is the only producer of LOW
   passes; it can only emit valid `LowReason` values.
2. Hand-curated entries never set `confidenceReason` (they are
   HIGH by construction).
3. Validation tests assert: LOW charts have non-empty reason; HIGH
   charts omit reason entirely.

**Multi-reason collapse: emit writes the first reason.** A panel
that trips multiple priors collapses to `verdict.reasons[0].value`
in the emit output. The autotriage CLI run remains the
authoritative full-reason report when the maintainer needs the
list; the per-pass `confidenceReason` on the lens page is the
primary failure code, not a full diagnostic dump.

```
+----------------------+   +---------------------+
| autotriage CLI       |   | mtfReadings.ts       |
| (full reason list)   |   | (first reason only)  |
+----------------------+   +---------------------+
        ^                            ^
        |   ChartVerdict.reasons     |
        |   tuple[LowReason, ...]    |
        |                            |
        +---- triage.triage() -------+
                  ^                  ^
                  |                  |
        +--------------------+       |
        | score_chart()      |-------+
        | check_all()        |  reason[0].value
        +--------------------+
```

### Hand-curated entries are HIGH

Operator-verified data from official manufacturer charts is treated
as HIGH. The field models trustworthiness, not provenance lineage —
a hand-eye-read entry whose values came from a Sigma or Fujifilm
optical-design chart is at least as trustworthy as an autotriage HIGH
pass, often more so. A three-way enum (`HIGH | LOW | OPERATOR`) was
considered and rejected: it would force a UI decision on what
"OPERATOR" means and create a second axis of meaning the user has
to reason about. Two states (HIGH / LOW) on a single axis
(trust the curve / verify before relying on this curve) is
enough.

### Sample data is kept on LOW passes

Per ADR-053 Q5 evidence: extracted readings on LOW passes are
predominantly within ±0.05 of ground truth (41/43 on the
`ttartisan-50mm-f1-2` stopped pass). Nulling samples would discard
mostly-accurate data because of a plausibility-prior violation. The
badge surfaces the gate's verdict to the user; the underlying data
stays available.

## Alternatives considered

### Alt 1 — `confidence?: "HIGH" | "LOW"` (optional)

Rejected. An optional field on day one means hand-curated entries
leave it undefined; the renderer has to treat undefined as "HIGH" by
convention. A missing field cannot then be distinguished from a
forgotten field, and TypeScript's exhaustiveness checks don't fire on
omission. Migration cost (adding `confidence: "HIGH"` to 182 chart
literals in `mtf-readings.ts`) was bounded; ran in one mechanical pass.

### Alt 2 — Three-way enum `HIGH | LOW | OPERATOR`

Rejected. Adds a state the user has to interpret without a clear
behavioural difference from HIGH. The intent of "OPERATOR" is
provenance, but the field's purpose is trust; an honest
provenance-tracking field would be a separate `provenance` field with
its own semantics, not a third confidence value.

### Alt 3 — Mirror `LowReason` as a TS string-literal union

Rejected. Forces manual sync on every reason-code change in ADR-052.
The cost is paid every time the autotriage gate adds a prior. The
free-form string + Python-side enum + validation test on the
TS side captures the contract without the sync burden.

### Alt 4 — Collapse multiple reasons into a `confidenceReasons: string[]`

Rejected. The lens page is a user-facing display surface; the badge
needs one primary failure mode, not a list. Operators who want the
full failure-mode list run `py -m mtfdigitizer.autotriage` for the
authoritative report. Surfacing the list on the page would
double-encode the same information.

## Consequences

### Immediate

- `MtfChart` carries `confidence: MtfConfidence` (required) and
  `confidenceReason?: string` (optional).
- All 182 existing chart literals in `src/data/mtf-readings.ts`
  migrate to `confidence: "HIGH"`.
- TTartisan-emit fans out 25 HIGH + 13 LOW per-pass verdicts that
  match ADR-053's Q2 numbers byte-for-byte.
- Two validation tests in `src/data/mtf-readings.test.ts` enforce
  the field contracts (HIGH/LOW, reason present iff LOW).
- Three pytest cases in `mtfdigitizer/tests/test_emit*.py` enforce
  the emit-side contract (the formatter accepts confidence + reason,
  HIGH emits no reason line, LOW emits the reason).

### Schema-evolution

- Adding a new LowReason code requires: add it to
  `mtfdigitizer/triage.py:LowReason`, no TS-side change.
- Adding a new confidence level (e.g. `MEDIUM`) is a breaking
  change requiring a new ADR.

### UI deferred

The lens-page badge and the `/wiki/mtf-confidence` explainer are
in #1134's scope but **not in this PR**. This ADR commits to the
schema; the UI is the next layer. The middle scope chosen this
session (schema + emit) ships the data shape so the next session
can focus on UI without redesign risk.

### Process

- Autotriage CLI remains the authoritative report for the
  multi-reason case; the emit step writes the first reason only.
- Manual edits to `src/data/mtf-readings.ts` that set
  `confidence: "LOW"` without a `confidenceReason` will fail the
  validation tests. This is by design.
