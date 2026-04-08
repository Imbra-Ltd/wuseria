# Fuji.me! — Technical Architecture

## 01. Abstract

This document covers the technical architecture decisions for Fuji.me! — an Astro static site with React islands, deployed to fujime.app. It explains what was chosen, what was rejected, and why. For coding conventions and agent instructions, see `CLAUDE.md`.


## 02. Architecture Overview

```
Phase 1 — Launch:
  Static site (Astro + React islands)
  → Data compiled to static HTML at build time
  → Interactive tables hydrated as React islands
  → Deployed to GitHub Pages
  → Affiliate links are plain <a> tags with tracking params

Phase 2 — Scoring:
  Same static site
  → Complete genre scoring (remaining 6 genres)
  → Systematic MTF review

Phase 3 — Revenue diversification:
  Same static site + Gumroad (merch) + Buttondown (newsletter)
  → Sponsored placements, high-commission affiliates, newsletter sponsorship
  → No backend needed

Phase 4 — Multi-system (if phase 3 gate passes):
  Same architecture, more data files (Sony E, Nikon Z, Canon RF)
```


## 03. Key Decisions

| Decision | Chosen | Rejected | Rationale |
|---|---|---|---|
| Data storage | Embedded TypeScript files | JSON files, REST API, CMS, database | Data changes monthly; no API or CMS needed. TypeScript over JSON because: compile-time type checking catches missing fields, IDE autocomplete on data arrays, and scoring functions import data directly without a parsing step. JSON (as used on braboj.me) works but loses type safety at the data layer. |
| Hosting | GitHub Pages | Vercel, Cloudflare Pages, Netlify | Already using GitHub; €0; no second account. Migrate to Vercel if bandwidth exceeds 100GB/month or SSR needed |
| Framework | Astro + React islands | Vite + React SPA, Next.js, plain Hugo | 80% static data display, 20% interactive. Astro ships zero JS by default, hydrates only sort/filter tables. Better SEO (pre-rendered HTML), better Core Web Vitals. solid-ai-templates recommends static-site-astro for this pattern. |
| Styling | Astro scoped styles + CSS Modules | Tailwind, inline styles, styled-components | Scoped styles for .astro pages, CSS Modules for React islands; no utility class overhead |
| State management | Local state only | Zustand, Redux, React Query | No server state (all data embedded); no shared state across unrelated components; `useState` + `useMemo` in React islands is sufficient |
| Routing | Astro file-based routing | React Router v6, TanStack Router | Built-in with Astro; `getStaticPaths()` generates 236 lens pages at build time |
| Scoring engine | Code-defined functions | ML model, database-driven rules | Scoring formulas are simple arithmetic; keeping them in code makes them testable and transparent |
| SEO | Astro native head + @astrojs/sitemap | react-helmet, manual sitemap | Pre-rendered HTML by default; per-page meta without a library; sitemap auto-generated |
| Newsletter | Buttondown | Substack, ConvertKit, Mailchimp | Free under 100 subscribers; €9/month after; minimal UI; no lock-in |
| Merch storefront | Gumroad | Shopify, custom checkout | Zero setup; handles payments; no full e-commerce build needed for 10-15 orders/month |


## 04. Data Model

### Lens

