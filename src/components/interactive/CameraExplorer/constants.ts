import type { ColumnAlign } from "../shared/table";

type CameraSortKey =
  | "model" | "year" | "megapixels" | "sensor" | "hasIbis"
  | "isWeatherSealed" | "mechanicalBurstFps" | "videoSpec"
  | "batteryLife" | "weight" | "price";

const COLUMNS: { key: CameraSortKey; label: string; align: ColumnAlign }[] = [
  { key: "model", label: "Model", align: "left" },
  { key: "year", label: "Year", align: "right" },
  { key: "megapixels", label: "MP", align: "right" },
  { key: "sensor", label: "Sensor", align: "left" },
  { key: "hasIbis", label: "IBIS", align: "center" },
  { key: "isWeatherSealed", label: "WR", align: "center" },
  { key: "mechanicalBurstFps", label: "FPS", align: "right" },
  { key: "videoSpec", label: "Video", align: "center" },
  { key: "batteryLife", label: "Battery", align: "right" },
  { key: "weight", label: "Weight", align: "right" },
  { key: "price", label: "Price", align: "right" },
];

const YEAR_RANGES: Record<string, [number, number]> = {
  "2022+": [2022, Infinity], "2019-2021": [2019, 2021],
  "2016-2018": [2016, 2018], "2012-2015": [2012, 2015],
};

const VIDEO_OPTIONS = ["8K", "6.2K", "4K", "1080p"];

const PRICE_RANGES: Record<string, [number, number]> = {
  "0-500": [0, 500], "500-1000": [500, 1000], "1000-2000": [1000, 2000],
  "2000-4000": [2000, 4000], "4000+": [4000, Infinity],
};

export type { CameraSortKey };
export { COLUMNS, YEAR_RANGES, VIDEO_OPTIONS, PRICE_RANGES };
