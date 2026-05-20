interface MtfReading {
  position: number; // image height in mm (0 = center)
  contrast10S: number; // 10 lp/mm sagittal
  contrast10M: number; // 10 lp/mm meridional
  resolution30S: number; // 30 lp/mm sagittal
  resolution30M: number; // 30 lp/mm meridional
}

interface MtfChart {
  aperture: string; // e.g. "f/1.4", "f/8"
  readings: MtfReading[];
}

type MtfType = "computed" | "measured";

interface MtfData {
  source: string; // attribution URL
  mtfType: MtfType;
  charts: MtfChart[];
}

export type { MtfReading, MtfChart, MtfData, MtfType };
