import type {
  Mount,
  BatteryType,
  MemoryCardType,
  CardSpeedClass,
} from "./common";
import type { ReviewSource } from "./review";

// =============================================================================
// TYPES
// =============================================================================

type EvfPosition = "center" | "corner" | "none";

type FormFactor = "standard" | "pro-grip" | "rangefinder" | "compact";

type EvfType = "electronic" | "hybrid" | "none";

type ScreenType = "tilting" | "articulating" | "fixed";

type ShutterType = "mechanical" | "electronic" | "both";

// Camera-level AF system, not lens motor (see AfMotor in lens.ts)
type AfSystemType = "CDAF" | "hybrid-PDAF";

type CameraSeries =
  | "X-Pro"
  | "X-T"
  | "X-H"
  | "X-E"
  | "X-S"
  | "X-M"
  | "X-A"
  | "GFX";

type SensorType =
  | "X-Trans I"
  | "X-Trans II"
  | "X-Trans III"
  | "X-Trans IV"
  | "X-Trans V"
  | "X-Trans V Stacked"
  | "Bayer"
  | "GFX CMOS"
  | "GFX CMOS II"
  | "GFX CMOS II HS";

type UsbType = "micro-USB" | "USB-C";

type SubjectDetect =
  | "animal"
  | "bird"
  | "car"
  | "motorcycle"
  | "bicycle"
  | "airplane"
  | "train";

type VideoSpec = "1080p" | "4K" | "6.2K" | "8K";

// =============================================================================
// CAMERA
// =============================================================================

interface Camera {
  // ===========================================================================
  // IDENTITY — all cameras are Fujifilm
  // ===========================================================================

  model: string;
  mount: Mount;
  year: number;
  isDiscontinued?: boolean;
  series: CameraSeries;
  evfPosition: EvfPosition;
  formFactor: FormFactor;

  // ===========================================================================
  // SENSOR
  // ===========================================================================

  sensor: SensorType;
  megapixels: number;
  sensorWidth?: number; // mm
  sensorHeight?: number; // mm
  isBsi?: boolean; // back-side illuminated
  isoMin?: number;
  isoMax?: number;

  // ===========================================================================
  // STABILISATION & WEATHER
  // ===========================================================================

  hasIbis?: boolean;
  isWeatherSealed?: boolean;

  // ===========================================================================
  // VIEWFINDER & SCREEN
  // ===========================================================================

  evfType?: EvfType;
  evfResolution?: number; // dots
  screenType?: ScreenType;
  screenResolution?: number; // dots
  hasTouchscreen?: boolean;

  // ===========================================================================
  // PERFORMANCE
  // ===========================================================================

  mechanicalBurstFps?: number;
  shutterType?: ShutterType;
  afType?: AfSystemType;
  afPoints?: number;
  pdafCoverage?: number; // % of sensor area
  hasFaceDetectAF?: boolean;
  subjectDetectAF?: SubjectDetect[];
  bufferDepth?: number; // frames
  electronicBurstFps?: number;
  hasPixelShift?: boolean;
  batteryLife?: number; // CIPA shots per charge
  batteryType?: BatteryType;

  // ===========================================================================
  // VIDEO
  // ===========================================================================

  videoSpec: VideoSpec;

  // ===========================================================================
  // FILM SIMULATIONS
  // ===========================================================================

  filmSimulations?: number;

  // ===========================================================================
  // STORAGE
  // ===========================================================================

  cardSlots?: number;
  cardType?: MemoryCardType;
  cardSpeedClass?: CardSpeedClass;

  // ===========================================================================
  // CONNECTIVITY
  // ===========================================================================

  hasFlashHotShoe?: boolean;
  hasBuiltInFlash?: boolean;
  usbType?: UsbType;
  hasTethering?: boolean;
  hasWifi?: boolean;
  hasBluetooth?: boolean;
  hasMicInput?: boolean;
  hasHeadphoneJack?: boolean;

  // ===========================================================================
  // PHYSICAL
  // ===========================================================================

  weight: number; // grams, body only
  width?: number; // mm
  height?: number; // mm
  depth?: number; // mm

  // ===========================================================================
  // PRICE
  // ===========================================================================

  price: number; // USD, rounded to nearest $250

  // ===========================================================================
  // REVIEW SOURCES
  // ===========================================================================

  reviewSources?: Partial<Record<ReviewSource, string>>;

  // ===========================================================================
  // LINKS
  // ===========================================================================

  officialUrl?: string;
}

// =============================================================================
// EXPORTS
// =============================================================================

export type {
  Camera,
  EvfPosition,
  FormFactor,
  EvfType,
  ScreenType,
  ShutterType,
  AfSystemType,
  CameraSeries,
  SensorType,
  UsbType,
  SubjectDetect,
  VideoSpec,
};
