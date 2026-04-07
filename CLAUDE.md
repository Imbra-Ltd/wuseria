# Fuji.me!

Lightweight Fuji lens and camera explorer with genre-based scoring.
Domain: fujime.app. Part of the me! series by braboj.me.

For architecture decisions and rationale, see `FUJI-ME-ARCHITECTURE.md`.
For product context, see `FUJI-ME.md`.


## Stack

- Language: TypeScript (strict mode)
- Framework: React 18+
- Bundler: Vite
- Routing: React Router v6
- State: local state (`useState`, `useMemo`) — no global store
- Styling: CSS Modules
- Test runner: Vitest + React Testing Library
- Package manager: npm
- Deployment: GitHub Pages via GitHub Actions


## Project structure

```
src/
  components/
    LensExplorer/
      LensExplorer.tsx
      LensExplorer.test.tsx
      LensExplorer.module.css
    CameraExplorer/
    GenreGuide/
    TradeDeals/
    Wiki/
    Accessories/
  data/
    lenses.ts          // Lens[]
    cameras.ts         // Camera[]
    accessories.ts     // Accessory[]
    wiki.ts            // WikiEntry[]
    genres.ts          // Genre configs + scoring functions
    affiliates.ts      // AffiliateLink[]
  hooks/
    useSort.ts
    useFilter.ts
  types/
    lens.ts
    genre.ts
    affiliate.ts
  utils/
    scoring.ts
    formatting.ts
  App.tsx
  main.tsx
public/
  CNAME               // fujime.app
tsconfig.json
vite.config.ts
package.json
```


## Commands

```
npm run dev       # develop — hot reload
npm run build     # production build
npm run preview   # preview production build locally
npm test          # run tests (watch mode)
tsc --noEmit      # type check without emitting files
```


## Git conventions

- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`
- Subject line under 80 characters, imperative mood
- Always work on a branch — never commit directly to `main`
- Branch naming: `feat/description`, `fix/description`, `chore/description`
- Do not commit `node_modules/`, `dist/`, `.env`, `.env.local`
- Lock file (`package-lock.json`) is committed
- Run `npm test && tsc --noEmit` before committing


## TypeScript

- `strict: true` — no exceptions
- No `any` — use `unknown` and narrow, or define a proper type
- Explicit return types on non-trivial functions
- Use `interface` for object shapes, `type` for unions and aliases
- Import types with `import type { ... }`
- No enums — use `as const` objects or string literal unions
- Follow `@typescript-eslint/recommended`
- Prettier owns all formatting


## Components

- One component per file — PascalCase filename matching component name
- Functional components only
- Props typed with an explicit `interface` in the same file
- No prop drilling beyond two levels — lift state or use context
- Reusable logic goes in `hooks/use[Name].ts`
- Keep components under ~150 lines — split if larger


## Styling

- CSS Modules — co-located with the component
- No inline styles except dynamic/computed values
- No hardcoded colours or spacing — use CSS custom properties in `:root`
- Global styles in `src/index.css` only
- Mobile-first: design for 640px, enhance for larger
- Dark theme


## Data rules

- All editable content in `src/data/*.ts` — never hardcode data in components
- TypeScript files, not JSON — gives type checking at build time and IDE autocomplete on the data itself; a missing field is a compile error, not a runtime surprise
- Prices in EUR, prefixed with `~`
- All prices must have `est: boolean` flag
- Affiliate URLs in `src/data/affiliates.ts` — never inline in components
- Affiliate links use `rel="nofollow sponsored"` and `target="_blank"`


## Testing

- Vitest for unit tests on utils, hooks, and scoring formulas
- React Testing Library for component tests — test behaviour, not implementation
- Prefer accessible queries (`getByRole`, `getByText`) over `getByTestId`
- Genre scoring functions MUST have unit tests
- Data files MUST have validation tests (no duplicates, no missing required fields)
- Run before every commit: `npm test && tsc --noEmit`


## SEO

- react-helmet for per-page titles and descriptions
- Sitemap generated at build time
- JSON-LD structured data for Product (lenses) and FAQPage (wiki)
- URL structure: `/lenses`, `/cameras`, `/genre/landscape`, `/wiki/aperture`
- Canonical URLs on all pages
- `robots.txt` and Open Graph meta tags required


## Performance

- Bundle size < 200KB gzipped
- LCP < 1.5s
- No external API calls on page load
- Mobile breakpoint: 640px (card layout below, table above)
- Core Web Vitals regressions are bugs


## Accessibility

- WCAG 2.1 AA target
- All interactive elements keyboard-accessible
- Semantic HTML — `<button>` not `<div onClick>`
- Every form input has an associated `<label>`
- Minimum text contrast ratio: 4.5:1
- `aria-label` on icon-only buttons and links
- axe-core in CI — zero violations before merge


## Design

- Dark background — data-dense layout
- Data tables with sortable column headers (click-to-sort)
- Mobile: card layout below 640px
- Genre scores as visual indicators (pips or bars)
- Prices prefixed with `~` and footnoted
- No stock photography
- No emojis in UI text


## Brand voice

- Direct and concise — no marketing fluff
- Opinionated — recommend, don't just list
- Technical but accessible — beginners should understand the genre guide
- Honest about limitations — "scoring is subjective, here's our methodology"
