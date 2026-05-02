# ADR-003: Astro with React islands

**Status:** Accepted
**Date:** 2026-04-08
**Supersedes:** Original Vite + React SPA decision

## Context

The site is ~80% static data display (lens specs, camera specs, wiki) and ~20% interactive (sort/filter tables, genre selector). SEO is critical — individual lens pages need to rank for per-lens queries.

## Decision

Use Astro as the framework with React islands for interactive components. Static output, zero JS by default, hydrate only where needed.

## Alternatives considered

| Alternative      | Why rejected                                                                             |
| ---------------- | ---------------------------------------------------------------------------------------- |
| Vite + React SPA | Ships all JS to the browser; poor SEO without SSR; was the original choice but abandoned |
| Next.js          | Heavier than needed; SSR not required for static data                                    |
| Plain Hugo       | No React ecosystem; harder to build interactive sort/filter tables                       |

## Consequences

- Pre-rendered HTML by default — excellent Core Web Vitals and SEO
- React islands hydrated only for sort/filter tables (`client:load`) and below-fold interactivity (`client:visible`)
- solid-ai-templates recommends static-site-astro for this pattern
- Astro file-based routing generates 200+ lens pages at build time via `getStaticPaths()`
- Most pages ship zero JS to the browser
