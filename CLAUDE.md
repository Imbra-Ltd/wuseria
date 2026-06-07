# Wuseria

> **MANDATORY STARTUP — DO THIS BEFORE YOUR FIRST RESPONSE**
>
> You MUST read every file listed below IN FULL using the Read tool before
> you respond to the user's first message. No exceptions. Do not summarize,
> skip, or defer. These files contain binding conventions that this CLAUDE.md
> inherits. If you respond without reading them, you are violating project rules.
>
> 1. `docs/solid-ai-templates/templates/base/core/quality.md`
> 2. `docs/solid-ai-templates/templates/base/core/testing.md`
> 3. `docs/solid-ai-templates/templates/base/core/review.md`
> 4. `docs/solid-ai-templates/templates/base/core/git.md`
> 5. `docs/solid-ai-templates/templates/base/core/docs.md`
> 6. `docs/solid-ai-templates/templates/base/core/readme.md`
> 7. `docs/solid-ai-templates/templates/base/core/config.md`
> 8. `docs/solid-ai-templates/templates/base/language/typescript.md`
> 9. `docs/solid-ai-templates/templates/base/security/security.md`
> 10. `docs/solid-ai-templates/templates/base/workflow/scope.md`
> 11. `docs/solid-ai-templates/templates/base/workflow/issues.md`
> 12. `docs/solid-ai-templates/templates/base/workflow/quality-gates.md`
> 13. `docs/solid-ai-templates/templates/base/workflow/ai-workflow.md`
> 14. `docs/solid-ai-templates/templates/base/workflow/release.md`
> 15. `docs/solid-ai-templates/templates/frontend/quality.md`
> 16. `docs/solid-ai-templates/templates/frontend/ux.md`
> 17. `docs/solid-ai-templates/templates/frontend/static-site.md`
> 18. `docs/solid-ai-templates/templates/stack/static-site-astro.md`
> 19. `docs/solid-ai-templates/templates/platform/github.md`

Fujifilm lens and camera explorer with genre-based scoring.
Domain: wuseria.com. By braboj.me.

For architecture decisions, see `docs/decisions/`. For development history, see `docs/dev-journal.md`.

