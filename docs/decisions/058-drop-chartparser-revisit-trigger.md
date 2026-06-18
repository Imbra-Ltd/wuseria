# ADR-058: Drop AI-ChartParser from ADR-057 ML-revisit triggers (upstream archived)

**Status:** Accepted; partially supersedes [ADR-057](057-reject-ml-chart-extraction.md)
**Date:** 2026-06-18

## Context

ADR-057 (2026-06-18) rejected ML-based chart extraction for v0.8.0 and
listed three revisit triggers for v0.9.0+. The first trigger names two
upstream repos:

> **LineFormer or AI-ChartParser publish a permissive LICENSE.**

Per ADR-057's Consequences section, the follow-up action was to file
LICENSE-clarification issues on both upstream repos. While executing
that follow-up in Session 163 (#1206 LineFormer, attempted equivalent
for AI-ChartParser), the AI-ChartParser upstream repo
(`ywking/ChartParser`, https://github.com/ywking/ChartParser) was found
to be **archived** by its owner.

Archived GitHub repos are read-only. Issues cannot be opened. PRs
cannot be merged. The probability of an archived repo receiving a
LICENSE addition is effectively zero — the maintainer has signalled
the project is no longer maintained.

This makes the AI-ChartParser branch of the trigger list **structurally
unreachable**. The trigger as written can never fire on that repo.
Leaving it in place misleads any future session re-reading ADR-057.

## Decision

Drop AI-ChartParser from the ADR-057 ML-revisit trigger list. The
trigger reduces to a single repo:

```
+----------------------------------------------------------------+
|   ADR-057 ML-revisit trigger #1                                |
+----------------------------------------------------------------+
|   BEFORE (ADR-057, 2026-06-18 AM):                             |
|     LineFormer OR AI-ChartParser publishes permissive LICENSE  |
|                                                                |
|   AFTER (this ADR, 2026-06-18 PM):                             |
|     LineFormer publishes permissive LICENSE                    |
|     (AI-ChartParser dropped — upstream archived)               |
+----------------------------------------------------------------+
```

The other two ADR-057 triggers (new OSS extractor emerges; legend-swatch
auto-calibration plateaus) are unchanged. The core ADR-057 decision
(reject ML for v0.8.0, pivot to legend-swatch auto-calibration) is
unchanged.

Upstream archive state of `ywking/ChartParser` is captured here for
audit trail — so a future session does not re-discover this and ask
why one of the two named repos was silently removed.

## Alternatives considered

### Edit ADR-057 in place

Strike the AI-ChartParser mention directly in ADR-057. **Rejected** —
ADRs are immutable once merged (per `base/docs.md`); the supersession
ADR is the documented mechanism for amendments. Keeping ADR-057 frozen
preserves the original decision context.

### Leave the trigger as written

Do nothing; let a future session re-discover the archived state.
**Rejected** — the trigger is structurally unreachable, and the next
re-reading would require re-running the GitHub API check that S163
already ran. Capturing the state once is cheaper than re-discovering it.

### Keep AI-ChartParser in the list with an "archived" annotation

Leave the name but add a parenthetical "(archived as of 2026-06-18)".
**Rejected** — a trigger that can never fire is not a trigger. The
annotation pattern bloats the trigger list without removing the dead
lead, which is the actual problem #1207 set out to fix.

## Consequences

- **ADR-057 trigger list reads with one repo.** Any session re-reading
  ADR-057 should also read this ADR; the partial-supersession banner
  on ADR-057 (added in the same PR as this ADR) makes the link
  discoverable.
- **#1207 closes** on the PR that merges this ADR.
- **#1206 (LineFormer LICENSE-watch) remains the sole upstream
  ML-trigger monitor.** No new monitor is created — there is no live
  upstream repo to monitor for AI-ChartParser.
- **No change to current digitizer behavior.** This ADR amends a
  v0.9.0+ revisit trigger; the v0.8.0 classical-CV pipeline is
  unaffected.
- **Process pattern preserved.** Verifying upstream state before filing
  an issue (the action that surfaced the archive) is the
  worth-keeping process finding — captured in the S163 journal entry
  rather than codified as a rule here.
