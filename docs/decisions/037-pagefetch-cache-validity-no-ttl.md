# ADR-037: pagefetch cache validity by content, not time (no TTL)

**Status:** Accepted
**Date:** 2026-05-29

## Context

`pagefetch`'s `FileCache` is permanent: `read()` returns any cached file
forever, keyed by `sha256(url)[:16]` plus a `.txt`/`.html` suffix. Two
freshness concerns prompted a review of whether the cache should expire:

- **Prices drift.** A price scraped today may be wrong in a month.
- **Products get discontinued.** A lens marked available, or a page that
  later 404s, could be served stale from cache.

The obvious lever is a time-based TTL (treat a cache file older than N days
as a miss). The question was whether that is the right tool.

`pagefetch` is a **research-time scraping tool**, not part of the live
site's request path. It is run by the agent and subagents while collecting
specs, MTF charts, and prices; the cache exists to make an iterative
research session cheap (avoid re-hitting a bot-protected retailer dozens of
times). Stale cache therefore has a different cost than it would for a
live application — and crucially, scraped values are copied into
`src/data/*.ts` (prices rounded to the nearest $50 and shown with `~`), so
the cached _page_ going stale does not change stored data on its own.

## Decision

**No TTL.** Cache validity is decided by content, not age. A cached
response is invalid — ignored and re-fetched — when its body is
recognizably:

- a bot-detection / throttle page (`is_bot_blocked`, ADR-035 / #881), or
- a 404 / gone error page (`is_error_page`: hard 404/410 and soft-404s
  served as HTTP 200 with a "not found" / "no longer available" body).

Non-200 responses and implausibly short stubs are never written to the
cache in the first place. Deliberate refreshes use the existing
`--no-cache` flag.

This maps the two concerns to the right mechanism:

- **Discontinuation** surfaces as a 404 / redirect / "no longer available"
  page — caught by `is_error_page` on both write (not cached) and read
  (cached error self-heals). A timer is not needed to detect it.
- **Price refreshes** are intentional passes the operator triggers with
  `--no-cache`, not something a background timer should decide. The fetcher
  does not know _why_ a fetch is happening; the operator does.

## Alternatives considered

- **Time-based TTL (mtime, default ~30 days).** Rejected. Adds a config
  knob and risks slowing every research session with needless re-fetches of
  data that has not changed (optical specs essentially never do), while not
  actually solving the stated concerns: a timer cannot tell a price change
  from a discontinuation, and both are better handled by content checks or
  an intentional `--no-cache` pass. Revisit only with evidence that prices
  go stale in a way `--no-cache` does not address.
- **Per-request `max-age` in `FetchOptions`.** Rejected for now — pushes a
  freshness decision onto every call site for a benefit `--no-cache`
  already covers. A possible future opt-in CLI `--max-age` flag (off by
  default) was noted but not built; YAGNI until a price-refresh workflow
  needs it.

## Consequences

- The cache stays simple: no timestamps beyond the filesystem, no metadata
  sidecar, no key-scheme change (the fixed `sha256(url)[:16]` scheme that
  on-disk caches depend on is untouched).
- A page that became a 404/gone after being cached self-heals on the next
  fetch; a genuine 404 is terminal (no wasteful browser escalation, since
  every tier returns the same error) and is not cached.
- Stale prices are an operator responsibility, refreshed with `--no-cache`
  during a deliberate price pass — consistent with prices being approximate
  estimates (rounded, `~`-prefixed) rather than live data.
- If evidence later shows time-based refresh is needed, this ADR is
  superseded by one introducing a TTL or `--max-age`; the content-validity
  checks remain regardless.
