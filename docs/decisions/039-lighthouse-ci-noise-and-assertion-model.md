# ADR-039: Skip Lighthouse CI on lockfile-only PRs and keep the single-run perf gate elsewhere

**Status:** Accepted
**Date:** 2026-05-30

## Context

The CI quality gate runs Lighthouse against the production build of every
pull request and asserts `categories:performance: ["error", { "minScore":
0.8 }]` on four URLs (`/`, `/lenses/`, `/cameras/`, `/genre/`). The default
`numberOfRuns` of `1` is implicit. A failing assertion blocks merge via
branch protection.

Session 104 (2026-05-30) merged four dependency-only PRs (#958, #959,
#960, #962). The fifth, **PR #961 (astro 6.3.7 → 6.4.2)**, failed
Lighthouse twice with a homepage performance score of `0.69` then `0.58`.
A single retry of the first failure passed at `≥ 0.80`. The three sibling
Dependabot PRs running Lighthouse the same minute against the same base
SHA all passed.

To check whether the astro 6.4 bump was a real regression, both builds
were produced locally back-to-back on the same machine and compared
byte-for-byte:

| Property                        | astro 6.3.7 (`main`) | astro 6.4.2 (PR #961) |
| ------------------------------- | -------------------- | --------------------- |
| Emitted files                   | 483                  | 483                   |
| Homepage `index.html` SHA-256   | `9fe89ed2…`          | `9fe89ed2…`           |
| `_astro/*.js` unique hashes     | 14                   | 14 (identical set)    |
| Total `dist/` size              | 20 MB                | 20 MB                 |
| Diff on full recursive SHA list | empty                | empty                 |

The two builds are bit-for-bit identical. The browser cannot tell them
apart, so Lighthouse cannot measure a real difference between them.

The six measurements collected against this single artifact:

| #   | Score | Run                             | Astro version |
| --- | ----- | ------------------------------- | ------------- |
| 1   | 0.69  | PR #961 SHA `b5af403`, original | 6.4.2         |
| 2   | ≥0.80 | PR #961 SHA `b5af403`, rerun    | 6.4.2         |
| 3   | 0.58  | PR #961 SHA `7c92eb7`, rebased  | 6.4.2         |
| 4   | ≥0.80 | PR #959 (eslint sibling)        | 6.3.7         |
| 5   | ≥0.80 | PR #960 (sitemap sibling)       | 6.3.7         |
| 6   | ≥0.80 | PR #962 (react sibling)         | 6.3.7         |

Three runs against bit-identical 6.4.2 artifacts produced scores spanning
`0.58 → ≥0.80` — at least 22 percentage points of variance. Three runs
against bit-identical 6.3.7 artifacts all passed. The variance is the
GitHub Actions shared runner, not the code. Pairing a single-run
performance score with a hard `error` threshold positioned roughly at the
score's mean guarantees false positives over time on any PR that happens
to land in the lower tail.

The current setup conflates two distinct intents:

1. **Catch real performance regressions** in code changes that affect the
   served bytes (component changes, new dependencies the browser
   executes, hydration changes, image policy changes).
2. **Re-measure performance** on every PR regardless of whether the
   served bytes changed.

(2) is the source of the false positives. (1) is the value the gate is
supposed to provide.

## Decision

**Skip the Lighthouse CI job on PRs that change only lockfile or
package-manifest files**, and leave the existing single-run / 0.80
threshold model in place for every other PR.

The existing `.github/workflows/ci.yml` already uses a `changes` job
(dorny/paths-filter or equivalent) to gate downstream jobs by what the PR
touched. Add a filter group that matches **only `package.json` and
`package-lock.json`** and is `true` when the PR's file set is a subset of
those paths. The `lighthouse` job runs unless that group is `true`. The
`build` job continues to run on every PR, so dependency-bump correctness
(compile, type-check, link check, gitleaks, CodeQL) is still verified.

Concretely:

- Dependency-only PRs (Dependabot bumps, manual `npm install` PRs) skip
  Lighthouse — the served bytes either don't change at all (as proven by
  the byte-identical check today) or change in ways the build job already
  catches.
- Code or content PRs run Lighthouse exactly as today — one run per URL,
  0.80 perf threshold, hard error.
- A PR that mixes a lockfile bump with a code change still runs
  Lighthouse, because the file-set is not a subset of the lockfile-only
  group.

The single-run, 0.80-threshold model on code PRs is deliberately
**unchanged**. Today's evidence quantifies the runner's variance but does
not by itself establish that the current threshold is the wrong threshold
for real code changes — only that it is the wrong gate for byte-identical
artifacts. Tightening or loosening the model on code PRs is a separate
decision worth its own evidence base.

If a code-PR Lighthouse failure later proves to also be a false positive,
the model on code PRs is revisited in a follow-up ADR, with the
alternatives in the next section as the starting menu.

## Alternatives considered

### A — `numberOfRuns: 3` with `aggregationMethod: median-run`

LHCI's canonical fix for single-run variance: take the median of three
runs. With three independent samples the median is robust to a single
outlier in either direction.

Rejected for the dependency-only case because it pays roughly +60s of CI
time on every PR to compensate for noise we are measuring on artifacts
that cannot have changed. The cost is constant; the benefit is zero on
the cases that caused this ADR.

Not adopted for code PRs either, in this ADR, because the cost is borne
on every code PR (the common case) to insure against a class of failure
that hasn't yet been demonstrated on a code PR. Worth revisiting if it
does.

### B — `numberOfRuns: 2` with `aggregationMethod: optimistic`

Cheaper than median-of-three (~+30s) and survives one bad run, but
survives only one. Today's evidence shows the astro 6.4 PR failed two
runs out of two on the rebased SHA — `optimistic` would still have
failed. Not a reliable fix even at the cost.

### C — Lower the perf threshold from 0.80 to ~0.65 with 1× run

The cheapest possible change: no CI time added, no workflow restructure.
The gate becomes a cliff detector — it fires only when something has
gone badly wrong.

Rejected because it weakens the signal everywhere to insure against
noise on a subset of PRs. A real code regression that drops perf from
0.85 to 0.70 would now ship silently. The dependency-only false positive
is solvable without paying this cost.

### D — Per-metric assertions (LCP, TBT, CLS) instead of the combined category score

The combined `categories:performance` score weights five metrics, of
which TBT and LCP are the dominant variance contributors on CI runners.
Asserting each metric independently against an absolute threshold (e.g.
LCP < 2.5s, CLS < 0.1) is closer to what we actually care about and is
documented to be less noisy than the combined score.

Rejected for this ADR because it is the largest change of the four — it
requires choosing thresholds per metric and validating them against a
real measurement baseline. That work is worth doing, but as its own
spike, not bundled with the immediate fix.

### E — Downgrade perf to `warn` and keep 1× run

The minimum change with the maximum loss of value. The perf number would
still be reported in the run output, but nothing would ever block on it.
Effectively removes the gate. Rejected — the goal is a working gate, not
no gate.

### F — Skip Lighthouse entirely on PRs

Remove the Lighthouse job from the PR workflow and run it only on
post-merge `main` builds. Cheapest possible CI on PRs. Rejected because
the value of a pre-merge perf gate is precisely that a regression is
caught before it ships. Catching it post-merge means rolling back, which
is far more disruptive than blocking a PR.

## Consequences

- Dependabot bumps and any other lockfile-only PRs merge without
  consulting Lighthouse. Today, four such PRs would have merged cleanly
  on this rule; one (PR #961) would not have been blocked at all.
- The pre-merge perf gate continues to defend `main` on every code or
  content change, with no regression in coverage for the changes that
  can actually affect served bytes.
- Lighthouse CI time on dependency-only PRs drops from roughly 90
  seconds to zero. Lighthouse CI time on code PRs is unchanged.
- The 0.80 / single-run / hard-error model on code PRs is retained on
  inertia. If the next Lighthouse failure on a code PR also turns out to
  be a false positive, this ADR explicitly invites a follow-up to pick
  one of the alternatives (median of three, per-metric, lower
  threshold) on the basis of new evidence rather than today's
  dependency-only data.
- The Lighthouse config `lighthouserc.json` does not change. The fix
  lives entirely in `.github/workflows/ci.yml`, scoped to the workflow
  layer, which is the right home for "when does this job run."

## Implementation

Implementation is out of scope for this ADR. The work to update
`.github/workflows/ci.yml` and verify the gate-skip on a follow-up
Dependabot PR is tracked in spike #978's acceptance criteria. The ADR
records the decision; the spike's remaining checkbox tracks the
mechanical change.
