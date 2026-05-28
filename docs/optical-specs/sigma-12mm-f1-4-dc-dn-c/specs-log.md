# Sigma 12mm f/1.4 DC DN C — Specs Log

## Sources checked

| Source           | URL                                      | Date       | Result                                                                                               |
| ---------------- | ---------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------- |
| Official (Sigma) | sigma-global.com/en/lenses/c025_12_14/   | 2026-05-28 | Found: 14 elements / 12 groups (2 SLD, 3 aspherical); filter φ62mm; weight 250g; MFD 17cm; mag 1:8.4 |
| `--verify` tool  | `py tools/sigma/fetch_specs.py --verify` | 2026-05-28 | Flagged 6 physical fields divergent (#902 Class B); clean after fix                                  |

## Findings

Physical-spec correction (#902). The stored **optical** block (14 elements /
12 groups, 2 SLD + 3 aspherical) **exactly matches** the official page, so the
official `c025_12_14` page is confirmed the same lens — only the physical block
had been entered from a different lens. Per the CLAUDE.md source-conflict rule
(official manufacturer page wins), the physical block was overwritten with the
official values:

- **weight:** 520 → **250** g (official; the 520 was wrong-lens data)
- **diameter:** 72.2 → **69.0** mm (official)
- **length:** 87 → **67.4** mm (official)
- **filterThread:** 72 → **62** mm (official φ62mm)
- **minFocusDistance:** 240 → **172** mm (official 17.2cm)
- **maxMagnification:** 0.19 → **0.119** (official; was wrong-lens data)

Downstream genre recompute (stored to match `computeAllGenreMarks`): `travel`
3 → 4 (lighter), `macro` 2 → 1 (lower magnification).

## Caveats

- Optical/scoring fields were not touched — they were already correct and
  confirmed by the matching official construction (14/12, 2 SLD, 3 aspherical).
- `--verify` is clean after the fix (11/11 Sigma lenses pass).
