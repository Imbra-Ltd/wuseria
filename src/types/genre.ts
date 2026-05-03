import type { FlCategory } from "./common";

// =============================================================================
// GENRE
// =============================================================================

type Genre =
  | "nightscape"
  | "portrait"
  | "landscape"
  | "sport"
  | "wildlife"
  | "street"
  | "travel"
  | "architecture"
  | "macro";

// =============================================================================
// GENRE CONFIG
// =============================================================================

interface GenreConfig {
  genre: Genre;
  name: string;
  tagline: string;
  description: string;
  typicalFl: FlCategory[];
}

// =============================================================================
// EXPORTS
// =============================================================================

export type { Genre, GenreConfig };
