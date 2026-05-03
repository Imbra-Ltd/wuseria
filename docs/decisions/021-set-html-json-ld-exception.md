# ADR-021: Allow set:html for JSON-LD structured data injection

**Status:** Accepted
**Date:** 2026-05-03

## Context

The project bans `set:html` in `.astro` files because it bypasses Astro's
automatic escaping — equivalent to `innerHTML` and a potential XSS vector.

However, JSON-LD structured data must be rendered inside a
`<script type="application/ld+json">` tag. Astro's `{expression}` syntax
HTML-escapes the output, which corrupts the JSON. The only way to inject
raw JSON into a script tag in Astro is `set:html`.

## Decision

Allow `set:html` exclusively for JSON-LD injection under these constraints:

1. The value MUST be `JSON.stringify(object)` — never a raw string or
   user-provided content
2. The object MUST be constructed entirely from server-controlled data
   (build-time imports from `src/data/`)
3. The target element MUST be `<script type="application/ld+json">`
4. No other use of `set:html` is permitted

## Alternatives considered

- **Astro Content Collections with built-in JSON-LD** — Astro has no
  native JSON-LD support; still requires manual script injection
- **External JSON-LD file per page** — adds build complexity with no
  security benefit since the data is the same
- **Omit JSON-LD entirely** — loses SEO structured data (Product,
  FAQPage schemas) which impacts search result presentation

## Consequences

- Four pages use this pattern: lenses, cameras, accessories, and wiki
  detail pages
- The `set:html` ban remains in force for all other contexts
- Linters and reviewers should not flag `set:html` when the pattern
  matches constraint 1-3 above