```typescript
interface Lens {

  // Identity
  brand: string;                // manufacturer name
  model: string;                // full model name
  type: "prime" | "zoom";       // prime or zoom lens
  mount: "X" | "GFX";           // mount system
  year?: number;                // release year
  discontinued?: boolean;       // no longer in production

  // Optical — specs
  focalLengthMin: number;       // min focal length, mm
  focalLengthMax: number;       // max focal length, mm
  maxAperture: number;          // widest f-number
  sweetSpot?: string;           // sharpest aperture
  apertureBlades?: number;      // blade count, bokeh shape
  circularAperture?: boolean;   // rounded blades, rounder bokeh stopped down
  maxMagnification?: number;    // reproduction ratio as decimal

  // Build
  ois: boolean;                 // optical stabilisation
  weatherSealed: boolean;       // weather resistant body
  autofocus: boolean;           // has autofocus motor
  afMotor?: string;             // "DC" | "STM" | "LM" — speed tier
  apertureRing: boolean;        // physical aperture ring
  apertureClickless?: boolean;  // declicked aperture ring
  focusRing: boolean;           // physical focus ring
  focusByWire?: boolean;        // electronic focus ring
  distanceScale?: boolean;      // distance markings on barrel
  smoothFocusRing?: boolean;    // smooth/declicked focus ring
  weight: number;               // weight in grams
  diameter?: number;            // max outer diameter, mm
  length?: number;              // mount to front element, mm
  filterThread?: number;        // filter thread diameter, mm
  rotatingFront: boolean;       // front element rotates on focus
  tripodMount: boolean;         // built-in tripod collar

  // Price
  price: number;                // approximate price, EUR
  priceEstimated: boolean;      // true if not retailer-confirmed

  // Optical quality — from MTF chart readings
  sweetSpotSharpness?: number;  // 0-2; sharpness at optimal aperture
  cornerSharpness?: number;     // 0-2; edge/corner resolution
  wideOpenSharpness?: number;   // 0-2; sharpness at max aperture
  astigmatism?: number;         // 0-2; low S/M separation = 2
  fieldCurvature?: number;      // 0-2; flatness of focus plane
  comaRating?: number;          // 0-2; point light deformation

  // Optical quality — NOT from MTF charts
  locaRating?: number;           // 0-2; longitudinal CA (not fixable in post)
  lateralCA?: number;            // 0-2; lateral CA (fixable in post)
  distortionRating?: number;    // 0-2; barrel/pincushion
  vignetting?: number;          // 0-2; corner light falloff
  bokehQuality?: number;        // 0-2; from blades + astigmatism + review
  flareResistance?: number;     // 0-2; ghosting/flare control

  // Other scoring inputs
  minFocusDistance?: number;    // closest focus distance, mm
  tiltShift: boolean;           // tilt-shift lens
  shiftRange?: number;          // max shift, mm (e.g. 7, 12, 15)
  tiltAngle?: number;           // max tilt, degrees (e.g. 8.5)
  imageCircle?: number;         // image circle diameter, mm
  tiltShiftIndependent?: boolean; // can tilt and shift independently
}
```

**Migration from prototype field names:**

| Prototype | Production | Reason |
|---|---|---|
| `type: "P" \| "Z"` | `type: "prime" \| "zoom"` | Self-documenting |
| `format` | `mount` | Correct term for lens compatibility |
| `flMin` / `flMax` | `focalLengthMin` / `focalLengthMax` | Readable without comment |
| `ap` | `maxAperture` | Unambiguous |
| `mtf` | Split into `sweetSpotSharpness`, `wideOpenSharpness`, `cornerSharpness`, `astigmatism`, `fieldCurvature`, `comaRating` | Single number replaced by individual MTF-sourced readings; `opticalScore` is now computed from these |
| `lm` | `afMotor` | Three tiers: DC, STM, LM instead of boolean |
| `wr` | `weatherSealed` | Standard industry term |
| `kg` | `weight` | Grams for both Lens and Camera; no unit in name |
| `thread` | `filterThread` | Distinguishes from mechanical threads |
| `price` | `price` | Unchanged; unit in comment only |
| `est` | `priceEstimated` | Readable as boolean |
| `af` (optional) | `autofocus` (required) | Default false for MF lenses |

**New fields:**

| Field | Why added |
|---|---|
| `year` | Filter current vs legacy; "released after 2020" |
| `discontinued` | Prevent recommending unavailable lenses |
| `macro` | Genre scoring — was fragile string match on model name |
| `comaRating` | Astro scoring — was hardcoded in scoring function |
| `bokehQuality` | Portrait scoring — was planned but missing from data |
| `minFocusDistance` | Macro and portrait relevance |

### Camera

