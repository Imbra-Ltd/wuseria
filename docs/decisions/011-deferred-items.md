# ADR-011: Deferred items and rationale

**Status:** Accepted
**Date:** 2026-04-06

## Context

Several features and architectural options were considered during design but intentionally deferred. Recording the rationale prevents revisiting settled decisions.

## Deferred items

| Item                            | Why deferred                                                 |
| ------------------------------- | ------------------------------------------------------------ |
| Server-side rendering           | Astro generates static HTML; SSR not needed                  |
| CMS for lens data               | Update frequency does not justify CMS complexity             |
| REST API                        | Data changes monthly; embedded data is faster and simpler    |
| Mobile app                      | PWA via Astro plugin if mobile usage is high                 |
| API for third-party consumption | No demand signal yet                                         |
| User-generated content          | Moderation overhead; not worth it at launch scale            |
| Price scraping                  | Legal grey area; use affiliate API price data instead        |
| Multi-language                  | English only at launch; Bulgarian if BG traffic justifies it |

## Consequences

- Architecture stays static through all four phases
- Revisit individual items if demand signals change
- Each item can be reconsidered independently — create a new ADR to supersede
