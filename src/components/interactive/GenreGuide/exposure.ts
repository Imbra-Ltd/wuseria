import type { Lens } from "../../../types/lens";
import type { ScoredGenre } from "../../../types/genre";

// =============================================================================
// RESULT TYPES
// =============================================================================

interface AstroExposure {
  maxT: number;
  actT: number;
  idealIso: number;
  ratio: number;
}

interface HandheldExposure {
  minShutter: number;
  idealIso: number;
  idealIsoRef: number;
}

// =============================================================================
// ASTRO — rule-of-500 exposure + ideal ISO
// =============================================================================

function astroExposure(
  lens: Lens,
  ev: number,
  iso: number,
  crop: number,
): AstroExposure {
  const fl = lens.focalLengthMin;
  const ap = lens.maxAperture;
  const maxT = 500 / (crop * fl);
  const idealIso = Math.round((ap * ap * 100) / (maxT * Math.pow(2, ev)));
  const actT = (ap * ap * 100) / (iso * Math.pow(2, ev));
  const ratio = actT / maxT;

  return { maxT, actT, idealIso, ratio };
}

// =============================================================================
// HANDHELD — minimum shutter + ideal ISO per genre rules
//
//   portrait:       1 / (2 × crop × FL)
//   sport/wildlife: 1 / (4 × crop × FL)
//   default:        1 / (√(MP/12) × crop × FL)
// =============================================================================

function handheldExposure(
  lens: Lens,
  genre: ScoredGenre,
  ev: number,
  crop: number,
  mp: number,
): HandheldExposure {
  const fl = lens.focalLengthMin;
  const ap = lens.maxAperture;
  const fRef = (8 * crop) / 1.5;

  let minShutter: number;
  if (genre === "portrait") {
    minShutter = 1 / (2 * crop * fl);
  } else if (genre === "sport" || genre === "wildlife") {
    minShutter = 1 / (4 * crop * fl);
  } else {
    minShutter = 1 / (Math.sqrt(mp / 12) * crop * fl);
  }

  const idealIso = Math.round(
    (ap * ap * 100) / (minShutter * Math.pow(2, ev)),
  );
  const idealIsoRef = Math.round(
    (fRef * fRef * 100) / (minShutter * Math.pow(2, ev)),
  );

  return { minShutter, idealIso, idealIsoRef };
}

// =============================================================================
// EXPORTS
// =============================================================================

export { astroExposure, handheldExposure };
export type { AstroExposure, HandheldExposure };
