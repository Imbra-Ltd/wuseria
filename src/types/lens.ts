import type { Mount, Brand } from "./common";

// =============================================================================
// TYPES
// =============================================================================

type LensType = "prime" | "zoom";

// DC = coreless, STM = stepping, LM = linear motor
type AfMotor = "DC" | "STM" | "LM";

// =============================================================================
// LENS
// =============================================================================

interface Lens {

  // ===========================================================================
  // IDENTITY
  // ===========================================================================

  brand: Brand;
  model: string;
  type: LensType;
  mount: Mount;
  year?: number;
  discontinued?: boolean;

  // ===========================================================================
  // OPTICAL SPECS
  // ===========================================================================

  focalLengthMin: number;
  focalLengthMax: number;
  maxAperture: number;

  // f-number where the lens is sharpest (e.g. 2.8, 4, 8)
  sweetSpotAperture?: number;

  apertureBlades?: number;
  circularAperture?: boolean;

  // Reproduction ratio as decimal (1.0 = life-size, 0.5 = half)
  maxMagnification?: number;

  // ===========================================================================
  // BUILD — absent = false for all booleans
  // ===========================================================================

  ois?: boolean;
  weatherSealed?: boolean;
  autofocus?: boolean;
  afMotor?: AfMotor;
  apertureRing?: boolean;
  apertureClickless?: boolean;
  focusRing?: boolean;
  focusByWire?: boolean;
  distanceScale?: boolean;
  smoothFocusRing?: boolean;

  // Grams
  weight: number;

  // Outer diameter, mm
  diameter?: number;

  // Mount to front element, mm
  length?: number;

  // Filter thread diameter, mm
  filterThread?: number;

  rotatingFront?: boolean;
  tripodMount?: boolean;

  // ===========================================================================
  // PRICE
  // ===========================================================================

  // USD, rounded to nearest $250
  price: number;

  // ===========================================================================
  // OPTICAL QUALITY — MTF chart readings (0–2 scale)
  // ===========================================================================

  sweetSpotSharpness?: number;
  cornerSharpness?: number;
  wideOpenSharpness?: number;
  astigmatism?: number;
  fieldCurvature?: number;
  coma?: number;

  // ===========================================================================
  // OPTICAL QUALITY — NOT from MTF charts (0–2 scale)
  // ===========================================================================

  longitudinalCA?: number;
  lateralCA?: number;
  distortion?: number;
  vignetting?: number;
  bokeh?: number;
  flareResistance?: number;

  // ===========================================================================
  // SCORING INPUTS
  // ===========================================================================

  // mm
  minFocusDistance?: number;

  tiltShift?: boolean;

  // mm
  shiftRange?: number;

  // Degrees
  tiltAngle?: number;

  // mm
  imageCircle?: number;

  tiltShiftIndependent?: boolean;

  // ===========================================================================
  // LINKS
  // ===========================================================================

  officialUrl?: string;
}

// =============================================================================
// EXPORTS
// =============================================================================

export type { Lens, LensType, AfMotor };
