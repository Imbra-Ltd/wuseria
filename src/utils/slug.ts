/**
 * Convert a model name to a URL slug.
 * "XF 23mm f/1.4" → "xf-23mm-f1-4"
 */
function toSlug(model: string): string {
  return model
    .toLowerCase()
    .replaceAll("/", "")
    .replaceAll(/[^a-z0-9]+/g, "-")
    .replaceAll(/(^-|-$)/g, "");
}

// Mirror of brandkit's `slug_prefix` overrides (ADR-056). Most brands
// slug as `toSlug(brand)`, but a few diverge: brandkit's Python tooling
// writes `docs/optical-specs/<slug>` paths (and mtf-readings keys
// follow them) using these prefixes. Only divergences belong here.
const BRAND_SLUG_OVERRIDE: Record<string, string> = {
  "Carl Zeiss": "Zeiss",
};

/**
 * Data-side slug for a lens: keys `mtfReadings` and names the
 * `docs/optical-specs/<slug>` directory. Diverges from the page-URL
 * slug (`toSlug(brand + " " + model)`) for brands with an ADR-056
 * override — e.g. "Carl Zeiss" pages live at `carl-zeiss-*` while
 * their data slugs are `zeiss-*`.
 */
function toDataSlug(brand: string, model: string): string {
  const dirBrand = BRAND_SLUG_OVERRIDE[brand] ?? brand;
  return toSlug(`${dirBrand} ${model}`);
}

export { toSlug, toDataSlug };
