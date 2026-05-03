# Wuseria

> **MANDATORY STARTUP — DO THIS BEFORE YOUR FIRST RESPONSE**
>
> You MUST read every file listed below IN FULL using the Read tool before
> you respond to the user's first message. No exceptions. Do not summarize,
> skip, or defer. These files contain binding conventions that this CLAUDE.md
> inherits. If you respond without reading them, you are violating project rules.
>
> 1. `docs/solid-ai-templates/base/quality.md`
> 2. `docs/solid-ai-templates/base/typescript.md`
> 3. `docs/solid-ai-templates/base/review.md`
> 4. `docs/solid-ai-templates/base/scope.md`
> 5. `docs/solid-ai-templates/base/git.md`
> 6. `docs/solid-ai-templates/base/docs.md`
> 7. `docs/solid-ai-templates/base/readme.md`
> 8. `docs/solid-ai-templates/base/issues.md`
> 9. `docs/solid-ai-templates/frontend/quality.md`
> 10. `docs/solid-ai-templates/frontend/ux.md`
> 11. `docs/solid-ai-templates/frontend/static-site.md`
> 12. `docs/solid-ai-templates/stack/static-site-astro.md`

Fujifilm lens and camera explorer with genre-based scoring.
Domain: wuseria.com. By braboj.me.

For architecture decisions, see `docs/decisions/`. For development history, see `docs/dev-journal.md`.

Quality conventions (SOLID, readability, code style, testing) are defined in
`docs/solid-ai-templates/` — a git submodule from
[Imbra-Ltd/solid-ai-templates](https://github.com/Imbra-Ltd/solid-ai-templates).

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

- `src/pages/` — Astro file-based routing (explore with `ls`)
- `src/layouts/` — shared page shells
- `src/components/static/` — `.astro` components that ship zero JS
- `src/components/interactive/` — React islands, each in its own directory with co-located tests, CSS module, and sub-components
- `src/components/interactive/shared/` — reusable UI pieces shared across islands
- `src/data/` — all editable content as TypeScript files (not JSON)
- `src/types/` — shared type definitions
- `src/hooks/` — reusable React hooks
- `src/utils/` — pure utility functions with co-located tests
- `src/styles/global.css` — CSS custom properties, base styles, dark theme
- `src/test/` — Vitest setup and test factories
- `public/` — static assets (favicon, icons, CNAME, robots.txt)

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

## 2. Code conventions

### 2.1 Git

- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`
- Subject line under 80 characters, imperative mood
- Always work on a branch — never commit directly to `main`
- Branch naming: `feat/description`, `fix/description`, `chore/description`
- Do not commit `node_modules/`, `dist/`, `.env`, `.env.local`
- Lock file (`package-lock.json`) is committed
- Run `npm run validate` before committing
- When creating GitHub issues, follow the formats in `docs/solid-ai-templates/base/issues.md` — use the correct label (`epic`, `bug`, `incident`, `question`) and body structure for each type

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

- All editable content in `src/data/*.ts` — never hardcode data in components
- Never hardcode derived counts or statistics — compute them from the data source at build time
- TypeScript files, not JSON — gives type checking at build time and IDE autocomplete on the data itself; a missing field is a compile error, not a runtime surprise
- Astro imports `.ts` data at build time; data never ships as JS to the browser
- Prices in USD by default (configurable in `src/data/config.ts`), rounded up to nearest $250
- All prices are approximate estimates — no `priceEstimated` flag needed
- UI renders prices with `~` prefix and currency symbol from config (e.g. `~$750`) — no separate footnote needed
- Review source directory in `src/data/reviews.ts` — methodology and trust per source
- Official product URLs on each Lens/Camera/Accessory via `officialUrl` field
- Review source links use `rel="nofollow sponsored"` and `target="_blank"`

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

## 6. Session Protocol

Follow `docs/solid-ai-templates/base/scope.md` for scope guard and end-of-session audit.
**The agent MUST enforce this protocol. If the user deviates, remind them.**

### 6.1 Start of session

1. Check which branch we're on — if not `main`, ask why
2. Check `git status` — if uncommitted changes exist, resolve before starting
3. Ask: "What's the theme for this session?" — agree on ONE theme
4. Review open issues for that theme before writing code

### 6.2 During the session

- **One theme per session.** If an unrelated topic comes up, create a GitHub issue for it and say: "Noted as #X — let's come back to it next session."
- **Always branch before coding.** No commits directly to `main` for feature work. Data fixes (single field updates) are acceptable on `main`.
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
[ ] 5. ADRs — record any architectural decisions in docs/decisions/
[ ] 6. CLAUDE.md — for each new convention/rule introduced, does it belong here? Name the section.
[ ] 7. README.md — for each new command, dependency, or structural change, is it reflected? Name the section.
[ ] 8. ONBOARDING.md — for each new tool, prerequisite, or setup step, is it documented? Name the section.
[ ] 9. PLAYBOOK.md — for each new command/script/workflow added, is it documented? Name the section.
[ ] 10. Submodules — check if upstream needs update
[ ] 11. Flag conventions for solid-ai-templates upstream — for each new pattern/convention introduced, explicitly state whether it's project-specific or reusable; if reusable, name the upstream template file it would go in
[ ] 12. Summarize what was done and what's next
```
