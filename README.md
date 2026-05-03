# Wuseria

[![CI](https://github.com/Imbra-Ltd/wuseria/actions/workflows/ci.yml/badge.svg)](https://github.com/Imbra-Ltd/wuseria/actions/workflows/ci.yml)
[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-nd/4.0/)

Fujifilm lens and camera explorer with genre-based scoring.

**Domain:** [wuseria.com](https://wuseria.com)
**By [braboj.me](https://braboj.me)**

## What it does

Wuseria helps Fujifilm photographers find the right lens for their shooting
genre. It scores every Fuji X and GFX lens against genres like nightscape,
landscape, portrait, street, architecture, sport, wildlife, travel, and macro
-- backed by optical quality data from trusted review sources.

- **Lens Explorer** -- browse, filter, and sort all Fujifilm-compatible lenses by specs
- **Camera Explorer** -- compare Fujifilm bodies with sortable specs
- **Accessories** -- Fujifilm accessories with compatibility info
- **Genre Guide** -- per-genre screeners with EV matrices, FL chips, and scored lens rankings
- **Wiki** -- photography terms and concepts with category filtering
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
    wiki/           # Markdown wiki entries (Content Collections)
  data/             # Lenses, cameras, accessories, genres, affiliates, reviews
  types/            # TypeScript interfaces
  hooks/            # Reusable React hooks
  utils/            # Scoring, formatting, slug utilities
  styles/           # Global CSS custom properties, dark theme
docs/
  decisions/        # Architecture Decision Records (ADRs)
  dev-journal.md    # Development history
  prototype/        # Original single-file prototype (reference only)
  solid-ai-templates/  # Quality convention templates (submodule)
public/             # Static assets (favicon, icons, robots.txt, CNAME)
```

## Commands

```bash
npm run dev          # hot reload at localhost:4321
npm run build        # production build to dist/
npm run preview      # preview production build
npm run lint         # ESLint
npm run format       # Prettier -- check formatting
npm run check        # astro check -- validate .astro files, types, content schemas
npm test             # run tests (Vitest, single run)
npm run test:watch   # run tests in watch mode (development)
npm run validate     # lint + format + check + test + build -- full CI suite
```

## Usage

Visit [wuseria.com](https://wuseria.com):

- **Find a lens** -- open Lenses, filter by mount/aperture/price, sort by any column → filterable table of 241 lenses with specs, prices, and links to detail pages
- **Pick a genre lens** -- open Genre Guide, select a genre tab, compare scored lenses → ranked list of lenses scored 0-10 for your chosen genre with EV matrix and FL recommendations
- **Learn a concept** -- open Wiki, browse by category or search for a term → 115 photography articles organized by category (optics, exposure, composition, technique)

For contributor workflows (adding lenses, cameras, wiki entries), see
[docs/PLAYBOOK.md](docs/PLAYBOOK.md) section 2.

## Conventions

See [CLAUDE.md](CLAUDE.md) for full project conventions:

- Conventional commits (`feat:`, `fix:`, `chore:`, etc.)
- Always work on a branch, never commit to main
- Run `npm run validate` before every commit
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

This work is licensed under [CC BY-NC-ND 4.0](LICENSE).
