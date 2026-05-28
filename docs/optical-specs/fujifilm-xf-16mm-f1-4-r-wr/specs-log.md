# Fujifilm XF 16mm f/1.4 R WR — Specs Log

## Sources checked

| Source              | URL                                         | Date       | Result                                                         |
| ------------------- | ------------------------------------------- | ---------- | -------------------------------------------------------------- |
| Official (Fujifilm) | via `tools/fujifilm/fetch_specs.py`         | 2026-05-28 | Authoritative physical specs; divergent fields corrected below |
| `--verify` tool     | `py tools/fujifilm/fetch_specs.py --verify` | 2026-05-28 | Flagged divergent physical fields (#896); clean after fix      |

## Findings

Physical-spec correction (#896 — Fujifilm reconciliation). Divergent fields
overwritten with the official spec-page values (official page wins per the
CLAUDE.md source-conflict rule):

- **weight:** 400 -> **375**

## Caveats

- Surfaced by `--verify` after the #906 extractor comma-weight fix made heavy-lens
  weights trustworthy. The extractor reads the official page correctly; these were
  stale/incorrect stored values.
- Optical/scoring fields untouched. Any downstream genreMarks were recomputed to
  match `computeAllGenreMarks`.
