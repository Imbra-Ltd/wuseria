import type { Lens } from "../types/lens";
import type { Genre, ScoredGenre } from "../types/genre";
import { genreConfigs } from "../data/genres";

// =============================================================================
// OPTICAL FIELD NAMES
// =============================================================================

const OPTICAL_FIELDS = [
  "centerStopped",
  "cornerStopped",
  "centerWideOpen",
  "cornerWideOpen",
  "astigmatism",
  "coma",
  "sphericalAberration",
  "longitudinalCA",
  "lateralCA",
  "distortion",
  "vignettingWideOpen",
  "vignettingStopped",
  "bokeh",
  "flareResistance",
] as const;

type OpticalField = (typeof OPTICAL_FIELDS)[number];

// Derived fields computed from lens specs, prefixed with _
type DerivedField = "_apertureScore" | "_weightScore" | "_magnificationScore";

type ScoringField = OpticalField | DerivedField;

const MIN_OPTICAL_FIELDS = 7; // 50% of 14

// =============================================================================
// GENRE FORMULA DEFINITIONS
// =============================================================================

interface GenreFormula {
  primary: ScoringField[];
  secondary: ScoringField[];
}

const genreFormulas: Record<ScoredGenre, GenreFormula> = {
  nightscape: {
    primary: ["coma", "astigmatism", "_apertureScore"],
    secondary: [
      "lateralCA",
      "centerWideOpen",
      "cornerWideOpen",
      "longitudinalCA",
      "vignettingWideOpen",
      "sphericalAberration",
    ],
  },
  landscape: {
    primary: ["cornerStopped", "centerStopped"],
    secondary: [
      "distortion",
      "lateralCA",
      "longitudinalCA",
      "vignettingStopped",
      "flareResistance",
      "astigmatism",
      "coma",
    ],
  },
  architecture: {
    primary: ["cornerStopped", "centerStopped", "distortion"],
    secondary: ["lateralCA", "vignettingStopped", "flareResistance"],
  },
  portrait: {
    primary: ["bokeh", "centerWideOpen"],
    secondary: [
      "longitudinalCA",
      "sphericalAberration",
      "vignettingWideOpen",
    ],
  },
  street: {
    primary: ["centerStopped", "_apertureScore"],
    secondary: [
      "centerWideOpen",
      "flareResistance",
      "longitudinalCA",
      "coma",
    ],
  },
  travel: {
    primary: ["centerStopped", "_weightScore"],
    secondary: ["_apertureScore", "flareResistance", "longitudinalCA"],
  },
  sport: {
    primary: ["centerWideOpen"],
    secondary: ["_apertureScore", "longitudinalCA", "lateralCA"],
  },
  wildlife: {
    primary: ["centerWideOpen", "centerStopped"],
    secondary: ["_apertureScore", "longitudinalCA", "lateralCA"],
  },
  macro: {
    primary: ["centerStopped", "_magnificationScore"],
    secondary: [
      "distortion",
      "lateralCA",
      "longitudinalCA",
      "sphericalAberration",
      "bokeh",
    ],
  },
};

// =============================================================================
// PHYSICAL PROPERTY SCORES
// =============================================================================

const W_PRIMARY = 3;
const W_SECONDARY = 1;

function apertureScore(maxAperture: number): number {
  if (maxAperture <= 1.4) return 2.0;
  if (maxAperture <= 2.0) return 1.5;
  if (maxAperture <= 2.8) return 1.0;
  if (maxAperture <= 4.0) return 0.5;
  return 0.0;
}

function weightScore(grams: number): number {
  if (grams < 200) return 2.0;
  if (grams <= 400) return 1.5;
  if (grams <= 700) return 1.0;
  if (grams <= 1000) return 0.5;
  return 0.0;
}

function magnificationScore(maxMagnification: number): number {
  if (maxMagnification >= 1.0) return 2.0;
  if (maxMagnification >= 0.5) return 1.5;
  if (maxMagnification >= 0.25) return 1.0;
  if (maxMagnification >= 0.15) return 0.5;
  return 0.0;
}

// =============================================================================
// SCORING ENGINE
// =============================================================================

/** Resolve a field value from the lens, computing derived fields as needed. */
function resolveField(lens: Lens, field: ScoringField): number | undefined {
  switch (field) {
    case "_apertureScore":
      return apertureScore(lens.maxAperture);
    case "_weightScore":
      return weightScore(lens.weight);
    case "_magnificationScore":
      return lens.maxMagnification != null
        ? magnificationScore(lens.maxMagnification)
        : undefined;
    default:
      return lens[field];
  }
}

/** Count how many of the 14 optical fields are populated. */
function opticalFieldCount(lens: Lens): number {
  return OPTICAL_FIELDS.filter((f) => lens[f] != null).length;
}

