# ADR-078: Widen the deploy-pages retry to three attempts with growing backoff

**Status:** Accepted
**Date:** 2026-07-07

## Context

ADR-077 scoped a single retry (two attempts, 30s backoff) to the
`actions/deploy-pages` step and recorded a concrete revisit trigger: "if
a deploy is ever observed where both automated attempts fail on backend
load (not a real diff or config fault), widen to a bounded loop of three
attempts with increasing backoff."

That trigger fired on 2026-07-06, run `28769781777` (the #1375 merge):

- Attempt 1 and attempt 2 both failed ~30s apart with
  `Deployment failed, try again later.`
- `build`/validate was green and wuseria.com served HTTP 200 throughout —
  a cosmetic red, not an outage.
- A manual `gh run rerun --failed` at +4 minutes succeeded in 15s.

This was a multi-minute Pages backend flake, not the S205-style sustained
outage. Two attempts spanning ~30s cannot bridge it; a third attempt at
+2–3 minutes would have.

## Decision

Widen the step-scoped retry to a bounded three-attempt sequence with
growing backoff. Everything else from ADR-077 is retained: the retry
stays scoped to the `deploy-pages` step, the deterministic `build` gate
is never retried, and no third-party retry action is introduced.

```
  build (validate + upload-pages-artifact)   <- deterministic, never retried
    |
    v
  deploy:
    attempt 1  actions/deploy-pages   continue-on-error
      | failure?
      |   no --> done
      v yes
    sleep 30
    attempt 2  actions/deploy-pages   continue-on-error
      | failure?
      |   no --> done
      v yes
    sleep 90
    attempt 3  actions/deploy-pages   (fail loud)
```

1. Attempts 1 and 2 run with `continue-on-error: true`; attempt 3 is NOT
   `continue-on-error`, so a triple failure fails the job loud — a real
   backend outage still surfaces.
2. Backoffs grow (30s, then 90s), placing the attempts at roughly +0s,
   +45s, and +2.5 minutes — inside the observed flake-recovery window.
3. `environment.url` reads the `page_url` output of whichever attempt
   published (`deployment || deployment-retry || deployment-final`).
4. The steps stay literal in the workflow rather than extracted into a
   composite action — ADR-077's open item, reconsidered and rejected
   again: one call site does not justify the abstraction, and literal
   steps keep per-attempt outcomes visible in the run UI.

Revisit trigger: if a deploy is ever observed where all three attempts
fail during a flake (site healthy, later manual re-run succeeds), do not
add a fourth attempt — reclassify per the S205 sustained-outage playbook
(PLAYBOOK §5.2) and reconsider a composite step with poll-based waiting
instead of fixed backoffs.

## Alternatives considered

| Alternative                                   | Rejected because                                                                                                                 |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Keep two attempts, re-run manually on flakes  | The fired trigger is exactly this cost recurring — the manual re-run per multi-minute flake is the problem ADR-077 deferred.     |
| Extract the retry into a composite action     | One call site; composite actions hide per-attempt outcomes in the run UI; literal steps remain the simplest thing that works.    |
| Longer single backoff (one retry at +3 min)   | Slower on the common one-hit flake ADR-077 measured — most failures recover in seconds, so the first retry should stay at 30s.   |
| `nick-fields/retry` or shell-loop reimplement | Rejected in ADR-077; unchanged — a `uses:` step cannot be wrapped, and a shell reimplement drops the action's URL/status wiring. |
| Unbounded retry loop until success            | Masks a genuine sustained outage; the bound is what keeps a real failure loud.                                                   |

## Consequences

### Positive

- A multi-minute Pages backend flake self-heals: attempts at ~+45s and
  ~+2.5 min bridge the observed recovery window without manual re-runs.
- The common one-hit flake still recovers at the first retry (+30s) —
  no latency added to the case ADR-077 already handled.
- A real build/validate failure is unaffected — `build` is never retried.

### Negative

- A genuine, persistent deploy outage now costs ~2.5 minutes of backoff
  and two extra failed attempts before the job goes red (was ~30s and
  one). Bounded and rare.
- The `deploy-pages` step is now triplicated in the workflow. Accepted
  for the same readability-over-abstraction reason as ADR-077.

### Neutral

- Supersedes ADR-077, which flips to `Superseded by ADR-078` in the same
  PR. The retry philosophy (step-scoped, deterministic gate untouched,
  first-party actions only) carries over unchanged.
