# ADR-086: PR CI mirrors the deploy test gate via an always-run job

**Status:** Accepted
**Date:** 2026-07-19

## Context

`deploy.yml` runs `npm run validate` unconditionally on every push to
`main`. `validate` chains `lint -> format -> check -> test -> build ->
check:links`, and the `test` step is `vitest run --coverage`. The vitest
data-integrity suite in `src/data/mtf-readings.test.ts` reads the
`docs/optical-specs/**` filesystem directly: it walks the directory for
`dirsWithLog` (dirs containing a `digitization-log.md`), enforces the
directory-name invariant against `toDataSlug`, and hashes primary MTF
charts for the same-product invariant.

The PR workflow `ci.yml` runs the same `validate` inside its `build`
job, but `build` is gated on the `code` paths-filter:

```
code: src/** public/** astro.config.mjs tsconfig.json
      package.json package-lock.json lighthouserc.json .github/workflows/**
```

That filter omits `docs/optical-specs/**`. A PR that only adds files
under `tools/**` plus a `docs/optical-specs/<slug>/digitization-log.md`
therefore skips `build` entirely, so the vitest suite never runs on the
PR. The `gate` aggregator only fails on a sub-job `failure`, and a
skipped `build` reports `skipped`, not `failure` — so the PR goes green.
The deploy is then the FIRST place the data-integrity check runs
post-merge, on `main`, blocking the site deploy.

This happened for real. PR #1441 added the Mitakon GFX profile
(`tools/**`) plus a `digitization-log.md` for the 65mm f/1.4 Tier-1
anchor, whose readings were intentionally not yet emitted to
`mtfReadings`. The `every accepted-extraction directory has a
mtfReadings entry` test flagged it only on the `main` deploy, which
failed; #1442 hotfixed it by adding the slug to `KNOWN_PENDING_EMIT`.
The upstream quality-gates template names this exact failure: "PR gate
MUST mirror the deploy gate" and "Skipped is not passed"
(`quality-gates-scope-agreement`).

ADR-076 established the same-shaped fix for the `format` step, but its
Neutral section asserted that "the other steps only read paths the
`code`/`tools` filters already cover." That was incomplete: the `test`
step reads `docs/optical-specs/**`, which neither filter covers. #1443
is the second cross-cutting exposure ADR-076's Open section anticipated
("If a future `validate` step gains a cross-cutting input beyond
Prettier ... re-evaluate the mirror rule when that lands"). ADR-076's
decision — the `format` always-run job — remains valid and in force;
only that side-observation was wrong, and this ADR records the
correction.

## Decision

Add a dedicated `test` job to `ci.yml` that runs `npm run test` on every
PR with no path filter, and wire it into the `gate` aggregator. `build`,
`lighthouse`, `pytest`, and `staleness` keep their (correct) path
filters.

```
                 +-----------+
                 |  changes  |  (paths-filter: code/lighthouse/tools/staleness)
                 +-----------+
                   |   |   |  \
   always-run      |   |   |   +--> pytest    (if tools)
  +---------+      |   |   +------> staleness (if tools|optical-specs)
  | format  |      |   +----------> build     (if code) --> lighthouse (if lighthouse)
  | prettier|      |
  +----+----+      |
  +---------+      |
  |  test   |      |
  | vitest  |      |
  +----+----+      |
       |           |
       v           v
     +--------------------------------------+
     |  gate  needs:[format,test,build,      |
     |        lighthouse,pytest,staleness]   |
     |  fail if ANY == 'failure'             |
     +--------------------------------------+
```

The `test` job does not check out the submodule — the vitest suite reads
`src/**` and `docs/optical-specs/**`, both in the main repo, never
`docs/solid-ai-templates/`. It reuses the npm cache. `build` still runs
`validate` (which re-runs `test`) on code-touching PRs; the redundant
vitest pass there is negligible and keeps the `test` job's trigger
enumeration-free — the same tradeoff ADR-076 accepted for `format`.

Branch protection already requires `gate`; because `gate` now depends on
`test` and fails when `test` fails, no branch-protection setting change
is needed.

## Alternatives considered

| Alternative                                                                    | Rejected because                                                                                                                                                          |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Add `docs/optical-specs/**` (or `**/digitization-log.md`) to the `code` filter | A filter must enumerate every path the vitest suite reads; the next test that reads a new tracked directory reopens the exact gap that broke `main`. Enumeration-fragile. |
| Make `build` run unconditionally on all PRs                                    | A docs- or tools-only PR would then run the full 462-page build, coverage suite, and link check needlessly. The test step is the exposure — mirror only it, per ADR-076.  |
| Rely on the existing `staleness` job (`extract --check`)                       | Different check: `extract --check` re-renders committed logs and fails on drift; it does not enforce the `mtfReadings`-entry / directory-name / same-product invariants.  |
| Status quo (deploy catches it)                                                 | A gate that runs only post-merge is a failure notification, not a gate — by the time it fires, `main` is already broken.                                                  |

## Consequences

### Positive

- A `docs/optical-specs/**` change that violates a data invariant fails
  the PR, before merge — the deploy is no longer the first line of
  defense for the vitest suite.
- Enumeration-free: no path list to keep in sync as new tests read new
  tracked directories. The safety net covers paths nobody thought to add
  to a filter.
- After this ADR, every `validate` step is mirrored on PRs: `format` and
  `test` run always; `lint`, `check`, `build`, and `check:links` read
  only paths the `code` filter already covers.

### Negative

- Every PR pays an extra `npm ci` + `vitest run --coverage`, including
  PRs a filter would have skipped. Deterministic and bounded; acceptable
  against a recurring `main`-red foot-gun.
- vitest runs twice on code-touching PRs (once in `test`, once inside
  `build`'s `validate`). Negligible cost, kept for simplicity — the same
  tradeoff ADR-076 accepted for `format`.

### Neutral

- `build`, `lighthouse`, `pytest`, and `staleness` retain their path
  filters; this ADR narrows the mirror rule to the second cross-cutting
  step (test), not a change to the others.
- Corrects, but does not supersede, ADR-076: that ADR's `format` job is
  unchanged and remains Accepted. Only its Neutral-section claim that the
  remaining `validate` steps read covered paths was incomplete, which
  #1443 exposed.

### Open

- All `validate` steps are now accounted for. If a future step gains a
  cross-cutting input beyond `src/**` and the covered manifest/config
  paths, it needs the same always-run treatment — re-evaluate the mirror
  rule when that lands.
