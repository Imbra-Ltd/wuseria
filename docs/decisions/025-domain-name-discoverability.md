# ADR-025: Domain name discoverability — wuseria.com vs wisteria confusion

**Status:** Accepted
**Date:** 2026-05-14
**Supersedes:** ADR-012

## Context

ADR-012 chose wuseria.com to eliminate trademark risk from the original
fujime.app domain. The name is a playful twist on "wisteria" (fuji =
wisteria in Japanese). The domain has been live since launch.

Issue #602 identified a discoverability problem: searching "wuseria" in
Google returns results dominated by "wisteria" (the plant). Google may
autocorrect or silently substitute the query. This undermines the most
basic discovery path — a user who hears about the site and searches by
name cannot find it.

This was not anticipated in ADR-012. The original decision optimized for
trademark safety and .com availability but did not evaluate search engine
disambiguation risk.

## Risk assessment

| Risk                                   | Severity | Notes                                                 |
| -------------------------------------- | -------- | ----------------------------------------------------- |
| Trademark (fujime.app)                 | High     | Eliminated by wuseria.com — ADR-012 decision stands   |
| Search confusion (wuseria vs wisteria) | Medium   | Google treats "wuseria" as misspelling of "wisteria"  |
| Brand establishment delay              | Medium   | New invented words take time to build search identity |
| Direct navigation                      | Low      | Users who know the URL can type wuseria.com directly  |

## Options evaluated

1. **Keep wuseria.com + reinforce** — structured data, Knowledge Panel
   claim, consistent branding in titles/meta/anchor text, Google Search
   Console. Wait for Google to learn the brand as site authority grows.
2. **Keep wuseria.com + paid search** — Google Ads for branded "wuseria"
   queries. Low cost (no competition for the term), high intent. Bridges
   the gap while organic recognition builds.
3. **Rename again** — choose a name that has no collision with existing
   dictionary words. Eliminates confusion but resets all SEO progress,
   requires new domain, and abandons any brand recognition already built.

## Decision

**Keep wuseria.com.** The trademark risk elimination from ADR-012 remains
the primary concern. The wisteria confusion is a temporary discovery
friction, not a fundamental flaw.

Rationale:

- The site is ~2 weeks old (launched late April 2026) with 106/461 pages
  indexed and ~200 total impressions. Switching cost is low right now —
  there is little accumulated authority to lose.
- However, renaming again (fujime.app → wuseria.com → ???) establishes a
  pattern of instability. A third domain in the project's lifetime signals
  indecision and resets whatever small momentum exists.
- Two weeks is far too early to evaluate search disambiguation. Google
  needs months to recognize a new proper noun. Judging now would be
  premature.
- "Wuseria" has zero competition as a brand term — once Google recognizes
  it as a distinct entity, it will own the entire first page of results.
  Every invented brand name faces this bootstrapping phase.
- The easter egg connection to wisteria/fuji is a feature of the brand
  identity, not a bug.

## Mitigation actions

1. Ensure "Wuseria" appears in page titles, OG tags, and JSON-LD
   `name` fields consistently
2. Claim Google Knowledge Panel when eligible
3. Register with Bing Webmaster Tools (#604) — diversify search engine
   presence
4. Monitor GSC for "wuseria" query impressions (#603) — track when
   Google begins treating it as a distinct entity
5. Consider branded paid search only if organic recognition stalls
   after 6 months

## Consequences

- wuseria.com remains the permanent domain — no further renaming
- #602 is resolved by this decision (keep + reinforce)
- Discovery metrics (GSC impressions for "wuseria" query) become a
  tracked KPI
- If after 12 months Google still autocorrects "wuseria" to "wisteria"
  with no improvement trend, revisit this ADR
