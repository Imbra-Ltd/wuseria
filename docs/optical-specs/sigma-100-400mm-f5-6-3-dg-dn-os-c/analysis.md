# Sigma 100-400mm f/5-6.3 DG DN OS C — MTF Chart Analysis

Source: [Official Sigma product page](https://www.sigma-global.com/en/lenses/c020_100_400_5_63/)

MTF charts:

- [sigma-100-400mm-f5-6-3-dg-dn-os-c-mtf-diffraction-wide.png](sigma-100-400mm-f5-6-3-dg-dn-os-c-mtf-diffraction-wide.png) — diffraction MTF (wide)
- [sigma-100-400mm-f5-6-3-dg-dn-os-c-mtf-diffraction-tele.png](sigma-100-400mm-f5-6-3-dg-dn-os-c-mtf-diffraction-tele.png) — diffraction MTF (tele)
- [sigma-100-400mm-f5-6-3-dg-dn-os-c-mtf-geometric-wide.png](sigma-100-400mm-f5-6-3-dg-dn-os-c-mtf-geometric-wide.png) — geometrical MTF (wide)
- [sigma-100-400mm-f5-6-3-dg-dn-os-c-mtf-geometric-tele.png](sigma-100-400mm-f5-6-3-dg-dn-os-c-mtf-geometric-tele.png) — geometrical MTF (tele)

## Chart provenance

Sigma publishes 16 MTF charts for this lens, covering four configurations
(bare lens on L/Sony full-frame, +TC-1411 1.4x, +TC-2011 2x, and a
dedicated Fujifilm X-mount set), each as a wide + tele pair, in both
diffraction and geometrical variants. Source page order:

| Source slot       | Configuration           | Variant         | End             |
| ----------------- | ----------------------- | --------------- | --------------- |
| 02_01 / 02_02     | bare L+Sony FF          | diffraction     | wide / tele     |
| 02_03 / 02_04     | bare L+Sony FF          | geometrical     | wide / tele     |
| 02_05 / 02_06     | +TC-1411 (L-mount only) | diffraction     | wide / tele     |
| 02_07 / 02_08     | +TC-1411 (L-mount only) | geometrical     | wide / tele     |
| 02_09 / 02_10     | +TC-2011 (L-mount only) | diffraction     | wide / tele     |
| 02_11 / 02_12     | +TC-2011 (L-mount only) | geometrical     | wide / tele     |
| **02_13 / 02_14** | **Fujifilm X mount**    | **diffraction** | **wide / tele** |
| **02_15 / 02_16** | **Fujifilm X mount**    | **geometrical** | **wide / tele** |

Wuseria is X-mount only. The four files in this folder are the Fujifilm
X-mount set (`02_13`–`02_16`). The other twelve charts (L+Sony FF and the
two L-mount-only teleconverter variants) were deleted in #1032 — they
are not used by any scoring on this site. The Sigma TC-1411 / TC-2011
teleconverters are L-mount only per the source page, so the X-mount
edition of this lens has no TC charts to rate against in any case.

## Chart legend

- At 100mm focal length (wide end) — Fujifilm X mount APS-C image circle
- Solid = Sagittal (S), Dashed = Meridional (M)
- Red lines = 10 lp/mm (contrast), Blue lines = 30 lp/mm (resolution)
- X-axis: image height (mm), Y-axis: contrast (0–1)

## Readings

> **Stale (2026-06-03):** the readings below were extracted from the
> bare full-frame wide-end chart (0–22mm image height). The canonical
> chart for this folder is now the Fujifilm X mount wide-end diffraction
> chart (0–14mm image height). Re-extract before relying on these
> values for scoring. Tracked by #793.

| Position | 10 lp/mm S | 10 lp/mm M | 30 lp/mm S | 30 lp/mm M |
| -------- | ---------- | ---------- | ---------- | ---------- |
| Center   | ~0.94      | ~0.93      | ~0.79      | ~0.78      |
| 5mm      | ~0.94      | ~0.93      | ~0.79      | ~0.78      |
| 10mm     | ~0.94      | ~0.94      | ~0.80      | ~0.78      |
| 15mm     | ~0.93      | ~0.91      | ~0.71      | ~0.68      |
| 20mm     | ~0.91      | ~0.88      | ~0.58      | ~0.45      |

## Astigmatism assessment

S/M divergence at 30 lp/mm (from the stale full-frame readings; re-check
once the X-mount chart is digitized):

- Center to ~10mm: S and M nearly overlapping, gap < 0.02
- 15mm: moderate divergence begins, gap ~0.03
- 20mm+: significant divergence, gap ~0.13-0.15
- 10 lp/mm lines show similar pattern but less pronounced

**Scoring:** Moderate-to-heavy divergence at edges → **1.0**
