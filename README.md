# Fuji.me!

Lightweight Fuji lens and camera explorer with genre-based scoring.

**Domain:** [fujime.app](https://fujime.app)
**Part of the me! series by [braboj.me](https://braboj.me)**

## Overview

Fuji.me! helps Fujifilm photographers find the right lens or camera for their
shooting genre. It scores every Fuji X and GFX lens against genres like
landscape, portrait, street, and astro — backed by optical quality measurements
from trusted review sources rather than subjective opinions.

## Quick start

Prerequisites: Node.js 20+, npm 10+

```bash
git clone --recursive https://github.com/Imbra-Ltd/me-fuji.git
cd me-fuji
npm install
npm run dev
```

Open [http://localhost:4321](http://localhost:4321) to see the site.

## Usage

Browse lenses, cameras, and accessories. Filter by genre to see how each lens
scores for your shooting style. Scores are computed from optical data — see
[docs/decisions/](docs/decisions/) for architecture decisions.

> Note: The site is in data migration phase. UI pages are planned for the
> Astro migration (see issue #57).

## Project structure

```
me-fuji/
├── src/
│   ├── components/
│   │   ├── interactive/  # React islands (LensExplorer, CameraExplorer, GenreGuide)
│   │   └── static/       # Astro components (zero JS shipped)
│   ├── data/             # Static data files (lenses, cameras, genres, reviews, config)
│   ├── test/             # Vitest setup
│   ├── types/            # TypeScript interfaces for all domain entities
│   ├── hooks/            # Reusable React hooks
│   └── utils/            # Genre queries and formatting utilities
├── docs/
│   ├── decisions/        # Architecture Decision Records (ADR-001 to ADR-013)
│   ├── dev-journal.md    # Development history and migration tracking
│   ├── prototype/        # Original single-file prototype (reference only)
│   ├── ONBOARDING.md     # New contributor guide
│   ├── PLAYBOOK.md       # Operational reference
│   └── solid-ai-templates/ # Quality convention templates (submodule)
├── public/               # Static assets (favicon, icons, robots.txt)
├── CLAUDE.md             # AI agent context and project conventions
├── eslint.config.js      # ESLint 9 flat config
├── vitest.config.ts      # Vitest configuration
└── package.json
```

## Development setup

```bash
git clone --recursive https://github.com/Imbra-Ltd/me-fuji.git
cd me-fuji
npm install
```

The `--recursive` flag pulls the `docs/solid-ai-templates` submodule. If you
already cloned without it, run `git submodule update --init`.

### Commands

```bash
npm run dev       # hot reload at localhost:4321
npm run build     # production build to dist/
npm run preview   # preview production build
npm run lint      # ESLint
npm test          # run tests (Vitest)
npm run check:all # lint + type check + test + build — full CI suite
```

### Checks before committing

```bash
npm run check:all
```

## Configuration reference

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| — | — | — | No environment variables required. All config is in `src/data/config.ts`. |

## Links

- [Architecture decisions](docs/decisions/)
- [Development journal](docs/dev-journal.md)
- [Onboarding guide](docs/ONBOARDING.md)
- [Operational playbook](docs/PLAYBOOK.md)
- [Quality conventions](docs/solid-ai-templates/)
- [GitHub Issues](https://github.com/Imbra-Ltd/me-fuji/issues)

## License

All rights reserved.
