# Sigma 10-18mm f/2.8 DC DN C — Specs Log

## Sources checked

| Source           | URL                                       | Date       | Result                                                  |
| ---------------- | ----------------------------------------- | ---------- | ------------------------------------------------------- |
| Official (Sigma) | sigma-global.com/en/lenses/c023_10_18_28/ | 2026-05-28 | Authoritative physical specs (length 62.0mm, MFD 116mm) |
| `--verify` tool  | `py tools/sigma/fetch_specs.py --verify`  | 2026-05-28 | Flagged 2 fields stale (#902 Class A); clean after fix  |

## Findings

Physical-spec correction (#902, Class A — official page authoritative per the
source-conflict rule):

- **length:** 63.8 → **62.0** mm
- **minFocusDistance:** 192 → **116** mm (official 11.6cm — the lens's true
  minimum at the wide end; the 192 figure was stale)

No genre-mark change. Optical/scoring fields untouched.
