# Sigma 23mm f/1.4 DC DN C — Specs Log

## Sources checked

| Source           | URL                                      | Date       | Result                                                |
| ---------------- | ---------------------------------------- | ---------- | ----------------------------------------------------- |
| Official (Sigma) | sigma-global.com/en/lenses/c023_23_14/   | 2026-05-28 | Authoritative physical specs (mag 0.137)              |
| `--verify` tool  | `py tools/sigma/fetch_specs.py --verify` | 2026-05-28 | Flagged 1 field stale (#902 Class A); clean after fix |

## Findings

Physical-spec correction (#902, Class A — small staleness delta; official page
authoritative per the source-conflict rule):

- **maxMagnification:** 0.15 → **0.137**

Downstream genre recompute (stored to match `computeAllGenreMarks`): `macro`
2 → 1 (lower magnification). Optical/scoring fields untouched.
