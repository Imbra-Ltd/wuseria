import type { Genre } from "./genre";
import type { Brand, Mount } from "./common";

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

export type { GenreLens };
