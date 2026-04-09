# Fuji.me! — Development Journal

## Architecture Overview

```
Phase 1 — Launch:
  Static site (Astro + React islands)
  -> Data compiled to static HTML at build time
  -> Interactive tables hydrated as React islands
  -> Deployed to GitHub Pages
  -> Affiliate links are plain <a> tags with tracking params

Phase 2 — Scoring:
  Same static site
  -> Complete genre scoring (remaining 6 genres)
  -> Systematic MTF review

Phase 3 — Revenue diversification:
  Same static site + Gumroad (merch) + Buttondown (newsletter)
  -> Sponsored placements, high-commission affiliates, newsletter sponsorship
  -> No backend needed

Phase 4 — Multi-system (if phase 3 gate passes):
  Same architecture, more data files (Sony E, Nikon Z, Canon RF)
```


## Migration from Prototype

The prototype is a single 3400-line JSX file with inline styles and embedded data.

| Step | What | Status |
|---|---|---|
| 1 | TypeScript interfaces for all data types | Done |
| 2 | Extract lens data into `src/data/lenses.ts` | Done — 242 lenses |
| 3 | Extract camera data into `src/data/cameras.ts` | Done — 39 bodies, 46 fields |
| 4 | Scaffold Astro + React islands | Pending (#57) |
| 5 | Extract wiki, accessories data | Done — accessories migrated, wiki pending (#4) |
| 6 | Split into Astro pages + React islands | Pending |
| 7 | Replace inline styles with Astro scoped styles + CSS Modules | Pending |
| 8 | Add affiliate link data and Trade Deals integration | Pending |
| 9 | Deploy to GitHub Pages with custom domain (CNAME) | Pending |

### Field renames (prototype to production)

| Prototype | Production | Reason |
|---|---|---|
| `type: "P" \| "Z"` | `type: "prime" \| "zoom"` | Self-documenting |
| `format` | `mount` | Correct term for lens compatibility |
| `flMin` / `flMax` | `focalLengthMin` / `focalLengthMax` | Readable without comment |
| `ap` | `maxAperture` | Unambiguous |
| `mtf` | Split into `sweetSpotSharpness`, `wideOpenSharpness`, `cornerSharpness`, `astigmatism`, `fieldCurvature`, `comaRating` | Single number replaced by individual MTF-sourced readings |
| `lm` | `afMotor` | Three tiers: DC, STM, LM instead of boolean |
| `wr` | `isWeatherSealed` | Standard industry term |
| `kg` | `weight` | Grams for both Lens and Camera; no unit in name |
| `thread` | `filterThread` | Distinguishes from mechanical threads |
| `est` | `priceEstimated` | Readable as boolean (later removed — all prices are estimates) |
| `af` (optional) | `hasAutofocus` (required) | Default false for MF lenses |


## Session Log

### Session 1 — Foundation (~2026-04-02)
**Chat:** [TypeScript prototype from Excel workbook](https://claude.ai/chat/6f050216-4961-498f-a4ef-e27dab2a0f5b)

- Bootstrapped from an Excel workbook with X-Mount lens data
- 4 tabs: Lens Explorer, Camera Explorer, Trade Deals, Genre Guide
- Added full GF/G-Mount lens lineup and complete Fujifilm camera body history (39 bodies)
- Designed core astronomy exposure logic — Ideal ISO metric with rule-of-500
- Added FL tile grid replacing aperture grid across all genres
- Mobile card layout below 640px breakpoint
- Mount-aware ISO/MP chips (X-Mount vs GFX)
- All prices converted BGN to EUR
- Calculator tab removed (code preserved with TODO)

### Session 2 — Genre Guide & UI Polish (~2026-04-03)
**Chat:** [Fuji.me changelog: lens and camera database expansion](https://claude.ai/chat/54e23966-1869-49e6-96b8-fdb4e58aeaff)

- Fixed critical missing closing brace bug in `handheldSuitability`
- IBIS column added and removed multiple times — settled on Mode "OIS/IBIS" label
- Fixed landscape filter incorrectly hiding lenses without physical OIS
- Fixed mode sort to use `idealIsoRef` for landscape
- WR column added
- Click-to-sort column headers replacing sort chips
- Landscape-specific filter panels (Mode/Features/Price)
- Same filter panel applied to Astronomy
- EV 9 set as landscape default
- All prices prefixed with `~`

### Session 3 — Wiki, Accessories & Genre Equipment (~2026-04-05)
**Chat:** [Session priorities and pending items](https://claude.ai/chat/b4f9f5b9-2582-4221-9c4a-694320e1dfdb)

- ISO chip fix — display full number (1600 not 1.6k)
- Wiki tab expanded to 104+ entries A-Z
- Accessories tab built from scratch — ~45 items across Flash, Battery Grip, Hand Grip, Power, Lens Accessory, Adapter, Remote, Audio, Body Accessory
- Camera Explorer — click-to-sort all 9 columns
- Genre Equipment panel — all 8 genres
- Portrait genre analyzed and implemented
- Sport/Wildlife mark scores — 4-criterion formula

### Session 4 — Third-party GFX Lenses & UI Fixes (~2026-04-05-06)

- Added 19 native G-Mount third-party lenses (Venus Laowa, Mitakon, Irix, TTartisan, AstrHori, Kipon, NiSi Athena Cinema)
- Tokina atx-m 11-18mm f/2.8 X added
- Column header alignment fixes
- Sort direction bug fixed
- Type column added to Lens Explorer
- Architecture matrix f/16 row added; sweet spot label now mount-aware
- Astronomy FL chips now filter lens list by FF-equivalent FL range

### Session 5 — Analysis, Design & Scoring System (~2026-04-06-07)
**Tool:** Claude Code (imbra-spikes repo)

- Product brief (FUJI-ME.md) — 15 sections, revenue model, competitive landscape
- Architecture document — stack, data model, scoring system
- Scoring system designed — 9 genres, universal formula, entrance pupil benchmarks
- Lenstip validation — real MTF data sourced for 10+ lenses
- Tilt-shift lens research — discovered 7 native X-Mount T/S lenses
- CLAUDE.md expanded to 20 sections
- Traffic playbook written
- Bookmarks added (16 scoring methodology references)
- Excel audit completed and xlsx removed
- Repo scaffolded (Vite + React + TypeScript, later switched to Astro)
- 54 GitHub tickets created across 6 epics

### Session 6 — Data Migration & Astro Switch (2026-04-08)
**Tool:** Claude Code (me-fuji repo)

- TypeScript interfaces: Lens (40+ fields), Camera (46 fields), Genre, Affiliate, Review
- Lens data migration: 242 lenses with full specs, verified URLs, mount audit
- Camera data migration: 39 bodies, 46 fields, prices refreshed to 2026 USD
- Framework switch: Vite + React SPA to Astro + React islands
- Type system additions: ReviewLink, ReviewSource (15 trusted sources), AffiliateLink
- Scoring strategy: Genre Guide shows only scored lenses; Lens Explorer shows all
- GitHub issues: #57 (Astro switch), #61-66 (wiki entries), #68 (camera scoring discussion)
- CLAUDE.md rewritten for Astro architecture

### Session 7 — Quality & Accessories (2026-04-09)
**Tool:** Claude Code (me-fuji repo)

- Accessory type system: discriminated unions, 18 sub-interfaces, 46 accessories migrated
- solid-ai-templates added as git submodule at `docs/solid-ai-templates/`
- ESLint 9 flat config (`eslint.config.js`) — passes clean, CI ticket #73 open
- Boolean rename: ~40 fields prefixed with is/has across types, data, architecture docs
- Camera.ts inline unit comments (`// grams`, `// mm` style)
- Project structure: README (9 sections), ONBOARDING.md, PLAYBOOK.md, .prettierrc, robots.txt
- CLAUDE.md organized into 5 groups
- Upstream solid-ai-templates PRs #20-29
- Accessory data refactored to use explicit sub-interface types per category
- ADRs extracted from architecture.md into `docs/decisions/` (this session)
