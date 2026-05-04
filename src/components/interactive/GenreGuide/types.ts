import type { Genre } from "../../../types/genre";
import type { GenreLens } from "../../../types/genre-lens";

interface GenreGuideProps {
  lenses: GenreLens[];
  defaultGenre?: Genre;
}

type SortKey =
  | "mark"
  | "brand"
  | "idealIso"
  | "weight"
  | "price"
  | "fl"
  | "aperture"
  | "rule500"
  | "coma"
  | "astigmatism"
  | "wr"
  | "ois"
  | "cornerStopped"
  | "centerStopped"
  | "centerWideOpen"
  | "distortion"
  | "flareResistance"
  | "bokeh"
  | "longitudinalCA"
  | "lateralCA"
  | "magnification";

interface EnrichedLens {
  lens: GenreLens;
  mark: number;
  isPick: boolean;
  idealIso: number | null;
  rule500: number | null;
  effectiveFl: number;
}

const SCORED_GENRES: Genre[] = [
  "nightscape",
  "landscape",
  "architecture",
  "street",
  "travel",
  "portrait",
  "sport",
  "wildlife",
  "macro",
];

export type { GenreLens, GenreGuideProps, SortKey, EnrichedLens };
export { SCORED_GENRES };
