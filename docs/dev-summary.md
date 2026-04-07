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

## Current State

| Tab | Status |
|---|---|
| Lens Explorer | ✅ 200+ lenses, X + GFX, all third-party |
| Camera Explorer | ✅ 39 bodies, click-to-sort |
| Accessories | ✅ ~45 items |
| Trade Deals | ✅ |
| Genre Guide | ✅ 8 genres, EV matrix, equipment lists |
| Wiki | ✅ 104+ entries |

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
- **Lens data: add XF 16-80mm f/4 R OIS WR** — missing from prototype. Popular travel zoom.
- **Lens data: add XC 35mm f/2** — missing from prototype. Budget prime.
- **Lens data: add Samyang 24mm f/3.5 Tilt/Shift** — missing. Another T/S option for X-Mount.
- **Lens data: add Samyang 20mm f/1.8, 21mm f/1.4, 50mm f/1.2, 50mm f/1.4, 135mm f/2, 300mm f/6.3** — missing Samyang lenses from Excel.
- **Lens data: add MKX 18-55mm T2.9, MKX 50-135mm T2.9** — Fuji cinema zooms, niche but complete database.
- **Lens data: add XF 70-300mm f/4-5.6 R LM OIS WR** — missing from prototype database. Popular tele landscape/wildlife lens. Find Lenstip/DXOmark MTF data for scoring.
- **MTF review: GFX lenses** — all GFX optical scores are placeholders. Find Lenstip/DXOmark data for GF 20-35mm, GF 32-64mm, GF 23mm, GF 45-100mm, GF 100-200mm and all other GFX lenses.
- **Lens data: add XF 18-120mm f/4 LM PZ WR** — missing from prototype database. Power zoom, video-oriented.
- **Lens data: add XF 500mm f/5.6 R LM OIS WR** — missing from prototype database. Super-tele for wildlife.
- **Lens data: add XF 150-600mm f/5.6-8 R LM OIS WR** — missing from prototype database. Super-tele zoom for wildlife.
- **Lens data: add XC 13-33mm f/3.5-6.3 OIS** — missing from prototype database. Budget kit zoom.
- **Lens data: add Laowa 12-24mm f/5.6 Zoom Shift CF** — missing from prototype database. Native X-Mount shift zoom for architecture.
- **Lens data: add TTArtisan 100mm f/2.8 Macro 2x Tilt-Shift (X-Mount)** — missing. Native X-Mount tilt-shift macro, ~$389. GFX version already in database.
- **Lens data: add TTArtisan 35mm f/1.4 Tilt (X-Mount)** — missing. Tilt only, ~$169.
- **Lens data: add 7Artisans 50mm f/1.4 Tilt-Shift (X-Mount)** — missing. Tilt + shift, ~$226.
- **Lens data: add AstrHori 50mm f/1.4 Tilt (X-Mount)** — missing. Tilt only, 15°, ~$200.
- **Lens data: add AstrHori 18mm f/5.6 Tilt-Shift (X-Mount)** — missing. Tilt + shift, architecture lens, ~$200.
- **Lens data: add AstrHori 85mm f/2.8 Macro Tilt (X-Mount)** — missing. Tilt macro, ~$250.
- **Lens data: add Lensbaby Composer Pro II + Sweet 35 (X-Mount)** — missing. Creative tilt 0-15°, ~$350.
- **Genre guide: Architecture T/S options** — page should cover three paths: (1) native T/S lenses (Laowa, TTArtisan, budget tilt), (2) Canon TS-E via Fringer adapter (gold standard for X-Mount), (3) regular lens + Lightroom perspective correction (practical for 90% of cases). For GFX: Fuji GF 30mm f/5.6 T/S and GF 110mm f/5.6 T/S Macro are world-class native options.
- **Lens data: add GF 30mm f/5.6 T/S** — missing. Native GFX tilt-shift, 24mm equiv, ±15mm shift, ~€4,000.
- **Lens data: add GF 110mm f/5.6 T/S Macro** — missing. Native GFX tilt-shift macro, 87mm equiv, ~€3,500.
- **Lens data: add Laowa 65mm f/2.8 2x Ultra Macro (X-Mount)** — missing. 2:1 magnification, native X-Mount.
- **Lens data: add TTArtisan 40mm f/2.8 Macro (X-Mount)** — missing. Budget 1:1 macro.
- **Lens data: add 7Artisans 60mm f/2.8 Macro (X-Mount)** — missing. Budget 1:1 macro.
- **Lens data: add Laowa 35mm f/2.8 Zero-D T/S 0.5x Macro (GFX)** — missing. Tilt-shift macro for GFX, announced Nov 2025.
- **Lens data: fix Laowa 15mm f/4.5 Zero-D Shift** — currently listed as X-Mount in prototype but NO native X-Mount version exists. Change to GFX or remove. Only available in Canon EF/RF, Nikon Z/F, Sony FE, Pentax K, L-mount, and GFX.
- **Wiki: Sunstars** — explain how aperture blade count determines sunstar points (odd × 2, even = same). Display computed sunstar count on lens detail pages.
- **UI: Sunstar display** — show computed sunstar points on lens detail page as display attribute (not scored).
