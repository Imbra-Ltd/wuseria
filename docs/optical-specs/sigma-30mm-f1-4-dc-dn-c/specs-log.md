# Sigma 30mm f/1.4 DC DN C — Specs Log

## Sources checked

| Source           | URL                                      | Date       | Result                                                          |
| ---------------- | ---------------------------------------- | ---------- | --------------------------------------------------------------- |
| Official (Sigma) | sigma-global.com/en/lenses/c016_30_14/   | 2026-05-28 | Authoritative physical specs (length 71.3mm, weight 280g)       |
| `--verify` tool  | `py tools/sigma/fetch_specs.py --verify` | 2026-05-28 | Flagged 2 physical fields stale (#902 Class A); clean after fix |

## Findings

Physical-spec correction (#902, Class A — small staleness deltas; official page
authoritative per the source-conflict rule):

- **length:** 73.3 → **71.3** mm
- **weight:** 265 → **280** g

No genre-mark change. Optical/scoring fields untouched.
