# ADR-027: Asset and spec storage strategy

**Status:** Accepted
**Date:** 2026-05-17
**Issue:** #693

## Context

MTF chart images (31 lenses) live in `docs/mtf-charts/` alongside companion
`.md` analysis files. ADR-026 requires these images rendered on lens detail
pages. The `docs/` directory is not processed by Astro's build pipeline, so
images there cannot benefit from optimization (format conversion, responsive
sizing, lazy loading). Implementation specs like the content spine were stored
in untracked `temp/` and referenced by ADRs without being committed.

## Decision

### Web assets: `src/assets/mtf/`

MTF chart images (.png) move to `src/assets/mtf/`. Astro's `<Image>` component
processes files in `src/assets/`, providing:

- Automatic format conversion (WebP/AVIF)
- Width/height attributes (prevents CLS)
- Lazy loading
- Responsive `srcset` generation

Naming convention: `{lens-slug}.png` — matches URL slugs already in use.

When no image exists for a lens, omit the MTF chart sub-section entirely.

Attribution: caption below each image — "Source: {brand} official specifications".

### Analysis files: `docs/mtf-charts/`

Companion `.md` files (chart readings, interpretation notes, source URLs) stay
in `docs/mtf-charts/`. These are developer reference used during scoring. May
optionally be rendered as page content during ADR-026 implementation.

### Implementation specs: `docs/specs/`

Implementation specifications referenced by ADRs live in `docs/specs/`.
First file: `lens-content-spine.md` (referenced by ADR-026).

### Optical diagrams: deferred

No sourcing strategy yet. Will revisit when lens configuration data is added
(see #565).

## Alternatives considered

| Alternative                           | Rejected because                                            |
| ------------------------------------- | ----------------------------------------------------------- |
| Keep images in `docs/mtf-charts/`     | Not processed by Astro; no optimization                     |
| Use `public/images/mtf/`              | Static copy only; no format conversion or responsive sizing |
| Merge .md analysis into `src/assets/` | Mixes developer reference with web assets                   |
| Keep specs in `temp/` (untracked)     | Not committed; disappears on clone                          |

## Consequences

- MTF chart images get automatic optimization (smaller payloads, modern formats)
- `docs/mtf-charts/` shrinks to .md files only (analysis + source attribution)
- `docs/specs/` provides a tracked home for implementation specs
- Migration task needed: move 31 .png files from `docs/mtf-charts/` to `src/assets/mtf/`
- Update .md analysis files to reference new image paths
