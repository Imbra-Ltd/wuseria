interface MtfReading {
  position: number; // image height in mm (0 = center)
  // Per-field values may be null when the chart extractor (or hand
  // curator) has no usable data for that frequency / orientation at
  // this position. Renderers break the polyline at nulls; tables show
  // a dash. Hand-curated entries from official manufacturer charts
  // typically have all four populated; digitizer-emitted entries may
  // not (per the ADR-038 B2 contract — never fabricate).
  contrast10S: number | null; // 10 lp/mm sagittal
  contrast10M: number | null; // 10 lp/mm meridional
  resolution30S: number | null; // 30 lp/mm sagittal
  resolution30M: number | null; // 30 lp/mm meridional
}

interface MtfChart {
  aperture: string; // e.g. "f/1.4", "f/8"
  focalLength?: number; // mm; set on zoom panels (wide + tele), omitted on primes
  readings: MtfReading[];
}

type MtfType = "computed" | "measured";

interface MtfData {
  source: string; // attribution URL
  mtfType: MtfType;
  charts: MtfChart[];
}

export type { MtfReading, MtfChart, MtfData, MtfType };
