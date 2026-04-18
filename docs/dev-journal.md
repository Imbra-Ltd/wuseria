# Wuseria — Development Journal

## Architecture Overview

```
Phase 1 — Launch & Scoring (COMPLETE):
  Static site (Astro + React islands), deployed to GitHub Pages
  -> 448 pages: 240+ lenses, 38 cameras, 46 accessories, 105 wiki, 9 genre screeners
  -> Genre scoring with OQ (Optical Quality) weighted formula
  -> Affiliate links as plain <a> tags with tracking params
  -> Domain: wuseria.com

Phase 2 — Revenue Diversification:
  Same static site
  -> Trade Deals section: used vs new price comparisons (MPB, KEH, eBay)
  -> High-commission affiliate programs (B&H, Amazon, Adorama, MPB, KEH)
  -> UX improvements: light theme, lens comparison, OQ filter
  -> Price audit, UI polish, remaining genre scoring

Phase 3 — Multi-system (if phase 2 gate passes):
  Same architecture + Gumroad (merch) + Buttondown (newsletter)
  -> Sponsored placements, newsletter sponsorship
  -> More mount data files (Sony E, Nikon Z, Canon RF)
  -> No backend needed
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
**Tool:** Claude Code (wuseria repo)

- TypeScript interfaces: Lens (40+ fields), Camera (46 fields), Genre, Affiliate, Review
- Lens data migration: 242 lenses with full specs, verified URLs, mount audit
- Camera data migration: 39 bodies, 46 fields, prices refreshed to 2026 USD
- Framework switch: Vite + React SPA to Astro + React islands
- Type system additions: ReviewLink, ReviewSource (15 trusted sources), AffiliateLink
- Scoring strategy: Genre Guide shows only scored lenses; Lens Explorer shows all
- GitHub issues: #57 (Astro switch), #61-66 (wiki entries), #68 (camera scoring discussion)
- CLAUDE.md rewritten for Astro architecture

### Session 7 — Quality & Accessories (2026-04-09)
**Tool:** Claude Code (wuseria repo)

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

### Session 8 — Astro Migration & Screeners (2026-04-09)
**Tool:** Claude Code (wuseria repo)

- Astro migration complete (#57 closed):
  - Scaffold with React integration, Base layout, dark theme
  - All page routes — 258 pages (lenses, cameras, genre, wiki, accessories, trade deals, 404)
  - tsconfig.json, astro.config.mjs, check:all script
- Lens Explorer MVP (PRs #101, #103, #104):
  - 9 sortable columns, chip + dropdown filters, text search
  - Mobile card layout, hero with dynamic count, filter panel
  - Warm golden accent (#e8a045) on cool dark theme
  - Code review: extracted ChipGroup, constants, memoized slugs
- Camera Explorer (PR #107):
  - 11 sortable columns, 11 filters
  - Series, year, sensor, video, body style, burst FPS, battery life
  - Shared components with Lens Explorer
- Accessories Explorer (PR #111):
  - 5 columns, category/price/mount/status filters
  - Compatibility search and badges (compatible camera/lens models)
- Docs restructured: 12 ADRs in docs/decisions/, dev-journal.md
- Upstream solid-ai-templates PRs #30-31 (typed arrays, dev journal, ADR format)
- ADR-012: domain name trademark risk — lenspip.me and lensing.me as candidates
- Issues created: #95 (hasAutofocus), #98 (field audit), #99 (coating), #100 (ghost lens), #102 (screener profiles epic), #105 (migration epic), #106 (FormFactor rename), #109 (domain decision), #110 (accessory prices)

### Session 9 — 2026-04-11

Tool: Claude Code (Opus 4.6)

**Genre scoring engine + data model review**

Genre guide implementation:
- Vitest + testing-library setup (vitest.config.ts, src/test/setup.ts)
- GenreGuide React island (mobile-first cards/table, EV scene selector, ISO/ND/FL controls)
- Exposure calculations (astroExposure, handheldExposure) co-located with component
- Genre index page (/genre) and per-genre pages (/genre/[genre])
- GenreScoreBadge.astro static component for mark pips
- ADR-013: curated genre scoring (supersedes ADR-007)

Data model deep review and cleanup:
- Lens: added genreMarks, editorialPicks, reviewSources; merged scoring onto Lens as single source of truth; removed separate GenreLensScore/genreLensScores; moved minFocusDistance to OPTICAL SPECS; created TILT-SHIFT section; renamed hasSmoothFocusRing to hasDampedFocusRing
- Genre: stripped GenreConfig to essentials (removed rule500, minShutter, scoringMethod, benchmarkLens, referenceFl); renamed label to tagline; recommendedFlRange → typicalFl: FlCategory[]; removed dead ScoreResult/ScoreBreakdown types; moved EvScene to common.ts, GenreDefault to component, AstroResult/HandheldResult to exposure.ts
- Camera: all booleans optional (absent=false); FormFactor slr→traditional, dslr-grip→grip; burstFps→mechanicalBurstFps, electronicShutterFps→electronicBurstFps; removed unused FilmSimulation type; added reviewSources
- Accessory: FujiCompatible→MountAccessory (WR removed from mixin); restored isArcaCompatible on PlateAccessory
- Common: added FlCategory, EvScene; renamed CardType→MemoryCardType; removed dead brands (Jaray, Opteka, Sainsonic)
- Review: added ReviewMethodology (lab|field), ReviewTrust (1-3), ReviewSourceInfo; removed editorial tier; removed ReviewLink (unused); removed "other" escape hatch; 16 sources in reviewSourceDirectory (src/data/reviews.ts)
- ADR-012: added wuseria.com/app/io domain candidates

### Session 10 — 2026-04-12

Tool: Claude Code (Opus 4.6)

**Scoring engine, optical data, 9 genre formulas**

Scoring engine (src/utils/scoring.ts):
- Primary floor + weighted average algorithm — primary fields (w=3) set the tier via floor, secondary fields (w=1) rank within tier
- 9 genre formulas: astro, landscape, architecture, portrait, street, travel, sport, wildlife, macro
- Physical property scores: apertureScore, weightScore, magnificationScore — computed from lens specs for genres where they enable/prevent the work
- computeGenreMark / computeAllGenreMarks functions
- 81 tests passing (snapshot tests against real lens data)

Optical quality data — 52 lenses scored:
- LensTip as primary source (trust 3, lab methodology), supplemented by OpticalLimits, Dustin Abbott, ePHOTOzine, Lonely Speck
- 14 optical fields per lens (0-2 scale): center/corner sharpness (stopped/wide open), astigmatism, coma, sphericalAberration, longitudinalCA, lateralCA, distortion, vignetting (wide open/stopped), bokeh, flareResistance
- ADR-014: optical quality rubric with per-field thresholds, sensor-normalized resolution, qualitative word-to-score mapping
- Summary page authority rule: LensTip summary page overrides individual test pages on contradiction
- Audited all 20 original scored lenses against LensTip summary pages, corrected 11 scores
- Samyang 12mm coma upgraded from 1.0 to 1.5 based on multi-source consensus (LensTip + Lonely Speck + Dustin Abbott)
- XF 80mm f/2.8 Macro cornerStopped upgraded from 0.5 to 1.0 (summary PRO: "good image quality on the edge")

Genre formulas validated:
- Astro: coma + astigmatism + apertureScore (lateralCA moved to secondary — correctable in post)
- Landscape: cornerStopped + centerStopped
- Architecture: cornerStopped + centerStopped + distortion
- Portrait: bokeh + centerWideOpen
- Street: centerStopped + apertureScore (zone focusing at f/8 is dominant technique — centerWideOpen secondary)
- Travel: centerStopped + weightScore (weight enables/prevents carrying the lens)
- Sport: centerWideOpen
- Wildlife: centerWideOpen + centerStopped
- Macro: centerStopped + magnificationScore (cornerStopped excluded — infinity test data doesn't reflect macro distances; focusDistance dropped — working distance depends on FL)

Key design decisions:
- FL is never a scoring input (creative choice, shown as filter presets)
- OIS, WR, AF are display attributes, not scoring inputs
- Weight and aperture ARE scoring inputs where they directly enable/prevent the work
- Zooms scored at mid-range FL, not extremes
- Lenses without sufficient optical data excluded from genre results entirely
- genreMarks populated on all 52 scored lenses for build-time access

PRs: #114 (scoring engine), #115 (macro genre integration)

### Session 11 — 2026-04-13

Tool: Claude Code (Opus 4.6)

**Nightscape genre screener — full UX build-out**

Genre Guide UX:
- Two-column layout: sidebar (EV scenes + equipment) | main (controls + matrix + lenses)
- Lens table spans full width below the grid
- Exposure matrix ported from prototype (Rule of 500, color-coded ISO viability)
- Genre renamed: Astrophotography → Nightscape Photography (covers stars, Milky Way, nightscapes)
- Genre index page replaced with direct screener (no card page)

Astro-specific screener:
- Dedicated columns: Mark, Brand, Model, FL, f/, Coma, Astig, Rule 500, Ideal ISO, WR, Price
- Filters matching columns 1:1: Mark, Type, Brand, f/, Coma, Astig, WR, Price
- Dynamic FL for zooms (shortest FL in overlap with selected range)
- Dynamic ISO per EV scene (auto-adjusts when clicking EV scenes)
- WR column with dot indicator (matching Lens Explorer style)
- Discontinued lenses hidden from screener
- Astro-specific footnote explaining primary/secondary scoring factors

EV scenes research and refinement:
- EV-to-Bortle mapping researched from Patat (2003), Benn & Ellison (1998), Leinert et al. (1998)
- Scene names updated: City center, Bright suburb, Suburb, Full moon, Rural town, Rural, Dark rural, Dark site, Excellent dark site, Pristine dark site
- Bortle scale shown in EV header for astro (genre-specific label override)
- Full moon labeled "(any site, ~Bortle 5-6)" — moon brightness independent of Bortle
- EV -7 = Bortle 1 solar max, EV -8 = Bortle 1 solar min
- Zodiacal light research: comparable to Milky Way brightness, not fainter
- Natural sky brightness floor: ~22.0 mag/arcsec² (EV -9 to -10), EV -8 confirmed achievable

Exposure matrix improvements:
- Standard f-stop scale: f/1.0, 1.4, 2.0, 2.8, 4.0, 5.6, 8, 11
- FL columns use actual Fuji X-mount focal lengths (not FF equivalents)
- FL ranges corrected: Ultra-wide 6-15mm, Wide 16-27mm, Standard 28-56mm, Tele 57-150mm, Super-tele 151+
- Amber threshold fixed: 1 full stop (was half stop)
- Matrix explanation text below legend

Visual polish:
- Mark pips: CSS circles (full + half), chip color scheme (accent fill)
- All table columns left-aligned
- Controls compact inline with labels
- Equipment panel font matched
- Footer: one line with links first, then FL disclaimer

Data quality:
- Lens data validation tests (94 tests passing)
- XF 80mm cornerStopped corrected 0.5→1.0 (LensTip summary: "good edge quality")

Wiki and issues:
- Wiki pages created for all 9 genres (#193-#202)
- Optical scoring explainer page planned (#205)
- Sample images for mark levels (#203)
- Editorial picks planned (#204)
- Astro accessories categories (#175)
- Bahtinov mask wiki entry (#174)
- Reusable genre screener epic (#122)

Key design insight:
- The screener is a planning tool, not a shopping page
- Workflow: Scene → Matrix → FL → Lens → Field reference
- Each element earns its place in the top-to-bottom decision funnel

PRs: #117-#212 (35+ PRs for screener build-out)

### Session 12 — 2026-04-15

Tool: Claude Code (Opus 4.6)

**Rebrand & launch — Wuseria goes live**

Rebrand:
- Full rebrand from Fuji.me! to Wuseria across 26 files (PR #247, closes #242)
- Brand name: Wuseria (no trademark conflict with Fujifilm)
- Domain: wuseria.com (registered on Namecheap, DNS configured for GitHub Pages)
- Repo renamed from me-fuji to wuseria, all clone URLs and references updated
- Footer updated: "Wuseria — Fujifilm lens & camera explorer by braboj.me"
- Historical files (ADR-012, prototype) left untouched as decision records

Deploy:
- GitHub Actions deploy workflow added (PR #248, closes #241)
- Build: checkout with submodules → Node 22 → npm ci → npm run build → upload artifact
- Deploy: official GitHub Pages deploy-pages@v4 action
- TypeScript downgraded from 6.0 to 5.9 (@astrojs/check requires ^5.0.0)
- Node upgraded from 20 to 22 in CI (Astro 6 requirement)

Homepage:
- Homepage redirects to /lenses via meta refresh (blog content planned for later)
- Nav brand links directly to /lenses (avoids redirect flash)

DNS:
- 4x A records pointing to GitHub Pages IPs
- CNAME www → imbra-ltd.github.io
- HTTPS enforced in GitHub Pages settings

Issues created:
- #249 — OQ filter for Lens Explorer (Phase 2)

Key decisions:
- Full rebrand (not hybrid) to avoid Fujifilm trademark risk
- wuseria.com confirmed after evaluating alternatives (Wusi, LensAtlas, Visu, etc.)
- TS 5.9 over dropping @astrojs/check or using .npmrc workaround

### Session 13 — 2026-04-16

Tool: Claude Code (Opus 4.6)

**Bug fixes, mobile UX, wiki cleanup**

Mobile nav:
- Added hamburger menu for screens < 640px (CSS + inline script, no React island)
- Brand + toggle on mobile, full horizontal nav on desktop
- Animated hamburger-to-X icon with aria-expanded for accessibility
- Bumped nav link font from 0.875rem to 1rem, added active underline indicator
- Increased brand-to-links spacing with gap: 2rem

Filter layout:
- Replaced flex-wrap with CSS Grid (2-col on mobile, auto-fit on desktop)
- Applied to filter dropdowns and chip rows across all 3 explorers
- Deterministic stacking — no more unpredictable wrap behaviour

Redirect flash:
- Styled index.astro redirect page with dark background (#0f1117)
- Removed visible "Redirecting..." text — instant dark-to-dark transition

Lens explorer cards:
- Replaced focal length with filter thread using Φ symbol in mobile cards

Lint / type fixes:
- Removed unused imports (ScoredGenre, OPTICAL_FIELDS, MIN_OPTICAL_FIELDS)
- Added missing FL_RANGES to useMemo dependency array
- Fixed 26 TypeScript errors in scripts: double-cast through unknown
- Removed stale git worktree that was polluting lint results

Wiki cleanup:
- Removed 10 academic/lab entries: angular-resolution, diffraction-limited-system,
  integrating-sphere, ulbricht-sphere, siemens-star, sitf, strehl-ratio,
  superlens, optical-resolution, aliasing
- Added Post-Processing category to content schema
- Moved 4 entries to Post-Processing: deblurring, deconvolution,
  gamma-correction, super-resolution-imaging
- Moved oversampling and moiré pattern from Optics to Sensor
- Wiki guiding principle established: entries should help beginners decide
  what to shoot and which lens to buy — no lab-only or theoretical content

Issues created:
- #254-#258 — Aberration wiki entries (astigmatism, distortion, chromatic
  aberration, spherical aberration, vignetting)
- #259 — Create Aberrations category and migrate entries
- #260-#263 — Post-processing technique entries (focus stacking, HDR,
  star stacking, panorama stitching)

Key decisions:
- Hamburger menu over horizontal scroll — users can't discover hidden links
- CSS Grid over flex-wrap for filters — deterministic 2-col on mobile
- Wiki rationale: beginner-friendly, decision-oriented, not academic

---

### Session 14 — 2026-04-18 — Issue Organization + Code Review

#### Issue reorganization
- Split Phase 2 catch-all milestone (58 issues) into 5 focused milestones:
  Phase 2 — SEO & Discovery, UI & UX, Wiki & Content, Equipment Database,
  Developer Tooling, Performance
- Phase 1 milestone fully cleared (0 open)
- Fixed 10 issue titles and 12 labels per base/issues.md

#### Code review + structure audit (PR #299, merged)
- Full code review against quality/SOLID/TypeScript/frontend conventions
- Full structure audit against base/docs, base/readme, base/git, etc.
- Created 11 issues (#288–#298) for findings
- Fixed 6 quick wins in PR #299

---

### Session 15 — 2026-04-18 — Code Review Fixes

Theme: clear all technical debt from the code review before Phase 2.

#### #295 — FL parameter in tripod matrices (PR #301)
- Investigated: shutter speed on a tripod is genuinely FL-independent
- Not a bug — added explanatory note to landscape/architecture matrices
- Created #300 for hyperfocal matrix tab (Phase 2 feature)

#### #290 — Extract duplicated types and helpers (PR #302)
- ColumnAlign type + makeAlignClasses() → shared/table.ts (3 consumers)
- formatFL() → utils/formatting.ts (3 consumers)
- makeLens() test factory → test/factories.ts (3 consumers)
- Net: +58 −93 lines

#### #288 — Split GenreGuide.tsx (PR #303)
- 1,041 lines → 13 focused modules
- Largest file: useGenreState.ts at 160 (pure state declarations)
- Orchestrator: GenreGuide.tsx at 109 lines
- Key extractions: useGenreState hook, useEnrichedLenses hook,
  FilterSelect reusable component, genreColumns data-driven column defs
- All 13 existing tests passed unchanged

#### #289 — Split LensExplorer and CameraExplorer (PR #304)
- LensExplorer: 375 → 4 files (max 121 lines)
- CameraExplorer: 326 → 4 files (max 115 lines)
- Same pattern: constants, filters, results, orchestrator

#### #291 — Add missing tests (PR #305)
- formatting.test.ts — formatShutter + formatFL
- slug.test.ts — toSlug edge cases
- useSort.test.ts — direction, key switch, stable prefix, nulls
- LensExplorer.test.tsx — render, search, type filter, clear, empty state
- CameraExplorer.test.tsx — render, search, clear, empty state
- Added makeCamera factory to test/factories.ts
- Test suite: 10 files, 132 tests, all passing

Key decisions:
- Tripod shutter speed is FL-independent — correct physics, not a bug
- Hyperfocal matrix is a new feature (#300), not a fix for #295
- CSS modules passed as props to sub-components (ChipGroup pattern)
- useGenreState at 160 lines accepted — pure state declarations
- FilterSelect extracted to eliminate repetitive dropdown boilerplate
