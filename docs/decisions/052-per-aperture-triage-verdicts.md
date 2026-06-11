# ADR-052: Per-aperture verdicts in the auto-triage gate

**Status:** Accepted
**Date:** 2026-06-11

## Context

`autotriage._run_pipeline` predates ADR-044 (multi-aperture per-chart
orchestrator) and ADR-043 (Fujifilm per-frequency chart sets). It still
makes a single `extract_chart()` call with the full unfiltered profile,
which:

1. Errors with `KeyError` on multi-aperture charts where the score /
   priors path references a curve from an aperture bucket the single
   extraction couldn't populate cleanly (e.g. TTartisan
   `stopped-10-red`).
2. On the one multi-aperture chart that survives (the Tier 1 anchor
   `ttartisan-50mm-f1-2`), produces a conflated verdict where max + stopped
   render-match precision blend into one number.
3. Means the gate has been silently inactive for the entire TTartisan
   cohort (#1112) and the Fujifilm-permfreq cohort (ADR-043) since
   those style families landed.

The runner additionally filters by `c.ground_truth`, which masked the
bug — only the GT-having anchor reached `_run_pipeline`, and it happened
to work. Lifting that filter (the goal of #1112's quantitative re-triage
ask) exposes the gap on every other multi-aperture chart.

`calibrate._extract_multi_aperture_chart` already solves the extraction
half for ADR-044; `calibrate._extract_per_frequency_chart` does the
same for ADR-043. The autotriage runner needs the same fan-out, plus
a per-aperture decision on what the verdict shape should look like.

The fan-out question has only one credible answer (run the gate per
aperture using the filtered profile, exactly like calibration). The
verdict-shape question is the real architectural choice: one chart-level
verdict or one per aperture.

## Decision

**`ChartVerdict` is emitted per (chart, aperture).** Single-aperture
charts continue to emit one verdict with `aperture=None`.

The `triage()` function itself stays unchanged — it's a pure rule over
render-match + priors, both of which operate on a single readings set.
The runner becomes responsible for fan-out:

```
+---------------------+
|  ReferenceChart      |
+---------------------+
          |
          v  (profile_for_chart)
+---------------------+
|  MtfProfile          |  apertures_per_chart=("max","stopped") ?
+---------------------+
          |
   +------+------+
   | yes         | no
   v             v
+--------+   +-----------+
| fan    |   |  single    |
| out    |   |  pipeline  |
| per    |   |  call      |
| aperture|  +-----------+
+--------+        |
   |              v
   v        +----------+
+--------+  | one      |
| N      |  | verdict  |
| verdicts| +----------+
+--------+
```

Aggregation rule for callers that need a single chart-level signal
(deploy-gate, summary count): a chart is `HIGH` iff every aperture is
`HIGH`. The aggregation lives in the caller, not the verdict; the
verdict stays per-aperture so the reason codes route the maintainer to
the actual failing aperture.

The same shape applies to ADR-043 per-frequency charts: each frequency
view is extracted independently with a filtered profile, so a verdict
per (chart, frequency) is the analogous unit. ADR-043 charts are out of
scope for this ADR's initial fix — the TTartisan ADR-044 case ships
first; ADR-043 fan-out is a follow-up issue. The verdict shape carries
an optional `pass_key` field that holds the aperture label for ADR-044
and is reserved for the frequency label for ADR-043.

### Why per-aperture, not per-chart

A multi-aperture chart's two extractions hit fully disjoint hue buckets
with disjoint failure modes — the max-aperture pass uses black + grey
curves, the stopped pass uses red + orange. A precision dip on `max-30-grey`
and a precision dip on `stopped-10-red` are different bugs. A
chart-level aggregate that just reports `LOW: PRECISION_BELOW_THRESHOLD`
buries which extraction is actually broken.

Per-aperture verdicts:

- Reason codes carry the failing aperture by construction (`(chart,
"max", PRECISION_BELOW_THRESHOLD)` is a different debug target from
  `(chart, "stopped", PRIOR_FAILED_CENTER_GE_EDGE)`)
- Render-match precision per aperture is computable today (the profile
  fan-out filters it for free); aggregating loses the granularity
- The maintainer routing in `triage.py:23` (`PRIOR_FAILED_*` → chart
  review, `*_BELOW_THRESHOLD` → extractor work) already reads as a
  per-failure-mechanism routing rule — making it per-aperture extends
  the same reasoning one layer
- Per-aperture is the diagnostic shape the quantitative re-triage of
  #1112 needs anyway; flattening to chart-level just to flatten loses
  exactly the signal the re-triage was trying to extract

### Why not aggregate to one verdict and put the aperture in reasons

Considered. Rejected: it shoves what is a first-class dimension (which
extraction pass failed) into a string field on a violation. Downstream
consumers (deploy-gate report, future cohort_triage runner) would need
to parse reason codes to reconstruct per-aperture status — exactly the
information the verdict is supposed to surface directly.

### Why not extend `ChartVerdict.profile_name` to include aperture

Considered. Rejected: `profile_name` is already a stable identifier
matching the declared profile in `profiles/declared.py`; suffixing it
(`"ttartisan-4color-dual-aperture/max"`) couples the verdict's identity
field to fan-out internals. A dedicated `pass_key` field carries the
semantics without overloading.

## Alternatives considered

1. **One chart-level verdict, aggregate fan-out internally.** Loses per-
   aperture diagnostic signal. Caller can always aggregate per-aperture
   verdicts to chart-level; the reverse is impossible.
2. **Keep single-call path, filter the profile per aperture inside
   `_run_pipeline`.** This is the fan-out we're doing — the choice is
   only whether to surface the resulting per-aperture decisions or
   collapse them.
3. **Don't fan out; emit a single conflated verdict using the full
   profile.** Status quo. Errors on most cohort charts and produces
   meaningless verdicts on the rest. The bug this ADR exists to fix.
4. **Per-curve verdicts (one per `freqNS` / `freqNM` field).** Too
   granular — render-match precision is naturally a per-extraction-pass
   number (mean across fields), and per-curve priors are already
   surfaced as `PriorViolation` entries inside one verdict's `reasons`.
   Per-aperture is the right slice.

## Consequences

- `ChartVerdict` gains an optional `pass_key: str | None` field. `None`
  for single-aperture charts (back-compat with all current consumers);
  the orchestrator-side aperture label for ADR-044 charts.
- `_run_pipeline` returns `list[tuple[ChartVerdict, ExtractedChart,
Path, PlotBox]]` instead of one tuple — single-aperture charts return
  a list of length 1.
- `triage_chart()` keeps its existing `ChartVerdict` return for the
  single-aperture case and gains a `triage_chart_all_apertures()`
  sibling for the multi-aperture case. Callers that don't care about
  fan-out can use `triage_chart()` on single-aperture charts; multi-
  aperture callers must use the new entry point.
- The `autotriage.main()` `c.ground_truth` filter is lifted; the gate
  runs on every chart with a `plot_box`. Today this expands the TTartisan
  cohort from 1 chart to 18 and exposes the per-aperture verdicts for
  each. ADR-043 per-frequency expansion lands in a follow-up issue.
- The 3-panel review writer (`write_review`) is called once per LOW
  verdict, so per-aperture LOW verdicts produce per-aperture review
  files. File naming gains the aperture suffix
  (`<slug>-max-review.html`).
- The findings doc (`referenceset/triage.md`) gains a per-aperture
  column. The PRECISION_THRESHOLD / IOU_THRESHOLD tuning stays
  shared across apertures for now; a follow-up may need per-aperture
  thresholds if the max + stopped passes turn out to have systematically
  different precision distributions.
- Pre-existing fixtures and tests that consume `ChartVerdict` keep
  working when `pass_key` defaults to `None`. The two test files
  affected (`test_triage.py`, `test_autotriage.py`) need updates for
  the new return shape of `_run_pipeline`.
