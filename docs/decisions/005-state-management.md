# ADR-005: Local state only (no global store)

**Status:** Accepted
**Date:** 2026-04-06

## Context

Interactive components (Lens Explorer, Camera Explorer, Genre Guide) need state for sort/filter controls. No server state exists — all data is embedded at build time.

## Decision

Use `useState` and `useMemo` within React islands. No global state library.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Zustand | No shared state across unrelated components; adds a dependency for no benefit |
| Redux | Same — massive overhead for local filter state |
| React Query | No server state to cache or sync |

## Consequences

- Each island manages its own sort/filter state independently
- No state synchronisation bugs between unrelated components
- If cross-island communication is ever needed, reconsider (unlikely given static architecture)
