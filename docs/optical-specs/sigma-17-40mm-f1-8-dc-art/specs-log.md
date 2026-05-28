# Sigma 17-40mm f/1.8 DC Art — Specs Log

## Sources checked

| Source           | URL                                       | Date       | Result                                                                                                          |
| ---------------- | ----------------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------- |
| Official (Sigma) | sigma-global.com/en/lenses/a025_17_40_18/ | 2026-05-28 | Found: 17 elements / 11 groups (4 SLD, 4 aspherical); 11 rounded blades; φ72.9 × 115.9mm; 535g; MFD 28cm; 1:4.8 |
| `--verify` tool  | `py tools/sigma/fetch_specs.py --verify`  | 2026-05-28 | Flagged 5 physical fields divergent (#902 Class A); clean after fix                                             |

## Findings

Physical-spec correction (#902). Official page confirmed same lens (17-40mm
F1.8, 17/11, 4 SLD + 4 aspherical — matches stored optical block). Physical
fields overwritten with official values per the source-conflict rule:

- **apertureBlades:** 7 → **11** (official "11 rounded diaphragm")
- **length:** 89.5 → **115.9** mm (official φ72.9 × 115.9)
- **diameter:** 72.2 → **72.9** mm (official; read directly from the live page)
- **weight:** 510 → **535** g (official L-mount weight)
- **minFocusDistance:** 300 → **280** mm (official 28cm)
- **maxMagnification:** 0.18 → **0.208** (official ratio 1:4.8 = 0.208)

## Caveats

- The large length delta (89.5 → 115.9) and blade-count change (7 → 11) were
  cross-checked against the live official page before applying — confirmed not a
  wrong-lens entry; the optical block matches exactly.
- `--verify` clean after the fix.
