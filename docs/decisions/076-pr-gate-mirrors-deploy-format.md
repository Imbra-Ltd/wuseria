# ADR-076: PR CI mirrors the deploy format gate via an always-run job

**Status:** Accepted
**Date:** 2026-07-04

## Context

`deploy.yml` runs `npm run validate` unconditionally on every push to
`main`, then publishes `dist/` to GitHub Pages. `validate` chains
`lint -> format -> check -> test -> build -> check:links`, and the
`format` step is `prettier --check .`, which inspects every tracked file
not listed in `.prettierignore` — including `docs/**/*.md` and root
Markdown.

The PR workflow `ci.yml` runs the same `validate` inside its `build`
job, but `build` is gated on the `code` paths-filter:

```
code: src/** public/** astro.config.mjs tsconfig.json
      package.json package-lock.json lighthouserc.json .github/workflows/**
```

That filter omits `docs/**` and root Markdown. A docs-only PR (e.g. a
dev-journal entry) therefore skips `build` entirely, so `prettier
--check` never runs on the PR. The `gate` aggregator only fails on a
sub-job `failure`, and a skipped `build` reports `skipped`, not
`failure` — so the PR goes green. The deploy is then the FIRST place a
docs Prettier violation surfaces: post-merge, on `main`, blocking the
site deploy.

This happened for real. PR #1360 (the S201 journal entry) left
unescaped underscores that Markdown parses as emphasis; `prettier
--check` flagged them only on the `main` deploy, which failed twice
before the #1361 hotfix. The upstream quality-gates template names this
exact failure: "PR gate MUST mirror the deploy gate"
(`quality-gates-scope-agreement`), and "Skipped is not passed".

ADR-039 established the opposite, valid case — skipping the _Lighthouse_
job on lockfile-only PRs — because Lighthouse is an output-measuring,
single-run-noisy gate. That reasoning does NOT extend to `validate`:
lint, format, type-check, test, and build are deterministic gates, which
the template says MUST NOT be skipped. The `code` filter over-reached by
skipping a deterministic gate on a path class (`docs/**`) that can still
break one of its steps.

## Decision

Add a dedicated `format` job to `ci.yml` that runs `prettier --check .`
on every PR with no path filter, and wire it into the `gate` aggregator.
`build`, `lighthouse`, and `pytest` keep their (correct) path filters.

```
                 +-----------+
                 |  changes  |  (paths-filter: code / lighthouse / tools)
                 +-----------+
                   |   |   |
   always-run      |   |   |
  +----------+     |   |   |
  |  format  |     |   |   +--> pytest    (if tools)
  | prettier |     |   +------> build     (if code) --> lighthouse (if lighthouse)
  |  --check |     |
  +----+-----+     |
       |           |
       v           v
     +--------------------------------+
     |  gate  needs:[format,build,     |
     |        lighthouse,pytest]       |
     |  fail if ANY == 'failure'       |
     +--------------------------------+
```

The `format` job does not check out the submodule (`.prettierignore`
excludes `docs/solid-ai-templates/`) and reuses the npm cache, so it
adds roughly 30 seconds to every PR. `build` still runs `validate`
(which re-runs `format`) on code-touching PRs; the redundant Prettier
pass there is negligible and keeps the `format` job's trigger
enumeration-free.

Branch protection already requires `gate`; because `gate` now depends on
`format` and fails when `format` fails, no branch-protection setting
change is needed.

## Alternatives considered

| Alternative                                          | Rejected because                                                                                                                                                     |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Add `docs/**` and root Markdown to the `code` filter | A filter must enumerate every Prettier-covered path; the next new top-level file type Prettier checks but the filter omits reopens the exact gap that broke `main`.  |
| Make `build` run unconditionally on all PRs          | Truest mirror, but a docs-only or tools-only PR would then run the full 462-page build, test suite, and link check needlessly. The format step is the only exposure. |
| Rely on the pre-commit hook to catch it locally      | Pre-commit is bypassable with `--no-verify` and is not a CI gate; the template requires CI to duplicate Layer 2 checks precisely because hooks can be skipped.       |
| Status quo (deploy catches it)                       | A gate that runs only post-merge is a failure notification, not a gate — by the time it fires, `main` is already broken.                                             |

## Consequences

### Positive

- A Prettier violation in any tracked path fails the PR, before merge —
  the deploy is no longer the first line of defense for formatting.
- Enumeration-free: no path list to keep in sync as new top-level files
  or directories appear. The safety net covers paths nobody thought to
  add to a filter.
- Mirrors the deploy's format step exactly, closing the
  `quality-gates-scope-agreement` gap without touching branch
  protection.

### Negative

- Every PR pays ~30 seconds for an always-run `npm ci` + `prettier`,
  including PRs that a filter would have skipped. Deterministic and
  cheap; acceptable against a recurring `main`-red foot-gun.
- Prettier runs twice on code-touching PRs (once in `format`, once
  inside `build`'s `validate`). Negligible cost, kept for simplicity.

### Neutral

- `build`, `lighthouse`, and `pytest` retain their path filters; this
  ADR narrows the mirror rule to the one cross-cutting step (format),
  not the whole `validate` chain — the other steps only read paths the
  `code`/`tools` filters already cover.
- Complements ADR-039 rather than reversing it: ADR-039 skips a noisy
  output-measuring gate; this ADR guarantees a deterministic gate runs.

### Open

- If a future `validate` step gains a cross-cutting input beyond
  Prettier (e.g. a Markdown link-checker over `docs/**`), it needs the
  same always-run treatment or an extended filter — re-evaluate the
  mirror rule when that lands.
