# Sigma 15mm f/1.4 DC DN C — Specs Log

## Sources checked

| Source           | URL                                      | Date       | Result                                                                                             |
| ---------------- | ---------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------- |
| Official (Sigma) | sigma-global.com/en/lenses/c026_15_14/   | 2026-05-28 | Found: 13 elements / 11 groups (1 FLD, 3 SLD, 3 aspherical); filter φ58mm; weight 240g; MFD 17.7cm |
| `--verify` tool  | `py tools/sigma/fetch_specs.py --verify` | 2026-05-28 | Flagged 5 physical fields divergent (#902 Class B); clean after fix                                |

## Findings

Physical-spec correction (#902). The stored **optical** block (13 elements /
11 groups, 1 FLD + 3 SLD + 3 aspherical) **exactly matches** the official
`c026_15_14` page — title "15mm F1.4 DC", same construction — so it is confirmed
the same lens; only the physical block had been entered from a different lens.
Per the CLAUDE.md source-conflict rule, the physical block was overwritten with
the official values:

- **weight:** 420 → **240** g (official)
- **diameter:** 73.4 → **69.0** mm (official)
- **length:** 81 → **62.8** mm (official)
- **filterThread:** 67 → **58** mm (official φ58mm)
- **minFocusDistance:** 250 → **177** mm (official 17.7cm)

Downstream genre recompute: `travel` 3 → 4 (lighter).

## Caveats

- Optical/scoring fields untouched — already correct, confirmed by the matching
  official construction (13/11, 1 FLD / 3 SLD / 3 aspherical).
- `--verify` clean after the fix.
