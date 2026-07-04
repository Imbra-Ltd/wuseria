# ADR-077: Retry the transient deploy-pages step once with backoff

**Status:** Accepted
**Date:** 2026-07-04

## Context

`deploy.yml` runs `build` (which runs `npm run validate`) then a `deploy`
job whose only step is `actions/deploy-pages@v5`. That step intermittently
fails with `Deployment failed, try again later.` — a rejection from the
GitHub Pages backend, not a fault in the diff. When it fires, `build` is
green and only `deploy` is red; a single manual `gh run rerun` of the
failed job succeeds.

The cost is not the deploy itself but the residue: it leaves `main`
transiently red, which trips the section 6.1 startup deploy-health check
next session and costs a manual re-run. It happened twice in one session
on 2026-07-04 (runs `28703448682` for #1361, `28705448157` for #1365) — in
both, `build` = success, `deploy` = failure at `Run actions/deploy-pages@v5`,
re-run succeeded.

This is an infra failure, not a diff failure — the exact distinction
`base/review.md` (CI signals) draws. The right response to a flaky infra
step is a scoped retry, not retrying the whole pipeline: the `build` job
is a deterministic gate and MUST NOT be retried, or a real failure there
would be masked.

```
  build (validate + upload-pages-artifact)   <- deterministic, never retried
    |
    v
  deploy:
    attempt 1  actions/deploy-pages   continue-on-error
    |  outcome == failure?
    |   yes --> sleep 30 --> attempt 2  actions/deploy-pages  (fail loud)
    |   no  --> done
```

## Decision

Scope a single retry to the `deploy-pages` step only:

1. First attempt runs with `continue-on-error: true`.
2. A `sleep 30` backoff runs only when the first attempt's `outcome` is
   `failure`, giving the Pages backend time to recover.
3. A second `actions/deploy-pages@v5` step runs only on first-attempt
   failure. It is NOT `continue-on-error`, so a double failure fails the
   job loud — a real backend outage still surfaces.
4. `environment.url` reads `steps.deployment.outputs.page_url ||
steps.deployment-retry.outputs.page_url`, so the environment reports
   whichever attempt published.

One retry (two attempts total) is chosen deliberately over 2–3: every
observed failure recovered on a single manual re-run, so a second retry
would be speculative. Revisit trigger: if a deploy is ever observed where
both automated attempts fail on backend load (not a real diff or config
fault), widen to a bounded loop of three attempts with increasing backoff.

## Alternatives considered

| Alternative                                                  | Rejected because                                                                                                                                                                  |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `nick-fields/retry` wrapping the deploy step                 | The action retries a shell `command`; it cannot re-invoke a `uses:` step, and `actions/deploy-pages` is a JS action. It would also add a third-party action to SHA-pin and track. |
| Re-implement deploy as `gh api` calls in a shell retry loop  | Drops the official action's environment-URL wiring and status polling, and re-creates backend behavior the action already handles — more surface to maintain for no gain.         |
| Retry the whole `deploy` job (job-level rerun)               | Coarser than needed; the artifact upload lives in `build`, so a job retry only re-runs the same single step this ADR already retries at step level, with worse readability.       |
| Tune `actions/deploy-pages` `timeout` / `error_count` inputs | Those govern status-polling patience after a deployment is created. The failure here is the create-deployment call being rejected up front, which no polling budget changes.      |
| Status quo (manual re-run)                                   | The recurring `main`-red is the whole cost the issue names; a manual re-run every few deploys is the problem, not the fix.                                                        |

## Consequences

### Positive

- A transient Pages backend rejection no longer leaves `main` red or
  costs a manual re-run — the deploy self-heals on the common one-hit case.
- No new third-party dependency: the retry uses only the same first-party
  action already trusted here.
- The deterministic `build` gate is untouched — a real build/validate
  failure still fails immediately with no retry masking it.

### Negative

- A genuine, persistent deploy outage now costs an extra ~30s backoff plus
  a second failed attempt before the job goes red. Bounded and rare.
- The `deploy-pages` step is duplicated in the workflow (attempt + retry).
  Kept literal rather than abstracted — one retry does not justify a
  composite action.

### Neutral

- Deploy topology changes (the `deploy` job gains a backoff and a
  conditional retry step), which is why this is recorded as an ADR.
- Complements ADR-076: that ADR guarantees a deterministic gate runs on
  every PR; this one absorbs non-deterministic infra noise on the deploy
  without weakening any deterministic gate.

### Open

- If both attempts are ever observed failing on backend load, widen to a
  bounded three-attempt loop with increasing backoff (the revisit trigger
  above), and reconsider extracting the retry into a composite step at
  that point.
