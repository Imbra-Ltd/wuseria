/** Lens mount system */
type Mount = "X" | "GFX";

/** Lens type — prime or zoom */
type LensType = "prime" | "zoom";

/** Autofocus motor type — speed tier */
type AfMotor = "DC" | "STM" | "LM";

interface Lens {
  // Identity
  brand: string;
  model: string;
  type: LensType;
  mount: Mount;
  year?: number;
  discontinued?: boolean;

  // Optical — specs
  focalLengthMin: number;
  focalLengthMax: number;
  maxAperture: number;
  sweetSpot?: string;
  apertureBlades?: number;
  circularAperture?: boolean;
  maxMagnification?: number;

  // Build
  ois: boolean;
  weatherSealed: boolean;
  autofocus: boolean;
  afMotor?: AfMotor;
  apertureRing: boolean;
  apertureClickless?: boolean;
  focusRing: boolean;
  focusByWire?: boolean;
  distanceScale?: boolean;
  smoothFocusRing?: boolean;
  weight: number;
  diameter?: number;
  length?: number;
  filterThread?: number;
  rotatingFront: boolean;
  tripodMount: boolean;

  // Price
  price: number;
  priceEstimated: boolean;

  // Optical quality — from MTF chart readings
  sweetSpotSharpness?: number;
  cornerSharpness?: number;
  wideOpenSharpness?: number;
  astigmatism?: number;
  fieldCurvature?: number;
  comaRating?: number;

  // Optical quality — NOT from MTF charts
  locaRating?: number;
  lateralCA?: number;
  distortionRating?: number;
  vignetting?: number;
  bokehQuality?: number;
  flareResistance?: number;

  // Other scoring inputs
  minFocusDistance?: number;
  tiltShift: boolean;
  shiftRange?: number;
  tiltAngle?: number;
  imageCircle?: number;
  tiltShiftIndependent?: boolean;
}

export type { Lens, LensType, Mount, AfMotor };
