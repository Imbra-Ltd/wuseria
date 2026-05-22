# Nokton 50mm f/1.2 — Notes

## MTF chart search (2026-05-22)

No MTF chart found from any source.

### Sources checked

- **cosina.co.jp product page (X-mount)** — construction diagram only, no MTF
  - URL: https://www.cosina.co.jp/voigtlander/x-mount/nokton-50mm-f1-2/
- **cosina.co.jp product page (E-mount)** — construction diagram only, no MTF
  - Confirmed: E-mount Nokton 50mm also has no MTF (while APO-LANTHAR 50mm F2 E-mount does)
- **Voigtlander catalog PDF** — construction diagram only, no MTF (pages 6, 14)
  - URL: https://www.cosina.co.jp/wp/wp-content/uploads/catalog/v-catalog.pdf
- **LensTip** — no review (as of 2026-05-22)
- **OpticalLimits** — page not found (404)
- **Dustin Abbott** — 404 on review URL
- **Phillip Reeve** — 404 on review URL
- **Radojuva** — announcement only

### Conclusion

Same Voigtlander policy: Noktons get no MTF, APO-LANTHARs do. Third-party measured MTF is the only path.

## Important: X-mount vs E-mount/VM are different designs

The X-mount Nokton 50mm f/1.2 is a **completely different lens** from the E-mount/VM version:

- X-mount: Sonnar-type, different element count and construction
- E-mount/VM: aspherical design, 8 elements in 6 groups

Reviews from other mounts **cannot be applied** to the X-mount version. This is a common buyer trap.

## Character lens classification

**Tier 1 purpose-built character lens.** The blueprint MTF analysis (temp/artisitc_blueprint_mtf.png) was modeled on this type of lens. Wide open shows high 10 lp/mm contrast but low 30 lp/mm microcontrast (glow signature), with strong S/T divergence in the transition field (swirl). Sharp when stopped down to f/5.6.

## Special elements (2026-05-21)

Added 2 atypical partial dispersion elements per Voigtlander catalog data (commit e1944c2).
