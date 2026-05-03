import type { ColumnDef } from "../shared/table";

type CameraSortKey =
  | "model"
  | "year"
  | "megapixels"
  | "sensor"
  | "hasIbis"
  | "isWeatherSealed"
  | "mechanicalBurstFps"
  | "videoSpec"
  | "batteryLife"
  | "weight"
  | "price";

const COLUMNS: ColumnDef<CameraSortKey>[] = [
  { key: "model", label: "Model", align: "left", width: "22%" },
  { key: "year", label: "Year", align: "right", width: "7%" },
  { key: "megapixels", label: "MP", align: "right", width: "6%" },
  { key: "sensor", label: "Sensor", align: "left", width: "12%" },
  { key: "hasIbis", label: "IBIS", align: "center", width: "6%" },
  { key: "isWeatherSealed", label: "WR", align: "center", width: "5%" },
  { key: "mechanicalBurstFps", label: "FPS", align: "right", width: "6%" },
  { key: "videoSpec", label: "Video", align: "center", width: "8%" },
  { key: "batteryLife", label: "Battery", align: "right", width: "8%" },
  { key: "weight", label: "Weight", align: "right", width: "8%" },
  { key: "price", label: "Price", align: "right", width: "8%" },
];

const YEAR_RANGES: Record<string, [number, number]> = {
  "2022+": [2022, Infinity],
  "2019-2021": [2019, 2021],
  "2016-2018": [2016, 2018],
  "2012-2015": [2012, 2015],
};

const VIDEO_OPTIONS = ["8K", "6.2K", "4K", "1080p"];

const PRICE_RANGES: Record<string, [number, number]> = {
  "0-500": [0, 500],
  "500-1000": [500, 1000],
  "1000-2000": [1000, 2000],
  "2000-4000": [2000, 4000],
  "4000+": [4000, Infinity],
};

export type { CameraSortKey };
export { COLUMNS, YEAR_RANGES, VIDEO_OPTIONS, PRICE_RANGES };
