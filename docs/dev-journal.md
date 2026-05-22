# Wuseria — Development Journal

## Architecture Overview

```
Phase 1 — Launch & Scoring (COMPLETE):
  Static site (Astro + React islands), deployed to GitHub Pages
  -> 458 pages: 241 lenses, 39 cameras, 46 accessories, 115 wiki, 9 genre screeners, 1 about
  -> Genre scoring with OQ (Optical Quality) weighted formula
  -> Affiliate links as plain <a> tags with tracking params
  -> Domain: wuseria.com

Phase 2 — Polish & Foundation (IN PROGRESS):
  Same static site, 6 workstreams:
  -> SEO & Discovery: search console, JSON-LD, Lighthouse, heading hierarchy
  -> UI & UX: light theme, product images, chip polish, URL params
  -> Wiki & Content: genre wiki entries, post-processing techniques
  -> Equipment Database: optical data, scoring coverage
  -> Developer Tooling: pre-commit hooks, coverage, CI badges, Dependabot
  -> Performance: LCP, bundle size, Core Web Vitals

Phase 3 — Revenue Diversification:
  Same static site
  -> Trade Deals section: used vs new price comparisons (MPB, KEH, eBay)
  -> High-commission affiliate programs (B&H, Amazon, Adorama, MPB, KEH)
  -> UX improvements: lens comparison, OQ filter
  -> Price audit, UI polish, remaining genre scoring

Phase 4 — Multi-system (if phase 3 gate passes):
  Same architecture + Gumroad (merch) + Buttondown (newsletter)
  -> Sponsored placements, newsletter sponsorship
  -> More mount data files (Sony E, Nikon Z, Canon RF)
  -> No backend needed
```

## Migration from Prototype

The prototype is a single 3400-line JSX file with inline styles and embedded data.

