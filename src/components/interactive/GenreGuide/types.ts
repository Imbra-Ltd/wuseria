import type { Lens } from "../../../types/lens";
import type { ScoredGenre } from "../../../types/genre";

interface GenreGuideProps {
  lenses: Lens[];
  defaultGenre?: ScoredGenre;
}

type SortKey =
  | "mark" | "brand" | "idealIso" | "weight" | "price"
  | "fl" | "aperture" | "rule500" | "coma" | "astigmatism" | "wr"
  | "ois" | "cornerStopped" | "centerStopped" | "centerWideOpen"
  | "distortion" | "flareResistance" | "bokeh" | "longitudinalCA"
  | "lateralCA" | "magnification";

interface EnrichedLens {
  lens: Lens;
  mark: number;
  isPick: boolean;
  idealIso: number | null;
  rule500: number | null;
  effectiveFl: number;
}

const SCORED_GENRES: ScoredGenre[] = [
  "nightscape", "landscape", "architecture", "street",
  "travel", "portrait", "sport", "wildlife", "macro",
];

export type { GenreGuideProps, SortKey, EnrichedLens };
export { SCORED_GENRES };
