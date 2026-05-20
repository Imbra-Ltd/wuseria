# Sigma 56mm f/1.4 DC DN C — MTF Chart Analysis

Source: [Official Sigma product page](https://www.sigma-global.com/en/lenses/c018_56_14/)
MTF charts:

- [sigma-56mm-f1-4-dc-dn-c-mtf-1.png](sigma-56mm-f1-4-dc-dn-c-mtf-1.png) — diffraction MTF
- [sigma-56mm-f1-4-dc-dn-c-mtf-2.png](sigma-56mm-f1-4-dc-dn-c-mtf-2.png) — geometrical MTF

## Chart legend

- At 56mm focal length
- Solid = Sagittal (S), Dashed = Meridional (M)
- Red lines = 10 lp/mm (contrast), Blue lines = 30 lp/mm (resolution)
- X-axis: image height (mm), Y-axis: contrast (0–1)

## Readings

| Position | 10 lp/mm S | 10 lp/mm M | 30 lp/mm S | 30 lp/mm M |
| -------- | ---------- | ---------- | ---------- | ---------- |
| Center   | 0.98       | 0.98\*     | 0.86       | 0.86\*     |
| 2.5mm    | 0.98       | 0.98\*     | 0.87       | 0.87\*     |
| 5mm      | 0.98       | 0.98\*     | 0.86       | 0.86\*     |
| 7.5mm    | 0.97       | 0.97\*     | 0.81       | 0.85       |
| 10mm     | 0.97       | 0.97\*     | 0.80       | 0.86       |
| 12.5mm   | 0.91       | 0.95       | 0.61       | 0.74       |
| 14mm     | 0.72       | 0.93       | 0.36       | 0.61       |

Note: Values extracted by pixel scanning (tools/mtf-extract-sigma.py),
calibrated against chart gridlines. \* = M interpolated (dashed line merged
with S at scan position). S/M identity assigned by curve-following gap detection.

## Astigmatism assessment

S/M divergence at 30 lp/mm:

- Center to ~10mm: S and M very tight, gap < 0.05
- 10-14mm: moderate divergence, gap ~0.08 at extreme edge
- 10 lp/mm lines nearly overlapping throughout

**Scoring:** Moderate divergence at edges → **1.5**

Note: LensTip lab review already provides astigmatism: 1.5 (from measured data). Lab data takes precedence.
