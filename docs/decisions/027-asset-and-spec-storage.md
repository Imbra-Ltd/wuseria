# ADR-027: Asset and spec storage strategy

**Status:** Accepted (revised 2026-05-18)
**Date:** 2026-05-17
**Issue:** #693

## Context

MTF chart images (31 lenses) live in `docs/mtf-charts/` alongside companion
`.md` analysis files. ADR-026 requires these charts rendered on lens detail
pages. Implementation specs like the content spine were stored in untracked
`temp/` and referenced by ADRs without being committed.

The original decision (2026-05-17) moved PNG images to `src/assets/mtf/` for
Astro image optimization. During implementation, a better approach emerged:
the `.md` analysis files already contain digitized readings (position, 10S,
10M, 30S, 30M values). Rendering SVG charts directly from this data eliminates
the need to serve raster images entirely.

## Decision

### MTF charts: SVG from data

MTF chart readings are stored in `src/data/mtf-readings.ts` as typed
TypeScript data (`MtfData` from `src/types/mtf.ts`). The static Astro
component `src/components/static/MtfChart.astro` renders SVG charts at build
time — no JS shipped to the browser.

Structure:

- `src/types/mtf.ts` — `MtfReading`, `MtfChart`, `MtfData` interfaces
- `src/data/mtf-readings.ts` — readings keyed by lens slug, with source URL
- `src/data/mtf-readings.test.ts` — data integrity tests
- `src/components/static/MtfChart.astro` — SVG renderer with legend

Each entry contains one or more aperture charts (e.g. wide-open + stopped
down), each with readings at measured image-height positions.

When no readings exist for a lens, the MTF chart sub-section is omitted.

Attribution: source link below charts — "Official manufacturer specifications".

### Reference images: `docs/mtf-charts/`

PNG images of official manufacturer MTF charts stay in `docs/mtf-charts/`
as developer reference. These are used during the digitization process
(visually reading values from curves) but are not served on the site.

### Analysis files: `docs/mtf-charts/`

Companion `.md` files (chart readings, interpretation notes, source URLs) stay
in `docs/mtf-charts/`. These are developer reference used during scoring.

### Implementation specs: `docs/specs/`

Implementation specifications referenced by ADRs live in `docs/specs/`.
First file: `lens-content-spine.md` (referenced by ADR-026).

### Optical diagrams: deferred

No sourcing strategy yet. Will revisit when lens configuration data is added
(see #565).

## Alternatives considered

| Alternative                           | Rejected because                                                                                                                                     |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Move PNGs to `src/assets/mtf/`        | Raster images are not themeable, not responsive to dark mode, and require a migration task for 31 files; data already exists in `.md` analysis files |
| Keep images in `docs/mtf-charts/`     | Not processed by Astro; no optimization                                                                                                              |
| Use `public/images/mtf/`              | Static copy only; no format conversion or responsive sizing                                                                                          |
| Merge .md analysis into `src/assets/` | Mixes developer reference with web assets                                                                                                            |
| Keep specs in `temp/` (untracked)     | Not committed; disappears on clone                                                                                                                   |

## Consequences

- MTF charts render as inline SVG — zero additional network requests, dark-theme compatible
- Chart styling uses CSS custom properties — consistent with site theme
- No image migration needed; `docs/mtf-charts/` keeps both `.png` and `.md` as developer reference
- `docs/specs/` provides a tracked home for implementation specs
- Digitization effort: each lens requires manually reading values from the manufacturer chart into `src/data/mtf-readings.ts`
- Data integrity enforced by co-located tests (sorted positions, 0-1 range, valid slugs)
