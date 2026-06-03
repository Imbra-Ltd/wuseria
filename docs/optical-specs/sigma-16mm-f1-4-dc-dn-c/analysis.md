# Sigma 16mm f/1.4 DC DN C — MTF Chart Analysis

Source: [Official Sigma product page](https://www.sigma-global.com/en/lenses/c017_16_14/)
MTF charts:

- [sigma-16mm-f1-4-dc-dn-c-mtf-diffraction.png](sigma-16mm-f1-4-dc-dn-c-mtf-diffraction.png) — diffraction MTF
- [sigma-16mm-f1-4-dc-dn-c-mtf-geometric.png](sigma-16mm-f1-4-dc-dn-c-mtf-geometric.png) — geometrical MTF

## Chart legend

- At 16mm focal length
- Solid = Sagittal (S), Dashed = Meridional (M)
- Red lines = 10 lp/mm (contrast), Blue lines = 30 lp/mm (resolution)
- X-axis: image height (mm), Y-axis: contrast (0–1)

## Readings

| Position | 10 lp/mm S | 10 lp/mm M | 30 lp/mm S | 30 lp/mm M |
| -------- | ---------- | ---------- | ---------- | ---------- |
| Center   | 0.96       | 0.96\*     | 0.81       | 0.79\*     |
| 2.5mm    | 0.96       | 0.96\*     | 0.82       | 0.79       |
| 5mm      | 0.96       | 0.96\*     | 0.82       | 0.77       |
| 7.5mm    | 0.96       | 0.96\*     | 0.78       | 0.74       |
| 10mm     | 0.93       | 0.95       | 0.68       | 0.72       |
| 12.5mm   | 0.83       | 0.93       | 0.59       | 0.64       |
| 14mm     | 0.71       | 0.89       | 0.50       | 0.56       |

Note: Values extracted by pixel scanning (tools/mtf-extract-sigma.py),
calibrated against chart gridlines. \* = M interpolated (dashed line merged
with S at scan position). S/M identity assigned by curve-following gap detection.

## Astigmatism assessment

S/M divergence at 30 lp/mm:

- Center to ~7.5mm: S above M, gap ~0.03-0.05
- M crosses above S between 7.5-10mm
- 10-16mm edge: moderate divergence (M > S), gap ~0.03-0.04
- 10 lp/mm lines show same crossing pattern, gap grows to ~0.04 at edge

**Scoring:** Moderate divergence at edges → **1.5**

Note: LensTip lab review already provides astigmatism: 1.0 (from measured data). Lab data takes precedence.