/**
 * Map a 0–2 capped value to a 1–5 mark in 0.5 steps.
 *
 * 0 → 1, 0.25 → 1.5, 0.5 → 2, 0.75 → 2.5, 1.0 → 3,
 * 1.25 → 3.5, 1.5 → 4, 1.75 → 4.5, 2.0 → 5
 */
function toMark(capped: number): number {
  return Math.min(5, Math.max(1, Math.round(capped * 4) / 2 + 1));
}

interface ScoreResult {
  mark: number;
  raw: number;
  floor: number;
  capped: number;
}

/**
 * Compute the genre mark for a lens using the primary floor + weighted
 * average algorithm. Returns null if the lens lacks sufficient data.
 */
function computeGenreMark(
  lens: Lens,
  genre: ScoredGenre,
): ScoreResult | null {
  // Must have optical data at all
  if (lens.centerStopped == null) return null;

  const formula = genreFormulas[genre];

  // All primary fields must be present
  const primaryValues: number[] = [];
  for (const field of formula.primary) {
    const value = resolveField(lens, field);
    if (value == null) return null;
    primaryValues.push(value);
  }

  // 50% optical field threshold
  if (opticalFieldCount(lens) < MIN_OPTICAL_FIELDS) return null;

  // Weighted average: primary (w=3) + available secondary (w=1)
  let sumW = 0;
  let sumWV = 0;

  for (let i = 0; i < formula.primary.length; i++) {
    sumW += W_PRIMARY;
    sumWV += W_PRIMARY * primaryValues[i];
  }

  for (const field of formula.secondary) {
    const value = resolveField(lens, field);
    if (value != null) {
      sumW += W_SECONDARY;
      sumWV += W_SECONDARY * value;
    }
  }

  const raw = sumWV / sumW;
  const floor = Math.min(...primaryValues);
  const capped = Math.min(raw, floor);
  const mark = toMark(capped);

  return { mark, raw, floor, capped };
}

/**
 * Compute genre marks for all genres that a lens qualifies for.
 * Returns a partial record of genre → mark.
 */
function computeAllGenreMarks(
  lens: Lens,
): Partial<Record<ScoredGenre, number>> {
  const marks: Partial<Record<ScoredGenre, number>> = {};
  for (const genre of Object.keys(genreFormulas) as ScoredGenre[]) {
    const result = computeGenreMark(lens, genre);
    if (result != null) {
      marks[genre] = result.mark;
    }
  }
  return marks;
}

// =============================================================================
// GENRE MARK LOOKUP (from pre-computed genreMarks on Lens)
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
    .sort((a, b) => b.genreMarks![genre]! - a.genreMarks![genre]!);
}

/** Check whether a genre has scoring data. */
function isScoredGenre(genre: Genre): genre is ScoredGenre {
  return genre in genreConfigs;
}

// =============================================================================
// OVERALL OPTICAL QUALITY — genre-usage-derived weights
// =============================================================================

const OPTICAL_WEIGHTS: Record<OpticalField, number> = {
  centerStopped: 4,
  centerWideOpen: 3,
  longitudinalCA: 2,
  lateralCA: 1.5,
  cornerStopped: 1.5,
  coma: 1.5,
  distortion: 1,
  astigmatism: 1,
  flareResistance: 1,
  bokeh: 1,
  sphericalAberration: 0.5,
  vignettingWideOpen: 0.5,
  vignettingStopped: 0.5,
  cornerWideOpen: 0.5,
};

/**
 * Compute an overall optical quality score (0–10) from a weighted average
 * of available optical fields. Returns null if fewer than 7 fields present.
 *
 * Weights are derived from genre formula usage: fields that appear as primary
 * in more genres get higher weight, so lenses that perform well across many
 * genres score higher.
 */
function computeOpticalQuality(lens: Lens): number | null {
  if (opticalFieldCount(lens) < MIN_OPTICAL_FIELDS) return null;

  let sumW = 0;
  let sumWV = 0;

  for (const field of OPTICAL_FIELDS) {
    const val = lens[field];
    if (val == null) continue;
    const w = OPTICAL_WEIGHTS[field];
    sumW += w;
    sumWV += w * val;
  }

  if (sumW === 0) return null;

  // Weighted average is 0–2, scale to 0–10
  const avg = sumWV / sumW;
  return Math.round(avg * 5 * 10) / 10;
}

// =============================================================================
// EXPORTS
// =============================================================================

export {
  // Scoring engine
  computeGenreMark,
  computeAllGenreMarks,
  toMark,
  apertureScore,
  weightScore,
  magnificationScore,
  resolveField,
  opticalFieldCount,
  genreFormulas,
  OPTICAL_FIELDS,
  OPTICAL_WEIGHTS,
  MIN_OPTICAL_FIELDS,
  // Overall optical quality
  computeOpticalQuality,
  // Lookup helpers
  getGenreMark,
  isEditorialPick,
  lensesForGenre,
  isScoredGenre,
};

export type { ScoreResult, GenreFormula, ScoringField, OpticalField };
