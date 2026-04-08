import type { Mount } from "./lens";

/** Camera body style based on viewfinder position */
type BodyStyle = "center-evf" | "corner-evf" | "no-evf";

/** EVF type */
type EvfType = "electronic" | "hybrid" | "none";

/** Screen articulation type */
type ScreenType = "tilting" | "articulating" | "fixed";

/** Shutter mechanism */
type ShutterType = "mechanical" | "electronic" | "both";

/** Autofocus system type */
type CameraAfType = "CDAF" | "hybrid-PDAF";

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

/** SD/CFexpress card type */
type CardType = "SD" | "UHS-II" | "CFexpress";

/** USB connector type */
type UsbType = "micro-USB" | "USB-C";

/** Subject detection categories */
type SubjectDetect = "animal" | "bird" | "car" | "motorcycle" | "bicycle" | "airplane" | "train";

interface Camera {
  // Identity
  model: string;
  mount: Mount;
  year: number;
  discontinued?: boolean;
  series: CameraSeries;
  bodyStyle: BodyStyle;

  // Sensor
  sensor: string;
  megapixels: number;
  sensorWidth?: number;
  sensorHeight?: number;
  bsi?: boolean;
  isoMin?: number;
  isoMax?: number;

  // Stabilisation & weather
  ibis: boolean;
  weatherSealed: boolean;

  // Viewfinder & screen
  evfType?: EvfType;
  evfResolution?: number;
  screenType?: ScreenType;

  // Performance
  burstFps?: number;
  shutterType?: ShutterType;
  afType?: CameraAfType;
  afPoints?: number;
  afCoverage?: number;
  faceDetectAF: boolean;
  subjectDetectAF?: SubjectDetect[];
  bufferDepth?: number;
  electronicShutterFps?: number;
  batteryLife?: number;

  // Video
  videoSpec: string;

  // Film simulations
  filmSimulations?: number;
  filmSimulationList?: string[];

  // Storage
  cardSlots?: number;
  cardType?: CardType;

  // Connectivity
  flashHotShoe: boolean;
  usbType?: UsbType;
  wifi?: boolean;
  bluetooth?: boolean;
  micInput: boolean;
  headphoneJack: boolean;

  // Physical
  weight: number;
  width?: number;
  height?: number;
  depth?: number;

  // Price
  price: number;

  // Links
  officialUrl?: string;
}

export type {
  Camera,
  BodyStyle,
  EvfType,
  ScreenType,
  ShutterType,
  CameraAfType,
  CameraSeries,
  CardType,
  UsbType,
  SubjectDetect,
};
