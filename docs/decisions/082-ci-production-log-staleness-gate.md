# ADR-082: Enforce production-log staleness in CI via an inputs-enumerated job

**Status:** Accepted
**Date:** 2026-07-18

## Context

`py -m mtfdigitizer.extract --check` re-renders every committed
production `digitization-log.md` in memory and exits non-zero on any
drift. Until now it ran only manually. The sole automated guard,
`test_extract_check_passes_after_fresh_write`, checks one sigma-16mm
slug in a `tmp_path` — not the committed tree.

This gate-by-omission let two Samyang logs drift on `main` after the
multifreq pipeline PRs (#1382, #1385, #1293) changed the extractor
without regenerating them; the staleness surfaced only during manual
S209 verification (#1386). `quality-gates-staleness` requires the
`--check` invocation to be a required CI status check on the relevant
paths.

The check's inputs are not just the generator source. It reads three
path classes, and compares the last against a fresh render of the
first two:

```
  +---------------+     +--------------------+     +----------------+
  | pipeline code | AND | source chart PNGs  | vs. | committed logs |
  | tools/**      |     | docs/optical-      |     | docs/optical-  |
  |               |     | specs/**/*-mtf.png |     | specs/**/*.md  |
  +---------------+     +--------------------+     +----------------+
              all three are inputs to `extract --check`
```

A filter gating only on `tools/**` would skip the gate on a
source-chart edit or a hand-edited log — the artifacts the check
compares against.

## Decision

Add a dedicated `staleness` CI job that runs
`python -m mtfdigitizer.extract --check` over the committed tree, wired
into the `gate` aggregator as a required check. Its path filter
enumerates every input the check reads: `tools/**`,
`docs/optical-specs/**`, and `.github/workflows/**`.

1. A dedicated job (not a step in `pytest`) so it runs in parallel and
   fires on `docs/optical-specs/**` changes that pytest's `tools`-only
   filter skips.
2. It invokes the same CLI a maintainer runs locally, so CI mirrors the
   local command exactly.
3. A PR touching none of the filtered paths skips the job — a
   legitimate skip-equivalent, since it cannot change the check's
   result.

## Alternatives considered

| Alternative                                                  | Rejected because                                                                                                               |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| A pytest test calling `check_logs()` over the committed tree | Runs only under the `tools` filter, so a source-chart or log edit skips it; also serializes ~2 min into the ~10-min unit suite |
| Filter on `tools/**` only                                    | Omits the source-chart and committed-log inputs — reopens the enumeration gap `quality-gates-scope-agreement` warns about      |
| Always-run job (no filter)                                   | Adds ~3 min to every PR, including ones that provably cannot change the result                                                 |

## Consequences

| Consequence                                               | Effect                                                                 |
| --------------------------------------------------------- | ---------------------------------------------------------------------- |
| Drift can no longer reach `main` silently                 | A pipeline change that forgets to regenerate a log fails the PR        |
| Hand-edited or source-chart-driven drift is caught        | The filter covers the artifact and asset paths, not just the generator |
| ~3 min added to PRs touching `tools/` or `optical-specs/` | Parallel with pytest; no net wall-clock cost                           |
| The manual `--check` remains the local step               | CI is the backstop, not the first line (shift-left)                    |
