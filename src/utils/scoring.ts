import type { Lens } from "../types/lens";
import type { Genre, ScoredGenre } from "../types/genre";
import { genreConfigs } from "../data/genres";

// =============================================================================
// GENRE MARK LOOKUP
// =============================================================================

/** Get the genre mark for a lens. Returns null if not scored. */
function getGenreMark(lens: Lens, genre: ScoredGenre): number | null {
  return lens.genreMarks?.[genre] ?? null;
}

/** Is this lens an editorial pick for the genre? */
function isEditorialPick(lens: Lens, genre: ScoredGenre): boolean {
  return lens.editorialPicks?.includes(genre) ?? false;
}

/** All lenses scored for a genre, sorted by mark descending. */
function lensesForGenre(lenses: Lens[], genre: ScoredGenre): Lens[] {
  return lenses
    .filter((l) => l.genreMarks?.[genre] != null)
    .sort((a, b) => (b.genreMarks![genre]! - a.genreMarks![genre]!));
}

/** Check whether a genre has scoring data. */
function isScoredGenre(genre: Genre): genre is ScoredGenre {
  return genre in genreConfigs;
}

// =============================================================================
// EXPORTS
// =============================================================================

export {
  getGenreMark,
  isEditorialPick,
  lensesForGenre,
  isScoredGenre,
};
