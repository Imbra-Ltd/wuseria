# ADR-004: Astro scoped styles and CSS Modules

**Status:** Accepted
**Date:** 2026-04-06

## Context

Need a styling approach that works for both Astro static pages and React island components without shipping a CSS runtime.

## Decision

Use Astro scoped `<style>` blocks for `.astro` page components and CSS Modules co-located with React islands.

## Alternatives considered

| Alternative       | Why rejected                                                       |
| ----------------- | ------------------------------------------------------------------ |
| Tailwind          | Utility class overhead; harder to scan in data-dense table layouts |
| Inline styles     | No hover/media query support; not maintainable                     |
| styled-components | Ships JS runtime; unnecessary for mostly-static pages              |

## Consequences

- Zero CSS runtime shipped
- Styles are co-located with components (easy to find, easy to delete)
- CSS custom properties in `:root` for theming (dark mode, spacing, colours)
- No global class name collisions