Quality conventions (SOLID, readability, code style, testing) are defined in
`docs/solid-ai-templates/` — a git submodule from
[Imbra-Ltd/solid-ai-templates](https://github.com/Imbra-Ltd/solid-ai-templates).

> **Note**: this CLAUDE.md is a known signal in the
> [solid-ai-templates viability audit](https://github.com/braboj/solid-ai-templates/issues/350)
> (meta-spike on whether templates deliver repeatable SOLID-grade quality)
> and the [deep-knowledge / tutorial-extraction spike](https://github.com/braboj/solid-ai-templates/issues/349).
> Bloat and the MANDATORY STARTUP block above are symptoms under
> investigation — do not replicate the pattern in other projects.

Project-specific overrides and additions follow below.

## 1. Project

### 1.1 Stack

- Language: TypeScript (strict mode)
- Framework: Astro (static output, zero JS by default)
- Interactive components: React islands via `@astrojs/react` (hydrated only where needed)
- Routing: Astro file-based routing
- State: local state (`useState`, `useMemo`) in React islands — no global store
- Styling: Astro scoped styles + CSS Modules for React islands
- Test runner: Vitest + React Testing Library
- Package manager: npm
- Deployment: GitHub Pages via GitHub Actions

### 1.2 Project layout conventions

Front-end source (`src/`):

| Path                                 | Purpose                                                                                    |
| ------------------------------------ | ------------------------------------------------------------------------------------------ |
| `src/pages/`                         | Astro file-based routing                                                                   |
| `src/layouts/`                       | shared page shells                                                                         |
| `src/components/static/`             | `.astro` components (zero JS)                                                              |
| `src/components/interactive/`        | React islands; each in its own directory with co-located tests, CSS module, sub-components |
| `src/components/interactive/shared/` | reusable UI shared across islands                                                          |
| `src/data/`                          | all editable content as TypeScript files                                                   |
| `src/types/`                         | shared type definitions                                                                    |
| `src/hooks/`                         | reusable React hooks                                                                       |
| `src/utils/`                         | pure utility functions with co-located tests                                               |
| `src/styles/global.css`              | CSS custom properties, base styles, dark theme                                             |
| `src/test/`                          | Vitest setup and test factories                                                            |
| `public/`                            | static assets (favicon, icons, CNAME, robots.txt)                                          |

Docs and reference data:

| Path                         | Purpose                                                                                                              |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `docs/audits/`               | 360-degree audits (timestamped) and SEO test plan                                                                    |
| `docs/optical-specs/<slug>/` | per-lens reference data: `analysis.md`, `scoring-log.md`, `specs-log.md`, diagrams, MTF charts. See ADR-031, ADR-033 |

Python tooling (`tools/`):

| Path                     | Purpose                                                                            |
| ------------------------ | ---------------------------------------------------------------------------------- |
| `tools/<brand>/`         | per-brand optical spec extraction (11 brands). See ADR-035, ADR-036, PLAYBOOK §2.8 |
| `tools/brandkit/`        | shared brand-tool library. See ADR-035                                             |
| `tools/pagefetch/`       | submodule-ready web fetcher. See `tools/pagefetch/README.md`, ADR-035, ADR-037     |
| `tools/mtfdigitizer/`    | unified MTF chart digitizer. See `tools/mtfdigitizer/README.md`, ADR-038           |
| `tools/lenstip/`         | LensTip lens index (2300+ lenses for instant ID lookup)                            |
| `tools/lookup.py`        | unified lens lookup; generates research URLs for all PLAYBOOK §2.8 sources         |
| `tools/crop-artifact.py` | content-aware cropper for diagrams / MTF charts                                    |

`tools/` is Python with its own pytest suites — excluded from the front-end
quality gate (`.prettierignore`, `eslint.config.js`, `ci.yml` path filter).
Verify with `py -m pytest` from `tools/`, never `npm run validate`.

### 1.3 Commands

```
npm run dev          # develop — hot reload at localhost:4321
npm run build        # production build to dist/
npm run preview      # preview production build locally
npm run lint         # ESLint
npm run format       # Prettier — check formatting
npm run check        # astro check — validate .astro files, types, content schemas
npm test             # run tests (Vitest, single run)
npm run test:watch   # run tests in watch mode (development)
npm run validate     # lint + format + check + test + build — full CI suite
```

### 1.4 Web fetching

- Use `py -m pagefetch <url>` (run from `tools/`) for all web page fetching — never WebFetch or Fetch tools. WebFetch truncates large pages silently. This applies to subagents too: instruct them to use `py -m pagefetch`.
- For bare CLI fetches in this project pass `--cache-dir ../.cache/fetch` so the fetch shares the project cache. Brand tools handle this automatically; only the bare CLI needs the flag.
- Use DuckDuckGo HTML search (`html.duckduckgo.com/html/?q=...`) when Google/Bing return CAPTCHAs.
- See `tools/pagefetch/README.md` (architecture, all CLI flags, cache rules, library API) and PLAYBOOK §2.7 (project-specific workflows).

## 2. Code conventions

### 2.1 Git

- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`
- Subject line under 80 characters, imperative mood
- Always work on a branch — never commit directly to `main`
- Branch naming: `feat/description`, `fix/description`, `chore/description`
- Do not commit `node_modules/`, `dist/`, `.env`, `.env.local`
- Lock file (`package-lock.json`) is committed
- Run `npm run validate` before committing
- Releases MUST follow PLAYBOOK 5.1 — never tag without bumping `package.json` first
- When creating GitHub issues, follow the formats in `docs/solid-ai-templates/templates/base/workflow/issues.md` — use the correct label (`epic`, `bug`, `incident`, `question`) and body structure for each type
- Every issue MUST have a type label, a priority label (P0–P4), and a milestone assigned at creation — no exceptions
- Creating a new directory or moving content between documents is an architectural decision — write the ADR **at the moment of the decision**, before creating the files
- Always ask before auto-merging PRs — never set `--auto` without explicit user permission

### 2.2 TypeScript

- `strict: true` — no exceptions
- No `any` — use `unknown` and narrow, or define a proper type
- Explicit return types on non-trivial functions
- Use `interface` for object shapes, `type` for unions and aliases
- Import types with `import type { ... }`
- No enums — use `as const` objects or string literal unions
- Follow `@typescript-eslint/recommended`
- Prettier owns all formatting
- `.astro` files formatted with the official Prettier Astro plugin

### 2.3 Type design

- Use discriminated unions for type families with a shared base and distinct variants
- Compose sub-interfaces when a domain has multiple categories with different fields
- Keep single-purpose types flat — do not compose for composition's sake
- Self-documenting names over comments — comment only intent that code cannot express
- Brief JSDoc (`/** one-liner */`) on exported utility functions where the name alone doesn't convey the transform
- No JSDoc on components (Props interface is self-documenting), types, or internal functions

### 2.4 Components

#### Astro components (static)

- Default to `.astro` — they ship zero JS
- Only reach for React when client-side state is genuinely required
- Static components live in `src/components/static/`
- One component per file — PascalCase filename

#### React islands (interactive)

- Interactive components live in `src/components/interactive/`
- Use `client:load` for above-the-fold interactive components
- Use `client:visible` for below-the-fold interactive components
- Do not use `client:only` unless SSR is enabled — it skips server rendering
- Never hydrate a component that does not need interactivity
- One component per file — PascalCase filename matching component name
- Functional components only
- Props typed with an explicit `interface` in the same file
- Reusable logic goes in `hooks/use[Name].ts`
- Keep components under ~150 lines — split if larger
- When splitting, follow this extraction order: `types.ts` → `constants.ts` → `helpers.ts` → hooks → UI sub-components → orchestrator
- Pass `styles` (CSS module) as a prop to sub-components — do not import a sibling's CSS module directly
- Pure declaration files (e.g. 25+ useState calls) may exceed 150 lines if splitting would be artificial

### 2.5 Styling

- Astro scoped `<style>` blocks for .astro page components
- CSS Modules — co-located with React island components
- No inline styles except dynamic/computed values
- No hardcoded colours or spacing — use CSS custom properties in `:root`
- Global styles in `src/styles/global.css` only
- Mobile-first: design for 640px, enhance for larger
- Dark theme

### 2.6 Data rules

#### Content storage

- All editable content in `src/data/*.ts` — never hardcode data in components
- TypeScript files, not JSON — gives type checking at build time and IDE autocomplete on the data itself; a missing field is a compile error, not a runtime surprise
- Astro imports `.ts` data at build time; data never ships as JS to the browser
- Never hardcode derived counts or statistics — compute them from the data source at build time

#### Pricing

- Prices in USD by default (configurable in `src/data/config.ts`), rounded up to nearest $50
- All prices are approximate estimates — no `priceEstimated` flag needed
- UI renders prices with `~` prefix and currency symbol from config (e.g. `~$750`)

#### Naming

- Lens model names MUST match official manufacturer naming — include all optical suffixes (ED, UMC, AS IF, APO, etc.), generation markers (II, Mark II), and series names (Argus, Athena Prime, Sniper)
- Aperture in model names always uses `f/X.X` format — never `fX.X`, `FX.X`, or `f/X` (omitting trailing `.0`)
- Products without glass elements (pinhole lenses, cap lenses) are accessories (`lens-accessory`), not lenses

#### Required fields

- Official product URLs on each Lens/Camera/Accessory via `officialUrl` field
- Downstream artifacts (MTF readings, emit scripts) MUST read `officialUrl` from `lenses.ts`, never re-derive a brand URL from the slug — see #1062
- Review source links use `rel="nofollow sponsored"` and `target="_blank"`
- All computed `genreMarks` MUST be stored on the lens — no omissions, even low scores (e.g. macro=1). Transparency over curation.
- `maxMagnification` MUST come from spec sheets or review measurements — never estimate from focal length and minimum focus distance (thin lens formula has ~39% median error)

#### Scoring

- Scoring methodology and fallback rules: `docs/decisions/014-optical-quality-rubric.md` — trust hierarchy, rubric thresholds, trust-2 aggregation, community consensus fallback, optical construction inference
- Scoring log format and field completeness rules: `docs/decisions/022-scoring-log-and-mtf-charts.md` — every entry must list all 14 optical fields with explicit undefined markers
- When scoring lenses, save official MTF charts and analysis to `docs/optical-specs/<slug>/`
- Review source directory: `src/data/reviews.ts` — methodology and trust per source

#### Specs-log workflow

- Every lens folder in `docs/optical-specs/<slug>/` MUST have a `specs-log.md` technical specs provenance log — document every source checked for construction diagrams, MTF charts, element counts, coatings, special glass, magnification (URL, date, result: found/not found/404/paywall), whether the search was successful or not, plus any caveats (e.g. different optical designs across mounts); distinct from `scoring-log.md` which covers OQ field scoring
- When verifying or adding optical specs, follow PLAYBOOK §2.8 step 6: specs-log first, then `lenses.ts`, no exceptions — and update `specs-log.md` in the same commit as any artifact added
- `specs-log.md` findings MUST use DB field names — `specialElements` (not `edElements`, `asphericalElements`, `hrElements`), `coating`, `maxMagnification`, etc.

#### Sources

- Samyang lenses are sold under multiple brand aliases (Rokinon, Bower, Walimex Pro, Vivitar) — search all aliases when looking for reviews
- optyczne.pl and lenstip.com are the same company (CO-NET Robert Olech) — never count as separate sources for trust-2 aggregation
- Verify lens mount availability before adding to the database — check official manufacturer pages and third-party lens lists; do not assume a lens exists in X-mount or GFX just because it exists in other mounts
- Source-conflict resolution: the official manufacturer page wins on any contested field; when a secondary source (incl. LensTip) is provably wrong on one verifiable field, distrust its other fields for that lens — it is likely mis-cataloged (e.g. LensTip listed 35mm f/1.4 as 10/9 vs official 8/5; do not adopt its physical specs either)
- Before a bulk `--verify` data pass, confirm the extractor is reliable first — see PLAYBOOK §2.8 for the workflow and the #906 / #896 cautionary tale

## 3. Quality

### 3.1 Testing

- Vitest for unit tests on utils, hooks, and scoring formulas
- React Testing Library for interactive component tests — test behaviour, not implementation
- Prefer accessible queries (`getByRole`, `getByText`) over `getByTestId`
- Use `getAllByText` for explorer content — table and cards both render (CSS handles visibility)
- Test factories live in `src/test/factories.ts` — use `makeLens`/`makeCamera` instead of inline objects
- Genre scoring functions MUST have unit tests
- Data files MUST have validation tests (no duplicates, no missing required fields)
- Run before every commit: `npm run validate`

### 3.2 SEO

- Astro native head management for per-page titles and descriptions
- @astrojs/sitemap integration for auto-generated sitemap
- JSON-LD structured data for Product (lenses) and FAQPage (wiki)
- Individual lens pages auto-generated via `getStaticPaths()` from data
- URL slugs are always lowercase: model `XF 23mm f/1.4` → slug `xf-23mm-f1-4`
- URL structure: `/lenses`, `/lenses/xf-23mm-f1-4`, `/cameras`, `/genre/landscape`, `/wiki/aperture`
- Canonical URLs on all pages
- `robots.txt` and Open Graph meta tags required

### 3.3 Performance

- Bundle size < 200KB gzipped (JS only — most pages ship zero JS)
- LCP < 1.5s
- No external API calls on page load
- Mobile breakpoint: 640px (card layout below, table above)
- Core Web Vitals regressions are bugs
- Static HTML by default — JS only for interactive islands

### 3.4 Accessibility

- WCAG 2.1 AA target
- All interactive elements keyboard-accessible
- Semantic HTML — `<button>` not `<div onClick>`
- Any non-focusable element (`<th>`, `<div>`, `<span>`) with `onClick` must use a `<button>` inside it — `onClick` alone does not make an element keyboard-reachable
- Every form input has an associated `<label>`
- Minimum text contrast ratio: 4.5:1
- `aria-label` on icon-only buttons and links
- axe-core in CI — zero violations before merge

## 4. Identity

### 4.1 Design

- Dark background — data-dense layout
- Data tables with sortable column headers (click-to-sort)
- Mobile: card layout below 640px
- Genre scores as visual indicators (pips or bars)
- Prices prefixed with `~`
- No stock photography
- No emojis in UI text

### 4.2 Brand voice

- Direct and concise — no marketing fluff
- Opinionated — recommend, don't just list
- Technical but accessible — beginners should understand the genre guide
- Honest about limitations — "scoring is subjective, here's our methodology"

## 5. Review process

Before reviews, read the relevant templates listed in the header.
Two distinct scopes:

### 5.1 Code review

Follow the priority order in `base/review.md` (security, correctness,
clarity, conventions). Apply `base/quality.md` rules (SOLID, readability,
naming, code style) and `base/typescript.md` rules (type design, boolean
prefixes, strictness) as the standard for correctness, clarity, and
convention checks. Run both MUST and SHOULD checklists from
`base/review.md` against the diff.

### 5.2 Structure audit

Verify every MUST from `base/docs.md` (standard documents, ADRs),
`base/readme.md` (9 required sections), `base/git.md` (README, .gitignore),
`frontend/static-site.md` (assets, robots.txt, SEO), and
`stack/static-site-astro.md` (.prettierrc, eslint config, Astro conventions).
Run after: new project setup, framework migration, adding a major layer
(backend, CI/CD), or before a release.

### 5.3 360-degree audit storage (upstream deviation)

`base/workflow/360.md` mandates a single `docs/360-audit.md` history file.
This project deliberately deviates: 360 results are stored as **verbose
dated reports** under `docs/audits/YYYY-MM-DD-360.md` — each with the full
per-dimension findings tables and the rationale for every grade, not just a
score row. This keeps one home for audit history (avoids the two-locations
split a separate history file creates) and preserves the reasoning behind
each score. Do NOT re-create `docs/360-audit.md`. Deviation flagged upstream.

## 6. Session Protocol

Follow `docs/solid-ai-templates/templates/base/workflow/scope.md` for scope guard and end-of-session audit.
**The agent MUST enforce this protocol. If the user deviates, remind them.**

### 6.1 Start of session

1. Check which branch we're on — if not `main`, ask why
2. Check `git status` — if uncommitted changes exist, resolve before starting
3. Clean up stale branches: `git fetch --prune` to remove stale remote tracking refs, then `git branch --merged main | grep -v main` to delete merged local branches
4. Check deploy health: `gh run list --branch main --limit 1` — if the latest deploy is not `completed/success`, flag it before starting work
5. Check open PRs: `gh pr list --state open` — flag Dependabot bumps, stale PRs, or anything awaiting review
6. Ask: "What's the theme for this session?" — agree on ONE theme
7. Review open issues for that theme before writing code

### 6.2 During the session

- **One theme per session.** If an unrelated topic comes up, create a GitHub issue for it and say: "Noted as #X — let's come back to it next session."
- **Always branch before coding.** No commits directly to `main` — no exceptions.
- **Build after every change.** Don't accumulate multiple changes without verifying.

### 6.3 End of session

When the user signals end of session ("wrap up", "let's finish",
"end session", "close out", or similar), print the full checklist below and execute
each item sequentially. Mark each item done (with result) before moving
to the next. Do not batch, skip, or summarize — visible sequential
execution prevents missed steps.

```
[ ] 1. All changes committed and pushed (via PR if branch-protected)
[ ] 2. Close completed issues (verify auto-close worked)
[ ] 3. Update epic checklists if relevant
[ ] 4. Dev journal entry (### heading, --- separator, PRs, issues, key changes, key decisions with ADR refs)
[ ] 5. Memory pointer — rewrite the `session_next_theme` memory file (and its MEMORY.md index line) to the current state: session number, what shipped, and the concrete next priority. This is the agent's only cross-session "where we left off" note and is NOT synced from git — if skipped it silently goes stale.
[ ] 6. ADRs — record any architectural decisions in docs/decisions/. Check: were any new directories created or content moved between documents? Each one needs an ADR.
[ ] 7. CLAUDE.md — for each new convention/rule, apply the doc-placement decision tree in `base/workflow/ai-workflow.md` §"Doc placement decision tree" (code → ADR → README → PLAYBOOK → CLAUDE.md → memory). CLAUDE.md contains rules only — not changelogs, package architecture, per-feature progress, or session logs. Each rule fits on one line; if it needs a paragraph, write an ADR and leave a one-line pointer here. Evaluate items individually; do not batch-dismiss.
[ ] 8. README.md — for each new command, dependency, or structural change, is it reflected? Name the section.
[ ] 9. ONBOARDING.md — for each new tool, prerequisite, or setup step, is it documented? Name the section.
[ ] 10. PLAYBOOK.md — first list every new command and script introduced this session. Then check: is each one documented? Name the section. Do not batch-dismiss.
[ ] 11. Submodules — check if upstream needs update
[ ] 12. Flag conventions for solid-ai-templates upstream — list each new convention/decision by name and evaluate individually. No blanket "nothing reusable." For each: state project-specific or reusable; if reusable, name the upstream template file and create an issue
[ ] 13. Review sources — list every new external link used this session for tech specs, optical specs, or lab/field reviews. For each: is it already in `src/data/reviews.ts` or `docs/bookmarks.md`? If not, bookmark it and evaluate whether it should be added as a review source.
[ ] 14. Summarize what was done and what's next
```