```typescript
interface Camera {

  // Identity
  model: string;              // "X-T5"
  mount: "X" | "GFX";         // mount system
  year: number;               // release year
  discontinued?: boolean;     // no longer in production
  series: string;             // X-Pro, X-T, X-H, X-E, X-S, X-M, X-A, GFX
  bodyStyle: string;          // "center-evf" | "corner-evf" | "no-evf"

  // Sensor
  sensor: string;             // "X-Trans CMOS 5 HR"
  megapixels: number;         // effective megapixels

  // Stabilisation & weather
  ibis: boolean;              // in-body image stabilisation
  weatherSealed: boolean;     // weather resistant body

  // Viewfinder & screen
  evfType?: string;           // "electronic" | "hybrid" | "none"
  evfResolution?: number;     // dots, e.g. 3 690 000
  screenType?: string;        // "tilting" | "articulating" | "fixed"

  // Performance
  burstFps?: number;          // max burst, mechanical shutter
  shutterType?: string;       // "mechanical" | "electronic" | "both"
  afType?: string;            // "CDAF" | "hybrid-PDAF"
  afPoints?: number;          // AF point count
  faceDetectAF: boolean;      // eye/face detection AF
  subjectDetectAF?: string[]; // e.g. ["animal","bird","car"]
  bufferDepth?: number;       // RAW shots before buffer full
  electronicShutterFps?: number; // e-shutter max burst fps
  batteryLife?: number;       // shots per charge (CIPA)

  // Video
  videoSpec: string;          // e.g. "6.2K 30p"

  // Storage
  cardSlots?: number;         // 1 or 2
  cardType?: string;          // "SD" | "UHS-II" | "CFexpress"

  // Connectivity
  flashHotShoe: boolean;      // has hot shoe
  usbType?: string;           // "micro-USB" | "USB-C"
  micInput: boolean;          // external microphone jack
  headphoneJack: boolean;     // audio monitoring output

  // Physical
  weight: number;             // weight in grams
  width?: number;             // body width, mm
  height?: number;            // body height, mm
  depth?: number;             // body depth, mm

  // Price
  price: number;              // approximate price, EUR
  priceEstimated: boolean;    // true if not retailer-confirmed
}
```

### Optical Score (computed)

`opticalScore` is **not a stored field** — it's a computed composite from the individual MTF-sourced readings. Different genres weight the components differently, but the general composite for sorting in the Lens Explorer is:

```typescript
function opticalScore(lens: Lens): number | null {
  // Returns 1-10 or null if insufficient data
  // Weighted: center 30%, corner 20%, wide-open 20%,
  //           astigmatism 15%, field curvature 15%
  // Exact weights are configurable per use case
}
```

**Data sources for each reading:**

| Field | Source | From MTF chart? |
|---|---|---|
| `sweetSpotSharpness` | Lenstip/Opticallimits center resolution at optimal aperture | Yes |
| `cornerSharpness` | Lenstip/Opticallimits edge resolution | Yes |
| `wideOpenSharpness` | MTF at max aperture vs sweet spot | Yes |
| `astigmatism` | Sagittal/Meridional line separation | Yes |
| `fieldCurvature` | MTF curve shape across field | Yes |
| `comaRating` | Lenstip/DPReview point source tests | Yes |
| `caRating` | Review sample images, CA charts | No |
| `distortionRating` | Review distortion measurements | No |
| `vignetting` | Review vignetting measurements | No |
| `bokehQuality` | Informed by `apertureBlades` + `astigmatism` + sample image review. Computed estimate when no review data. | Partial |
| `flareResistance` | Review backlit sample images | No |

### Genre Scoring

Scores are **computed at render time**, not stored. Each genre has a pure function that takes a `Lens` and returns a result. No pre-computed score arrays — single source of truth, never stale.

```typescript
type Genre = "astro" | "portrait" | "landscape" | "sport"
           | "wildlife" | "street" | "travel" | "architecture"
           | "macro";

interface ScoreResult {
  mark: number;           // 1-5, step 0.5
  breakdown: {            // per-criterion scores for transparency
    [criterion: string]: number;
  };
  disqualified: boolean;  // hard disqualifier triggered
  reason?: string;        // why disqualified
}

// Each genre is a pure function: Lens → ScoreResult
function scoreAstro(lens: Lens): ScoreResult { ... }
function scorePortrait(lens: Lens): ScoreResult { ... }
// etc.
```

