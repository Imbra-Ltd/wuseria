# 7Artisans 10mm f/2.8 AF — Specs Log

## Sources checked

| Source              | URL                                                         | Date       | Result                                                                                 |
| ------------------- | ----------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------- |
| Official (Shopify)  | 7artisans.store/products/af-10mm-f2-8-aps-c-lens-for-e-fx-z | 2026-05-27 | Found: 11 elements / 10 groups, ED + HR + aspherical glass                             |
| LensTip             | lenstip.com                                                 | 2026-05-27 | Not listed                                                                             |
| Radojuva            | radojuva.com                                                | 2026-05-27 | Not found                                                                              |
| DPReview            | dpreview.com                                                | 2026-05-27 | Not listed                                                                             |
| Google Image Search | google.com                                                  | 2026-05-27 | Diagram + MTF found embedded in official composite marketing images; cropped and saved |

## Findings

- **opticalElements:** 11 (official spec table: "Optical Structure: 11 elements in 10 groups")
- **opticalGroups:** 10 (official)
- **specialElements:** aspherical, ED, HR (official construction diagram legend names three
  glass types: "Extra-low Dispersion Element", "High Refraction Element",
  "Aspherie [Aspherical] Lens"). Recorded qualitatively — see caveat.
- **coating:** none stated (no coating named on page; product copy references "advanced
  nano-coating" on the related AF 27mm but not on this 10mm page)
- **maxMagnification:** not found (official states MFD 0.3m only — not estimated per project rule)
- **constructionDiagram:** found — `construction-diagram.jpg` (official, saved this PR)
- **MTF chart:** found — `mtf-chart.jpg` (official; OTF vs Y-field 0–14.2mm, T1-T3 / S1-S3. NOTE: the official page swaps the labels — the file captioned "AF/MF Switch Button" is the real MTF, the one captioned "MTF" is the construction diagram.)

## Caveats

- The official construction diagram color-codes the three glass types (yellow = ED,
  blue = HR, red = aspherical) but does NOT print numeric per-type counts. Exact counts
  (e.g. "2 ED, 2 HR, 3 aspherical") are not published, so `specialElements` is recorded
  qualitatively as the three glass types present rather than with counts.
- This is the only AF lens in the 7Artisans X-mount lineup (STM stepper motor).
- Construction diagram / MTF were published only inside composite marketing images
  (generic filenames); recovered by visual inspection per PLAYBOOK 2.8 and cropped to
  separate artifacts. Earlier pass wrongly reported "not found".
