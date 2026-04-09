# Onboarding

## Prerequisites

- Node.js 20+
- npm 10+
- Git

## First-time setup

```bash
git clone --recursive https://github.com/Imbra-Ltd/me-fuji.git
cd me-fuji
npm install
```

The `--recursive` flag pulls the `docs/solid-ai-templates` submodule.

## Running locally

```bash
npm run dev       # hot reload at localhost:4321
npm run build     # production build to dist/
npm run preview   # preview production build
```

## Checks before committing

```bash
npm run lint      # ESLint
npm test          # Vitest (when configured)
```

## Key files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | AI agent context and project conventions |
| `docs/architecture.md` | Architecture decisions and data model |
| `docs/solid-ai-templates/` | Quality convention templates (submodule) |
| `src/types/` | TypeScript interfaces for all domain entities |
| `src/data/` | Static data files imported at build time |

## Branch workflow

1. Create a branch: `feat/description`, `fix/description`, or `chore/description`
2. Make changes, run checks
3. Push and open a PR against `main`
4. After merge, delete branch and pull main
