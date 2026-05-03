import type { Genre } from "../../../types/genre";
import type { Brand, Mount } from "../../../types/common";

interface GenreLens {
  brand: Brand;
  model: string;
  mount: Mount;
  type: "prime" | "zoom";
  focalLengthMin: number;
  focalLengthMax: number;
  maxAperture: number;
  sweetSpotAperture?: number;
  maxMagnification?: number;
  hasOis?: boolean;
  isWeatherSealed?: boolean;
  isDiscontinued?: boolean;
  weight: number;
  price: number;
  genreMarks?: Partial<Record<Genre, number>>;
  editorialPicks?: Genre[];
  centerStopped?: number;
  cornerStopped?: number;
  centerWideOpen?: number;
  astigmatism?: number;
  coma?: number;
  longitudinalCA?: number;
  lateralCA?: number;
  distortion?: number;
  bokeh?: number;
  flareResistance?: number;
}

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
