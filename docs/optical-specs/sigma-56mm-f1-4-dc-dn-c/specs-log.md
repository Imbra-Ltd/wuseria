# Sigma 56mm f/1.4 DC DN C — Specs Log

## Sources checked

| Source           | URL                                      | Date       | Result                                                  |
| ---------------- | ---------------------------------------- | ---------- | ------------------------------------------------------- |
| Official (Sigma) | sigma-global.com/en/lenses/c018_56_14/   | 2026-05-28 | Authoritative physical specs (length 57.5mm, mag 0.135) |
| `--verify` tool  | `py tools/sigma/fetch_specs.py --verify` | 2026-05-28 | Flagged 2 fields stale (#902 Class A); clean after fix  |

## Findings

Physical-spec correction (#902, Class A — small staleness deltas; official page
authoritative per the source-conflict rule):

- **length:** 59.5 → **57.5** mm
- **maxMagnification:** 0.14 → **0.135**

No genre-mark change. Optical/scoring fields untouched.
