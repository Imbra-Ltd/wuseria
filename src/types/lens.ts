import type { Mount, Brand } from "./common";
import type { Genre } from "./genre";
import type { ReviewSource } from "./review";

// =============================================================================
// TYPES
// =============================================================================

type LensType = "prime" | "zoom";
type LensCategory = "photo" | "cine";

// DC = coreless, STM = stepping, LM = linear motor
type AfMotor = "DC" | "STM" | "LM";

type ScoringStatus = "niche" | "new" | "discontinued" | "specialty" | "pending";

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
  category: LensCategory;
  mount: Mount;
  year?: number;
  isDiscontinued?: boolean;

  // ===========================================================================
  // OPTICAL CONSTRUCTION
  // ===========================================================================

  opticalElements?: number;
  opticalGroups?: number;
  specialElements?: string[]; // e.g. ["2 aspherical", "1 ED"]
  coating?: string[]; // e.g. ["Super EBC", "Nano-GI"]

  // ===========================================================================
  // OPTICAL SPECS
  // ===========================================================================

  focalLengthMin: number;
  focalLengthMax: number;
  maxAperture: number;

  // f-number where the lens is sharpest (e.g. 2.8, 4, 8)
  sweetSpotAperture?: number;

  apertureBlades?: number;
  hasCircularAperture?: boolean;

  // Reproduction ratio as decimal (1.0 = life-size, 0.5 = half)
  maxMagnification?: number;

  // mm
  minFocusDistance?: number;

  // ===========================================================================
  // BUILD — absent = false for all booleans
  // ===========================================================================

  hasOis?: boolean;
  isWeatherSealed?: boolean;
  afMotor?: AfMotor;
  hasApertureRing?: boolean;
  isApertureClickless?: boolean;
  hasFocusRing?: boolean;
  isFocusByWire?: boolean;
  hasDistanceScale?: boolean;

  // Grams
  weight: number;

  // Outer diameter, mm
  diameter?: number;

  // Mount to front element, mm
  length?: number;

  // Filter thread diameter, mm
  filterThread?: number;

  hasRotatingFront?: boolean;
  hasTripodMount?: boolean;

  // ===========================================================================
  // PRICE
  // ===========================================================================

  // USD, rounded to nearest $250
  price: number;

  // ===========================================================================
  // OPTICAL QUALITY — MTF chart readings (0–2 scale)
  // ===========================================================================

  centerStopped?: number;
  cornerStopped?: number;
  centerWideOpen?: number;
  cornerWideOpen?: number;
  astigmatism?: number;
  coma?: number;
  sphericalAberration?: number;

  // ===========================================================================
  // OPTICAL QUALITY — lab tests and field reports (0–2 scale)
  // ===========================================================================

  longitudinalCA?: number;
  lateralCA?: number;
  distortion?: number;
  vignettingWideOpen?: number; // at max aperture
  vignettingStopped?: number; // at f/5.6 or f/8
  bokeh?: number;
  flareResistance?: number;

  // ===========================================================================
  // TILT-SHIFT
  // ===========================================================================

  isTiltShift?: boolean;

  // mm
  shiftRange?: number;

  // Degrees
  tiltAngle?: number;

  // mm
  imageCircle?: number;

  isTiltShiftIndependent?: boolean;

  // ===========================================================================
  // SCORING STATUS
  // ===========================================================================

  scoringStatus?: ScoringStatus;

  // ===========================================================================
  // GENRE SCORING
  // ===========================================================================

  genreMarks?: Partial<Record<Genre, number>>;
  editorialPicks?: Genre[];

  // ===========================================================================
  // REVIEW SOURCES — URLs keyed by source, highest-rigour source was used
  // for optical quality fields
  // ===========================================================================

  reviewSources?: Partial<Record<ReviewSource, string>>;

  // ===========================================================================
  // COMMUNITY
  // ===========================================================================

  communityNotes?: string[];

  // ===========================================================================
  // LINKS
  // ===========================================================================

  officialUrl?: string;
}

// =============================================================================
// EXPORTS
// =============================================================================

export type { Lens, LensCategory, LensType, AfMotor, ScoringStatus };
