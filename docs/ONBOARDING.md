# Onboarding

New contributor guide for Wuseria

## 1. Prerequisites

**Required:**

- Node.js 22+ (the `lint-staged` pre-commit hook and CI require Node 22)
- npm 10+
- Git
- [GitHub CLI](https://cli.github.com/) (`gh`) — used for PRs and issues

**Optional (for full local quality gate):**

- [lychee](https://github.com/lycheeverse/lychee) — broken link checker
  ```bash
  choco install lychee        # Windows
  brew install lychee         # macOS
  ```
- [gitleaks](https://github.com/gitleaks/gitleaks) — secret scanner
  ```bash
  choco install gitleaks      # Windows
  brew install gitleaks       # macOS
  ```

## 2. First-time setup

```bash
git clone --recursive https://github.com/Imbra-Ltd/wuseria.git
cd wuseria
npm install
```

For Python tools (optional — needed only to run mtfdigitizer, brand
extractors, or pagefetch's higher-tier fetchers):

```bash
cd tools && pip install -r requirements.txt   # mtfdigitizer + brand tests + pytest
pip install playwright nodriver seleniumbase  # pagefetch tiers 2-4 (optional)
playwright install chromium                   # required only if using tier 2
```

`tools/requirements.txt` pins the mtfdigitizer image-processing deps
(opencv-python, numpy, scikit-image, Pillow) plus pytest + pytest-xdist.
The browser libraries on the second line stay optional — pagefetch
imports them lazily and falls back gracefully if absent. Run the Python
tool tests:

```bash
cd tools && py -m pytest                       # full suite (~3 min with xdist)
cd tools && py -m pytest pagefetch/tests/      # just pagefetch
```

The `--recursive` flag pulls the `docs/solid-ai-templates` submodule. If you
already cloned without it, run `git submodule update --init`.

## 3. Verify the setup

```bash
npm run dev
```

Open [http://localhost:4321](http://localhost:4321). You should see the homepage
with stats, workflow cards, and scoring overview. Confirm the dev server starts
without errors.

To verify linting and tests:

```bash
npm run lint
npm test
```

Expected output: 11 test files, 175+ tests passing, coverage above 85% on
all metrics. To run the full quality gate (lint + format + types + tests + build):

```bash
npm run validate
```

## 4. Key files

| File                       | Purpose                                                 |
| -------------------------- | ------------------------------------------------------- |
| `CLAUDE.md`                | AI agent context and project conventions                |
| `docs/decisions/`          | Architecture Decision Records                           |
| `docs/dev-journal.md`      | Development history and migration tracking              |
| `docs/PLAYBOOK.md`         | Operational reference — git workflow, data ops, release |
| `docs/solid-ai-templates/` | Quality convention templates (submodule)                |
| `src/types/`               | TypeScript interfaces for all domain entities           |
| `src/data/`                | Static data files imported at build time                |
| `docs/prototype/`          | Original single-file prototype (reference only)         |

## 5. Project context

Wuseria scores Fujifilm lenses against shooting genres (landscape, portrait,
street, astro, etc.) using MTF chart data from trusted review sources. See
[docs/decisions/](decisions/) for architecture decisions and
`src/types/` for the data model.

Key domain concepts:

- **Lens Explorer** — shows all lenses, filterable by specs
- **Genre Guide** — shows only lenses with optical data, scored per genre
- **Scoring** — computed from measurable optical properties, not subjective reviews
- **Trusted sources** — ranked list in [PLAYBOOK section 2.5](PLAYBOOK.md)

## 6. Daily workflow

See [PLAYBOOK.md](PLAYBOOK.md) for all operations:

- Section 1 — Git workflow (branch, commit, PR, merge)
- Section 2 — Data operations (add lenses, cameras, accessories)
- Section 3 — Maintenance (quality conventions, ADRs, prototype)
- Section 4 — Release and deploy
