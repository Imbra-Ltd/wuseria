# ADR-031: Optical Specs Directory Structure

**Status:** Accepted
**Date:** 2026-05-20

## Context

MTF charts were stored flat in `docs/mtf-charts/` with inconsistent naming,
wrong frequency labels, mixed file formats (webp, gif, jpg, png), and no
per-lens metadata. During a lens-by-lens verification audit, it became clear
that each lens needs its own folder to co-locate MTF charts, optical design
diagrams, and provenance notes (source URLs, CMS bugs, alternative sources).

## Decision

Create `docs/optical-specs/` with one subfolder per lens. Each subfolder
contains:

- MTF chart PNGs with the naming convention
  `{lens-slug}-{wide|tele}-{frequency}lp.png`
- `specs-log.md` when the source is not the official Fujifilm specifications page
  or when known issues exist (wrong charts on official page, CMS duplicates)
- Optical design diagrams (future)

Verified lenses are moved from `docs/mtf-charts/` to `docs/optical-specs/`.
Unverified files remain in `docs/mtf-charts/` until reviewed.

All image files are standardized to PNG format.

GFX MTF chart frequencies vary per lens (10/15/20/40/45 lp/mm) — there is
no single convention across the GFX lineup. XF/XC lenses use 15/45 lp/mm.

## Alternatives considered

1. **Keep flat structure** — rejected; no room for per-lens metadata, naming
   collisions between lens versions
2. **Subdirectories under mtf-charts/** — rejected; the scope expanded beyond
   MTF charts to include optical design and notes

## Consequences

- Each verified lens has a single source of truth for optical reference data
- Provenance is documented per lens via `specs-log.md`
- `docs/mtf-charts/` becomes a staging area for unverified files
- Third-party lens charts (Samyang, Sigma, Viltrox) still need verification
  and migration