| Step | What                                                         | Status                                         |
| ---- | ------------------------------------------------------------ | ---------------------------------------------- |
| 1    | TypeScript interfaces for all data types                     | Done                                           |
| 2    | Extract lens data into `src/data/lenses.ts`                  | Done — 242 lenses                              |
| 3    | Extract camera data into `src/data/cameras.ts`               | Done — 39 bodies, 46 fields                    |
| 4    | Scaffold Astro + React islands                               | Pending (#57)                                  |
| 5    | Extract wiki, accessories data                               | Done — accessories migrated, wiki pending (#4) |
| 6    | Split into Astro pages + React islands                       | Pending                                        |
| 7    | Replace inline styles with Astro scoped styles + CSS Modules | Pending                                        |
| 8    | Add affiliate link data and Trade Deals integration          | Pending                                        |
| 9    | Deploy to GitHub Pages with custom domain (CNAME)            | Pending                                        |

### Field renames (prototype to production)

| Prototype          | Production                                                                                                             | Reason                                                         |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| `type: "P" \| "Z"` | `type: "prime" \| "zoom"`                                                                                              | Self-documenting                                               |
| `format`           | `mount`                                                                                                                | Correct term for lens compatibility                            |
| `flMin` / `flMax`  | `focalLengthMin` / `focalLengthMax`                                                                                    | Readable without comment                                       |
| `ap`               | `maxAperture`                                                                                                          | Unambiguous                                                    |
| `mtf`              | Split into `sweetSpotSharpness`, `wideOpenSharpness`, `cornerSharpness`, `astigmatism`, `fieldCurvature`, `comaRating` | Single number replaced by individual MTF-sourced readings      |
| `lm`               | `afMotor`                                                                                                              | Three tiers: DC, STM, LM instead of boolean                    |
| `wr`               | `isWeatherSealed`                                                                                                      | Standard industry term                                         |
| `kg`               | `weight`                                                                                                               | Grams for both Lens and Camera; no unit in name                |
| `thread`           | `filterThread`                                                                                                         | Distinguishes from mechanical threads                          |
| `est`              | `priceEstimated`                                                                                                       | Readable as boolean (later removed — all prices are estimates) |
| `af` (optional)    | `hasAutofocus` (required)                                                                                              | Default false for MF lenses                                    |

## Session Log

### Session 1 — Foundation

**Date:** 2026-04-02
**Tool:** Claude.ai (prototype)
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

### Session 2 — Genre Guide & UI Polish

**Date:** 2026-04-03
**Tool:** Claude.ai (prototype)
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

### Session 3 — Wiki, Accessories & Genre Equipment

**Date:** 2026-04-05
**Tool:** Claude.ai (prototype)
**Chat:** [Session priorities and pending items](https://claude.ai/chat/b4f9f5b9-2582-4221-9c4a-694320e1dfdb)

- ISO chip fix — display full number (1600 not 1.6k)
- Wiki tab expanded to 104+ entries A-Z
- Accessories tab built from scratch — ~45 items across Flash, Battery Grip, Hand Grip, Power, Lens Accessory, Adapter, Remote, Audio, Body Accessory
- Camera Explorer — click-to-sort all 9 columns
- Genre Equipment panel — all 8 genres
- Portrait genre analyzed and implemented
- Sport/Wildlife mark scores — 4-criterion formula

### Session 4 — Third-party GFX Lenses & UI Fixes

**Date:** 2026-04-06
**Tool:** Claude.ai (prototype)

- Added 19 native G-Mount third-party lenses (Venus Laowa, Mitakon, Irix, TTartisan, AstrHori, Kipon, NiSi Athena Cinema)
- Tokina atx-m 11-18mm f/2.8 X added
- Column header alignment fixes
- Sort direction bug fixed
- Type column added to Lens Explorer
- Architecture matrix f/16 row added; sweet spot label now mount-aware
- Astronomy FL chips now filter lens list by FF-equivalent FL range

### Session 5 — Analysis, Design & Scoring System

**Date:** 2026-04-07
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

### Session 6 — Data Migration & Astro Switch

**Date:** 2026-04-08
**Tool:** Claude Code (wuseria repo)

- TypeScript interfaces: Lens (40+ fields), Camera (46 fields), Genre, Affiliate, Review
- Lens data migration: 242 lenses with full specs, verified URLs, mount audit
- Camera data migration: 39 bodies, 46 fields, prices refreshed to 2026 USD
- Framework switch: Vite + React SPA to Astro + React islands
- Type system additions: ReviewLink, ReviewSource (15 trusted sources), AffiliateLink
- Scoring strategy: Genre Guide shows only scored lenses; Lens Explorer shows all
- GitHub issues: #57 (Astro switch), #61-66 (wiki entries), #68 (camera scoring discussion)
- CLAUDE.md rewritten for Astro architecture

### Session 7 — Quality & Accessories

**Date:** 2026-04-09
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

### Session 8 — Astro Migration & Screeners

**Date:** 2026-04-09
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

### Session 9 — Genre Scoring Engine & Data Model Review

**Date:** 2026-04-11
**Tool:** Claude Code (Opus 4.6)

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

### Session 10 — Scoring Engine, Optical Data & Genre Formulas

**Date:** 2026-04-12
**Tool:** Claude Code (Opus 4.6)

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

### Session 11 — Nightscape Genre Screener

**Date:** 2026-04-13
**Tool:** Claude Code (Opus 4.6)

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

### Session 12 — Rebrand & Launch

**Date:** 2026-04-15
**Tool:** Claude Code (Opus 4.6)

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

### Session 13 — Bug Fixes, Mobile UX & Wiki Cleanup

**Date:** 2026-04-16
**Tool:** Claude Code (Opus 4.6)

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

### Session 14 — Issue Organization & Code Review

**Date:** 2026-04-18
**Tool:** Claude Code (Opus 4.6)

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

### Session 15 — Code Review Fixes

**Date:** 2026-04-18
**Tool:** Claude Code (Opus 4.6)

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

---

### Session 16 — 360 Analysis, Pre-Launch Fixes & Landing Page

**Date:** 2026-04-29
**Tool:** Claude Code (Opus 4.6)

360-degree analysis:

- Updated solid-ai-templates submodule (30 new commits, PR #312)
- Ran code review, structure audit, and 4-perspective 360 analysis in parallel
- Scores: Value B+, Quality B+, Viability B+, Discovery D+, Overall D+
- Created 21 issues (#313–#333) from findings
- Closed 1 false positive (#313 — Brand sort key was correct)
- Identified code review agent error: misread genreColumns.ts line 10

Pre-launch fixes (P1s resolved):

- #317 — Removed Trade Deals stub page and links from 3 explorers (PR #339)
- #315 — Added OG image (dark/light variants) + summary_large_image Twitter card (PR #341)
- #314 — Landing page: hero punchline, stats strip (build-time computed), scoring explanation, origin story (PR #343)
- #316 — Analytics: added Plausible then switched to Umami Cloud free tier (PRs #344, #345)
- #277 — Google Search Console verification meta tag (PR #346)
- #113 — Branch protection on main: required status checks, enforce admins, no force push
- #311 — Column header alignment: sort buttons now use justify-content matching column text-align (PR #347)
- #280 — Lighthouse audit: Home 98/95/100/100, Lenses 73/91/100/100 → created #349 (contrast), #350 (LCP)
- #279 — JSON-LD validation: structurally valid, image field blocked on #337

Infrastructure:

- Added CI workflow for PRs (.github/workflows/ci.yml) — required by branch protection
- Cleaned 18 stale branches (11 merged local, 11 merged remote, 7 squash-merged local)
- Triaged 76 issues with priority labels (P1–P4)
- Closed 4 duplicates (#73, #250, #278, #310)

Feature:

- #348 — Added "Not scored" option to OQ filter in Lens Explorer (PR #348)

CLAUDE.md updates:

- Added rule: never hardcode derived counts — compute from data at build time

Upstream (solid-ai-templates):

- #78 — Structure audit should decompose compound sections into individual sub-clauses
- #79 — Add rule against hardcoded derived counts and statistics

User feedback captured:

- #336 — Light theme option (from photographers)
- #337 — Product images for equipment (from photographers)
- #342 — Review scoring methodology wiki (outdated content)

Key decisions:

- Umami over Plausible — free tier allows 3 sites
- Landing page: stats strip over feature cards (avoids nav duplication)
- Hero punchline: weight + accent alternation inspired by imbra.io
- "Document everything, share everything" kept as origin story, not primary tagline
- OG image: dark variant as default, light kept for future theme toggle
- Wuseria name origin (misspelled Wisteria/Fuji) stays as easter egg

---

### Session 17 — Bugs & Fixes

**Date:** 2026-05-01
**Tool:** Claude Code (Opus 4.6)

Accessibility fixes:

- #349 — Contrast ratio: bumped --color-text-muted from #8a8fa8 to #9a9fb6 (PR #354)
  - Badge on bg-hover: 4.59:1 → 5.59:1, card text on bg-surface: 5.26:1 → 6.41:1
- #330 — Added global :focus-visible styles for all anchor elements (PR #358)
  - 2px solid accent outline, consistent with existing sort button focus styles

Performance:

- #350 — LCP on Lens Explorer: limit initial render to 50 lenses (PR #355)
  - "Show all N lenses" button expands full list
  - Filters active: all matching results shown immediately (no pagination)

SEO:

- #321 — Added rel="nofollow sponsored" on review source links (PR #357)
  - Only lens detail pages have review source links (cameras/accessories confirmed clean)

Housekeeping:

- Updated solid-ai-templates submodule (10 commits behind → current) (PR #356)
- Removed hardcoded counts from README (240+, 38, 46, 115) per no-hardcoded-counts rule (PR #356)
- #328 — Removed stale affiliates.ts reference from CLAUDE.md (PR #359)
  - Updated "affiliate links" rule to "review source links" to match actual usage

Session protocol consolidation:

- Aligned CLAUDE.md session protocol with upstream formats/agents.md (section 0 → section 6) (PR #363)
- Added base/scope.md to key references (PR #362)
- End-of-session now references base/scope.md 10-step audit instead of incomplete local checklist (PR #361, #362)
- Removed "commit before switching" rule (covered by base/scope.md)

Upstream issues created (solid-ai-templates):

- #104 — Add focus-visible rule to frontend/ux.md
- #105 — Align formats/agents.md session protocol with base/scope.md
- #106 — Add startup hygiene and build-after-change rules to base/scope.md

Key decisions:

- "Show all" button over pagination — explorer users sort/filter and need full list access
- Contrast fix via single CSS custom property — all 80+ usages updated automatically
- focus-visible (not focus) — mouse clicks don't trigger outline
- Session protocol lives at section 6 (matching upstream), with project-specific overrides only

---

### Session 18 — Pre-Launch First Impressions

**Date:** 2026-05-01
**Tool:** Claude Code (Opus 4.6)

License:

- Added LICENSE file to repo root (PR #365, closes #322)
- Initially proprietary, then switched to CC-BY-NC-ND-4.0 (PR #366)
- Researched GitHub license detection: only 13 "featured" licenses + a few CC variants
- CC-BY-NC-ND-4.0 not in GitHub's licensee database — About section stays blank
- Decision: keep CC-BY-NC-ND-4.0 for legal protection over GitHub badge visibility
- Audited solid-ai-templates (CC-BY-4.0, detected) and tutorial-git (CC-BY-NC-SA-4.0, not detected — created braboj/tutorial-git#236)

Meta SEO (PR #365, closes #329):

- Rewrote meta titles across 8 page templates with intent signals and differentiators
- Rewrote meta descriptions as pitches, not feature statements
- Index pages: "Fujifilm Lenses Compared", "Which Lens for Your Genre?"
- Detail pages: "Review Data", "Specs", "Best Lenses for [Genre]"

OG images (PR #365, closes #340):

- Resized both variants from 1731x909 to 1280x640 (2:1 ratio)
- Center-cropped to improve composition balance
- File sizes reduced: dark 1.2MB→641KB, light 877KB→516KB

Key decisions:

- CC-BY-NC-ND-4.0 over proprietary — legal protection + allows public repo on free tier
- Stay public — scoring data is derived from public sources, niche risk is low, portfolio value is high
- Meta descriptions as pitches per solid-ai-templates/frontend/static-site.md SEO rules

---

### Session 19 — SEO Closure & Performance

**Date:** 2026-05-01
**Tool:** Claude Code (Opus 4.6)

Docs:

- Fixed phase numbering in dev journal — milestones were renumbered in session 14 but overview never updated (PR #369)
- Phase 2 is now "Polish & Foundation" (6 workstreams), Phase 3 "Revenue", Phase 4 "Multi-system"

SEO & Discovery (epic #48 closed):

- #281 — Heading hierarchy audit: all pages pass, genre screener had zero H1 (PR #371)
- Genre H1 initially dynamic per tab, caused CLS — changed to static "Genre Screener"
- Epic fully complete, all 11 tasks checked off

Release:

- Tagged v0.2.0 — bumped package.json from 0.0.0 (Astro scaffold default)
- Discovered release process gap: base/git.md doesn't mention package version bump

Performance (#229, PR #373):

- Trimmed serialized data across all explorers:
  - LensExplorer: 40+ → 16 fields, gzip 26KB → 17KB (-35%)
  - CameraExplorer: 46 → 15 fields, raw 125KB → 88KB (-30%)
  - GenreGuide: 40+ → 25 fields, gzip 24KB → 16KB (-33%)
- Inlined all CSS via `build.inlineStylesheets: "always"` — zero render-blocking requests
- Attempted hero extraction (H1 from React to static Astro) — reverted, worse perceived perf
- Moved misassigned issues: #309 → UI & UX, #228 → Equipment Database
- Updated epic with current baseline and concrete remaining tasks
- Created ExplorerCamera and GenreLens lean interfaces
- Created pickGenreFields utility

Infrastructure:

- #382 — Lighthouse CI added to PR workflow (PR #383)
  - Runs on 4 key pages: /, /lenses/, /cameras/, /genre/
  - Thresholds: Performance >= 80 (error), A11y/SEO/BP >= 90 (warn)
  - Results uploaded as GitHub Actions artifacts
- Created 5 retroactive issues (#375-#379) for completed work, linked in epic
- Created 3 issues (#380-#382) for remaining performance tasks

Upstream issues created:

- solid-ai-templates #108 — Keep dev journal phases in sync with milestones
- solid-ai-templates #109 — Add package version bump to release process

CI improvements:

- #370 — Skip Lighthouse on docs-only changes via dorny/paths-filter (PR #386)
- #387 — Enforce item-by-item scope.md audit in CLAUDE.md session protocol

Issues created:

- #370 — Skip CI on docs-only changes (done)
- #375-#379 — Retroactive issues for completed performance work (closed)
- #380 — Externalize data to JSON (spike, open)
- #381 — View Transitions evaluation (spike, open)
- #382 — Lighthouse CI (done)

Upstream issues created:

- solid-ai-templates #110 — Add 'check each item independently' to end-of-session audit

Key decisions:

- Don't sacrifice perceived performance for Lighthouse scores — hero extraction caused visible flash
- Static H1 with variable-length text causes CLS on tab switch — use fixed text
- Data trimming is invisible to users — pure win
- CSS inlining trades 2KB gzip for eliminating render-blocking round-trip
- Real-world LCP (2.0s on PageSpeed) matters more than simulated 3G (3.5s)
- Hybrid session protocol: reference scope.md + project-specific additions (not full inline)

---

### Session 20 — Performance Spike Evaluation

**Date:** 2026-05-01
**Tool:** Claude Code (Opus 4.6)

Theme: evaluate performance spikes #380 and #381.

Spike evaluation:

- #380 — Externalize data to static JSON: **rejected** (ADR-016)
  - 17-19 KB gzip payloads are tiny; externalizing adds fetch waterfall
  - AppShell approach already tried and reverted in session 16
  - SEO regression risk with client-side fetch on static site
- #381 — Astro View Transitions: **adopted** (ADR-017)
  - DOM morphing eliminates full-page flash between pages
  - One-component addition (`<ClientRouter />` in Base.astro)
  - ~244 bytes gzip overhead per page — negligible

Implementation (#389, PR #391):

- Added `<ClientRouter />` from `astro:transitions` to Base.astro
- Updated hamburger menu script to re-init on `astro:page-load`
- Used `cloneNode` to prevent duplicate event listeners
- All CI checks pass including Lighthouse

Epic #229 (Performance Optimization) closed — all 9 tasks complete.

PRs merged:

- #390 — ADRs for spikes #380 and #381
- #391 — View Transitions implementation

Issues closed: #380, #381, #389, #229 (epic)

Key decisions:

- View Transitions improve perceived speed, not Lighthouse metrics — UX quality over benchmark scores
- Data externalization is the wrong direction for a static site with small payloads
- 13 lines of change is acceptable complexity for instant navigation

---

### Session 21 — UI & UX Quick Wins & CSS Consolidation

**Date:** 2026-05-01
**Tool:** Claude Code (Opus 4.6)

PRs merged:

- #395 — aria-sort on GenreTable, About page, workflow sections on homepage
- #402 — ADR-018 clickable styles consolidation (spike)
- #403 — Extract shared interactive styles into shared.module.css
- #404 — Standardize focus-visible on all interactive elements
- #406 — Restyle learn-more buttons, fix wiki chips View Transition bug

Issues closed: #270, #309 (wontdo), #320, #394, #398 (spike), #399, #400, #401, #405
Issues created: #394, #396, #397, #398, #399, #400, #401, #405
Upstream issues: solid-ai-templates #111, #112, #113, #114

Key changes:

- 458 pages (added About page)
- Shared CSS module eliminates 568 lines of duplication across explorers
- All interactive elements have consistent focus-visible (WCAG 2.1 AA)
- Homepage has workflow sections (Find your gear, Plan your shoot)
- Wiki chips bug fixed (DOMContentLoaded → astro:page-load for View Transitions)

Key decisions:

- ADR-018: Extract shared CSS module, keep two button families (accent-primary for actions, link-primary for navigation)
- Defer affiliate disclosure and feedback button until traffic/affiliates exist
- DRY, KISS, YAGNI flagged as missing core principles in solid-ai-templates

---

### Session 22 — UI & UX Polish, URL Params, Detail Page

**Date:** 2026-05-01
**Tool:** Claude Code (Opus 4.6)

PRs merged:

- #408 — Polish chip group design across explorers and genre guide
- #409 — Persist Lens Explorer filters in URL params
- #411 — Show sunstar points on lens detail page
- #414 — Show genre mark scale (/5) on lens detail page

Issues closed: #36 (outdated), #37, #274, #275, #396, #397, #415
Issues created: #410 (wiki sunstars), #412 (mobile sort), #413 (OQ coloring), #415 (mark scale)
Issues deferred: #271 → Phase 2 Wiki & Content (needs UX rethink)

Key changes:

- Chip groups: 44px touch targets on mobile, label-above-buttons layout, 2-column grid, hover/focus-visible polish, removed ~50 lines duplicated CSS from AccessoriesExplorer
- ChipGroup component: added chipButtons wrapper for layout control
- Genre controls: column stack on mobile, consistent sizing with explorers
- Lens Explorer filters persist in URL search params (shareable, bookmarkable)
- New useUrlFilters hook in src/hooks/ (reusable for Camera/Accessories)
- Sunstar points computed from aperture blades on lens detail page
- Genre marks show "/5" scale for context

Key decisions:

- Genre scoring formula breakdown prototyped but reverted — too detailed for the card format, needs different UX approach
- Keep genre chip sizing compact (content-width) vs explorer chips (equal-width grid) — different interaction contexts
- URL param names kept short: q, mount, type, brand, ois, wr, af, status, fl, aperture, thread, oq, price

---

### Session 23 — UI & UX Milestone Closure

**Date:** 2026-05-01
**Tool:** Claude Code (Opus 4.6)

PRs merged:

- #419 — Mobile sort, OQ color coding, feedback link, remove price footnote

Issues closed: #320 (already done), #412, #413, #265, #418, #246 (wontdo), #46 (epic)
Issues created: #418 (price footnote removal)
Milestone closed: Phase 2 — UI & UX (27/27)

Triage: moved #394, #270, #410 to Wiki & Content; #269 to Revenue; #251, #266, #272, #300, #336 to Phase 4; closed #246 as wontdo.

Key changes:

- Mobile sort controls: new shared MobileSort component (generic, reusable), integrated in all 3 explorers inside the filter box
- OQ scale changed from 0-10 to 0-2 (raw weighted average, no x5 multiplier) — single scale across the entire site
- OQ color coding: traffic-light colors matching FieldVal thresholds (green 1.5+, amber 1.0+, red <1.0)
- OQ filter ranges updated to 0-2 scale
- Feedback mailto link added to footer (contact@imbra.io)
- Price footnote removed from all explorers (~ prefix is sufficient)
- CLAUDE.md updated: removed price footnote rule

Key decisions:

- ADR-019: Display OQ on native 0-2 scale for consistency with optical field scores
- Feedback in footer, not nav — nav reserved for content pages
- Mobile sort inside filter box, not floating — visually grouped with other controls
- Light theme deferred to Phase 4 — dark-only is a brand choice, dual-theme adds maintenance overhead

---

### Session 25 — Pre-commit Hooks and Script Conventions

**Date:** 2026-05-02
**Tool:** Claude Code (Opus 4.6)

PRs: #428
Issues closed: #325 (pending merge)
Issues created: #427 (resolve astro check warnings), solid-ai-templates#126, #127

Key changes:

- Installed husky + lint-staged for Layer 2 quality gate (pre-commit hooks)
- lint-staged runs ESLint + Prettier on staged .ts/.tsx, Prettier on .astro/.json/.md/.css
- Added .prettierignore to exclude submodule, prototype, build output
- One-time Prettier formatting pass across entire codebase (109 files)
- Added `format` script (prettier --check) — closes Layer 3 Prettier gap
- Renamed `check:all` to `validate` — avoids collision with `check` (astro check)
- Renamed `test` to `vitest run` (single run), added `test:watch` for development
- `validate` now composes all named scripts: lint + format + check + test + build

Key decisions:

- Script naming: short verbs without namespace prefix for primary commands (lint, format, check, test); colon variants for modes (test:watch); `validate` for the full gate
- Two-commit strategy: formatting-only commit separate from functional changes to keep git blame useful
- Upstream issue created for standardizing npm scripts in solid-ai-templates
- Upstream: added testability as first-class quality attribute (pure functions, boundary architecture, SOLID-to-testing connection)
- Upstream: replaced cherry-picked design patterns with principle statement — all patterns enable testability
- Submodule bumped to pick up upstream changes (PRs #128, #129)

---

### Session 26 — Ticket Reassessment

**Date:** 2026-05-02
**Tool:** Claude Code (Opus 4.6)

Housekeeping pass across all open issues (49 → 46).

Closed issues:

- #244 — CLAUDE.md audit (done repeatedly across sessions)
- #331 — Bus factor docs (mitigations already in place)
- #334 — Sharp exclusion (transitive dep, not actionable)
- #342 — Scoring methodology review (merged into #205)

Created issues:

- #429 — Epic: Aberration wiki entries (groups #254-259)
- #430 — Epic: Genre photography guides (groups #193-202)

Changes:

- #273 — Added missing P3 priority label
- #336 — Light theme demoted from P2 to P3 (Phase 4, not urgent)
- #337 — Converted from task to spike (image sourcing needs research first)
- Enabled auto-merge on the repository

---

### Session 27 — Dependency Housekeeping

**Date:** 2026-05-03
**Tool:** Claude Code (Opus 4.6)

Resolved all `astro check` warnings and processed first batch of Dependabot PRs.

PRs merged:

- #451 — Resolve all astro check hints and warnings (closes #427)
- #453 — Bump GitHub Actions to latest major versions (checkout v6, setup-node v6, upload-pages-artifact v5, deploy-pages v5)
- Dependabot auto-merged: dorny/paths-filter v4, astro 6.2.1, @astrojs/react 5.0.4, react-dom 19.2.5, typescript-eslint 8.59.1, eslint-plugin-react-hooks 7.1.1, jsdom 29.1.1

Issues:

- #427 closed (astro check warnings resolved)
- #452 created — track ESLint 9→10 and TypeScript 5→6 major upgrades (blocked on downstream peer deps)
- Closed Dependabot PRs #447, #449, #450 (peer dependency conflicts)

Key decisions:

- Combined 4 GitHub Actions Dependabot PRs into one PR to avoid cascading rebase delays
- ESLint 10 requires coordinated upgrade with @eslint/js 10; TypeScript 6 blocked until @astrojs/check and @typescript-eslint support it
- Added `eslint-plugin-sonarjs` for cognitive complexity and code smell enforcement
- Added `max-depth` (3) and `no-console` ESLint rules; scripts/ exempted (CLI tools)
- Added `.editorconfig` for UTF-8 + LF enforcement across editors

Upstream feedback for solid-ai-templates:

- `platform/github.md` SHOULD recommend Dependabot (solid-ai-templates#131)
- Stack quality gates SHOULD include `eslint-plugin-sonarjs` for cognitive complexity (solid-ai-templates#130)

---

### Session 28 — Resolve Sonarjs Warnings

**Date:** 2026-05-03
**Tool:** Claude Code (Opus 4.6)

PRs merged:

- #465 — Resolve all sonarjs warnings and fix boolean sorting

Issues closed: #460, #463
Issues created: #463 (bug: boolean sort), #464 (task: home page redesign)

Key changes:

- Resolved all 33 sonarjs warnings across 34 files
- Promoted 4 sonarjs rules from `warn` to `error` in eslint config
- Removed redundant `ScoredGenre` type alias — replaced with `Genre` everywhere
- Extracted shared helpers: `ariaSortValue`, `sortIndicatorChar` (table.ts), `viabilityClass`, `landscapeCatClass` (helpers.ts)
- Extracted filter predicates (`passesExactFilter`, `passesBooleanFilter`, `passesRangeFilter`, etc.) to reduce cognitive complexity in all 3 explorers and genre guide
- Replaced `compareLenses` switch with data-driven `SORT_GETTERS` lookup
- Converted `GenreRowCells` if-chain to switch, extracted `dotClass` and `formatSweetSpot` helpers
- Extracted `compareValues` in `useSort` hook — fixed pre-existing bug where boolean columns (OIS, WR) were not sortable
- 134 tests passing (132 + 2 new boolean sort tests), 458 pages built

Key decisions:

- Data-driven sort comparator over switch — eliminates cognitive complexity from case proliferation
- Composable filter predicates over inline conditionals — each predicate is independently testable and reduces `&&` operator complexity
- `ScoredGenre` removal — all genres now have scoring formulas, the alias served no purpose

---

### Session 29 — Developer Tooling + Bug Fixes

**Date:** 2026-05-03
**Tool:** Claude Code (Opus 4.6)

PRs merged:

- #467 — Add gitleaks, CodeQL, lychee link checking; upgrade ESLint 9→10, TS 5→6; ADR-020
- #468 — Sort nulls last regardless of direction; guard range filters against invalid URL params
- #469 — Preserve Astro history state in useUrlFilters replaceState
- #470 — Show all lenses on sort (reverted in #472 — pagination workaround, not the real fix)
- #472 — Boolean columns start descending on first click; coerce undefined to false for sort

Issues closed: #452, #455, #456, #457, #458, #459, #471
Issues created: #471 (bug: boolean sort default direction), #473 (task: fill missing OIS/WR data), #474 (task: data distribution tests), #475 (task: factory defaults)

Key changes:

- CI: gitleaks secret detection (CLI, not paid action), CodeQL SAST, lychee link checking with --root-dir
- Toolchain: ESLint 9→10, TypeScript 5→6, @astrojs/check 0.9.8→0.9.9
- ADR-020: defer code quality platform (SonarCloud) until 3+ contributors
- useSort: nulls always last (direction-independent), descFirstKeys for boolean columns, undefined→false coercion
- useUrlFilters: replaceState preserves Astro's ClientRouter history.state
- Range filters: guard against invalid URL params across all three explorers

Bug post-mortem — #471 (OIS/WR column sort not toggling):

- Symptom: clicking OIS column header twice showed same order both times
- Root cause: zero lenses had hasOis: false — only true or undefined. Null-last logic put undefined at end regardless of direction, making asc/desc identical
- Why missed: test factories used explicit false values that didn't exist in production data; compareValues refactoring (#465) moved null checks inside function but test only covered ascending
- Fix: coerce undefined to false for boolean sort columns (descFirstKeys); start boolean columns descending
- Prevention: #474 (data distribution tests), #475 (factory defaults mirror real data), solid-ai-templates#136 (review checks)

Key decisions:

- Gitleaks CLI over gitleaks-action — action requires paid license for org repos
- Test coverage threshold (#457) already enforced — closed without changes
- Pagination expansion on sort reverted — undefined→false coercion is the real fix; expansion won't scale to thousands of lenses
- descFirstKeys parameter on useSort — boolean columns start true-first, matching user intent

Upstream flagged (solid-ai-templates):

- #132 — Factory defaults + data validation conventions
- #133 — Boolean columns sort descending first
- #134 — Pagination expands on sort (closed — workaround, not convention)
- #135 — Lychee needs --root-dir for static sites
- #136 — Three code review checks from post-mortem
- #137 — Post-mortem convention for P0/P1 bugs and incidents

---

### Session 30 — Phase 2 UI & UX Closeout

**Date:** 2026-05-03
**Tool:** Claude Code (Opus 4.6)

PRs merged: #484 (table column stability + URL filters), #486 (column width tuning)
Issues closed: #483, #478
Issues created: #485 (homepage redesign epic)
Issues deferred: #477 (changelog → folded into #485)

Key changes:

- Stabilized explorer table column widths using `table-layout: fixed` with `<colgroup>` percentage widths — eliminates layout shift on sort
- Added `ColumnDef<K>` interface to shared table utilities — centralizes key, label, align, and width per column
- Replaced 11 `useState` calls in CameraExplorer and 6 in AccessoriesExplorer with `useUrlFilters` hook — filter state now syncs to URL for shareable links, matching LensExplorer pattern
- Tuned lens table column proportions: Brand 12%, Model 22%, FL 8% — prevents clipping on zoom focal lengths and long brand names

Key decisions:

- Homepage changelog (#477) deferred — user wants a broader homepage redesign with three-column layout and feature voting (#485), changelog will be part of that
- `table-layout: fixed` chosen over `min-width` approach — fully prevents width shifts vs only reducing them
- Percentage-based colgroup widths — totals intentionally under 100% (90%) to let browser distribute remaining space as padding
- ONBOARDING.md — fixed stale homepage description (was "redirected to Lens Explorer", now shows actual homepage)

---

### Session 31 — Test Suite Improvements and Developer Tooling

**Date:** 2026-05-03
**Tool:** Claude Code (Opus 4.6)

PRs: #492 (open)
Issues closed: #475, #474 (on merge)
Issues progressed: #417 (partial — audit complete, coverage excellent)
Issues created: #490 (rulesets spike), #491 (developer.md guide)

Key changes:

- Test suite: 139 → 173 tests across 11 files
- Coverage: 86.5% → 94.9% statements, 89.4% → 98.6% lines
- Added `makeExplorerLens` factory — booleans default to undefined, matching real data shape
- Added boolean field distribution validation with `it.fails` for known data gaps (#473)
- Added `useUrlFilters` hook tests, `computeOpticalQuality` tests, `pickGenreFields` test
- Added filter behavior tests for all three explorers (mount, FL, price, WR, status, IBIS, series, mark)
- Added regression tests for bugs #313 (brand sort key) and #434 (empty pips)
- Added `npm run test:report` — HTML test results + coverage map in reports/
- Added `npm run lighthouse` — local Lighthouse CI with HTML reports in reports/
- Installed `@vitest/ui` and `@lhci/cli` as devDeps
- Updated ONBOARDING with test verification steps and optional tools (lychee, gitleaks)
- Updated PLAYBOOK with sections 2.8-2.10 (link checker, secret scanning, testing)
- Added SEO/discovery bookmarks to docs/bookmarks.md

Key decisions:

- Boolean distribution tests use `it.fails` for known data gaps — auto-flags when #473 fixes the data
- Coverage only tracks `src/utils/` and `src/hooks/` (component test coverage not enforced by thresholds)
- Lighthouse reports go to `reports/lighthouse/` (filesystem upload target in lighthouserc.json)
- lychee and gitleaks are optional local tools (not npm packages, need system install)

Upstream candidates for solid-ai-templates:

- `test:report` as a MAY command in stack templates (HTML coverage + test results)
- `it.fails` pattern for known data gaps (expected failures that auto-flag when fixed)
- Local report generation convention for CI-only tools (Lighthouse, lychee, gitleaks)

---

### Session 32 — Developer Tooling Refactors

**Date:** 2026-05-03
**Tool:** Claude Code (Opus 4.6)

PRs merged: #495 (shared utils + MarkPips styles), #496 (journal metadata)
Issues closed: #318, #319, #417, #479
Issues moved: #491 → Phase 4

Key changes:

- Extracted `formatCategory` + `CATEGORY_LABELS` to `src/utils/formatting.ts` — eliminated duplication between AccessoriesExplorer and [slug].astro
- Moved MarkPips styles to `shared/MarkPips.module.css` — no longer imports sibling's CSS module
- Removed dead `.sweetSpot` CSS class from GenreGuide.module.css
- Added `formatCategory` tests (175 total, 94.9% coverage)
- Added PLAYBOOK section 2.11 — Umami analytics verification checklist (4-step manual test)
- Retroactively added `**Date:**` and `**Tool:**` metadata to all 31 session entries
- Manually verified Umami tracking: script loads, page views register, no duplicates with View Transitions

Key decisions:

- MarkPips gets its own CSS module (not styles-as-prop) — simpler than threading styles through all consumers; convention satisfied by owning the module rather than importing a sibling's
- Umami integration is structurally sound — `is:inline` + `defer` in head, auto-tracks SPA navigations
- developer.md (#491) deferred to Phase 4 — not needed until contributors join

---

### Session 33 — Developer Tooling Milestone Closure

**Date:** 2026-05-03
**Tool:** Claude Code (Opus 4.6)

PRs:

- #498 — ADR-021: set:html exception for JSON-LD injection (closes #324)
- #499 — Replace README contributor workflows with user-facing Usage section (closes #338)

Issues closed (wontdo):

- #40 — Lens template snippet (TypeScript strict mode provides the guardrail)
- #332 — CONTRIBUTING.md (YAGNI — solo maintainer)
- #480 — Commit hash in footer (information disclosure concern)
- #481 — Release process / manual testing gates (CI gates sufficient)
- #482 — Deploy pipeline on/off switch (YAGNI)

Key changes:

- Epic #47 (Developer Tooling) completed and closed
- Phase 2 — Developer Tooling milestone closed (39 issues total)
- Bundle size monitoring marked as covered by Lighthouse CI performance gate
- README now has proper user-facing Usage section per base/readme.md

Key decisions:

- ADR-021: set:html allowed exclusively for JSON-LD via JSON.stringify() of server-controlled data
- Commit hash in footer rejected on security grounds (unnecessary information disclosure)
- Deploy switch, release gates, CONTRIBUTING.md all rejected as YAGNI for solo-maintained static site

---

### Session 34 — Solid-AI-Templates Convention Sweep

**Date:** 2026-05-04
**Tool:** Claude Code (Opus 4.6, 1M context)

PRs (wuseria):

- #518 — Add docs/360-audit.md to track audit score history (closes #517)
- #519 — Remove duplicate score scale, bump submodule
- #520 — Add gate job for fast docs-only merges
- #521 — Bump solid-ai-templates submodule (4 upstream PRs)

PRs (solid-ai-templates):

- #141 — 360 audit tracking section
- #142 — Grading scale +/- modifiers
- #143 — CI/CD patterns (8 patterns)
- #144 — Testing, frontend, security patterns (24 patterns)
- #145 — Security rules + pipeline patterns split
- #148 — Batch quick wins (11 issues)
- #152 — Dev journal entry

Issues closed: #517 (wuseria), 12 upstream issues

Key changes:

- New `docs/360-audit.md` — persists audit scores in the repo
- Gate job pattern in CI — docs-only PRs merge in ~10s instead of ~2min
- 40 reusable patterns added upstream (CI/CD, testing, frontend, security)
- New `base/security.md` — 12-section application security rules
- 11 quick wins batch: focus-visible, Dependabot, lychee, review checks, post-mortems, test factories, sonarjs, boolean sort, explicit audit steps

Key decisions:

- 360 audit scores stored in repo, not agent memory (upstream convention)
- Gate job as single required CI check — conditional jobs skip for irrelevant paths
- Pattern files separate from rules files (different purpose, different audience)
- Architecture spikes created: composition over inheritance (#151), pattern resolution (#149, #150)

---

### Session 35 — Solid-AI-Templates Architecture Spikes

PRs: none (decisions only, no code changes)
Issues closed: braboj/solid-ai-templates#151, #149, #150
Issues created: braboj/solid-ai-templates#154 (implementation task), #155 (repo org spike)

Resolved three architecture spikes for the solid-ai-templates dependency model:

- **#151 — Composition over inheritance**: ADR-004 drafted. Remove devsecops
  and cicd from quality-gates depends_on. Core tier (5 files: quality, git,
  docs, readme, testing) always loaded. Stacks compose opt-in tiers explicitly.
  Stack classification: deployed services need devsecops + cicd, static sites
  and libraries do not. Platform templates are facades (no devsecops dep).
- **#149 — Pattern file integration**: Pattern files (~1700 lines) removed
  from dependency graph entirely. Moved to docs/patterns/ as human reference.
  Rules files keep one-line pattern summaries. LLMs already know standard
  patterns from training data — agent context needs conventions, not tutorials.
- **#150 — Agent-side resolution**: Resolution algorithm is build-time
  (tools/sync.py), not runtime. Generates explicit file lists for CLAUDE.md
  startup blocks. Agents read the list as-is — no manifest parsing needed.
  Algorithm: core → stack deps → extras → platform, all recursive.

Key decisions (all in ADR-004):

- Manifest `core:` top-level list as single source of truth for core tier
- File headers must match manifest (direct deps only, no transitive expansion)
- 3 stale headers found: astro (8→2), hugo (6→1), tutorial (10→3)
- Extras use RESOLVE_DEPS (recursive) for safety
- Full IDs everywhere (explicit over implicit)
- No profiles, no auto-convention, no pattern resolution logic

---

### Session 36 — Dependency Update Sweep

PRs merged: #523, #524, #525, #526, #527, #529, #530, #531, #532
Issues closed: none
Issues created: none

Merged all 9 pending Dependabot PRs plus one manual fix:

- **astro** 6.2.1 → 6.3.1
- **github/codeql-action** 3 → 4
- **typescript-eslint** 8.59.1 → 8.59.2
- **react-dom** 19.2.5 → 19.2.6
- **lint-staged** 16.4.0 → 17.0.4 (major — drops Node 20, requires 22.22.1+)
- **@types/node** 24.12.2 → 25.6.2 (major — type definitions only)
- **globals** 17.4.0 → 17.6.0
- **zod** 4.4.2 → 4.4.3
- **react** 19.2.5 → 19.2.6 (manual PR #532 — Dependabot bumped react and react-dom separately causing version mismatch)

Key decisions:

- React and react-dom must be bumped together — Dependabot's separate PRs cause test failures due to version mismatch enforcement in React 19
- lint-staged 17 requires Node 22.22.1+ — CI uses latest 22.x (fine), local dev machine at 22.13.1 (warning only)
- Also committed session 35 journal entry and submodule bump that were left uncommitted

---

### Session 37 — Milestone Restructure and Trailing Slash Fix

Tool: Claude Code (Opus 4.6)

PRs merged:

- #537 — fix: enforce trailing slash to resolve GSC redirect indexing issues

Issues closed:

- #535 — GSC "Page with redirect" indexing issue

Issues created:

- #538 — Add CI check for trailing slash consistency in internal links

Key changes:

- Restructured milestones: collapsed 6 phase-based milestones into Backlog + Expedite + v0.5.0 (sprint)
- Set `trailingSlash: "always"` in Astro config
- Fixed all internal links (static, dynamic, nav, canonical URLs) to use trailing slashes
- Defined v0.5.0 sprint: "Complete optical scores for all lenses" (7 issues)

Key decisions:

- Milestones follow sprint model: version-named sprints (v0.5.0), Backlog for future work, Expedite for bugs/incidents
- Milestone strategy is project-specific, not upstream to solid-ai-templates
- GSC redirect root cause: GitHub Pages 301-redirects /path to /path/, Astro's default `trailingSlash: "ignore"` allowed inconsistent links

---

### Session 38 — SEO and Indexing

Tool: Claude Code (Opus 4.6)

PRs merged:

- #540 — feat: add trailing slash CI check and fix twitter:image meta
- #541 — feat: add beta version indicator under the Wuseria logo

Issues closed:

- #538 — Add CI check for trailing slash consistency in internal links
- #507 — Fix missing twitter:image meta tag
- #534 — Add beta version indicator under the Wuseria logo

Key changes:

- Added `scripts/check-trailing-slashes.ts` — scans `dist/**/*.html` for internal hrefs missing trailing slashes
- Integrated as `npm run check:links` into the `validate` pipeline
- Added `twitter:image`, `og:image:width`, `og:image:height` meta tags to base layout
- Added subtle "beta" pill badge next to Wuseria brand name in nav header
- Created `docs/seo-test-plan.md` — manual SEO test plan covering GSC, Umami, Lighthouse, and technical checks
- Submitted sitemap to Google Search Console (manual action)
- Moved #507 and #534 into v0.5.0 milestone

Key decisions:

- ~100/458 pages indexed is likely crawl pace on a young site, not a mass thin content issue (only 1 page flagged as "Crawled - not indexed")
- Thin content analysis: camera pages are weakest (zero prose), but not blocking indexing yet — revisit if GSC flags more pages
- SEO test plan frequency: weekly GSC checks until 400+ indexed, then monthly

---

### Session 39 — Lens Scoring by Brand (Viltrox)

Tool: Claude Code (Opus 4.6)

PRs:

- #558 — feat: score Viltrox lenses and restructure scoring docs

Issues closed:

- #548 — Score remaining Fujifilm lenses (no trusted data; MKX deferred)
- #549 — Score remaining Viltrox lenses (all 5 scored)
- #10, #11, #12, #13, #14 — Superseded by brand-based scoring epic

Issues created:

- #554 — Epic: lens optical quality and genre scoring by brand
- #555 — Spike: evaluate scoring methodology for cinema lenses (MKX)
- #556 — Spike: find efficient workflow for extracting review data from bot-blocked sites
- #557 — Bug: audit and fix genre mark mismatches across all scored lenses

Key changes:

- Scored 5 Viltrox lenses: AF 9mm f/2.8 Air (OQ 1.6), AF 28mm f/4.5 (OQ 1.2), AF 35mm f/1.7 (OQ 1.6), AF 56mm f/1.4 STM (OQ 1.3), AF 85mm f/1.8 II (OQ 1.4)
- Extracted scoring log from ADR-014 into `docs/scoring-log.md` — ADR now contains rubric rules only
- Added `docs/mtf-charts/` — official MTF chart images with companion `.md` analysis files
- Consolidated old per-field issues (#10-14, #514) into brand-priority epic (#554)
- Updated PLAYBOOK step 5 to reference `scoring-log.md` instead of ADR-014
- Scoring coverage: 94 → 99 lenses (39% → 41%)

Key decisions:

- Scoring by brand priority (Fujifilm → Viltrox → Sigma → Samyang → ...) instead of by optical field
- All computed genre marks must be stored, even low scores (transparency over curation)
- Official MTF charts can be used as fallback for astigmatism (S/M divergence)
- MTF chart images stored in repo with companion analysis documenting readings and scoring rationale
- CineD not added as review source — cinema methodology doesn't map to still photography rubric (spike #555)
- Bot-blocked review sites (ePHOTOzine, DCW) need a workflow solution (spike #556)
- ADR-022: scoring log extraction, MTF chart storage, genre mark completeness
- New CLAUDE.md rule: new directory or doc restructuring = write ADR before creating files
- Genre mark consistency test added — catches stored vs computed mismatches at build time

Upstream:

- solid-ai-templates#312 — ADR trigger rule for structural changes (reusable convention)

---

### Session 40 — Score Sigma Lenses and Fix Search Trim

PRs: #561 (open), merged #558 (Viltrox from session 39)
Issues: #559 (search trim bug, created + fixed), #560 (backfill scoring log, created)

Key changes:

- Merged PR #558 from session 39 (Viltrox scoring)
- Scored Sigma 17-40mm f/1.8 DC Art from LensTip + Dustin Abbott (full 15 optical fields)
- Added astigmatism from official MTF charts for 3 Sigma lenses missing the field (12mm, 10-18mm, 100-400mm)
- Downloaded and analyzed official MTF charts for all 11 Sigma lenses with companion .md files
- Backfilled scoring log entries for all 10 scored Sigma lenses (traceability per ADR-022)
- Fixed bug: search filters return no results when query has trailing spaces (#559)
- Sigma 16-300mm f/3.5-6.7 remains unscored — no trusted review data available yet
- Identified 6 scorable Samyang lenses for next session

Key decisions:

- Backfilling scoring log for 60+ Fujifilm lenses deferred to #560 (P3) — documentation, not scoring
- Official MTF chart S/M divergence used as astigmatism fallback per ADR-014 (3 lenses benefited)

---

### Session 41 — Samyang Lens Scoring

PRs: #567 (open)
Issues closed: #551 (via PR)
Issues created: #562 (model name audit), #563 (MTF scraper), #564 (scoring log backfill), #565 (optical construction fields), #566 (image-based inference spike)
Issues updated: #554 (epic — Samyang checked off), #560 (Samyang backfill complete)

Key changes:

- Scored 16 new Samyang lenses (100 -> 116 total, 18/20 Samyang scored, 97.6% field coverage)
- Added 20 MTF chart images + companion analysis files to docs/mtf-charts/
- Expanded review source directory from 17 to 32 sources (international: France, Germany, Sweden, Japan, Hong Kong)
- Upgraded DxOMark + The Digital Picture to trust-3; added Lloyd Chambers + Lonely Speck as trust-3
- Created scripts/fetch-page.py (Playwright) for bot-blocked sites

Key decisions:

- Trust-2 source aggregation rule added to ADR-014: 2 trust-2 sources = 1 trust-3 per field
- Community consensus fallback added to ADR-014: tiered cap (3 sources=1.0, 5+=1.5, 5+ with data=2.0)
- Optical construction inference applied for SA: aspherical elements + zero complaints = 1.5 (conservative)
- ADR-022 updated: scoring log entries must list all 14 fields with explicit undefined markers
- MTF chart astigmatism fallback validated: chart-derived scores applied to 135mm f/2 (2.0) and AF 12mm (0.5)
- Coma-corner correlation tested empirically: 14% outlier rate, not reliable for scoring (ADR rule preserved)
- Fisheye distortion scored 0.0 by design (intentional barrel distortion)

---

### Session 42 — Laowa Lens Scoring

PRs: #568 (merged — restore fetch script), #570 (open — Laowa scoring)
Issues closed: #552 (via PR #570)
Issues created: #569 (spike — scoring feasibility for budget Chinese brands)
Issues updated: #554 (epic — Laowa checked off)

Key changes:

- Scored Laowa Argus 33mm f/0.95 CF APO (14 optical fields, 8 genre marks, 3 trust-3 sources)
- Removed 2 lenses from database: 10mm f/2 Zero-D (MFT only), 15mm f/2 Zero-D (no X-mount)
- Added 4 missing X-mount lenses: 4mm f/2.8 Fisheye, 8-16mm f/3.5-5 Zoom CF, 10mm f/4 Cookie, Argus 25mm f/0.95 CF APO
- Fixed existing data: 12-24mm year (2022→2024), weight (497→575g), shift (10→7mm), price (1250→750); 33mm blades (14→9), year (2020→2021)
- Restored lost scripts/fetch-samyang-mtf.py with --dry-run, --seq, --temp flags
- Added temp/ to .gitignore
- All 8 GFX Laowa lenses remain unscorable (no trusted lab data)
- Scoring log entry added for 33mm f/0.95 with conflict resolution notes
- Scoring coverage: 117/243 lenses (net +2 lenses in DB from add/remove)

Key decisions:

- 12-24mm f/5.6 Zoom Shift CF left unscored: too new (2024), only proxy data from C-Dreamer (different optical formula)
- GFX third-party lenses are a data desert: zero trust-3 quantitative reviews across all 8 lenses
- Verified complete Laowa X-mount lineup against multiple sources; corrected database accordingly

---

### Session 43 — Voigtlander Scoring and Global Source Scan

Tool: Claude Code. PR [#571](https://github.com/Imbra-Ltd/wuseria/pull/571).

- Scored 2 Voigtlander lenses from LensTip: Ultron 27mm f/2, Nokton 35mm f/0.9 Aspherical
- Added scoring log entries for all 7 Voigtlander lenses (including existing Nokton 35mm f/1.2)
- Documented 4 lenses as unscorable: Nokton 23mm f/1.2, Nokton 50mm f/1.2, Color-Skopar 18mm f/2.8, Macro APO-Ultron 35mm f/2
- Fixed Nokton 50mm f/1.2 X-mount specs: discovered it's an exclusive APS-C Sonnar design (290g, 9 elem/8 groups), not a rehoused SE. Weight 492→290g, filter 52→58mm, MFD 450→390mm
- Deep scan of 40+ review sources across 10+ languages (German, French, Italian, Japanese, Chinese, Korean, Russian, Nordic, Dutch, Czech)
- Added 8 new review sources: digitalkamera.de, fotoMAGAZIN, Focus Review, Fotografi Digitali (lab trust-2); Asobinet, Fujiya Camera, Map Camera KASYAPA, Radojuva (field trust-2). Total: 40 sources (10 trust-3, 30 trust-2)
- Confirmed optyczne.pl = lenstip.com (same company, must never count as separate sources)
- Epic #554 completed — all 6 brand scoring tasks done
- Scoring coverage: 119/243 (49%)

Issues created: #572 (lens page SEO spike), #573 (evaluate new sources), #574 (in-house testing spike), #575 (composite trust-2 scoring rule spike)

Key decisions:

- Lab-quality lens testing is concentrated in ~15 sites globally (Europe + USA). No Chinese, Korean, or Russian lab sites exist. Japanese sites are qualitative only despite Cosina being Japanese
- Nokton 50mm f/1.2 X-mount is a completely different optical design from VM/SE versions — data from other mounts does not apply
- Macro APO-Ultron 35mm f/2 reached 6 of 7 fields from trust-2 aggregation (Fujiya + KASYAPA) but falls 1 short of MIN_OPTICAL_FIELDS; composite scoring rule (#575) could unlock it

---

### Session 44 — Lens Model Name Audit

Tool: Claude Code. PRs [#579](https://github.com/Imbra-Ltd/wuseria/pull/579), [#580](https://github.com/Imbra-Ltd/wuseria/pull/580).

- Full audit of all 243 lens model names against B&H Photo and official manufacturer sites
- Normalized aperture format to `f/X.X` across 16 lenses (7Artisans, Handevision, Kamlan, Meyer Optik, Samyang, Laowa)
- Added missing optical suffixes to 15 Samyang lenses (ED, AS, IF, UMC, NCS, CS) to match scoring log
- Fixed Fujifilm names: removed spurious LM from XF 16/2.8, XF 23/2.8, XF 56/1.2 R WR
- Fixed 7Artisans: 10mm AF not a fisheye (rectilinear); 18mm is UFO not Cap; added Fisheye to 7.5mm
- Fixed Mitakon 20mm aperture f/2.4→f/2, added "Super Macro"
- Fixed AstrHori 18mm: Shift not Tilt-Shift; 40mm GFX dropped M suffix
- NiSi: added ASPH to Sunstar lenses; renamed Athena→Athena Prime (8 GFX cine lenses)
- Added Laowa APO suffix to 65mm, Viltrox Air suffix to AF 35mm f/1.7, Laowa Argus prefix to 33mm
- Removed phantom Mitakon Speedmaster 50mm f/0.95 — never existed for X-mount (full-frame only)
- Added generation markers: 7Artisans 7.5mm Fisheye II, 60mm Macro Mark II, all 4 Meyer Optik lenses (II)
- Fixed Trioplan 50mm aperture f/2.9→f/2.8 (Mark II changed it)
- Added 7Artisans 35mm f/1.2 Mark II and 55mm f/1.4 Mark II as separate entries
- Fixed 7Artisans Mark I weights: 35mm 200→150g, 55mm 300→272g
- Confirmed Meike 25mm f/0.95 and 60mm f/2.8 Macro valid (meikeglobal.com, B&H gap)
- Total: 57+ naming fixes, 1 lens removed, 2 lenses added. DB now 244 lenses, 461 pages

Issues created: #577 (7Artisans Mark II audit — closed), #578 (questionable mount availability — closed)

---

### Session 45 — Homepage SEO

**Date:** 2026-05-13
Tool: Claude Code. PR [#582](https://github.com/Imbra-Ltd/wuseria/pull/582).

- Reinforced H1 keywords ("Fujifilm", "lens", "scored", "genre") in homepage body sections (#544)
- Increased homepage word count past 250-word SEO minimum (#545)
- Removed overpromising lens count from subtitle — was claiming all 244 lenses "rated against genres" when only ~48% are scored
- Subtitle now count-free: "Fujifilm lenses scored for your genre"
- Merged PR #580 (model name audit followup from session 44)
- Cleaned up stale local branches

Issues created: #581 (Lighthouse a11y 0.85 on /genre/), #583 (evaluate removing stats bar), #584 (update meta description)

---

### Session 46 — Sigma Scoring Completion

**Date:** 2026-05-13
Tool: Claude Code. PRs [#585](https://github.com/Imbra-Ltd/wuseria/pull/585), [#586](https://github.com/Imbra-Ltd/wuseria/pull/586).

- Merged PR #585 (Lighthouse a11y fix for /genre/ page, #581)
- Scored last Sigma lens: 16-300mm f/3.5-6.7 DC OS C — 13/14 optical fields from The Digital Picture (trust-3) and ePHOTOzine (trust-2), 8 genre marks
- Fixed 7 spec errors on the 16-300mm: year, magnification, blades, weight, diameter, length, min focus distance
- Added 4 official MTF charts + companion analysis for astigmatism inference
- Closed #559 (search trailing spaces bug — already fixed in prior session)
- Closed #562 (model name audit — already resolved in PR #579)
- Moved 5 issues to Backlog milestone: #556, #563, #565, #566, #574
- Expanded Samyang MTF script from 15→20 lenses (full coverage)
- Created Sigma MTF scraper script covering all 11 lenses with dual URL pattern support
- Both scripts now skip existing files by default; `--force` flag to re-download
- Scoring coverage: 120/244 (49.2%), all 11 Sigma lenses complete

---

### Session 47 — Scoring Methodology

- PR #589
- Closed #587 (trust criteria), #575 (composite scoring), #573 (multilingual sources), #588 (MTF format)
- Moved #560, #564 to Backlog milestone
- ADR-023: formal trust-level criteria — 3 criteria per methodology type (lab: reproducibility, field coverage, consistency; field: controlled methodology, per-field analysis, domain authority)
- ADR-024: composite trust-2 field scoring — 3-tier system (dual trust-2 → no cap, trust-2 + trust-1 corroboration → no cap, single trust-2 → cap 1.5)
- Promoted ePHOTOzine trust-2 → trust-3 (Imatest lab, verified on XF 56mm f/1.2 R and Sigma 15mm f/1.4 DC C)
- Promoted ColorFoto trust-2 → trust-3 (Image Engineering lab, LP/BH PDFs freely downloadable)
- Evaluated 5 trust-2 sources for potential trust-3: Photography Blog (no — qualitative only), CineD (no — camera lab, not lenses), Amateur Photographer (no — no numerical data), Les Numeriques (inconclusive — cookie wall), ColorFoto (yes — promoted)
- Evaluated 4 remaining multilingual candidates: all rejected (Xitek — no methodology, fotoaparat.cz — qualitative/no X-mount, leclaireur.fnac.com — cameras only, Progresso Fotografico — site dead)
- ADR-022 updated with canonical MTF companion file format
- Removed non-conformant MTF file (sigma-16-300mm wrong slug + free-form prose)
- All 34 MTF companion files verified conformant
- Trust-3 sources: 8 lab + 5 field = 13 total (up from 5 lab + 5 field = 10)

---

### Session 47 — Complete Priority Brand Scoring

- Tool: Claude Code (Opus 4.6)
- PR #592
- Issues created: #590 (officialUrl validation tests), #591 (genre page verification after renames)
- Moved #569, #572 from v0.5.0 to Backlog
- Epic #554 ready to close on merge

Key changes:

- Researched all trust sources for 6 remaining priority brand lenses (Voigtlander 4, Samyang 2)
- All 4 Voigtlander X-mount lenses unscorable — zero trusted review coverage
- Samyang 20mm f/1.8: partially scored (3/14 fields from ePHOTOzine + Lonely Speck), below genre mark threshold
- Samyang 300mm f/6.3: unscorable mirror lens, zero trust-3 reviews
- Documented all 18 remaining priority brand lenses (+ Fujifilm 5, Venus Laowa 13) with not-scored comments and scoring log entries
- All scoring log entries expanded with full 14-field tables per ADR-022

Spec fixes:

- Samyang 20mm: model name 20mm f/1.8 → 20mm f/1.8 ED AS UMC, apertureBlades 8 → 7, year 2018 → 2016
- Samyang 300mm: model name → 300mm f/6.3 ED UMC CS Reflex, apertureBlades 8 → 0 (mirror lens), hasApertureRing → false
- Laowa 15mm f/4.5R Shift GFX: fixed broken officialUrl
- Laowa 8-15mm f/2.8 GFX: fixed officialUrl pointing to wrong product variant

Key finding: Voigtlander Nokton 50mm f/1.2 X-mount is a completely different optical design (9 elem/8 groups Sonnar) from the E-mount/VM versions (8 elem/6 groups aspherical) — existing reviews cannot be applied

---

### Session 48 — Pre-release Review and v0.5.0 Tag

- Tool: Claude Code (Opus 4.6)
- PR #598
- Tagged v0.5.0, closed milestone
- Closed #593 (deep review), #594-#597 (code quality fixes)
- Created #599 (negative conditions), #600 (glossary vs wiki spike), #601 (lens suffix guide), #602 (brand name discoverability), #603 (search visibility audit), #604 (Bing Webmaster Tools)
- Created v0.6.0 milestone: content depth and SEO

Deep review findings and fixes:

- Stale scale references (0-10, 0-100) corrected across README, scoring.ts, 2 wiki articles — all now reflect 0-2/1-5 scale per ADR-019
- .gitignore: added .DS_Store, Thumbs.db, desktop.ini, .vscode/, \*.swp
- Magic numbers: extracted X_CROP_FACTOR, GFX_CROP_FACTOR, RULE_OF_500_FACTOR, NIGHTSCAPE_DEFAULT_ISO_X/GFX, OQ_THRESHOLD_HIGH/MID — 17+ occurrences across 9 files replaced
- DRY: extracted passesBooleanFilter, passesExactFilter, passesMaxFilter, passesMinFilter, passesRangeFilter, passesStatusFilter, passesSearchFilter to src/utils/filters.ts — removed from 3 consumer files
- Bug: added descFirstKeys to useMemo dependency array in useSort.ts
- CSS: moved all hardcoded hex colors from MarkPips.module.css and GenreGuide.module.css to CSS custom properties in global.css

360 analysis update:

- Value: B+ → A- (all 9 genres live, 120/244 scored, 461 pages)
- Quality: B+ → A- (176 tests, all MUST violations fixed)
- Viability: B+ → A- (24 ADRs, CI solid, scoring methodology formalized)
- Discovery: D+ → C (canonical URLs, sitemap, OG tags, but only 106/461 pages indexed, 201 total impressions)

GSC data: 106/461 pages indexed (23%), ranking only for wiki content ("golden ratio", "bortle scale"). Lens pages not indexed — thin content confirmed as root cause. v0.6.0 reprioritized: #603 (search audit P1) and #572 (lens page SEO P1) are the top priorities

---

### Session 49 — Fill Boolean Fields

- PRs: #607 (fill hasOis/isWeatherSealed for all 244 lenses), #608 (set Sigma/Tamron WS to true)
- Issues closed: #473
- Issues created: #606 (3-level weatherSealing scale)
- Key changes:
  - All 244 lenses now have explicit `hasOis` and `isWeatherSealed` values — zero undefined
  - hasOis: 27 true (Fujifilm OIS, Sigma OS, Tamron VC), 217 false
  - isWeatherSealed: 67 true (Fujifilm WR, Sigma dust/splash, Tamron moisture-resistant, NiSi 9mm, Irix), 177 false
  - Moved fields from PENDING_BOOLEAN_FIELDS to POPULATED_BOOLEAN_FIELDS, removed it.fails block
  - Added Fujifilm-specific validation test (177 tests, 0 expected failures)
- Key decisions:
  - Weather sealing threshold: `true` for any documented sealing (mount gaskets, dust/splash resistant) — consistent with NiSi 9mm precedent
  - 3-level scale deferred to #606 to distinguish partial vs full sealing

---

### Session 50 — SEO Spike and Data Completeness

- PRs: #621 (Fujifilm build fields + ADR-025 + Samyang + TTartisan + tooling)
- Issues closed: #602 (domain discoverability), #612-#619 (superseded by per-brand approach)
- Issues created: #611 (epic: fill all given spec fields), #620 (spike: issue age policy), #622-#642 (per-brand data fill tickets)
- Key changes:
  - ADR-025: keep wuseria.com despite wisteria search confusion — too early to judge at 2 weeks
  - Removed `hasDampedFocusRing` from Lens type — does not discriminate meaningfully
  - Filled build/handling fields for Fujifilm (66), Samyang (20), TTartisan (19) = 105 lenses
  - All Fujifilm lenses: hasRotatingFront=false, hasFocusRing=true confirmed from photographyblog
  - All Samyang/TTartisan MF lenses: non-rotating front, distance scale, clicked aperture confirmed from official pages + AI overview
  - TTartisan AF 75mm f/2 X-mount confirmed via B&H + TTartisan store (official page only listed E/Z/L)
  - Set hasApertureRing=false for 7 Fujifilm lenses without rings (5 XC, XF 18-120mm PZ, GF 35-70mm)
  - Added fetch-page.py caching (.cache/fetch/) and full-page screenshots with lazy-load scrolling
  - Added audit-brand.ts script for comprehensive field coverage reporting
  - Restructured epic #611 from per-field to per-brand, expanded scope to all given spec fields (not just build)
- Key decisions:
  - ADR-025: wuseria.com stays — trademark safety over search disambiguation (ref ADR-012)
  - Field dependency rules: isApertureClickless absent when hasApertureRing=false; afMotor absent = MF
  - Content generation plan stored in memory, deferred until data gaps filled (ref #572)
  - hasDampedFocusRing removed — all non-budget lenses have damped rings, field always true
  - Per-brand workflow more efficient than per-field — one pass fills all specs from one source

---

### Session 51 — Backfill Build Fields: Samyang, TTartisan, 7Artisans

- PRs: #646 (Samyang + TTartisan + 7Artisans build fields)
- Issues closed: #624 (7Artisans build fields, auto-close via PR)
- Issues created: #644 (score all 19 TTartisan lenses), moved #43 (Equipment Database Completion) to v0.6.0
- Key changes:
  - Samyang (20 lenses): diameter 20/20, length 20/20, maxMagnification 16/20, macro genre marks added for 9 lenses
  - TTartisan (19 lenses): diameter 19/19, length 19/19, maxMagnification 9/19, hasApertureRing fixed for AF 27mm
  - 7Artisans (18 lenses): diameter 18/18, length 18/18, maxMagnification 16/18, all boolean build fields filled (was 0/18)
  - Fixed 7Artisans 7.5mm Fisheye II apertureBlades 7->5 (official store spec)
  - Fixed 7Artisans 18mm UFO hasApertureRing true->false (fixed aperture body cap)
  - Replaced discontinued 7Artisans 50mm f/1.2 (2020) with Mark II (2025)
  - Assessed fujixpassion.com as trust-1 (not added to review sources)
  - Validated thin lens magnification formula against 130 lenses — median 39% error, not usable as fallback
- Key decisions:
  - No calculated maxMagnification fallback — formula too unreliable (39% median error across 130 lenses)
  - LensTip spec database is best source for maxMagnification on budget lenses (7Artisans, TTartisan)
  - LensTip page IDs don't match URL names — must verify Manufacturer/Model fields on every page
  - digitalkamera.de useful for dimensions but rarely has magnification
  - Discontinued lenses removed when unbuyable and replaced by new version
- Sources used: lksamyang.com, ttartisan.store, 7artisans.store, LensTip spec DB, digitalkamera.de, Dustin Abbott, Phillip Reeve, allphotolenses.com, cameradecision.com, photosynthesis.bg, photozone.de

---

### Session 52 — Venus Laowa and Meike Build Field Backfill

- PRs: #650
- Issues closed: #625 (Venus Laowa), #626 (Meike)
- Epic: #611 (fill all given spec fields)
- Key changes:
  - Filled build fields for all 16 Venus Laowa lenses (8 X-mount, 8 GFX) — 100% complete
  - Filled build fields for all 14 Meike lenses (5 discontinued, 9 current) — 95% (5 discontinued missing maxMagnification)
  - Data corrections: Venus Laowa 100mm T/S maxMagnification 2.0→1.0, 55mm T/S filterThread 82→77, 15mm f/4.5R apertureBlades 5→14
  - Data corrections: Meike 85mm Macro maxMagnification 1.0→1.5, apertureBlades fixes on 5 lenses, 12mm f/2.0 filterThread 67→62
  - Added missing macro genre marks for 9mm f/2.8 and Argus 33mm (triggered by new maxMagnification)
  - Clarified ADR-002 Cloudflare Pages rejection rationale
- Key decisions:
  - Estimated maxMagnification values (calculated from focal length + min focus) are not accepted — only spec-confirmed values
- Sources used: venuslens.net, laowalenses.ca, meikeglobal.com, LensTip spec DB, Dustin Abbott, Phillip Reeve, OpticalLimits, ePHOTOzine, Thom Hogan/sansmirror, B&H Photo, Radojuva, CameraDecision, Digitec Galaxus

---

### Session 53 — Viltrox, Sigma, NiSi Backfill

- PRs: #654 (open)
- Issues: #627, #628, #629 (will auto-close on merge)
- Epic: #611 — now 11/25 brands done
- Key changes:
  - Filled build fields for all 13 Viltrox lenses — 6 have aperture rings (13mm clicked, 23/33/56mm f/1.4 clickless, 27/75mm Pro clicked), 7 do not (Air series, pancake, 85mm II)
  - Filled build fields for all 11 Sigma lenses — 3 newer (12mm, 15mm 2024; 17-40mm Art 2025) have aperture rings, 8 older do not
  - Filled build fields for all 10 NiSi lenses — 2 Sunstar X-mount + 8 Athena Prime GFX
  - NiSi Athena corrections from official brochure: apertureBlades 9→10, weights updated to GFX-specific values (860g core, 1040g 135mm)
  - Added maxMagnification + minFocusDistance + diameter + length for Viltrox 15mm/25mm/56mm f/1.7
  - Added NiSi 15mm f/4 Sunstar specs from phillipreeve review (maxMagnification 0.13, minFocusDistance 200, diameter 79, length 77)
  - Added macro genre marks for 3 Viltrox Air lenses (triggered by new maxMagnification)
- Key decisions:
  - NiSi Athena maxMagnification left unfilled — cinema manufacturers don't publish it; can't estimate per ADR-014 rules
  - Sigma aperture ring appeared on mirrorless lenses starting late 2024 (12mm, 15mm DC DN C) and 2025 (17-40mm Art)
- Sources used: sigma-global.com, viltrox.com (Playwright), LensTip build quality pages, OpticalLimits, Dustin Abbott, Phillip Reeve, NiSi official brochure (PDF), nisi-lens.com, NiSi Optics USA, CineD, Duclos Lenses, B&H Photo

---

### Session 54 — PLAYBOOK Restructure and Quality Pipeline

- Tool: Claude Code (Opus 4.6)
- PRs: #673 (wuseria, auto-merge pending), solid-ai-templates #315 (merged)
- Issues: #672 (will auto-close on #673 merge), solid-ai-templates #316, #317 (created)
- Key changes:
  - Restructured PLAYBOOK from 4 sections to 5 — added dedicated Quality section (section 3)
  - Quality section has 15 subsections covering full pipeline: validate overview, pre-commit hooks, Prettier, astro check, Vitest, eslint-plugin-sonarjs, Lighthouse, lychee, gitleaks, CodeQL, Dependabot, Umami, GSC, PageSpeed Insights, Screaming Frog
  - Updated trust-3 source table from 6 to 12 sources
  - Added missing utility scripts (fetch-sigma-mtf.py, list-unscored.ts)
  - Applied consistent "what (tool)" naming convention to all subsections
  - Removed Seobility (redundant with Screaming Frog)
  - Updated solid-ai-templates docs.md: 5-section PLAYBOOK structure with extensibility clause
- Key decisions:
  - Quality is a distinct PLAYBOOK chapter, not a subsection of Domain operations or Maintenance
  - Manual verification tools (Umami, GSC, PSI, Screaming Frog) belong in Quality alongside automated checks — they drive code changes
  - Screaming Frog replaces Seobility — full-site crawl supersedes per-page browser check
  - Projects MAY extend beyond the 5 base sections; Release and deploy MUST remain last

---

### Session 55 — Expedite Backlog and Type-Checked Linting

- Tool: Claude Code (Opus 4.6)
- PRs: #674 (submodule bump), #675 (version bump + CLAUDE.md rule), #677 (aperture format), #678 (zero fractions + type-checked linting)
- Issues closed: #647 (release v0.5.0), #649 (aperture format), #645 (zero fractions), #679 (type-checked linting)
- Issues created: #676 (CI version-match check, P4 Backlog)
- Key changes:
  - Bumped package.json from 0.4.0 to 0.5.0 — release had used wrong flow (no-build instead of version manifest)
  - Added release rule to CLAUDE.md: "Releases MUST follow PLAYBOOK 5.1"
  - Normalized f/2 to f/2.0 in 11 lens models (4 more than issue listed)
  - Removed 845+ unnecessary .0 from numeric literals across data and source files
  - Added eslint-plugin-unicorn with no-zero-fractions (S7748) and prefer-number-properties (S7773)
  - Added explicit comparators to all bare .sort() calls (S2871)
  - Enabled type-checked ESLint linting via projectService — activated 67 sonarjs rules that were silently inert
  - Fixed 45 type-checked violations: prefer-read-only-props (25), no-unnecessary-type-assertion (7), restrict-plus-operands (7), no-base-to-string (6), prefer-regexp-exec (3), no-alphabetical-sort (2), restrict-template-expressions (1)
  - Used recommended (not recommendedTypeChecked) to avoid no-unsafe-\* failures on CSS modules and Astro content imports in CI
- Key decisions:
  - recommendedTypeChecked breaks CI due to unresolved CSS module and Astro content types — use recommended + projectService instead
  - Pre-commit lint ~7s per file with type checking — acceptable for lint-staged
  - Added 4 more unicorn rules: no-negated-condition (S7735), prefer-string-replace-all (S7781), prefer-export-from (S7763), prefer-global-this (S7764)
  - Merged duplicate import/import-type statements across 9 files (S3863)
  - Lens detail pages now show all build fields with em-dash for missing values — 6 new fields added (clickless aperture, focus ring, focus by wire, distance scale, rotating front, tripod mount)
  - Expedite milestone fully cleared

---

### Session 56 — Spec Backfill for 13 Remaining Brands

- Tool: Claude Code (Opus 4.6)
- PRs: #683
- Issues closed: #630, #631, #632, #633, #634, #635, #636, #637, #638, #639, #640, #641, #642
- Epic #611: 24/25 tasks done (only #609 isInternalFocusing remains)
- Key changes:
  - Backfilled all given spec fields for 53 lenses across 13 brands: Voigtlander (7), AstrHori (7), Mitakon (6), Handevision (5), Meyer Optik (4), Tamron (4), Tokina (4), Lensbaby (4), Carl Zeiss (3), Kamlan (3), Sirui (3), Pergear (3), single-lens brands (4)
  - New fields per lens: hasCircularAperture, maxMagnification, hasFocusRing, isApertureClickless, hasDistanceScale, hasRotatingFront, hasTripodMount, diameter, length
  - 40+ data corrections found during research (apertureBlades, filterThread, weight, minFocusDistance)
  - Added macro genre marks to 4 scored lenses (Voigtlander Nokton 35mm f/1.2, Ultron 27mm, Nokton 35mm f/0.9, Carl Zeiss Touit 12mm, Touit 32mm)
  - 8 maxMagnification values sourced from LensTip, Phillip Reeve, and Google AI Search
  - Used 7 parallel research agents for initial data gathering
- Key decisions:
  - Subagents don't read CLAUDE.md or PLAYBOOK — must include relevant rules in agent prompts
  - Always read PLAYBOOK 2.8 before launching spec research agents — LensTip and Radojuva are priority sources for maxMagnification
  - 17 lenses have genuinely unpublished maxMagnification — confirmed across all playbook sources, web search, and PDF catalogs

---

### Session 57 — Content Strategy and SEO Spike

- Tool: Claude Code (Opus 4.6)
- PRs: #696
- Issues closed: #572 (spike), #611 (epic), #622, #623, #684
- Issues created: #684, #693, #694, #695
- Milestones: created v0.7.0; trimmed v0.6.0 from 29 → 3 issues
- Key changes:
  - ADR-026: Lens detail page content strategy (7-section page structure)
  - Nav button renamed "Genre Guide" → "Genres"
  - Spike: maxMagnification fallback — concluded no action needed (all missing lenses score bucket 0)
  - Spike: isInternalFocusing field — researched, prototyped, discarded (needs per-lens verification, deferred to video genre)
  - Spike #572: content generation feasibility — recommended IMPLEMENT
- Key decisions:
  - ADR-026: deterministic prose from optical scores at build time (ref: `docs/decisions/026-lens-page-content-generation.md`)
  - 4 optical quality clusters (sharpness, aberrations, rendering, distortion) — not 14 sub-headings
  - 9 per-genre explanations with pros AND cons derived from formula fields
  - `scoringStatus` enum for missing data transparency
  - `communityNotes: string[]` for user opinions (deferred population)
  - Focus on 120 scored lenses first — usable pages over data completeness
  - v0.7.0 milestone: content depth, implementing ADR-026

---

### Session 58 — v0.7.0 Spikes and Lightweight Promise

- Tool: Claude Code (Opus 4.6)
- PRs: #700, #702, #703, #704
- Issues closed: #693 (spike), #695 (spike), #697 (bug)
- Issues created: #701 (structured data review check), #705 (PWA offline support)
- Upstream: solid-ai-templates#319 (structured data semantic accuracy), solid-ai-templates#320 (ADR conventions)
- Key changes:
  - Removed misleading `offers` from JSON-LD on all product pages (not a store)
  - ADR-026 updated: unscored lenses get ~150-200 words of spec-based content (no noindex needed)
  - ADR-026 expanded: phrase tables, genre formulas, templates, worked example folded in from content spine
  - ADR-027: asset storage strategy — MTF charts as generated SVG, readings table inline, chart as linked asset
  - Content spine deleted — implementation specs belong in their ADR
  - `docs/specs/` created then removed (folded into ADR)
  - Homepage hero tagline: "No install. No login. No bloat. Works on 3G in the field."
- Key decisions:
  - ADR-027: generate own MTF chart SVGs, not manufacturer images (copyright, consistency)
  - ADR-027: readings table inline (3G-friendly), SVG chart as linked asset (ref: `docs/decisions/027-asset-and-spec-storage.md`)
  - Unscored pages are not thin — specs provide enough content without noindex
  - No forward references between ADRs — self-contained or reference backward only
  - Implementation specs fold into their ADR, not separate files
  - "No install" not "No app" — future-proofs for PWA (#705)
  - Wiki page titles must match search queries, not internal jargon
  - OQ scores need source provenance (reviewed, mtf, inferred) — #709
- Second half:
  - PR #710: optimized 10 wiki page titles against GSC query data
  - Issue #698 closed
  - Issues created: #707 (MTF score automation), #708 (construction score automation), #709 (score provenance)
  - Upstream: solid-ai-templates#321 (SEO strategy checks for structure audit)

---

### Session 59 — ADR-026 Content Generation Prototype

- Tool: Claude Code (Opus 4.6 1M)
- **solid-ai-templates upstream**: 3 PRs (#322, #323, #324), 13 issues closed — ADR conventions, wrap-up checklist, post-release verification, PLAYBOOK naming, HTTPS enforcement, trailing slash, structured data, type-checked ESLint, SEO strategy, manual verification tools
- Submodule updated: PR #712
- **Release v0.6.0**: PR #713, tag pushed (was missed from milestone close)
- **ADR-026 prototype**: PR #716
  - `src/utils/lens-content.ts` — content generation utility with phrase tables, genre fit analysis, optical cluster assessments, alternatives finder, meta description
  - `src/pages/lenses/[slug].astro` — full redesign: summary (verdict + genre tiers + strengths/weaknesses), specifications (with optical construction), optical quality (pip table + cluster assessments), genre fit (chip overview + primary/secondary per genre), reviews, alternatives, TOC, back-to-top
  - `src/content/wiki/scoring-methodology.md` — expanded with 14-field descriptions, 4 clusters, genre formula table, primary/secondary explanation
  - `src/types/lens.ts` — added opticalElements, opticalGroups, specialElements
  - Data fixes: XF 56mm price $1000→$1200, magnification 0.09→0.14, removed dead fujivsfuji link, added thephoblographer review
  - 16 new tests for lens-content utility
- Convention change: price rounding $250 → $50
- Issues created: #714 (backfill trust-3 reviews for XF 56mm), #715 (price verification workflow)
- Epic #694: 5/9 tasks complete

---

### Session 60 — Alternatives Ranking Rework

- **Tool:** Claude Code (Opus 4.6)
- **Theme:** v0.7.0 epic — alternatives logic (#717) and portrait scoring spike (#718)

#### PRs merged

- **#719** — Alternatives rework: ±20% proportional FL range, OQ-based sorting, type grouping (5 same + 3 other), discontinued filter
- **#720** — ADR-028: alternatives ranking algorithm
- **#721** — Remove data fix exception for main commits

#### Issues closed

- **#717** — Rework alternatives logic (auto-closed by PR #719)
- **#718** — Portrait aperture scoring spike (closed, no change — aperture in secondary affects 3/94 lenses by -0.5, in primary is destructive)

#### Issues created

- **#718** — Evaluate adding aperture score to portrait genre formula

#### Key decisions

- OQ is the right genre-neutral sort for alternatives (ADR-028)
- Portrait formula unchanged — floor mechanism makes aperture either negligible (secondary) or destructive (primary)
- Macro lenses are valid portrait alternatives (fstoppers article reference)
- No commits to main, no exceptions (removed data fix clause from CLAUDE.md)

#### Bookmark added

- Macro lenses for portraiture (fstoppers.com) in `docs/bookmarks.md`

---

### Session 61 — MTF Chart SVG Rendering

- **Tool:** Claude Code (Opus 4.6)
- **Theme:** Render MTF charts as inline SVG from pixel-extracted data

#### PRs created

- **#724** — MTF charts as SVG from pixel-extracted data

#### Key changes

- New types: `MtfReading`, `MtfChart`, `MtfData` in `src/types/mtf.ts`
- New data: `src/data/mtf-readings.ts` with 3 digitized lenses (Sigma 16mm, Sigma 56mm, Samyang 12mm)
- New component: `MtfChart.astro` — static SVG renderer with legend, zero JS
- New tool: `tools/mtf-extract-sigma.py` — automated pixel extraction from Sigma MTF chart PNGs
- New tool: `tools/mtf-overlay.html` — visual overlay verification
- MTF charts integrated into lens detail page Specifications section

#### Key decisions

- ADR-027 revised: SVG-from-data replaces PNG image migration (no `src/assets/mtf/` needed)
- Per-brand extraction scripts (`mtf-extract-sigma.py`, future `mtf-extract-samyang.py`)
- Curve-following gap detection reliably distinguishes solid (S) from dashed (M) lines through crossings
- Edge readings beyond last grid line added via rightmost-pixel detection

#### Next

- Build `tools/mtf-extract-samyang.py` for Samyang chart format (different colors/line styles)
- Digitize remaining ~28 lens charts
- Spike #707 (automate sharpness/astigmatism from MTF data) now feasible with digitized readings

---

### Session 62 — MTF Extraction Accuracy Fix

- **Tool:** Claude Code (Opus 4.6)
- **Theme:** Fix continuity bug in Samyang MTF pixel extraction and review PR #725

#### PRs updated

- **#725** — Samyang MTF chart extraction tool and readings data (added fix commit)

#### Issues created

- **#726** — Apply continuity-based curve tracing to Sigma MTF extraction tool (task, P3, v0.7.0)
- **#727** — Skeletonization-based MTF curve extraction pipeline (spike, P3, v0.7.0)
- **solid-ai-templates#325** — Add deploy health check to session startup checklist (upstream)

#### Key changes

- Fixed `pick_y` in `mtf-extract-samyang.py` — was always selecting topmost pixel cluster (`min(centroids)`), now uses continuity-based selection (closest to previous position's y value)
- Fixed missing position 0 fallback — rows with partial data no longer skipped entirely
- Re-extracted all 20 Samyang lenses with corrected algorithm
- Example fix: 12mm f/2 at f/8 position 14 `resolution30M`: 0.97 → 0.23 (matches chart)
- Added deploy health check to CLAUDE.md session startup protocol (step 3)

#### Key decisions

- Continuity-based cluster selection is a general pattern — applies to Sigma tool too (#726)
- Skeletonization (Otsu + Zhang-Suen) explored as root-cause alternative to heuristic fixes (#727)
- Deploy health check added to session protocol after discovering 19h stuck GitHub Pages deploy

#### Next

- Merge PR #725
- Apply continuity fix to Sigma extraction tool (#726)
- Evaluate skeletonization pipeline (#727)
- Continue ADR-026 implementation (#694)

---

### Session 63 — MTF Extraction and Optical Quality Architecture

**Tool:** Claude Opus 4.6 (1M context)

#### PRs

- #734 — skeletonization MTF extraction tool + ADR-029

#### Issues closed

- #727 — Skeletonization-based MTF curve extraction pipeline (spike, ADAPT)
- #730 — MTF inference validation (spike, revised conclusions after literature review)

#### Issues created

- #732 — Collect missing tele-end MTF charts for Sigma zoom lenses
- #733 — Evaluate contrast fields and consistency scoring for genre formulas

#### Key changes

- **MTF extraction tool v2** (`tools/mtf-extract-skeleton.py`):
  Color isolation → skeletonize → connected components for S/M classification.
  Sigma: no dilation, fragment width classifies solid vs dashed. Samyang: dilate
  for anti-aliasing, 4-color masks. Occlusion fill for overlapping curves.
  Auto-detects grid step (APS-C 2.5mm vs full-frame 5mm). Zero gaps across
  all 31 charts (20 Samyang + 11 Sigma).

- **Spike #730 revised conclusions**: Initially concluded MTF can't predict
  scores (data correlation showed no signal). After authoritative literature
  review (Nikon USA, Zeiss H.H. Nasse, LensRentals Roger Cicala, Eckhardt
  Optics), revised: the optical relationships are valid (sharpness, astigmatism,
  bokeh tendency). The limitation is computed vs measured MTF — not MTF itself.
  ADR-014 fallback #2 stands.

- **ADR-029**: Splits Optical Quality into Overview + Optical Design Analysis +
  Lab & Field Tests. Design Analysis covers MTF chart analysis, rendering
  character (contrast-resolution gap for "pop" vs clinical), stopped-down
  behavior, cross-frame consistency, and optical construction. Confidence
  tiers: measured MTF (Sigma Art, Zeiss, Leica) gets direct language,
  computed MTF gets qualified language. Enables ~100-150 extra words for
  unscored lenses.

#### Key decisions

- ADR-029 (supersedes ADR-026 section 3)
- Rendering character readable from 10 vs 30 lp/mm gap — but current genre
  scoring has no contrast fields, only resolution (#733 created)
- Construction inference uses confident language ("controls CA" not "designed
  to control") — these are physical optical properties
- Variance disclaimer tied to computed vs measured MTF, not brand tier
- Coating data needed for flare analysis (#99 updated with ADR-029 context)

#### Next

- Merge PR #734
- #733 — evaluate contrast fields and consistency scoring for genre formulas
- #726 — apply continuity fix to Sigma extraction tool
- #728 — MTF chart wiki page
- Continue ADR-026 implementation (#694)

---

### Session 64 — Genre Formula Validation Spike

**Tool:** Claude Code (Opus 4.6)

#### PRs

None — research-only session.

#### Issues closed

- #733 — Evaluate contrast fields and consistency scoring for genre formulas (spike, P2)

#### Issues created

- #737 — Document per-genre field rationale in ADR-013 (task, P2)

#### Key changes

- Spike #733 evaluated three proposed genre formula changes:
  1. Contrast fields (10 lp/mm) — rejected, only 18% of scored lenses have MTF readings data
  2. Consistency scoring (center-corner delta) — rejected, only 5/120 lenses change marks (4%), 87% floor-capped
  3. `_apertureScore` in portrait — rejected, only 3 lenses change and all downward (penalizes slow lenses)
- Validated portrait formula is correct: XF 56mm f/1.2 R's low portrait mark (2) reflects real photographer experience — forum evidence shows lens was mostly shot at f/1.4-f/2, softness at f/1.2 was tolerated not celebrated, WR replacement universally considered better
- Confirmed aperture rationale: street/travel need fast aperture for uncontrolled lighting; portrait is shot in controlled light (studio, reflectors)
- Identified documentation gap: ADR-013 has formula table but no per-field photographic rationale (#737)

#### Key decisions

- Genre formulas confirmed correct as-is — no ADR needed
- Consistency score useful for OQ page prose (ADR-029) but not for genre scoring
- Per-genre field rationale to be added to ADR-013 (#737)

#### Next

- #737 — document per-genre field rationale in ADR-013
- #565 — backfill optical construction fields
- #735 — implement ADR-029 OQ content generation
- #726 — apply continuity fix to Sigma extraction tool
- #728 — MTF chart wiki page

---

### Session 66 — MTF Chart Verification and Optical Specs Restructure

**Tool:** Claude Code (Opus 4.6)

#### PRs

- None yet (branch: `feat/optical-construction-and-coating`)

#### Key changes

- Lens-by-lens verification of all Fujifilm MTF charts against official specs pages
- Fixed GFX frequency labels — each GF lens uses different lp/mm (10/15/20/40/45), not uniform
- Converted all MTF images to PNG (was webp/gif/jpg mix)
- Added `wide-` prefix to all zoom wide-end files for consistency
- Downloaded missing charts from Fujifilm CDN (zoom wide/tele gaps)
- Replaced wrong charts: legends saved as charts, GFX data on APS-C lenses, CMS duplicates
- Created `docs/optical-specs/` with per-lens subfolders (ADR-031)
- Verified and moved 55 Fujifilm lenses; 5 remain unverified in `docs/mtf-charts/`
- Added `notes.md` per lens when source is non-official or problematic

#### Key decisions

- ADR-031: optical-specs directory structure with per-lens subfolders
- Fujifilm en-us specs pages have frequent CMS bugs; global pages (`/global/`) are more reliable
- Third-party lenses (Samyang, Sigma, Viltrox) pending review

#### Next

- Review third-party MTF charts (Samyang, Sigma, Viltrox)
- Fix remaining 5 unverified Fujifilm lenses
- Add official URLs to GF lens database entries

---

### Session 67 — Optical Construction & Tool Consolidation

**Tool:** Claude Code (Opus 4.6)

#### PRs

- None yet (branch: `feat/fujifilm-optical-specs`)

#### Key changes

- Refactored Fujifilm fetch scripts from `scripts/` into `tools/fujifilm/` with shared `common.py` module
- Corrected `specialElements` for 5 lenses: XF 18-55mm (+1 ED), XF 18-135mm (+2 ED), XF 55-200mm (+1 Super ED), MKX 18-55mm (+6 Super ED), MKX 50-135mm (+2 Super ED)
- Converted all construction images from webp/jpg to PNG format
- Copied construction images into per-lens `docs/optical-specs/` subdirectories (35 lenses)
- Added 29 MTF charts to `docs/mtf-charts/`
- Documented issues: MKX 50-135mm wrong construction image, XF 16-55mm wrong diagram on official page

#### Key decisions

- None (continuation of ADR-031 implementation)

#### Next

- Continue optical construction diagrams for XF primes
- Review and verify remaining unverified Fujifilm lenses
- Third-party MTF chart review

---

### Session 68 — Fujifilm Optical Specs Completion

**Tool:** Claude Code (Opus 4.6)

#### PRs

- #764 — Complete Fujifilm optical specs collection

#### Key changes

- Copied 26 XF + 4 XC construction images from `docs/optical-construction/` into per-lens `docs/optical-specs/` folders
- Converted and moved 10 unverified MTF charts from `docs/mtf-charts/` (webp/jpg to PNG)
- Removed 29 verified Fujifilm files from `docs/mtf-charts/` (only Samyang remains)
- Visually verified all 45 XF + XC construction diagrams
- Found and removed 1 invalid diagram: XC 16-50mm (unlabeled third-party, dark background)
- Sourced XC 16-50mm construction from Digital Photography Live (official Fujifilm diagram rehosted)
- Sourced XC 15-45mm construction from LensTip (priority source — missed by web search)
- XC 35mm construction copied from XF 35mm f/2.0 R WR (same optical formula, documented in notes)
- Result: 65/66 Fujifilm lenses complete (only MKX 50-135mm T2.9 remains — no MTF published, construction deferred)

#### Key decisions

- None (continuation of ADR-031 implementation)

#### Lesson learned

- Construction diagrams and MTF charts are embedded images in review articles — web search engines index text, not image contents. Always check PLAYBOOK 2.8 priority sources (LensTip, Radojuva, Phillip Reeve) directly before falling back to generic web search. The XC 15-45mm diagram was on LensTip the whole time.

#### Next

- Merge PR #764
- MKX 50-135mm construction: manual fetch from official page
- Start next brand in epic #739 (Samyang or Sigma — scored P2 brands first)

---

### Session 69 — ADR-029 Prerequisites and Samyang Tool

**Tool:** Claude Code (Opus 4.6)

#### PRs

- #765 — mtfType field, Samyang optical data, and extraction tool (auto-merge pending)

#### Key changes

- Added `mtfType: "computed" | "measured"` to `MtfData` type — all 22 MTF entries set to `"computed"`
- Removed `docs/optical-construction/` (64 files already migrated to `docs/optical-specs/` per ADR-031)
- Backfilled `opticalElements`, `opticalGroups`, `specialElements`, `coating` for all 20 Samyang lenses from official product pages
- New `tools/samyang/` extraction tool: `fetch_specs.py`, `audit.py`, `common.py`
  - Extracts specs, MTF charts, and construction diagrams from Samyang product pages
  - Targeted spec table block extraction avoids false positives from navigation links
  - Plain urllib (no Playwright needed) — Samyang pages are static HTML
  - Page caching via `.cache/fetch/*.html`

#### Key decisions

- Sigma published MTF charts are computed (design data), not measured — corrected understanding from ADR-029 which grouped Sigma Art with Zeiss/Leica as measured. Correction deferred to a separate fix.
- 86/244 lenses now have optical construction data (Fujifilm 66 + Samyang 20)
- Wrap-up checklist steps 6 and 9 strengthened: must enumerate new files/directories/commands before evaluating — prevents batch-dismissing structural changes
- Upstream issue: solid-ai-templates#327 (scope.md checklist fix)

#### Next

- Merge PR #765
- Correct ADR-029 Sigma MTF classification
- Continue #565/#99 backfill for remaining brands (Sigma, Carl Zeiss next per epic #739)
- #735 — implement ADR-029 OQ content generation (prereqs now partially met)
- MKX 50-135mm construction: manual fetch from official page

---

### Session 71 — Sigma Optical Specs and Folder Structure

#### PRs

- #768 — Sigma optical specs, tools, and folder structure formalization

#### Issues created

- #767 — Add wiki entry for MTF charts (P3 task)

#### Key changes

- Migrated 11 Sigma MTF charts from `docs/mtf-charts/` to `docs/optical-specs/`
- Created `tools/sigma/` extraction tools (fetch_specs.py, audit.py, common.py)
  - Plain urllib like Samyang — Sigma pages are static HTML
  - Extracts elements, groups, special elements (FLD, SLD, aspherical), coating
  - Fallback detection for pages without explicit counts (marked with `~` prefix)
  - Downloads construction diagrams and MTF charts (diffraction + geometrical)
  - Fixed URL pattern to handle naming variants across Sigma page generations
- Downloaded construction diagrams for all 11 Sigma lenses
- Downloaded official MTF charts: diffraction + geometrical for all 11 lenses
- Populated optical construction fields in lenses.ts for all 11 Sigma lenses
- Verified special element counts against construction diagrams (visual inspection) and cross-validated with independent sources (OpticalLimits, B&H, Imaging Resource, Dustin Abbott)
- Documented Sigma diffraction vs geometrical MTF chart types in analysis files
- Removed 11 duplicate MTF files (old migration copies identical to downloaded versions)
- Renamed all 45 `notes.md` → `analysis.md` per ADR-033
- Moved XF 16-55mm back to `notes.md` (operational content, not analysis)
- Removed repeated ADR-014 boilerplate from 23 analysis files
- Updated Fujifilm audit tool to reference `analysis.md`

#### Key decisions

- ADR-032: Use diffraction MTF for scoring and display — comparable across all manufacturers, includes real-world diffraction constraints. Geometrical MTF retained in optical-specs for reference only.
- ADR-033: Per-lens optical-specs folder structure — `analysis.md` (predictions), `scoring-log.md` (per-lens justification, incremental migration from monolith), `notes.md` (optional operational notes). Cross-lens comparison is the database's job.
- SLD is a glass material property, aspherical is a surface shape — a single element can be both (e.g. Sigma 56mm f/1.4)
- Sigma construction diagram color legend: red outline = aspherical, yellow fill = FLD, blue fill = SLD

#### Next

- Continue brand backfill (Carl Zeiss, Tamron next per epic #739)
- #767 — wiki entry on MTF charts
- Incremental migration of monolithic scoring-log.md to per-lens files

---

### Session 72 — Viltrox Optical Specs Collection

PRs: #768 (Sigma merge), #769 (Viltrox optical specs)
Issues closed: #742 (Sigma), #746 (Viltrox)
Epic: #739 — Sigma and Viltrox checked off

#### Key changes

- Merged PR #768 (Sigma optical specs from previous session)
- Created `tools/viltrox/` extraction tools (fetch_specs, audit, download_images, common)
- Populated optical construction fields for all 13 Viltrox lenses: opticalElements, opticalGroups, specialElements, coating
- Downloaded MTF charts and construction diagrams for all 13 lenses from Viltrox Shopify theme pages and LensTip
- Normalized all coating to "HD Nano multilayer coating" (brand-level standard confirmed via Dustin Abbott, Viltrox product images, distribution channel spec sheets)
- Converted all images from JPG to PNG per project convention
- Replaced undersized images (768px CDN variants) with full-resolution originals
- Replaced 27mm f/1.2 Pro construction with LensTip cross-section diagram
- ADR-033 updated: PNG image format requirement formalized
- Brand-level coating default added to Viltrox tools (inferred with flag)
- Download tool improved: broad CDN pattern matching, size variant deduplication

#### Key decisions

- ADR-033 amendment: all optical spec images must be PNG (ref ADR-033)
- Viltrox coating is a brand-level attribute — same "HD Nano multilayer coating" across entire lineup, not per-lens
- Shopify JSON API misses theme-embedded images — must scrape full HTML with broad patterns
- PetaPixel not added as review source — news/editorial site, no systematic optical testing

#### Next

- Continue brand backfill (Carl Zeiss, Tamron, Venus Laowa next per epic #739)
- #767 — wiki entry on MTF charts

---

### Session 73 — Docs Folder Cleanup

PRs: #770 (session 72 wrap-up merge), #772 (docs cleanup)
Issues created: #771 (lens database audit against third-party lists)
Issues updated: #560 (expanded to all brands with missing scoring logs)

#### Key changes

- Migrated 77 scoring log entries from monolithic `docs/scoring-log.md` to per-lens `docs/optical-specs/<slug>/scoring-log.md` — completes ADR-033 migration
- Folded lens content spine spec (`docs/specs/lens-content-spine.md`) into ADR-026 — phrase tables, genre formulas, derived fields, alternatives logic, meta template
- Deleted `docs/specs/` directory (content merged into ADR-026)
- Deleted `docs/mtf-charts/` directory (6 files, superseded by `docs/optical-specs/`)
- Deleted `docs/scoring-log.md` (152KB, fully migrated to per-lens files)
- Created `docs/audits/` — split `docs/360-audit.md` into timestamped `2026-04-29-360.md` and `2026-05-03-360.md`
- Moved `docs/seo-test-plan.md` to `docs/audits/seo-test-plan.md`
- Updated all cross-references in CLAUDE.md, README.md, PLAYBOOK.md, ADR-014, ADR-022, ADR-026, ADR-033
- Identified 43 scored lenses with no scoring log documentation (gap: Fujifilm 40, Viltrox 8, Carl Zeiss 3, Tamron 4, Tokina 4)

#### Key decisions

- Per our ADR convention, implementation specs fold into the ADR itself — no separate spec files
- ADR filenames describe the decision topic, not current state — ADR-022 filename kept as-is
- SEO test plan is an audit checklist by nature — belongs in `docs/audits/`, referenced from PLAYBOOK 3.16

#### Next

- Continue brand backfill (Carl Zeiss, Tamron, Venus Laowa next per epic #739)
- #560 — backfill scoring logs for 43 scored lenses missing documentation
- #767 — wiki entry on MTF charts
- #771 — audit lens database against third-party X-mount/GFX lists

---

### Session 74 — Optical Spec Tools: Carl Zeiss, Tamron, Tokina

PRs: #774 (optical spec tools and data)
Issues closed: #740 (Carl Zeiss), #743 (Tamron), #744 (Tokina)
Epic: #739 — Carl Zeiss, Tamron, Tokina checked off (7/9 scored brands done)

#### Key changes

- Created `tools/tamron/` extraction tools (common, fetch_specs, audit) — plain urllib, dual-page spec parsing (main + /spec.html)
- Created `tools/tokina/` extraction tools (common, fetch_specs, audit) — plain urllib, alt-text scraping for special elements
- Created `tools/zeiss/` extraction tools (common, fetch_specs, audit) — PDF datasheet download (product pages return 404)
- Populated optical specs for all 4 Tamron lenses: elements, groups, special (LD, XLD, GM aspherical, hybrid aspherical), coating (BBAR/BBAR G2)
- Populated optical specs for all 4 Tokina lenses: elements, groups, special (aspherical, SD), coating (Multi-coating)
- Downloaded PDF datasheets for all 3 Zeiss Touit lenses
- Extracted MTF charts, construction diagrams, vignetting, and distortion charts from Zeiss PDFs
- Fixed Zeiss Touit physical specs from datasheet verification (weight, diameter, length, minFocusDistance)
- All audits pass: Zeiss 3/3, Tamron 4/4, Tokina 4/4

#### Key decisions

- Zeiss Touit lenses are discontinued — no live product pages, officialUrl points to PDF datasheets on zeiss.com
- Zeiss tool downloads PDFs rather than scraping HTML (unique among brand tools)
- Tamron specs split across two pages (main product page + /spec.html) — tool concatenates both
- Tokina puts special element names in image alt text — tool extracts alt attributes before stripping tags

#### Next

- Venus Laowa optical specs (16 lenses, #745)
- Voigtlander optical specs (#747)
- #767 — wiki entry on MTF charts

---

### Session 75 — Tamron Tech Spec Verification

PRs: #774 (updated with fixes)
Issues closed: none
Issues created: solid-ai-templates#329 (no-force-push convention)

#### Key changes

- Fixed aperture blades for 3 Tamron lenses (9→7 for B060, B061, A057) — official spec pages confirm 7
- Fixed X-mount dimensions for 3 lenses (B060, B070, B061) — tool had used Sony E-mount values
- Added missing fluorine coating to all 4 Tamron lenses — product pages list it separately from optical coatings
- Added missing 2 LD special elements to B070 (17-70mm) — confirmed by LensTip and PhotographyBlog, not on Tamron's own page
- Fixed Tamron extraction tool (`tools/tamron/common.py`) to detect fluorine coating
- Updated ADR-033 to allow SVG format alongside PNG for optical spec images
- Added spec verification step to PLAYBOOK 2.8 (fill and verify tech specs per brand)

#### Key decisions

- No force push — use merge instead of rebase when resolving conflicts on pushed branches (solid-ai-templates#329)
- SVG allowed for optical spec images (ADR-033 update) — vector format preserves chart text at any scale
- Protective coatings (fluorine) are often listed separately from optical coatings on manufacturer pages — extraction tools must check both sections
- PLAYBOOK 2.8 now includes image cross-check step: verify extracted data against construction diagrams

#### Next

- Tokina tech spec verification (4 lenses)
- Venus Laowa optical specs (16 lenses, #745)
- Voigtlander optical specs (#747)

---

### Session 76 — Tokina Tech Spec Verification

- **Tool:** Claude Code (claude-opus-4-6)
- **Branch:** `fix/tokina-tech-specs`

#### Issues

- Created #779 — Add tech spec cross-validation to brand fetch tools (P2, v0.7.0)

#### Key changes

- Fixed all 4 Tokina officialUrl values: hyphens → underscores to match tokinalens.com URL scheme
- Fixed afMotor on all 4 Tokina lenses: "LM" → "STM" (official pages confirm ST-M stepping motor)
- Fixed maxMagnification on all 4 lenses against official specs (23mm: 0.15→0.1, 33mm: 0.15→0.1, 56mm: 0.14→0.1, 11-18mm: 0.25→0.11)
- Fixed weight: 23mm 285→276g, 33mm 270→285g
- Added missing hasApertureRing: false on 11-18mm zoom
- Converted 6 Tokina optical-spec images from JPG to PNG for consistency

#### Key decisions

- Tokina PLUS branding is packaging-only refresh (June 2022) — no optical or spec changes, no model rename needed
- Existing fetch tools only verify optical construction (elements/groups/coating) and field presence — they do not cross-validate tech specs (weight, magnification, motor type) against official pages; #779 tracks the gap
- PNG is the project convention for optical-spec images (195 PNG vs 6 JPG before this session); JPGs converted

#### Next

- Venus Laowa optical specs (16 lenses, #745)
- Voigtlander optical specs (#747)
- Tech spec cross-validation for all brand tools (#779)

---

### Session 77 — Voigtlander Optical Specs & Character Lens Research

- **Tool:** Claude Code (claude-opus-4-6)
- **Branch:** `feat/voigtlander-optical-specs`

#### PRs

- #781 — feat: Voigtlander optical specs extraction tool and data (open, from previous session)

#### Issues created

- #783 — Explore Artistic Quality (AQ) scoring via MTF blueprint matching (spike, P2, Backlog)
- #784 — Draft forum questions for character lens rendering discussion (task, P3, Backlog)

#### Issues updated

- #511 — Establish community presence for discovery — added task references (#699, #784)

#### Key changes

- Assessed all ~23 third-party character lenses in the database (Voigtlander Noktons, 7Artisans f/0.95 series, TTartisan, Lensbaby, Meyer Optik, Zhongyi Speedmaster)
- Identified the core problem: OQ rubric (ADR-014) penalizes character lenses because all 14 fields score "more corrected = better"
- Proposed AQ (Artistic Quality) as a parallel scoring dimension using MTF blueprint matching against archetype curves (Classic Glow, Soap Bubble, Swirl, Soft Classic)
- Documented Nikon DC Nikkor 105mm f/2D as prior art — mechanical SA correction ring validates that character is quantifiable on a continuous scale
- Discovered Voigtlander's deliberate MTF publication policy from their catalog PDF (cosina.co.jp): APO-LANTHAR lenses get MTF charts, Noktons do not — confirms character lenses operate on a different quality axis
- Discovered Voigtlander PORTRAIT HELIAR 75mm F1.5 (E-mount) has an SA correction ring — Voigtlander's own DC concept
- Researched MTF data availability for legendary character lenses — confirmed systematic scarcity; third-party measured data is the only path for X-mount Noktons
- Drafted 22 forum questions across 8 themes for community discovery and data gathering
- Formalized `notes.md` → renamed to `specs-log.md` as mandatory technical specs provenance log (ADR-033 update); pairs with `scoring-log.md`

---

### Session 78 — Venus Laowa Optical Specs (Coating & Cleanup)

- **Tool:** Claude Code (claude-opus-4-6)
- **Branch:** `feat/venus-laowa-optical-specs`

#### PRs

- (pending) Venus Laowa optical specs — 14 commits, ready for PR creation

#### Key changes

- Added coating data for all 16 Venus Laowa lenses: 7 with Frog Eye Coating (FEC, hydrophobic front-element), 9 with generic multi-coating (Venus Laowa doesn't name their AR multi-coating)
- Converted 14 JPG + 1 WebP images to PNG for format consistency across optical-specs
- Created specs-log.md provenance logs for all 16 lenses (mandatory per ADR-033)
- Sources: venuslens.net (cached via SeleniumBase), photographyblog.com, PetaPixel, 4KShooters, B&H Photo, jonasrask, Fstoppers, Digital Camera World, OpticalLimits, Phillip Reeve, LensTip, DustinAbbott

#### Key decisions

- Frog Eye Coating is a hydrophobic surface coating (like Fujifilm fluorine), not an anti-reflective optical coating — stored in `coating[]` field alongside AR coatings for consistency with how Fujifilm stores `"fluorine"`
- Lenses without a named coating get `["multi-coating"]` — all modern lenses have AR coatings, Venus Laowa just doesn't brand theirs

#### Key decisions

- AQ is a spike (#783), not a commitment — must validate feasibility of blueprint threshold matching before building
- Legendary lenses (Nikon DC, Helios 44, Trioplan) are conceptual references for archetype definition, not data sources
- AQ validation should focus on X-mount lenses with available MTF data (Fujifilm magic trio, Voigtlander Noktons via third-party, 7Artisans)
- Forum questions serve dual purpose: community discovery (#511) and AQ data gathering (#783)

#### Next

- Merge PR #781 (Voigtlander optical specs)
- Venus Laowa optical specs (#745)
- AQ spike research (#783) when MTF data pipeline is more complete

---

### Session 79 — TTartisan Optical Specs & Manual Verification

- **Tool:** Claude Code (claude-opus-4-6)
- **Branch:** `feat/ttartisan-optical-specs`

#### PRs

- #787 — feat: TTartisan optical specs for all 19 lenses (open, CI pending)

#### Issues created

- #788 — Explore optical design patterns as a data dimension (spike, P3, Backlog)
- #789 — Add wiki entry for optical glass types and element shapes (task, P3, Backlog)

#### Issues updated

- #739 — Collect optical specs epic: checked off #745 (Venus Laowa), #747 (Voigtlander), #762 (TTartisan)

#### Key changes

- Built `tools/ttartisan/` extraction tool (plain urllib, no Cloudflare) with fetch_specs.py, audit.py, common.py
- Populated optical fields for all 19 TTartisan lenses (11 X-mount MF, 4 X-mount AF, 4 GFX)
- Downloaded MTF charts and construction diagrams for 18/19 lenses (AF 56mm from Shopify CDN)
- Corrected 28 pre-existing tech spec errors across 17 lenses (apertureBlades, weight, filterThread, minFocusDistance)
- Added MC Multi-Layer coating to all 19 lenses (brand standard from DJ Optical, CVD process)
- Manual lens-by-lens verification: found special elements in 7 construction diagrams not mentioned in page text
- Converted all images to PNG
- Added fcracer.com as trust-2 field review source
- Added Northlight Images as specialist T/S bookmark

#### Key decisions

- TTartisan uses MC Multi-Layer coating as brand standard (DJ Optical CVD process) — normalized across all 19 lenses
- Construction diagrams are authoritative over page text for special elements (page text omits glass types that diagrams show)
- `specialElements` stores glass types (HR, ED, LD) not design patterns (achromatic doublet) for consistency — design patterns deferred to #788
- Diagram label names take precedence over page text names (e.g. "LD" over "UD", "Extra low Dispersion" over "ultra-low dispersion")
- 500mm f/6.3 had entirely wrong specs from older product version — all corrected against current official page
- Per-lens provenance workflow added to PLAYBOOK 2.8 step 6: specs-log first, lenses.ts second (root cause: missed 7/19 logs by batching)
- CLAUDE.md references PLAYBOOK as single source of truth (no duplication)

#### Next

- Merge PR #787 when CI passes
- Continue optical specs collection: 7Artisans (#748, 18 lenses) is next by size
- #779 should include a validate mode that cross-checks lenses.ts against official pages
- #788 explore design patterns, #789 wiki for glass types

---

### Session 79 — Optical Specs Quick Wins and Milestone Cleanup

**Tool:** Claude Code (Opus 4.6 1M)

#### PRs

- #834 — Optical specs for Irix, Kipon, SLR Magic; move Thingyfy to accessories

#### Issues closed

- #751 (Irix), #753 (Kipon), #760 (SLR Magic), #763 (Thingyfy), #762 (TTartisan), #732 (Sigma MTF charts), #771 (lens audit — superseded by #820)

#### Issues created

- #790 — Epic: Digitize MTF charts (v0.8.0, 27 tasks)
- #791–#815 — Per-brand MTF digitization tasks
- #816 — Add 8 Irix cine lenses (Backlog)
- #817 — Add 11 Kipon lenses (Backlog)
- #818 — Add 13 SLR Magic lenses (Backlog)
- #819 — Add missing brands: Brightin Star, Kase, Yongnuo, Thypoch, Astra Lab (Backlog)
- #820 — Epic: Audit lens database (~175 missing lenses, Backlog)
- #821–#833 — Per-brand missing lens tasks (Backlog)

#### Key changes

- Thingyfy Pinhole Pro X moved from lenses to accessories (no glass = accessory)
- Irix 45mm f/1.4 GFX: full specs + MTF chart + distortion map + construction diagram
- Kipon IBERIT 75mm f/2.4 GFX: specs only (nothing published by Kipon)
- SLR Magic HyperPrime 50mm T0.95: specs + weight/length corrections
- "Quick win" single-lens brands turned out to have 32 missing lenses between them

#### Key decisions

- v0.7.0 focused on optical specs collection only; everything else moved out
- v0.8.0 focused on MTF digitization only
- Lens database audit (#820) → Backlog (not optical specs)
- Lenses without glass elements are accessories, not lenses

#### Workflow improvements (CLAUDE.md + PLAYBOOK)

- Always verify brand's full lens lineup before researching specs (PLAYBOOK 2.8 step 1)
- Use Google Image Search for construction diagrams and MTF charts (PLAYBOOK 2.8 step 4)
- Use fetch-page.py over WebFetch/Fetch — WebFetch truncates large pages silently (CLAUDE.md 1.4)
- alikgriffin.com tables are AJAX-loaded (Ninja Tables) — documented API endpoint (PLAYBOOK 2.8)

#### Next

- Merge PR #834
- Continue optical specs: Handevision (5 lenses), Kamlan (3), Pergear (3)
- Then larger brands: 7Artisans (18), Meike (14), NiSi (10), AstrHori (7)