**Why computed, not stored:** 200 lenses × 9 genres = 1,800 scores. Trivial to compute on every render. Storing them means two things to keep in sync — if a lens field changes (e.g. `cornerSharpness` after MTF review), stored scores go stale silently.

**Universal formula:** `mark = round(total / maxTotal * 8 + 2) / 2`
Range 1-5, step 0.5. Same formula for every genre — only the criteria and maxTotal change.

**All scores are optics/physics only.** Binary features (WR, OIS, AF motor, filter thread, distance scale, etc.) are filter badges in the UI, not scoring inputs.

| Genre | Criteria | maxTotal | Inputs from Lens | Disqualifier |
|---|---|---|---|---|
| Astro | light (Lonely Speck formula, 0-2) + coma (0-2) | 4 | `focalLengthMin`, `maxAperture`, `mount`, `comaRating` | `wideOpenSharpness ≤ 1` |
| Portrait | blur (entrance pupil, benchmark 50mm, 0-2) + bokeh (0-2) + wideOpenSharpness (0-2) | 6 | `focalLengthMin/Max`, `maxAperture`, `bokehQuality`, `wideOpenSharpness` | None |
| Landscape | sweetSpotSharpness (0-2) + cornerSharpness (0-2) | 4 | `sweetSpotSharpness`, `cornerSharpness` | None |
| Sport | light (entrance pupil, benchmark 50mm, 0-2) + wideOpenSharpness (0-2) | 4 | `focalLengthMax`, `maxAperture`, `wideOpenSharpness` | None |
| Wildlife | light (entrance pupil, benchmark 100mm, 0-2) + wideOpenSharpness (0-2) | 4 | `focalLengthMax`, `maxAperture`, `wideOpenSharpness` | None |
| Street | wideOpenSharpness (0-2) + locaRating (0-2) | 4 | `wideOpenSharpness`, `locaRating` | None |
| Travel | sweetSpotSharpness (0-2) + wideOpenSharpness (0-2) + locaRating (0-2) | 6 | `sweetSpotSharpness`, `wideOpenSharpness`, `locaRating` | None |
| Architecture | distortionRating (0-2) + cornerSharpness (0-2) + sweetSpotSharpness (0-2) | 6 | `distortionRating`, `cornerSharpness`, `sweetSpotSharpness` | None |
| Macro | maxMagnification (0-2, 1.0=2) + sweetSpotSharpness (0-2) + cornerSharpness (0-2, proxy for field curvature) | 6 | `maxMagnification`, `sweetSpotSharpness`, `cornerSharpness` | None |

**Entrance pupil benchmarks (per mount):**

| Genre | X-Mount benchmark | GFX benchmark |
|---|---|---|
| Portrait | 50mm (XF 50mm f/1.0) | 69mm (GF 110mm f/2.0) |
| Sport | 50mm (XF 50-140mm f/2.8) | — |
| Wildlife | 100mm (XF 200mm f/2.0) | — |

**For zooms:** scored at max focal length with the aperture at that FL.

**Filter badges (all genres, shown in UI, not scored):**
WR, OIS, AF motor (DC/STM/LM), autofocus, filter thread, rotating front, distance scale, focus by wire, aperture ring, aperture clickless, smooth focus ring, tripod mount, tilt-shift, shift range, tilt angle, circular aperture, weather sealed

**Display attributes (not scored, not filtered):**
Flare resistance, sunstar points (computed from aperture blades), flare character, image circle

### Affiliate Link

```typescript
interface AffiliateLink {
  retailer: string;       // "mpb", "amazon", "bhphoto"
  url: string;            // Base URL with tracking params
  lens: string;           // Lens model reference
  region: string;         // "eu", "us", "uk"
}
```


## 05. Data Management Strategy

**All phases — Embedded data.** All data in `src/data/*.ts` files, imported at build time. Updates = edit file → push → auto-deploy. No CMS — the dataset changes a few times per month; a CMS adds complexity that isn't justified. No backend — subscriptions were dropped from the roadmap. This architecture stays static through all four phases; multi-system (phase 4) adds more data files, not infrastructure.


## 06. Individual Lens Pages

