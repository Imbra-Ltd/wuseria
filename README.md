# Fuji.me!

Lightweight Fuji lens and camera explorer with genre-based scoring.

**Domain:** [fujime.app](https://fujime.app)
**Part of the me! series by [braboj.me](https://braboj.me)**

## Overview

Fuji.me! helps Fujifilm photographers find the right lens or camera for their
shooting genre. It scores every Fuji X and GFX lens against genres like
landscape, portrait, street, and astro — backed by MTF chart data and
measurable optical properties rather than subjective reviews.

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
[docs/architecture.md](docs/architecture.md) for the scoring methodology.

> Note: The site is in data migration phase. UI pages are planned for the
> Astro migration (see issue #57).

## Project structure

```
me-fuji/
├── src/
│   ├── data/           # Static data files (lenses, cameras, config)
│   ├── types/          # TypeScript interfaces for all domain entities
│   ├── hooks/          # Reusable React hooks (planned)
│   └── utils/          # Scoring and formatting utilities (planned)
├── docs/
│   ├── architecture.md # Architecture decisions and data model
│   ├── decisions/      # Architecture Decision Records
│   ├── ONBOARDING.md   # New contributor guide
│   ├── PLAYBOOK.md     # Operational reference
│   └── solid-ai-templates/ # Quality convention templates (submodule)
├── public/             # Static assets (favicon, icons, robots.txt)
├── CLAUDE.md           # AI agent context and project conventions
├── eslint.config.js    # ESLint 9 flat config
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
npm test          # run tests (when configured)
```

### Checks before committing

```bash
npm run lint
```

## Configuration reference

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| — | — | — | No environment variables required. All config is in `src/data/config.ts`. |

## Links

- [Architecture and data model](docs/architecture.md)
- [Onboarding guide](docs/ONBOARDING.md)
- [Operational playbook](docs/PLAYBOOK.md)
- [Quality conventions](docs/solid-ai-templates/)
- [GitHub Issues](https://github.com/Imbra-Ltd/me-fuji/issues)

## License

All rights reserved.
