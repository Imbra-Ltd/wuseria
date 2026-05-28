# Fujifilm GF 100-200mm f/5.6 R LM OIS WR — Specs Log

## Sources checked

| Source              | URL                                         | Date       | Result                                                         |
| ------------------- | ------------------------------------------- | ---------- | -------------------------------------------------------------- |
| Official (Fujifilm) | via `tools/fujifilm/fetch_specs.py`         | 2026-05-28 | Authoritative physical specs; divergent fields corrected below |
| `--verify` tool     | `py tools/fujifilm/fetch_specs.py --verify` | 2026-05-28 | Flagged divergent physical fields (#896); clean after fix      |

## Findings

Physical-spec correction (#896 — Fujifilm reconciliation). Divergent fields
overwritten with the official spec-page values (official page wins per the
CLAUDE.md source-conflict rule):

- **maxMagnification:** 0.19 -> **0.2**
- **filterThread:** 72 -> **67**

## Caveats

- Surfaced by `--verify` after the #906 extractor comma-weight fix made heavy-lens
  weights trustworthy. The extractor reads the official page correctly; these were
  stale/incorrect stored values.
- Optical/scoring fields untouched. Any downstream genreMarks were recomputed to
  match `computeAllGenreMarks`.
