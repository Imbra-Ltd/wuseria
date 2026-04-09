/** Photography genre for scoring */
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

/** Per-criterion score (0–2) with the criterion name as key */
type ScoreBreakdown = Record<string, number>;

/** Result of scoring a lens for a specific genre */
interface ScoreResult {
  /** Final score, 1–5 in 0.5 steps */
  mark: number;
  /** Per-criterion scores for transparency */
  breakdown: ScoreBreakdown;
  /** Hard disqualifier triggered (e.g. wideOpenSharpness ≤ 1 for astro) */
  disqualified: boolean;
  /** Why disqualified */
  reason?: string;
}

export type { Genre, ScoreResult, ScoreBreakdown };
