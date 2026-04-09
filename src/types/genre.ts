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

// =============================================================================
// SCORE RESULT
// =============================================================================

type ScoreBreakdown = Record<string, number>;

interface ScoreResult {

  // 1–5 in 0.5 steps
  mark: number;

  // Per-criterion scores for transparency
  breakdown: ScoreBreakdown;

  isDisqualified: boolean;
  reason?: string;
}

// =============================================================================
// EXPORTS
// =============================================================================

export type { Genre, ScoreResult, ScoreBreakdown };
