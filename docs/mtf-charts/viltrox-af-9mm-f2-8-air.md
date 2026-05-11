# Viltrox AF 9mm f/2.8 Air — MTF Chart Analysis

Source: [Official Viltrox product page](https://viltrox.com/products/af-9mm-f2-8-xf)
Image: [viltrox-af-9mm-f2-8-air.jpg](viltrox-af-9mm-f2-8-air.jpg)

## Chart legend

- Black lines = f/2.8, Blue lines = f/8
- Solid = Sagittal (S), Dashed = Meridional (M)
- Thick lines = 10 lp/mm (contrast), Thin lines = 30 lp/mm (resolution)
- X-axis: distance from center (mm), Y-axis: MTF (0–1)

## Readings

### At f/2.8 (black)

| Position | 10 lp/mm S | 10 lp/mm M | 30 lp/mm S | 30 lp/mm M |
| -------- | ---------- | ---------- | ---------- | ---------- |
| Center   | ~0.97      | ~0.95      | ~0.83      | ~0.83      |
| 4mm      | ~0.96      | ~0.93      | ~0.82      | ~0.80      |
| 8mm      | ~0.93      | ~0.90      | ~0.73      | ~0.70      |
| 10mm     | ~0.88      | ~0.85      | ~0.65      | ~0.58      |
| 14mm     | ~0.80      | ~0.65      | ~0.48      | ~0.45      |

### At f/8 (blue)

| Position | 10 lp/mm S | 10 lp/mm M | 30 lp/mm S | 30 lp/mm M |
| -------- | ---------- | ---------- | ---------- | ---------- |
| Center   | ~0.95      | ~0.93      | ~0.83      | ~0.82      |
| 4mm      | ~0.95      | ~0.93      | ~0.82      | ~0.80      |
| 8mm      | ~0.93      | ~0.92      | ~0.80      | ~0.75      |
| 10mm     | ~0.92      | ~0.90      | ~0.78      | ~0.68      |
| 14mm     | ~0.88      | ~0.90      | ~0.75      | ~0.60      |

## Astigmatism assessment

S/M divergence at 30 lp/mm:

- **At f/2.8:** S and M closely matched center through midframe (gap <0.05).
  Divergence increases from ~8mm outward. At 14mm: S ~0.48, M ~0.45 —
  gap ~0.03. Moderate overall.
- **At f/8:** S and M closely matched in center. At 14mm edge: S ~0.75,
  M ~0.60 — gap ~0.15. More divergence at f/8 edges than f/2.8.

**Scoring:** Moderate divergence at edges, well matched center-to-midframe
→ **1.5**

Confirms Dustin Abbott's field assessment: "low astigmatism, sagittal and
meridional planes closely aligned."

Per ADR-014 MTF chart fallback:

- S/M nearly overlapping → 2.0
- Moderate divergence → 1.0–1.5
- Heavy divergence → 0–0.5
