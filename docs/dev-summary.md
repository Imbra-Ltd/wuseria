# Fuji.me! Prototype — Development Summary

## Overview
Single-file React JSX app for Fujifilm lens and camera reference. Working file: `photography-prototype.jsx`. Part of the **me! series** by [braboj.me](https://braboj.me).

**Domain:** fujime.app (decided)  
**Monetisation:** Side income — 5 streams: affiliate links, merchandise (card decks), sponsored placements, high-commission affiliates (courses/presets), newsletter sponsorship. Subscriptions dropped — see FUJI-ME.md for rationale.
**Long-term:** Expand beyond Fujifilm to Sony E, Nikon Z, Canon RF etc. Data model stays system-agnostic from day one; UI launches Fuji-only.

---

## Session 1 — Foundation *(~2026-04-02)*
**Chat:** [TypeScript prototype from Excel workbook](https://claude.ai/chat/6f050216-4961-498f-a4ef-e27dab2a0f5b)

- Bootstrapped from an Excel workbook with X-Mount lens data
- 4 tabs: Lens Explorer, Camera Explorer, Trade Deals, Genre Guide
- Added full **GF/G-Mount lens lineup** and complete **Fujifilm camera body history** (39 bodies)
- Designed core **astronomy exposure logic** — Ideal ISO metric (`f² × 100 / (maxT × 2^EV)`) with rule-of-500
- Added **FL tile grid** replacing aperture grid across all genres
- **Mobile card layout** below 640px breakpoint
- Mount-aware ISO/MP chips (X-Mount vs GFX)
- All prices converted **BGN → EUR** (÷1.956)
- Calculator tab removed (code preserved with TODO)
- I/O error prevented final file delivery; transcript saved for recovery

---

## Session 2 — Genre Guide & UI Polish *(~2026-04-03)*
**Chat:** [Fuji.me changelog: lens and camera database expansion](https://claude.ai/chat/54e23966-1869-49e6-96b8-fdb4e58aeaff)

- Fixed critical **missing closing brace** bug in `handheldSuitability` (broke module parser)
- IBIS column added and removed multiple times — settled on **Mode "OIS/IBIS"** label
- Fixed landscape filter incorrectly hiding lenses without physical OIS (IBIS users were excluded)
- Fixed mode sort to use `idealIsoRef` for landscape
- **WR column** added, carried through both suitability functions
- **Click-to-sort column headers** (↑/↓) replacing sort chips
- **Landscape-specific filter panels** (Mode/Features/Price, inverted amber labels, single row)
- Same filter panel applied to Astronomy (Features/Price)
- EV 9 set as landscape default
- All prices prefixed with `~`

---

## Session 3 — Wiki, Accessories & Genre Equipment *(~2026-04-05)*
**Chat:** [Session priorities and pending items](https://claude.ai/chat/b4f9f5b9-2582-4221-9c4a-694320e1dfdb)

- **ISO chip fix** — display full number (1600 not 1.6k)
- **Wiki tab** expanded to 104+ entries A-Z with `acro:true` flag:
  - Full AF taxonomy (Passive, CDAF, PDAF, Hybrid, DFD, LiDAR, IR)
  - Full lighting section (Flash, Speedlight, TTL, HSS, Softbox, Beauty dish, etc.)
  - Composition entries (Rule of thirds, Leading lines, S-curve, etc.)
  - Lens/equipment terms (OIS, WR, IBIS, APD, T/S, TC, Macro, ND, Sweet spot, etc.)
  - Non-acronym entries promoted to use full descriptive name as primary label
- **Accessories tab** built from scratch — ~45 items across Flash, Battery Grip, Hand Grip (MHG-XT3/4/5/XH/XPRO2), Power, Lens Accessory, Adapter, Remote, Audio, Body Accessory
  - Legacy body coverage (X-T1/2/3 era)
  - All compat fields with concrete model lists
- **Camera Explorer** — click-to-sort all 9 columns
- **Genre Equipment panel** — all 8 genres, left column, dot-separated, system-ui 11px, accessories only
- **Portrait genre** analyzed and implemented — EV 0–14, ISO 3200 ceiling, fast AF = native lenses only, FL range 23–200mm FF, 3 sub-scenarios (group/indoor/outdoor)
- **Sport/Wildlife mark scores** — 4-criterion formula (LM + Reach + Aperture + OIS, scaled 0–5), dummy values
- App subtitle updated to current form

---

## Session 4 — Third-party GFX Lenses & UI Fixes *(~2026-04-05–06)*
**Chat:** [Current session](https://claude.ai/chat/2026-04-05-22-06-24-fujime-prototype-dev)

### GFX Third-party Lens Database
Added 19 native G-Mount third-party lenses:
- **Venus Laowa**: 17mm f/4 Zero-D, 55mm f/2.8 T/S, 100mm f/2.8 T/S
- **Mitakon**: Speedmaster 65mm f/1.4
- **Irix**: 45mm f/1.4 Dragonfly (WR)
- **TTartisan**: 11mm f/2.8 Fisheye, 90mm f/1.25, 100mm f/2.8 Macro 2X
- **AstrHori**: 55mm f/5.6, 75mm f/4
- **Kipon**: IBERIT 75mm f/2.4 (270g, 49mm — lightest third-party GFX lens)
- **NiSi Athena Cinema**: 8 lenses (14mm T2.4, 18mm T2.2, 25/35/40/50/85mm T1.9, 135mm T2.2) — 46mm image circle, may vignette at GFX corners

### X-Mount Additions
- **Tokina atx-m 11-18mm f/2.8 X** — first Tokina zoom for X-mount (320g, 67mm, ~550 EUR, AF)

### UI Fixes
- **Column header alignment** — Brand/Model/Type left-aligned, numerics right-aligned
- **Sort direction bug** fixed — `sortDir` added to `useMemo` dependency array
- **Type column** added to Lens Explorer (sortable, P/Z)
- **Accessories** — Description maxWidth:300 with word wrap; Model maxWidth:120
- **Architecture matrix** — f/16 row added; sweet spot label now mount-aware (f/8 APS-C / f/11 GFX); dynamic label in subtitle
- **Astronomy FL chips** now filter lens list by FF-equivalent FL range
- **Price column** renamed `~€`; footnote added: *"Prices are approximate — see Trade Deals for current market rates"*
- Subtitle updated to: *"Lightweight · Fuji Screener · me! series · by braboj.me"*

---

## Session 5 — Analysis, Design & Scoring System *(~2026-04-06–07)*
**Tool:** Claude Code (imbra-spikes repo)

This session completed the full analysis and design phase, preparing for implementation.

### Product Brief (FUJI-ME.md)
- 15 numbered sections, rated 9/10 by shark assessment
- Target audience with Jobs-to-Be-Done, market sizing (300k-1M Fuji, 1.5-5M multi-system)
- Competitive landscape with Ken Rockwell analysis and Moore positioning statement
- Moat assessment (honest: weak, speed-based)
- 5 revenue streams: affiliate, merch (6 card deck types), sponsored, high-commission, newsletter
- Industry benchmarks sourced (Hostinger, wecantrack, Affilimate)
- Revenue timeline: €0-15 months 1-3, €200-450 months 10-12, €500-1000 months 18-24
- High-ticket insight: B&H at 8% on €1,500 lens = €120 per sale
- Success criteria with kill criteria and feedback channel
- Budget: €17/year phases 1-3, €300-500/year phases 4-5
- Mobile-first section added

### Architecture (FUJI-ME-ARCHITECTURE.md)
- Stack: Vite + React 18 + TypeScript + CSS Modules + GitHub Pages
- Lens interface: 40+ fields across identity, optical specs, build, price, scoring inputs
  - Renamed all fields from prototype (ap→maxAperture, lm→afMotor, etc.)
  - Added: afMotor (DC/STM/LM), circularAperture, rotatingFront, tripodMount, distanceScale, focusByWire, apertureClickless, smoothFocusRing, tiltShift, shiftRange, tiltAngle, imageCircle, dimensions
  - Removed opticalScore as stored field — now computed from individual MTF readings
  - Split caRating → locaRating (not fixable in post) + lateralCA (fixable)
  - Split centerSharpness → sweetSpotSharpness + wideOpenSharpness
- Camera interface: 32 fields (added series, bodyStyle, afType, faceDetectAF, subjectDetectAF, bufferDepth, electronicShutterFps, screenType, usbType, micInput, headphoneJack)
- Individual lens pages (phase 2) — auto-generated from data, one URL per lens for SEO

### Scoring System — 9 Genres
Universal formula: `mark = round(total / maxTotal * 8 + 2) / 2` (range 1-5, step 0.5)
All optics/physics only — features are UI filter badges.

| Genre | Criteria | maxTotal | Validated |
|---|---|---|---|
| Astro | light (Lonely Speck formula) + coma; disqualifier wideOpenSharpness ≤ 1 | 4 | ✅ 10 lenses, real coma data |
| Portrait | blur (entrance pupil, 50mm benchmark) + bokeh + wideOpenSharpness | 6 | ✅ Web consensus, Lenstip |
| Landscape | sweetSpotSharpness + cornerSharpness | 4 | ✅ 10 lenses, real Lenstip data |
| Sport | light (entrance pupil, 50mm benchmark) + wideOpenSharpness | 4 | ✅ Multiple sources |
| Wildlife | light (entrance pupil, 100mm benchmark) + wideOpenSharpness | 4 | ✅ Multiple sources |
| Street | wideOpenSharpness + locaRating | 4 | ✅ XF 35mm f/1.4 LoCA confirmed |
| Travel | sweetSpotSharpness + wideOpenSharpness + locaRating | 6 | ✅ Web consensus |
| Architecture | distortionRating + cornerSharpness + sweetSpotSharpness | 6 | ✅ Lenstip + T/S research |
| Macro | maxMagnification + sweetSpotSharpness + cornerSharpness (field curvature proxy) | 6 | ✅ Lenstip |

Key scoring decisions:
- Entrance pupil benchmarks per mount (portrait 50mm, sport 50mm, wildlife 100mm)
- Separated sport and wildlife (different benchmarks)
- Street uses LoCA (night shooting fringing — confirmed from personal XF 35mm f/1.4 experience)
- Field curvature uses cornerSharpness as proxy (direct data not available from reviews)
- Flare resistance is display attribute, not scored (mitigable, sometimes creative)
- All features (WR, OIS, AF, filter thread, etc.) moved to UI filter badges

### Lenstip Validation
Real MTF data sourced for 10+ lenses:
- XF 18mm f/1.4: 93.5 lp/mm center (record on X-T2)
- XF 56mm f/1.2 WR: 92.8 lp/mm center, 75.3 wide open
- XF 90mm f/2.0: 78.5 lp/mm (record on X-E1)
- XF 50mm f/1.0: 48 lp/mm wide open (barely above decency — confirmed soft)
- XF 10-24mm f/4: 69-70 lp/mm center, weak edges at 24mm
- XF 50-140mm f/2.8: 51-59 lp/mm at f/2.8, 72 lp/mm at sweet spot
- XF 100-400mm: 50 lp/mm at 400mm
- Viltrox 75mm f/1.2: 85 lp/mm at f/1.2
- XF 23mm f/2.8 WR: 81+ lp/mm at f/4.0
- Sensor ceiling awareness: X-E1 ~75 lp/mm, X-T2 ~93 lp/mm (cross-sensor comparison invalid)

### Tilt-Shift Lens Research
Discovered 7 native X-Mount T/S lenses (most missing from database):
- Laowa 12-24mm f/5.6 Zoom Shift CF, TTArtisan 100mm f/2.8 T/S, TTArtisan 35mm f/1.4 Tilt, 7Artisans 50mm f/1.4 T/S, AstrHori 50mm f/1.4 Tilt, AstrHori 18mm f/5.6 T/S, AstrHori 85mm f/2.8 Tilt
- Canon TS-E via Fringer adapter is gold standard for X-Mount architecture
- GFX has world-class native T/S: GF 30mm f/5.6 T/S and GF 110mm f/5.6 T/S Macro
- Fixed incorrect Laowa 15mm f/4.5 Shift listed as X-Mount (doesn't exist — GFX only)

### CLAUDE.md — 20 Sections
Compared against solid-ai-templates and added 6 missing sections:
State management, API integration, Quality attributes, Debug code, Security, Documentation

### Traffic Playbook
Step-by-step guide: Reddit/Facebook engagement, monthly content calendar, backlink outreach, example replies, what-not-to-do list. ~1.5 hrs/week traffic + ~1 hr/week maintenance.

### Bookmarks
Added 16 scoring methodology references, T/S lens reviews, Fringer adapter, community consensus sources, DXOmark, Dustin Abbott, Phillip Reeve.

### Excel Audit
Audited photography.xlsx against prototype. Found:
- XF 16-80mm f/4 (major missing travel zoom), Samyang 24mm f/3.5 T/S, MKX cinema lenses
- 3 wiki topics from Excel not in prototype (aspect ratios, focus modes, filter types)
- Removed xlsx — all data superseded by prototype

### Repo & Project Structure
- All 8 product briefs standardised to 14-section structure
- Consolidated products/ → projects/ folder
- Created Imbra-Ltd/me-fuji repo, scaffolded Vite + React + TypeScript
- Copied CLAUDE.md + docs (architecture, prototype, dev-summary, bookmarks)
- Created 54 tickets in 6 epics across 4 milestone phases
- Labels: migration, lens-data, wiki, ui, scoring, tooling, phase-2, fix, epic

### PRs Merged This Session
- #29: ImContext spike, me-fuji resources, AI strategy fix
- #30: Products → projects consolidation, me-fuji briefs, scoring system
- #31: Standardise all product briefs, xlsx removal, CLAUDE.md sections
- #32: Remove --- separators from CLAUDE.md
- #33: IDE lens template snippet TODO

---

## Session 6 — Data Migration & Astro Switch *(2026-04-08)*
**Tool:** Claude Code (me-fuji repo)

### TypeScript Interfaces (#1)
- Lens (40+ fields), Camera (32 fields), Genre/ScoreResult, AffiliateLink, ReviewLink
- All types match ARCHITECTURE.md spec with field renames from prototype

### Lens Data Migration (#2) — 236 lenses
- Migrated 164 lenses from prototype.jsx with full field mapping
- Added 13 missing lenses from dev-summary TODOs (#17-#21)
- Added 58 lenses from database audit (lens-db.com, alikgriffin.com, manufacturer sites)
- Added XF 23mm f/1.4 R LM WR (Mark II) — last missing Fujifilm lens
- Closed #2, #17, #18, #19, #20, #21, #22, #23

### Spec Expansion — all 236 lenses
- Fujifilm (68 lenses): year, apertureBlades, circularAperture, maxMagnification, minFocusDistance, diameter, length, afMotor, focusByWire, distanceScale, discontinued, officialUrl
- Sigma/Tamron/Tokina (20): full specs from manufacturer sites
- Viltrox/Sirui/Samyang (35): full specs
- All MF third-party (96): year, apertureBlades, focusByWire, minFocusDistance
- All 236 lenses have officialUrl pointing to specific product pages

### Framework Switch Decision
- Switched from Vite + React SPA to **Astro + React islands**
- Rationale: 80% static data display, SEO critical, solid-ai-templates recommends static-site-astro
- Updated CLAUDE.md, architecture.md, all GitHub issues/epics
- Removed Vite scaffold (App.tsx, main.tsx, vite.config.ts, tsconfigs, eslint.config.js, index.html)

### Type System Additions
- ReviewLink + ReviewSource (15 trusted sources, ordered by rigour)
- AffiliateLink generalized (lens → product, typed retailer/region)
- officialUrl added to Lens and Camera interfaces
- Ken Rockwell removed from ReviewSource (competitor reference only)

### GitHub Issues
- Created #56 EPIC: Automation & Growth (8 sections: data freshness, link validation, community, content, SEO, data quality, CI/CD, dependency management)
- Created #57: Switch to Astro + React islands
- Updated #42, #6, #7, #8, #38, #46, #47, #48 for Astro architecture
- Closed 8 lens-data issues (all completed)

### Documentation
- CLAUDE.md rewritten for Astro (structure, commands, components, styling, SEO)
- Bookmarks reorganized to match ReviewSource type
- .gitattributes added for LF line endings
- Fujifilm model names normalized to official uppercase (XF/XC/GF/MKX)

### Camera Data Migration (#3) — 39 bodies, 46 fields
- Migrated all 39 Fujifilm camera bodies from prototype.jsx
- 46 fields per camera (vs 32 in architecture doc)
- Refactored `bodyStyle` → `evfPosition` + `formFactor` (cleaner separation)
- New fields beyond spec: sensorWidth/Height, bsi, isoMin/Max, pdafCoverage,
  filmSimulations, wifi, bluetooth, screenResolution, touchscreen, batteryType,
  pixelShift, builtInFlash, tethering, officialUrl
- Prices refreshed to 2026 USD (new retail + used market)

### Lens Data Refinements
- Prices normalized to USD, $250 steps; removed `priceEstimated` (all estimates)
- Currency config: `src/data/config.ts` with DEFAULT_CURRENCY
- All 242 lens officialUrl links verified; 28 broken URLs fixed
- Meike lineup refreshed: 5 discontinued, 9 current lenses added
- NiSi 15mm f/4 Sunstar added; Kamlan 32mm f/1.1 added
- Removed 3 ghost lenses (Tamron 50-400mm, Voigtlander Nokton D, Laowa 15mm Shift X)
- Systematic mount audit: all 174 third-party lenses verified for X/GFX availability
- Zeiss Touit: marked discontinued, URLs → PDF datasheets
- 7Artisans 35mm f/2 marked discontinued; 50mm f/1.05 → f/0.95 corrected
- Total: 242 lenses (down from 245 after removing ghosts + discontinued corrections)

### Scoring Strategy Decision
- Genre Guide shows only lenses with optical review data (scored lenses)
- Lens Explorer shows all 242 lenses (specs only, no scoring needed)
- No camera genre scoring — feature checklists per genre instead (#68)

### New GitHub Issues
- #61-66: Wiki entries for BSI, pixel shift, ISO range, film simulations, PDAF coverage, battery types
- #67: Camera price refresh (merged)
- #68: Discussion — camera genre scoring vs feature checklists

---

## Current State

| Area | Status |
|---|---|
| Lens data | ✅ 242 lenses, full specs, all brands, officialUrl, verified |
| Camera data | ✅ 39 bodies, 46 fields, prices refreshed |
| Accessories | ❌ In prototype only — migration pending (#5) |
| Wiki | ❌ In prototype only — migration pending (#4) |
| Genre scoring | ❌ Types defined, functions pending (#9) |
| Framework | Astro scaffold pending (#57) — Vite removed |
| UI | No components yet — pending Astro scaffold |

---

## Product Roadmap

### Trade Deals
1. Filter recommended lenses by genre
2. Links to live deals per lens (affiliate links)
3. Newsletter deal roundups

### Platform Expansion
- Launch Fuji-only at fujime.app
- Expand to Sony E, Nikon Z, Canon RF in later phases (phase 4)
- Data model already system-agnostic (`format` field, variable `crop`, mount-neutral EV logic)

See `FUJI-ME.md` for the full roadmap and revenue model.

---

## Pending TODOs

- **Price review** — systematic audit; many prices may still be in BGN (confirmed: XF 10-24mm was 2000 BGN → should be ~1000 EUR)
- **Systematic MTF review** *(dedicated session)* — fetch Lenstip/Opticallimits resolution data for all lenses. Compute weighted score: `0.3 × center_contrast + 0.2 × center_resolution + 0.2 × edge_contrast + 0.3 × edge_resolution`, normalized to 1–10. Note test sensor per review for cross-generation normalization. Lenses without Lenstip coverage → fallback to Opticallimits / The-Digital-Picture. Start with Astronomy lenses, then extend to all genres. Output: updated `mtf` field per lens + reference sheet with sources.
- **Astronomy scoring** — formula finalized: `mark = points + 1` where `points = aperture(0-2) + coma(0-2)`, MTF ≤ 6 = disqualifier (mark 1). Implemented for X-Mount and GFX. Coma values are research-based (Lenstip, DPReview, National Parks at Night). MTF values still subjective — will be updated by systematic MTF review above.
- **Genre scoring — remaining genres** — Street, Travel, Portrait, Sport, Wildlife, Landscape, Architecture all need criteria defined and marks computed (currently dummy values). Do after MTF review is complete so scores incorporate accurate MTF data.
- **Portrait mark scoring** — formula proposed: bokeh(0-2) + wide aperture sharpness(0-2) + CA control(0-1); pending MTF review
- **Landscape mark scoring** — primary criterion: corner sharpness; pending MTF review
- **UI improvements** — alternating rows, truncated name tooltips, larger MTF pips, mobile overflow fix
- **Trade Deals** — genre filter, live deal links, notifications, user profiles (see roadmap above)
- **Product** - check if a new genre is feasible here, seems to be indoor mostly similar to portrait
- **Wiki: Bortle scale** — add Bortle scale (1-9 light pollution classification) to wiki; link to lightpollutionmap.app; relevant for astro genre guide
- **Wiki: Body styles** — explain Fuji body styles: center-EVF (X-T, X-H, X-S, most GFX), corner-EVF (X-Pro, X-E, GFX 50R, GFX 100RF), no-EVF (X-A, X-M). Include which series fits which shooting style.
- **Wiki: Scoring methodology** — one entry per genre explaining how scores are calculated. Astro: Lonely Speck light formula + coma rating. Portrait: bokeh + wide-open sharpness + aperture + AF + CA. Link to data sources (Lenstip, Opticallimits). Transparency builds trust.
- **Wiki: MTF charts** — how to read MTF charts: S10 = contrast, S30 = resolution, Sagittal vs Meridional separation = astigmatism, curve shape = field curvature. What MTF cannot show: distortion, vignetting, flare, colour.
- **Wiki: Coma** — what coma is, why it matters for astro, how to identify it in sample images, link to Lonely Speck methodology.
- **Wiki: AF motors** — DC (coreless, slowest, audible), STM (stepping, mid, near-silent), LM (linear, fastest, silent). Which genres need which. Why older XF lenses feel sluggish.
- **Wiki: Diffraction limit** — why macro shots are soft at f/22 on APS-C. Diffraction limit ~f/11 on X-Mount, ~f/14 on GFX. Not a lens property — same for all lenses on the same sensor. Explain the trade-off: depth of field vs diffraction softening.
- **IDE: Lens template snippet** — create an IDE snippet/template that pre-fills the Lens interface structure with all required fields. Reduces new lens entry from manual typing to filling in values.
- **Wiki: Aspect ratios** — from Excel. Social media (1:1, 4:5), print (3:2, 5:4), fine art (16:9, panoramic). Orientation guide.
- **Wiki: Focus modes** — from Excel. AF-S (single), AF-C (continuous), zone, wide/tracking. PDAF vs CDAF behaviour per mode. Detailed.
- **Wiki: Filter types** — from Excel. CPL, ND (fixed/variable), graduated, UV/protective, IR, color, effect (diffusion). When to use each.
- ~~**Lens data: add XF 16-80mm, XC 35mm, Samyang T/S, MKX, etc.**~~ — **Done** (Session 6: all 236 lenses migrated)
- ~~**Lens data: add tilt-shift, macro, GFX lenses**~~ — **Done** (Session 6)
- **Lens data: fix Laowa 15mm f/4.5 Zero-D Shift** — currently listed as X-Mount but NO native X-Mount version exists. Change to GFX or remove. (#16)
- **MTF review: GFX lenses** — all GFX optical scores are placeholders. (#24)
- **Genre guide: Architecture T/S options** — cover native T/S, Canon TS-E via Fringer, Lightroom correction. (#39)
- **Wiki: Sunstars** — aperture blade count → sunstar points. (#32)
- **UI: Sunstar display** — computed sunstar points on lens detail page. (#37)
