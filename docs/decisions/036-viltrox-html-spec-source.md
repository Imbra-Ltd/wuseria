# ADR-036: Viltrox specs sourced from theme HTML, not Shopify JSON

**Status:** Accepted
**Date:** 2026-05-28

## Context

Viltrox runs a Shopify storefront. The original `ViltroxExtractor`
(ADR-035) read specs from the Shopify product JSON API: `normalize_url`
appended `.json` to the product URL, and `extract_optical` parsed the
`product.body_html` field, which once held a small spec table.

Verifying `extract_physical` for Viltrox (#897, split out as #901) found
that Viltrox has since moved its specs. The `.json` endpoint's
`body_html` is now ~250–400 characters of marketing prose — no element
count, filter size, weight, blades, or magnification. The current
extractor only still passed its tests because its committed fixture was a
stale JSON capture from before the change; against live pages it returned
almost nothing.

The specs now live in a `<table>` rendered in the **theme HTML** of the
product page. This is the same split the image scraper already documented
(`download_images.py`, ADR-035): Shopify themes embed content that the
JSON API does not expose.

Two properties of the table complicate parsing:

- It lists **one value column per mount** the lens ships in, in **no
  fixed order** — e.g. `E / Z / XF` on the 27mm, `E / X / EF-M / Z` on
  the 33mm. The X-mount column is not at a fixed index.
- Labels and units **drift across product generations**: `Lens Size` vs
  `Outer Diameter Size`, `Filter Size` as `φ67mm` vs `Φ52` (lower/upper
  phi, with or without `mm`), `Number of Aperture Blades` vs `Aperture
Blades`, `Shooting Distance` vs `Focus Range`, `Max.Magnification`
  `0.15X` vs `0.1`.

## Decision

Re-source `ViltroxExtractor` from the Shopify JSON to the theme HTML
product page.

- `normalize_url` becomes identity — the `lenses.ts` Viltrox URLs are
  already the HTML page URLs (the image scraper fetches them directly).
- `_spec_rows` parses the spec `<table>` into `{label: value}`, selecting
  the **X-mount column** dynamically: it reads the `Mount Type` row, finds
  the cell containing `X-mount`, and uses that column index for every row.
  Single-value rows use their one value; with no `Mount Type` row the last
  column wins.
- `extract_optical` and `extract_physical` read from the table, using
  **synonym sets** per field to absorb label drift, and numeric parses
  that ignore the `Φ`/`φ` sign, the `≈`/`=` weight prefix, and a trailing
  `X` on magnification.
- Special-element counts are scanned **only in the product description
  block** (`.product__description` / `.rte`), never the full page. The
  766 KB theme page is full of CSS/JS hex (a color-scheme UUID ending
  `…b953ed` would otherwise read as `953 ED`). Most pages name no counts,
  so `[]` is the common, correct result.

## Alternatives considered

- **Keep the JSON source.** Rejected — the JSON no longer carries specs;
  the extractor would silently return nothing against live pages.
- **Hard-code the X-mount column index.** Rejected — the column order
  differs per lens; a fixed index reads the wrong mount's values.
- **Scan the whole page for special elements.** Rejected — produces
  garbage from CSS/JS hex (`953 ED`, `5 HR`). Scoping to the description
  block and accepting `[]` when no count is named is honest; missing is
  better than wrong.

## Consequences

- `extract_physical` works for Viltrox, verified live against all 13
  lenses (7 clean, 6 with stored-data divergences triaged into #902).
- The extractor reflects Viltrox's current site; the stale JSON fixture is
  removed in favour of two trimmed HTML fixtures covering both column
  orderings and the label/unit drift.
- Special-element counts are no longer extracted from Viltrox pages
  (they are not structurally present). Existing `specialElements` in
  `lenses.ts` are unaffected; future entries rely on review sources for
  this field, per the optical rubric.
- Viltrox is the only brand whose spec source is theme HTML rather than a
  structured page or API; the synonym-set + dynamic-column approach is
  contained in `ViltroxExtractor` and does not affect the brandkit
  contract.
