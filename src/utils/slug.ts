/**
 * Convert a model name to a URL slug.
 * "XF 23mm f/1.4" → "xf-23mm-f1-4"
 */
function toSlug(model: string): string {
  return model
    .toLowerCase()
    .replace(/\//g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

export { toSlug };
