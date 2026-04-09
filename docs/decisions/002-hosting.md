# ADR-002: GitHub Pages for hosting

**Status:** Accepted
**Date:** 2026-04-06

## Context

The site is fully static (Astro output). Needs a CDN-backed host with custom domain support and zero ongoing cost.

## Decision

Deploy to GitHub Pages via GitHub Actions. Custom domain: fujime.app.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Vercel | Requires a second account; free tier is sufficient but GitHub Pages is simpler |
| Cloudflare Pages | Same — additional account for no current benefit |
| Netlify | Same tier; no advantage over GitHub Pages at current scale |

## Consequences

- Zero cost (already using GitHub)
- Git-push deploy via Actions
- Limits: 100GB/month bandwidth, 10-minute build timeout
- Migration path: switch to Vercel or Cloudflare Pages if limits are hit — same git-push model, 10-minute migration
