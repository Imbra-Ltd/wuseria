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

type ScoreBreakdown = Record<string, number>;

interface ScoreResult {

  /** 1–5 in 0.5 steps */
  mark: number;

  /** Per-criterion scores for transparency */
  breakdown: ScoreBreakdown;

  disqualified: boolean;
  reason?: string;
}

export type { Genre, ScoreResult, ScoreBreakdown };
