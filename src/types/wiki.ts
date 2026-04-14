// =============================================================================
// WIKI ENTRY
// =============================================================================

interface WikiEntry {
  /** URL slug — lowercase, hyphenated (e.g. "bortle-scale") */
  slug: string;

  /** Display title (e.g. "Bortle Scale") */
  title: string;

  /** One-line summary for index page and meta description */
  summary: string;

  /** Full article body in plain text paragraphs */
  body: string[];

  /** Related wiki slugs for cross-linking */
  related?: string[];
}

// =============================================================================
// EXPORTS
// =============================================================================

export type { WikiEntry };
