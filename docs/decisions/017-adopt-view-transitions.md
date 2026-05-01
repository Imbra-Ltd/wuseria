# ADR-017: Adopt Astro View Transitions for navigation speed

**Status:** Accepted
**Date:** 2026-05-01

## Context

Spike #381. Each navigation between explorer pages (/lenses, /cameras,
/genre, /accessories) triggers a full page reload and React re-hydration.
Prefetch is already enabled (hover strategy, all links), so the HTML is
pre-fetched but the browser still does a full document swap.

Astro 6.1.5 ships `<ClientRouter />` (from `astro:transitions`) which
enables client-side DOM morphing with the View Transitions API. The
question: does this improve perceived navigation speed with acceptable
risk?

## Decision

Adopt View Transitions by adding `<ClientRouter />` to `Base.astro`.

## Implementation

1. Import and add `<ClientRouter />` in `Base.astro` `<head>`
2. Update the hamburger menu inline script to use `astro:page-load`
   event instead of top-level execution (scripts in `<head>` only run
   once with client-side routing)
3. Verify React island hydration works correctly after DOM swap
4. Test navigation between all explorer pages on mobile and desktop
5. Measure perceived navigation time before and after

### What NOT to do

- Do not add `transition:persist` on React islands - each page has a
  different island component (LensExplorer, CameraExplorer, etc.),
  so persist would not match across pages
- Do not add custom transition animations - the default crossfade is
  sufficient and avoids jank on low-end devices
- Do not persist filter state across pages - this is not expected
  behavior (each explorer is independent)

## Alternatives considered

### Keep full page reloads with prefetch only

The current approach. Prefetch warms the cache but the browser still
parses and renders the full document from scratch.

**Rejected because:** View Transitions is a one-component addition that
eliminates the full-page flash. The prefetched HTML is already in cache;
View Transitions simply swaps the DOM instead of discarding it.

### SPA framework (Next.js, Remix)

Full client-side routing with shared React tree.

**Rejected because:** Massive migration cost, ships far more JS, and
breaks the zero-JS-by-default architecture. Astro View Transitions
achieves the same perceived speed with a fraction of the complexity.

## Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Hamburger menu breaks after transition | High | Use `astro:page-load` event listener |
| React hydration timing issues | Medium | Test all islands; fallback is `transition:animate="none"` |
| Inline scripts run twice or not at all | Medium | Audit all inline scripts in Base.astro |
| Browser without View Transitions API | Low | Graceful degradation to full reload (built-in) |

## Consequences

- Navigation between pages feels instant (DOM morph instead of reload)
- Header/footer do not flash or re-render during navigation
- Inline scripts in Base.astro must use `astro:page-load` lifecycle
  event for re-initialization
- Future islands can use `transition:persist` if the same component
  appears on multiple pages (not applicable today)
- Lighthouse navigation-based audits may need adjustment since
  client-side routing changes how page loads are measured