Each lens gets its own URL: `/lens/xf-23mm-f1-4`. Auto-generated from the data file at build time — no manual page authoring. This is the primary SEO play: each page targets a high-intent query ("fuji xf 23mm f1.4 review").

**Page content (auto-generated):**
- Lens name, brand, key specs
- Genre scores across all 8 genres (computed)
- Score breakdown per genre (why it scored 4/5 for landscape)
- One-line verdict per genre ("Best budget landscape prime")
- Affiliate links (Amazon, B&H, MPB)
- "Compare with" links to similar lenses
- No long-form review text — structured data, not wall of text

**Why this matters:** Ken Rockwell ranks for "fuji xf 23mm f1.4" because he has a dedicated page for it. A single table on `/lenses` can't compete for per-lens queries. 200+ lens pages = 200+ indexable URLs targeting specific high-intent searches.

**Implementation:** Vite static site generation at build time. Loop over `lenses.ts`, generate one HTML page per lens. No runtime rendering — fully static, cacheable, fast.


## 07. SEO Strategy

| Aspect | Approach | Rationale |
|---|---|---|
| Rendering | Client-side SPA + static lens pages (SSG) | SPA for the interactive screener; static pages for per-lens SEO |
| Individual lens pages | Static generation at build time (phase 2) | 200+ indexable URLs; targets per-lens search queries |
| Meta tags | react-helmet | Per-page titles and descriptions |
| Sitemap | Generated at build time | From lens, genre, and wiki data |
| Structured data | JSON-LD | Product (lens pages) and FAQPage (wiki) |
| URL structure | `/lenses`, `/lens/xf-23mm-f1-4`, `/genre/landscape`, `/wiki/aperture` | Clean, human-readable, keyword-rich |


## 08. Performance Targets

| Target | Value | Rationale |
|---|---|---|
| Bundle size | < 200KB gzipped | All data + app must fit; no lazy loading needed at Fuji-only scale |
| LCP | < 1.5s | No API calls on load; data is in the bundle |
| Mobile breakpoint | 640px | Card layout below, table above — matches prototype |


## 09. Deployment

```
git push main
  → GitHub Actions runs vite build
  → Deploys to GitHub Pages
  → Available at fujime.app (CNAME)
```

Zero-downtime. No database. No server. No containers. Cost: €0.

**Fallback:** if GitHub Pages hits limits (100GB/month bandwidth, 10-minute build timeout), switch to Vercel or Cloudflare Pages — same git-push deploy model, better CDN, preview deploys per branch. Migration is a 10-minute repo connection, not a rewrite.


## 10. Migration from Prototype

The prototype is a single 3400-line JSX file with inline styles and embedded data.

| Step | What | Status |
|---|---|---|
| 1 | TypeScript interfaces for all data types | Done — Lens (40+ fields), Camera (32), Genre, Affiliate, Review |
| 2 | Extract lens data into `src/data/lenses.ts` | Done — 236 lenses with full specs + officialUrl |
| 3 | Scaffold Astro + React islands (replaces Vite + React SPA) | Next |
| 4 | Extract camera, wiki, accessories data | Pending |
| 5 | Split into Astro pages + React islands for interactive parts | Pending |
| 6 | Replace inline styles with Astro scoped styles + CSS Modules | Pending |
| 7 | Add affiliate link data and Trade Deals integration | Pending |
| 8 | Deploy to GitHub Pages with custom domain (CNAME) | Pending |

The prototype is the spec. Every feature in it is confirmed working — migration is restructuring, not redesign.


## 11. Deferred

| Item | Why deferred |
|---|---|
| Server-side rendering | Astro generates static HTML; SSR not needed |
| CMS for lens data | Frequency of updates doesn't justify CMS complexity |
| REST API | Data changes monthly; embedded data is faster and simpler |
| Mobile app | PWA via Vite plugin if mobile usage is high |
| API for third-party consumption | No demand signal yet |
| User-generated content (reviews, ratings) | Moderation overhead; not worth it at launch scale |
| Price scraping | Legal grey area; use affiliate API price data instead |
| Multi-language | English only at launch; Bulgarian if BG traffic is significant |
