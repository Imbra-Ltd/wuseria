# ADR-016: Reject data externalization to static JSON endpoints

**Status:** Accepted
**Date:** 2026-05-01

## Context

Spike #380. The lens, camera, and genre data is serialized inline into
`<astro-island props="">` attributes in the HTML. After session 19 data
trimming, gzipped sizes are /lenses 17 KB, /cameras 10 KB, /genre 19 KB.
Real-world LCP on /lenses is 2.0 s (PageSpeed Insights field data).

The question: would moving this data to static JSON files fetched
client-side after hydration improve LCP?

## Decision

Reject. Keep data inline in Astro island props.

## Alternatives considered

### Static JSON endpoints fetched client-side

The island would render a loading state, hydrate, fetch `/api/lenses.json`,
then render the data.

**Rejected because:**

1. **Fetch waterfall.** HTML load -> JS hydrate -> fetch JSON -> render.
   Currently: HTML load -> render (data already present). Adding a network
   round-trip after hydration increases time-to-content, not decreases it.

2. **Already tried and reverted.** Session 16 reverted "Approach B
   (AppShell)" for exactly this reason: first-load regression from fetch
   waterfall and JS bundle increase.

3. **SEO regression.** With `output: "static"` and no SSR, data fetched
   client-side is invisible to crawlers. The current inline approach
   produces fully crawlable HTML.

4. **Diminishing returns.** 17-19 KB gzip is smaller than a single hero
   image. Further optimization of this payload cannot produce a
   perceptible improvement.

5. **Complexity cost.** Adds API endpoint files, fetch logic, loading
   states, and error handling for zero user-visible benefit.

### Static JSON with `<script type="application/json">`

Embed JSON in a script tag instead of island props, read it on hydration.

**Rejected because:** Astro's built-in binary serialization format already
compresses better than raw JSON (~40-50% smaller) through reference
deduplication. Switching to plain JSON would increase payload size.

## Consequences

- Data remains inline in Astro island props (current architecture unchanged)
- No `src/pages/api/` directory needed
- Future data growth (more lenses/cameras) may revisit this if gzipped
  HTML exceeds ~50 KB, but current trajectory (256 lenses = 17 KB gzip)
  suggests this is far off
- Performance improvements should focus on other vectors (View Transitions,
  bundle splitting, image optimization)
