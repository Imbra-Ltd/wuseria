import type { Mount, Brand } from "./common";

/** Lens type — prime or zoom */
type LensType = "prime" | "zoom";

/** Autofocus motor type — speed tier */
type AfMotor = "DC" | "STM" | "LM";

interface Lens {
  // Identity
  brand: Brand | string;
  model: string;
  type: LensType;
  mount: Mount;
  year?: number;
  discontinued?: boolean;

  // Optical — specs
  /** Minimum focal length, mm */
  focalLengthMin: number;
  /** Maximum focal length, mm (same as min for primes) */
  focalLengthMax: number;
  maxAperture: number;
  /** Sharpest aperture as f-number (e.g. 2.8, 4, 8) */
  sweetSpotAperture?: number;
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
  focusRing?: boolean;
  focusByWire?: boolean;
  distanceScale?: boolean;
  smoothFocusRing?: boolean;
  /** Weight in grams, body only */
  weight: number;
  /** Maximum outer diameter, mm */
  diameter?: number;
  /** Mount to front element, mm */
  length?: number;
  /** Filter thread diameter, mm */
  filterThread?: number;
  rotatingFront?: boolean;
  tripodMount?: boolean;

  // Price
  /** Approximate price in USD, rounded to $250 */
  price: number;

  // Optical quality — from MTF chart readings (0–2 scale)
  sweetSpotSharpness?: number;
  cornerSharpness?: number;
  wideOpenSharpness?: number;
  astigmatism?: number;
  fieldCurvature?: number;
  coma?: number;

  // Optical quality — NOT from MTF charts (0–2 scale)
  longitudinalCA?: number;
  lateralCA?: number;
  distortion?: number;
  vignetting?: number;
  bokeh?: number;
  flareResistance?: number;

  // Other scoring inputs
  /** Minimum focus distance, mm */
  minFocusDistance?: number;
  tiltShift?: boolean;
  /** Maximum shift range, mm */
  shiftRange?: number;
  /** Maximum tilt angle, degrees */
  tiltAngle?: number;
  /** Image circle diameter, mm */
  imageCircle?: number;
  tiltShiftIndependent?: boolean;

  // Links
  officialUrl?: string;
}

export type { Lens, LensType, AfMotor };
