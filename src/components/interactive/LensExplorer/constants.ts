import type { ColumnDef } from "../shared/table";

interface ExplorerLens {
  brand: string;
  model: string;
  year?: number;
  mount: string;
  type: "prime" | "zoom";
  focalLengthMin: number;
  focalLengthMax: number;
  maxAperture: number;
  filterThread?: number;
  hasOis?: boolean;
  isWeatherSealed?: boolean;
  afMotor?: string;
  weight: number;
  price: number;
  isDiscontinued?: boolean;
  opticalQuality?: number | null;
}

interface LensExplorerProps {
  lenses: ExplorerLens[];
}

type LensSortKey =
  | "brand"
  | "model"
  | "year"
  | "focalLengthMin"
  | "maxAperture"
  | "filterThread"
  | "hasOis"
  | "isWeatherSealed"
  | "afMotor"
  | "weight"
  | "opticalQuality"
  | "price";

const COLUMNS: ColumnDef<LensSortKey>[] = [
  { key: "brand", label: "Brand", align: "left", width: "9%" },
  { key: "model", label: "Model", align: "left", width: "20%" },
  { key: "year", label: "Year", align: "left", width: "6%" },
  { key: "focalLengthMin", label: "FL", align: "right", width: "7%" },
  { key: "maxAperture", label: "f/", align: "right", width: "5%" },
  { key: "filterThread", label: "\u03A6", align: "right", width: "5%" },
  { key: "hasOis", label: "OIS", align: "center", width: "5%" },
  { key: "isWeatherSealed", label: "WR", align: "center", width: "5%" },
  { key: "afMotor", label: "AF", align: "center", width: "6%" },
  { key: "weight", label: "Weight", align: "right", width: "8%" },
  { key: "opticalQuality", label: "OQ", align: "right", width: "6%" },
  { key: "price", label: "Price", align: "right", width: "8%" },
];

const INITIAL_PAGE_SIZE = 50;

const APERTURE_OPTIONS = [
  "0.95",
  "1.0",
  "1.2",
  "1.4",
  "1.8",
  "2.0",
  "2.8",
  "3.5",
  "4.0",
  "4.5",
  "5.6",
  "6.3",
  "8.0",
];
const FILTER_THREAD_OPTIONS = [
  "39",
  "43",
  "46",
  "49",
  "52",
  "55",
  "58",
  "62",
  "67",
  "72",
  "77",
  "82",
  "95",
  "none",
];

const FL_RANGES: Record<string, [number, number]> = {
  "0-14": [0, 14],
  "15-23": [15, 23],
  "24-35": [24, 35],
  "36-100": [36, 100],
  "101-300": [101, 300],
  "300+": [300, Infinity],
};

const OQ_RANGES: Record<string, [number, number]> = {
  "1.5+": [1.5, 2],
  "1.0-1.4": [1.0, 1.4],
  "0.5-0.9": [0.5, 0.9],
  "0-0.4": [0, 0.4],
};

const PRICE_RANGES: Record<string, [number, number]> = {
  "0-250": [0, 250],
  "250-500": [250, 500],
  "500-1000": [500, 1000],
  "1000-2000": [1000, 2000],
  "2000+": [2000, Infinity],
};

export type { ExplorerLens, LensExplorerProps, LensSortKey };
export {
  COLUMNS,
  INITIAL_PAGE_SIZE,
  APERTURE_OPTIONS,
  FILTER_THREAD_OPTIONS,
  FL_RANGES,
  OQ_RANGES,
  PRICE_RANGES,
};
