// Sagittal/meridional pair at one spatial frequency. Either value MAY
// be null when the source chart has no usable data for that
// orientation at this position. Renderers break the polyline at nulls;
// tables show a dash. Hand-curated entries from official manufacturer
// charts typically have both populated; digitizer-emitted entries may
// not (per the ADR-038 B2 contract — never fabricate).
interface MtfSampleSM {
  S: number | null; // sagittal
  M: number | null; // meridional
}

interface MtfReading {
  position: number; // image height in mm (0 = center)
  // Per-frequency S/M samples. Key is the spatial frequency in lp/mm
  // (10, 15, 20, 30, 40, 45, ...). Brands publish at different
  // frequencies — Sigma/Samyang/7Artisans/Tokina/Viltrox at {10, 30};
  // Fujifilm GF primes at {15, 20, 40}; Fujifilm GF zooms at
  // {10, 20, 40}; Fujifilm XF at {15, 45}. A reading row MAY omit
  // frequencies entirely — nothing forces a row to populate
  // frequencies the lens does not publish.
  //
  // Every row in the same `MtfChart` MUST carry the same key set —
  // validation tests enforce this. See ADR-042.
  samples: Record<number, MtfSampleSM>;
}

type MtfConfidence = "HIGH" | "LOW";

interface MtfChart {
  aperture: string; // e.g. "f/1.4", "f/8"
  focalLength?: number; // mm; set on zoom panels (wide + tele), omitted on primes
  // Per-pass confidence (ADR-053, ADR-054). HIGH covers hand-curated
  // entries and autotriage HIGH verdicts; LOW means autotriage flagged
  // this pass (render-match precision below threshold or a plausibility
  // prior violated — see `confidenceReason`). Samples are kept on LOW
  // passes; the lens page surfaces the verdict with a badge.
  confidence: MtfConfidence;
  // ADR-052 reason code on LOW passes (e.g. `precision_below_threshold`,
  // `prior_failed_center_ge_edge`). Omitted on HIGH passes.
  confidenceReason?: string;
  readings: MtfReading[];
}

type MtfType = "computed" | "measured";

interface MtfData {
  mtfType: MtfType;
  charts: MtfChart[];
}

export type {
  MtfReading,
  MtfSampleSM,
  MtfChart,
  MtfData,
  MtfType,
  MtfConfidence,
};
