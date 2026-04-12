import type { FlCategory } from "./common";

// =============================================================================
// GENRE
// =============================================================================

type Genre =
  | "astro"
  | "portrait"
  | "landscape"
  | "sport"
  | "wildlife"
  | "street"
  | "travel"
  | "architecture"
  | "macro";

// All genres now have scoring formulas
type ScoredGenre = Genre;

// =============================================================================
// GENRE CONFIG
// =============================================================================

interface GenreConfig {
  genre: ScoredGenre;
  name: string;
  tagline: string;
  description: string;
  typicalFl: FlCategory[];
}

// =============================================================================
// EXPORTS
// =============================================================================

export type {
  Genre,
  ScoredGenre,
  GenreConfig,
};
