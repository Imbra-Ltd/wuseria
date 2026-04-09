import type { Mount, BatteryType, CardType, CardSpeedClass } from "./common";

type EvfPosition = "center" | "corner" | "none";

type FormFactor = "slr" | "dslr-grip" | "rangefinder" | "compact";

type EvfType = "electronic" | "hybrid" | "none";

type ScreenType = "tilting" | "articulating" | "fixed";

type ShutterType = "mechanical" | "electronic" | "both";

/** Camera-level AF system, not lens motor (see AfMotor in lens.ts) */
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

type SubjectDetect = "animal" | "bird" | "car" | "motorcycle" | "bicycle" | "airplane" | "train";

type VideoSpec = "1080p" | "4K" | "6.2K" | "8K";

type FilmSimulation =
  | "Provia"
  | "Velvia"
  | "Astia"
  | "Classic Chrome"
  | "Pro Neg Hi"
  | "Pro Neg Std"
  | "Monochrome"
  | "Sepia"
  | "ACROS"
  | "ACROS+Ye"
  | "ACROS+R"
  | "ACROS+G"
  | "Eterna"
  | "Eterna Bleach Bypass"
  | "Classic Neg"
  | "Nostalgic Neg"
  | "Reala ACE";

interface Camera {

  // Identity — all cameras are Fujifilm

  model: string;
  mount: Mount;
  year: number;
  discontinued?: boolean;
  series: CameraSeries;
  evfPosition: EvfPosition;
  formFactor: FormFactor;

  // Sensor

  sensor: SensorType;
  megapixels: number;

  /** mm */
  sensorWidth?: number;

  /** mm */
  sensorHeight?: number;

  /** Back-side illuminated */
  bsi?: boolean;

  isoMin?: number;
  isoMax?: number;

  // Stabilisation & weather

  ibis: boolean;
  weatherSealed: boolean;

  // Viewfinder & screen

  evfType?: EvfType;

  /** Dots */
  evfResolution?: number;

  screenType?: ScreenType;

  /** Dots */
  screenResolution?: number;

  touchscreen?: boolean;

  // Performance

  burstFps?: number;
  shutterType?: ShutterType;
  afType?: AfSystemType;
  afPoints?: number;

  /** Percentage of sensor area with phase-detection pixels */
  pdafCoverage?: number;

  faceDetectAF: boolean;
  subjectDetectAF?: SubjectDetect[];
  bufferDepth?: number;
  electronicShutterFps?: number;

  /** Multi-shot sensor shift for higher resolution output */
  pixelShift?: boolean;

  /** CIPA shots per charge */
  batteryLife?: number;

  batteryType?: BatteryType;

  // Video

  videoSpec: VideoSpec;

  // Film simulations

  filmSimulations?: number;

  // Storage

  cardSlots?: number;
  cardType?: CardType;
  cardSpeedClass?: CardSpeedClass;

  // Connectivity

  flashHotShoe: boolean;
  builtInFlash?: boolean;
  usbType?: UsbType;
  tethering?: boolean;
  wifi?: boolean;
  bluetooth?: boolean;
  micInput: boolean;
  headphoneJack: boolean;

  // Physical

  /** Grams, body only */
  weight: number;

  /** mm */
  width?: number;

  /** mm */
  height?: number;

  /** mm */
  depth?: number;

  // Price

  /** USD, rounded to nearest $250 */
  price: number;

  // Links

  officialUrl?: string;
}

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
  FilmSimulation,
};
