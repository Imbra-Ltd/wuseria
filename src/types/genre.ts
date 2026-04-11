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

// Genres with scoring data implemented so far
type ScoredGenre = Exclude<Genre, "macro">;

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
