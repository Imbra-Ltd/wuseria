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

/** Result of scoring a lens for a specific genre */
interface ScoreResult {
  mark: number;
  breakdown: Record<string, number>;
  disqualified: boolean;
  reason?: string;
}

export type { Genre, ScoreResult };
