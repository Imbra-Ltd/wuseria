# Samyang 85mm f/1.4 AS IF UMC -- MTF Chart Analysis

Source: [Official Samyang product page](https://www.lksamyang.com/en/product/product-view.php?seq=311)
Image: [samyang-85mm-f1-4-as-if-umc-mtf.png](samyang-85mm-f1-4-as-if-umc-mtf.png)

## Chart legend

- FF lens
- Solid dark = Sagittal (S), Solid light = Meridional (M)
- Red lines = 10 lp/mm (contrast), Grey lines = 30 lp/mm (resolution)
- X-axis: distance from center of frame (mm), Y-axis: contrast (0-1)
- Two charts: MAX. aperture (f/1.4) and F8

## Readings -- MAX. aperture (f/1.4)

| Position | 10 lp/mm S | 10 lp/mm M | 30 lp/mm S | 30 lp/mm M |
| -------- | ---------- | ---------- | ---------- | ---------- |
| Center   | ~0.90      | ~0.90      | ~0.70      | ~0.65      |
| 5mm      | ~0.90      | ~0.95      | ~0.65      | ~0.60      |
| 10mm     | ~0.90      | ~0.97      | ~0.63      | ~0.55      |
| 15mm     | ~0.92      | ~0.95      | ~0.57      | ~0.55      |
| 21mm     | ~0.75      | ~0.90      | ~0.52      | ~0.50      |

## Readings -- F8

| Position | 10 lp/mm S | 10 lp/mm M | 30 lp/mm S | 30 lp/mm M |
| -------- | ---------- | ---------- | ---------- | ---------- |
| Center   | ~1.00      | ~1.00      | ~0.95      | ~0.95      |
| 10mm     | ~1.00      | ~0.99      | ~0.97      | ~0.90      |
| 15mm     | ~1.00      | ~0.97      | ~0.90      | ~0.72      |
| 21mm     | ~0.97      | ~0.90      | ~0.53      | ~0.50      |

## Astigmatism assessment

S/M divergence at 30 lp/mm:

FF lens. 10 lp/mm: M rises above S at edge (crossing). 30 lp/mm: both drop with moderate gap. At f/8: heavy divergence at FF edge. LensTip lab measured 10.4% (1.0).

**Score: 1.0 (moderate-heavy; lab data: 1.0 -- consistent)**

## Known extraction limitation (#1282)

The digitized M curves in the shipped SVG follow the wrong shape in the mid-field on the MAX panel: gold dashed freq10M tracks red S10 from ~0-15mm before jumping to actual pink at the edge; blue dashed freq30M traces the dark-grey S30 dip-and-recover at ~7-15mm instead of the smooth light-grey M30 descent. Mechanism is halo subtraction (ADR-059, ADR-062) erasing legitimate M pixels where S/M overlap vertically, with sister fallback copying S values. All 22 paired calibration cells stay within ±0.05 tolerance because the coarse 11-point sampling happens to land where S/M magnitudes are numerically close. Tracked in #1282.
