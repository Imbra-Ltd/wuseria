# ADR-008: Individual lens pages for SEO

**Status:** Accepted
**Date:** 2026-04-06

## Context

Per-lens search queries ("fuji xf 23mm f1.4 review") are high-intent. Competitors like Ken Rockwell rank because they have a dedicated page per lens. A single table on `/lenses` cannot compete for these queries.

## Decision

Auto-generate one page per lens at build time via `getStaticPaths()`. Each page targets a specific high-intent search query.

## Approach

- Astro native head management for per-page titles and descriptions
- `@astrojs/sitemap` for auto-generated sitemap
- JSON-LD structured data (Product for lenses, FAQPage for wiki)
- Canonical URLs on all pages
- URL slugs lowercase: `XF 23mm f/1.4` -> `xf-23mm-f1-4`

## Consequences

- 200+ indexable URLs targeting specific searches
- No manual page authoring — pages generated from data
- Structured data improves rich snippet eligibility
- Each page includes genre scores, spec breakdown, affiliate links, and comparison links
