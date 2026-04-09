# ADR-006: Astro file-based routing

**Status:** Accepted
**Date:** 2026-04-08

## Context

The site needs routes for lens explorer, camera explorer, individual lens pages (200+), genre pages, and wiki entries.

## Decision

Use Astro's built-in file-based routing. Dynamic routes via `getStaticPaths()` generate individual pages from data at build time.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| React Router v6 | Client-side only; requires SPA; no static page generation |
| TanStack Router | Same — designed for SPAs, not static sites |

## Consequences

- Routes map directly to file structure (`src/pages/lenses/[slug].astro`)
- `getStaticPaths()` generates 200+ lens pages from `lenses.ts` at build time
- No client-side routing overhead
- Adding a new route = adding a new file
