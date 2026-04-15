# ADR-015: Astro Content Collections for wiki entries

**Status:** Accepted
**Date:** 2026-04-14

## Context

The wiki started as 11 entries in `src/data/wiki.ts` with `body: string[]` (plain text paragraphs). After migrating the prototype glossary, the file grew to 115 entries and 1200+ lines. Content is limited to flat paragraphs — no headings, lists, tables, bold, or inline links. Richer pages like Scoring Methodology need structured content that plain strings cannot express.

## Decision

Move wiki entries from `src/data/wiki.ts` to Astro Content Collections (`src/content/wiki/*.md`). Each entry becomes a standalone Markdown file with typed frontmatter. Astro validates the schema at build time and renders Markdown to HTML at zero JS cost.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Keep `wiki.ts` with markdown strings | Markdown inside TS string literals is hard to author and review. No syntax highlighting, no linting, awkward escaping. |
| Keep `wiki.ts` with structured body blocks (union types) | Type-safe but verbose — every heading, list, and table needs a type discriminant. Authoring friction grows with content complexity. |
| MDX files | Adds React hydration overhead for content that is purely static. Markdown suffices — no interactive components needed inside wiki articles. |
| External CMS | Same rejection as ADR-001 — adds complexity for a solo-maintainer project with monthly updates. |

## Consequences

- Each wiki entry is a `.md` file — natural authoring with headings, lists, tables, bold, links
- Frontmatter schema (`src/content.config.ts`) enforces required fields at build time — same safety as TS types
- Git diff per entry — easier reviews when updating one article
- `src/data/wiki.ts` is removed; wiki index and detail pages read from `getCollection("wiki")`
- Existing deep articles (11) gain full Markdown formatting; prototype entries (104) keep their single-paragraph content and can be expanded incrementally
- No JS shipped — Astro renders Markdown to static HTML at build time
