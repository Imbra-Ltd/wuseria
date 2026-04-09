import type { Mount } from "./common";

/** EVF position on the body */
type EvfPosition = "center" | "corner" | "none";

/** Ergonomic form factor */
type FormFactor = "slr" | "dslr-grip" | "rangefinder" | "compact";

/** EVF type */
type EvfType = "electronic" | "hybrid" | "none";

/** Screen articulation type */
type ScreenType = "tilting" | "articulating" | "fixed";

/** Shutter mechanism */
type ShutterType = "mechanical" | "electronic" | "both";

/** Autofocus system type (camera-level, not lens motor) */
type AfSystemType = "CDAF" | "hybrid-PDAF";

/** Camera series within Fujifilm lineup */
type CameraSeries =
  | "X-Pro"
  | "X-T"
  | "X-H"
  | "X-E"
  | "X-S"
  | "X-M"
  | "X-A"
  | "GFX";

/** Sensor generation */
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

/** USB connector type */
type UsbType = "micro-USB" | "USB-C";

/** Subject detection categories */
type SubjectDetect = "animal" | "bird" | "car" | "motorcycle" | "bicycle" | "airplane" | "train";

/** Battery model */
type BatteryType = "NP-W126" | "NP-W126S" | "NP-W235" | "NP-T125";

/** Video resolution tier */
type VideoSpec = "1080p" | "4K" | "6.2K" | "8K";

/** Film simulation name */
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
  // Identity
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
  /** Sensor width, mm */
  sensorWidth?: number;
  /** Sensor height, mm */
  sensorHeight?: number;
  bsi?: boolean;
  isoMin?: number;
  isoMax?: number;

  // Stabilisation & weather
  ibis: boolean;
  weatherSealed: boolean;

  // Viewfinder & screen
  evfType?: EvfType;
  /** EVF resolution, dots */
  evfResolution?: number;
  screenType?: ScreenType;
  /** Screen resolution, dots */
  screenResolution?: number;
  touchscreen?: boolean;

  // Performance
  burstFps?: number;
  shutterType?: ShutterType;
  afType?: AfSystemType;
  afPoints?: number;
  /** Phase-detection AF coverage, percentage of sensor area */
  pdafCoverage?: number;
  faceDetectAF: boolean;
  subjectDetectAF?: SubjectDetect[];
  bufferDepth?: number;
  electronicShutterFps?: number;
  pixelShift?: boolean;
  /** CIPA shots per charge */
  batteryLife?: number;
  batteryType?: BatteryType;

  // Video
  videoSpec: VideoSpec;

  // Film simulations
  filmSimulations?: number;
  filmSimulationList?: FilmSimulation[];

  // Storage
  cardSlots?: number;
  cardType?: import("./common").CardType;
  cardSpeedClass?: import("./common").CardSpeedClass;

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
  /** Weight in grams, body only */
  weight: number;
  /** Body width, mm */
  width?: number;
  /** Body height, mm */
  height?: number;
  /** Body depth, mm */
  depth?: number;

  // Price
  /** Approximate price in USD, rounded to $250 */
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
  BatteryType,
  VideoSpec,
  FilmSimulation,
};
