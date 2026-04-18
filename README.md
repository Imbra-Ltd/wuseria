# Wuseria

Fujifilm lens and camera explorer with genre-based scoring.

**Domain:** [wuseria.com](https://wuseria.com)
**By [braboj.me](https://braboj.me)**

## What it does

Wuseria helps Fujifilm photographers find the right lens for their shooting
genre. It scores every Fuji X and GFX lens against genres like nightscape,
landscape, portrait, street, architecture, sport, wildlife, travel, and macro
-- backed by optical quality data from trusted review sources.

- **Lens Explorer** -- browse, filter, and sort 240+ lenses by specs
- **Camera Explorer** -- compare 38 Fujifilm bodies with sortable specs
- **Accessories** -- 46 Fujifilm accessories with compatibility info
- **Genre Guide** -- per-genre screeners with EV matrices, FL chips, and scored lens rankings
- **Wiki** -- 115 photography terms and concepts with category filtering
- **Detail pages** -- per-lens, per-camera, and per-accessory pages for SEO

## Quick start

Prerequisites: Node.js 20+, npm 10+

```bash
git clone --recursive https://github.com/Imbra-Ltd/wuseria.git
cd wuseria
npm install
npm run dev
```

Open [http://localhost:4321](http://localhost:4321).

## Stack

- **Framework:** Astro (static output, zero JS by default)
- **Interactive components:** React islands via `@astrojs/react`
- **Language:** TypeScript (strict mode)
- **Wiki:** Astro Content Collections (Markdown files)
- **Styling:** Astro scoped styles + CSS Modules for React islands
- **Testing:** Vitest + React Testing Library
- **Deployment:** GitHub Pages via GitHub Actions

## Project structure

```
src/
  pages/            # Astro file-based routing
  components/
    interactive/    # React islands (LensExplorer, CameraExplorer, GenreGuide, etc.)
    static/         # Astro components (zero JS)
  content/
    wiki/           # 115 Markdown wiki entries (Content Collections)
  data/             # Lenses, cameras, accessories, genres, affiliates, reviews
  types/            # TypeScript interfaces
  hooks/            # Reusable React hooks
  utils/            # Scoring, formatting, slug utilities
  styles/           # Global CSS custom properties, dark theme
docs/
  decisions/        # Architecture Decision Records (ADR-001 to ADR-015)
  dev-journal.md    # Development history
  prototype/        # Original single-file prototype (reference only)
  solid-ai-templates/  # Quality convention templates (submodule)
public/             # Static assets (favicon, icons, robots.txt, CNAME)
```

## Commands

```bash
npm run dev       # hot reload at localhost:4321
npm run build     # production build to dist/
npm run preview   # preview production build
npm run lint      # ESLint
npm run check     # astro check (validate .astro + type check)
npm test          # run tests (Vitest)
npm run check:all # lint + check + test + build -- full CI suite
```

## How to add a new lens

1. Open `src/data/lenses.ts`
2. Add a new entry to the `lenses` array following the `Lens` interface in `src/types/lens.ts`
3. All fields are type-checked at build time -- the compiler will catch missing required fields
4. Run `npm run check:all` before committing

## How to add a wiki entry

1. Create a new `.md` file in `src/content/wiki/` (e.g. `my-topic.md`)
2. Add frontmatter: `title`, `category`, `summary`, and optionally `fullTitle` and `related`
3. Write the body in Markdown -- headings, lists, tables, links all work
4. The schema in `src/content.config.ts` validates your frontmatter at build time

## Conventions

See [CLAUDE.md](CLAUDE.md) for full project conventions:
- Conventional commits (`feat:`, `fix:`, `chore:`, etc.)
- Always work on a branch, never commit to main
- Run `npm run check:all` before every commit
- No `any` in TypeScript, no inline styles, no hardcoded data in components

## Configuration

No environment variables are required. Site-level settings (currency, site
name) are in `src/data/config.ts`. All content lives in `src/data/*.ts`
files, type-checked at build time.

## Links

- [Architecture decisions](docs/decisions/)
- [Development journal](docs/dev-journal.md)
- [Quality conventions](docs/solid-ai-templates/)
- [GitHub Issues](https://github.com/Imbra-Ltd/wuseria/issues)

## License

All rights reserved.
