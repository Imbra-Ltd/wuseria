# Fuji.me!

Lightweight Fuji lens and camera explorer with genre-based scoring.
Domain: fujime.app. Part of the me! series by braboj.me.

For architecture decisions, see `docs/decisions/`. For development history, see `docs/dev-journal.md`.

Quality conventions (SOLID, readability, code style, testing) are defined in
`docs/solid-ai-templates/` — a git submodule from
[Imbra-Ltd/solid-ai-templates](https://github.com/Imbra-Ltd/solid-ai-templates).
Key references:
- `docs/solid-ai-templates/base/quality.md` — SOLID, readability, maintainability
- `docs/solid-ai-templates/base/typescript.md` — type design, naming, strictness
- `docs/solid-ai-templates/base/review.md` — peer review checklist
- `docs/solid-ai-templates/base/git.md` — git workflow
- `docs/solid-ai-templates/frontend/quality.md` — frontend design patterns
- `docs/solid-ai-templates/frontend/ux.md` — UX and accessibility

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

### 1.2 Project structure

```
src/
  pages/
    index.astro                   // Homepage
    lenses/
      index.astro                 // /lenses — lens explorer
      [slug].astro                // /lenses/xf-23mm-f1-4 — per-lens page
    cameras/
      index.astro                 // /cameras — camera explorer
    genre/
      [genre].astro               // /genre/landscape — per-genre page
    wiki/
      index.astro                 // /wiki — A-Z index
      [slug].astro                // /wiki/aperture — per-entry page
    trade-deals.astro             // /trade-deals
    accessories.astro             // /accessories
    404.astro                     // Custom error page
  layouts/
    Base.astro                    // HTML shell, nav, footer, global meta
    LensDetail.astro              // Layout for individual lens pages
  components/
    static/                       // .astro — zero JS shipped
      Header.astro
      Footer.astro
      LensCard.astro
      LensSpecTable.astro
      GenreScoreBadge.astro
      WikiEntry.astro
      PriceTag.astro
    interactive/                  // React — hydrated as islands
      shared/
        ChipGroup.tsx             // Reusable chip filter group
        constants.ts              // Shared filter constants (RESET_VALUE)
      LensExplorer/
        LensExplorer.tsx          // Sort/filter table (client:load)
        LensExplorer.test.tsx
        LensExplorer.module.css
      CameraExplorer/
        CameraExplorer.tsx        // Sort/filter table (client:load)
        CameraExplorer.test.tsx
        CameraExplorer.module.css
      GenreGuide/
        GenreGuide.tsx            // Genre selector + scoring (client:load)
        GenreGuide.test.tsx
        GenreGuide.module.css
        exposure.ts               // EV scene evaluation logic
        exposure.test.ts
      TradeDealsFilter/
        TradeDealsFilter.tsx      // Filter deals (client:visible)
        TradeDealsFilter.module.css
  data/
    lenses.ts                     // Lens[]
    cameras.ts                    // Camera[]
    accessories.ts                // Accessory[]
    wiki.ts                       // WikiEntry[]
    genres.ts                     // Genre configs + EV scenes
    affiliates.ts                 // AffiliateLink[]
    reviews.ts                    // Review source directory
  hooks/
    useSort.ts
  types/
    lens.ts
    camera.ts
    genre.ts
    affiliate.ts
    review.ts
  utils/
    slug.ts
    scoring.ts
    scoring.test.ts
    formatting.ts
  styles/
    global.css                    // CSS custom properties, base styles, dark theme
  test/
    setup.ts                      // Vitest setup (e.g. RTL matchers)
public/
  favicon.svg
  icons.svg
  CNAME                           // fujime.app
  robots.txt
astro.config.mjs
tsconfig.json
vitest.config.ts
package.json
```

### 1.3 Commands

```
npm run dev       # develop — hot reload at localhost:4321
npm run build     # production build to dist/
npm run preview   # preview production build locally
npm run lint      # ESLint
npm run check     # astro check — validate .astro files and type check
npm run check:all # lint + check + test + build — full CI suite
npm test          # run tests (Vitest)
```


## 2. Code conventions

### 2.1 Git

- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`
- Subject line under 80 characters, imperative mood
- Always work on a branch — never commit directly to `main`
- Branch naming: `feat/description`, `fix/description`, `chore/description`
- Do not commit `node_modules/`, `dist/`, `.env`, `.env.local`
- Lock file (`package-lock.json`) is committed
- Run `npm run check:all` before committing

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
- TypeScript files, not JSON — gives type checking at build time and IDE autocomplete on the data itself; a missing field is a compile error, not a runtime surprise
- Astro imports `.ts` data at build time; data never ships as JS to the browser
- Prices in USD by default (configurable in `src/data/config.ts`), rounded up to nearest $250
- All prices are approximate estimates — no `priceEstimated` flag needed
- UI renders prices with `~` prefix and currency symbol from config (e.g. `~$750`)
- Footnote on all price displays: "All prices are approximate USD estimates"
- Affiliate URLs in `src/data/affiliates.ts` — never inline in components
- Review source directory in `src/data/reviews.ts` — methodology and trust per source
- Official product URLs on each Lens/Camera/Accessory via `officialUrl` field
- Affiliate links use `rel="nofollow sponsored"` and `target="_blank"`


## 3. Quality

### 3.1 Testing

- Vitest for unit tests on utils, hooks, and scoring formulas
- React Testing Library for interactive component tests — test behaviour, not implementation
- Prefer accessible queries (`getByRole`, `getByText`) over `getByTestId`
- Genre scoring functions MUST have unit tests
- Data files MUST have validation tests (no duplicates, no missing required fields)
- Run before every commit: `npm run check:all`

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
- Prices prefixed with `~` and footnoted
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
