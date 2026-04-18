import type { Lens } from "../../../types/lens";
import type { ColumnAlign } from "../shared/table";

interface ExplorerLens extends Lens {
  opticalQuality?: number | null;
}

interface LensExplorerProps {
  lenses: ExplorerLens[];
}

type LensSortKey =
  | "brand" | "model" | "year" | "focalLengthMin" | "maxAperture"
  | "filterThread" | "hasOis" | "isWeatherSealed" | "afMotor"
  | "weight" | "opticalQuality" | "price";

const COLUMNS: { key: LensSortKey; label: string; align: ColumnAlign }[] = [
  { key: "brand", label: "Brand", align: "left" },
  { key: "model", label: "Model", align: "left" },
  { key: "year", label: "Year", align: "left" },
  { key: "focalLengthMin", label: "FL", align: "right" },
  { key: "maxAperture", label: "f/", align: "right" },
  { key: "filterThread", label: "\u03A6", align: "right" },
  { key: "hasOis", label: "OIS", align: "center" },
  { key: "isWeatherSealed", label: "WR", align: "center" },
  { key: "afMotor", label: "AF", align: "center" },
  { key: "weight", label: "Weight", align: "right" },
  { key: "opticalQuality", label: "OQ", align: "right" },
  { key: "price", label: "Price", align: "right" },
];

const APERTURE_OPTIONS = ["0.95", "1.0", "1.2", "1.4", "1.8", "2.0", "2.8", "3.5", "4.0", "4.5", "5.6", "6.3", "8.0"];
const FILTER_THREAD_OPTIONS = ["39", "43", "46", "49", "52", "55", "58", "62", "67", "72", "77", "82", "95", "none"];

const FL_RANGES: Record<string, [number, number]> = {
  "0-14": [0, 14], "15-23": [15, 23], "24-35": [24, 35],
  "36-100": [36, 100], "101-300": [101, 300], "300+": [300, Infinity],
};

const OQ_RANGES: Record<string, [number, number]> = {
  "8+": [8, 10], "6-7.9": [6, 7.9], "4-5.9": [4, 5.9], "0-3.9": [0, 3.9],
};

const PRICE_RANGES: Record<string, [number, number]> = {
  "0-250": [0, 250], "250-500": [250, 500], "500-1000": [500, 1000],
  "1000-2000": [1000, 2000], "2000+": [2000, Infinity],
};

export type { ExplorerLens, LensExplorerProps, LensSortKey };
export { COLUMNS, APERTURE_OPTIONS, FILTER_THREAD_OPTIONS, FL_RANGES, OQ_RANGES, PRICE_RANGES };
