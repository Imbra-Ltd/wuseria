# Sigma 18-50mm f/2.8 DC DN C — Specs Log

## Sources checked

| Source           | URL                                       | Date       | Result                                                               |
| ---------------- | ----------------------------------------- | ---------- | -------------------------------------------------------------------- |
| Official (Sigma) | sigma-global.com/en/lenses/c021_18_50_28/ | 2026-05-28 | Authoritative physical specs (filter 55mm, length 74.5mm, MFD 121mm) |
| `--verify` tool  | `py tools/sigma/fetch_specs.py --verify`  | 2026-05-28 | Flagged 3 fields stale (#902 Class A); clean after fix               |

## Findings

Physical-spec correction (#902, Class A — small staleness deltas; official page
authoritative per the source-conflict rule):

- **filterThread:** 52 → **55** mm
- **length:** 76.5 → **74.5** mm
- **minFocusDistance:** 124 → **121** mm

No genre-mark change. Optical/scoring fields untouched.
