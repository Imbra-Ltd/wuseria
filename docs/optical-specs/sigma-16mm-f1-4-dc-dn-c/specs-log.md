# Sigma 16mm f/1.4 DC DN C — Specs Log

## Sources checked

| Source           | URL                                      | Date       | Result                                                          |
| ---------------- | ---------------------------------------- | ---------- | --------------------------------------------------------------- |
| Official (Sigma) | sigma-global.com/en/lenses/c017_16_14/   | 2026-05-28 | Authoritative physical specs (length 90.3mm, weight 415g)       |
| `--verify` tool  | `py tools/sigma/fetch_specs.py --verify` | 2026-05-28 | Flagged 2 physical fields stale (#902 Class A); clean after fix |

## Findings

Physical-spec correction (#902, Class A — small staleness deltas; official page
authoritative per the source-conflict rule):

- **length:** 92.3 → **90.3** mm
- **weight:** 405 → **415** g

No genre-mark change. Optical/scoring fields untouched.
