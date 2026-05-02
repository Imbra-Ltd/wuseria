# ADR-001: Embedded TypeScript files for data storage

**Status:** Accepted
**Date:** 2026-04-06

## Context

The site needs a data layer for ~240 lenses, ~40 cameras, ~50 accessories, and wiki entries. Data changes a few times per month. Options range from a CMS or database to flat files.

## Decision

Store all data in `src/data/*.ts` files, imported at build time. TypeScript rather than JSON.

## Alternatives considered

| Alternative                 | Why rejected                                                        |
| --------------------------- | ------------------------------------------------------------------- |
| JSON files                  | No compile-time type checking; missing fields are runtime surprises |
| REST API                    | Data changes monthly; API adds infrastructure for no benefit        |
| CMS (Contentful, Sanity)    | Adds complexity, cost, and a second system to maintain              |
| Database (SQLite, Postgres) | Requires a backend; overkill for static data                        |

## Consequences

- Compile-time type checking catches missing fields immediately
- IDE autocomplete on data arrays
- Scoring functions import data directly without a parsing step
- Updates require a code push and redeploy (acceptable at current change frequency)
- No non-developer editing path — acceptable for a solo-maintainer project
