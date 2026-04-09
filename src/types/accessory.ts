import type { Mount, Brand, BatteryType, StorageType } from "./common";
import type { Genre } from "./genre";

// ---------------------------------------------------------------------------
// Shared string literal unions — no magic strings
// ---------------------------------------------------------------------------

/** Mount systems beyond Fujifilm (for adapter sourceMount) */
type AdapterMount =
  | Mount
  | "Leica M"
  | "Canon EF"
  | "Canon RF"
  | "Nikon F"
  | "Nikon Z"
  | "Sony E"
  | "Pentax K"
  | "Hasselblad XCD"
  | "Fuji H";

type HeadType = "ball" | "geared" | "gimbal" | "pan-tilt" | "video";
type PlateType = "arca-swiss" | "manfrotto-rc2" | "proprietary";
type FilterType = "CPL" | "ND" | "GND" | "UV" | "black-mist" | "IR" | "light-pollution";
// StorageType imported from common.ts
type BagType = "backpack" | "sling" | "shoulder" | "holster" | "rolling";
type StrapType = "neck" | "sling" | "wrist" | "harness";
type ConnectionType = "wired-2.5mm" | "wired-usb" | "bluetooth" | "radio" | "wifi";
type MicPattern = "stereo" | "shotgun" | "omni" | "cardioid";
type TripodMaterial = "carbon-fiber" | "aluminum" | "basalt";

// ---------------------------------------------------------------------------
// Mixin — Fuji-specific compatibility fields
// ---------------------------------------------------------------------------

interface FujiCompatible {
  mount?: Mount;
  compatibleWith?: string[];
  weatherSealed?: boolean;
}

// ---------------------------------------------------------------------------
// Base — truly universal fields that apply to every accessory
// ---------------------------------------------------------------------------

interface AccessoryBase {
  brand: Brand;
  model: string;
  year?: number;
  discontinued?: boolean;
  description: string;
  genres?: Genre[];
  weight?: number;
  price: number;
  officialUrl?: string;
}

// ---------------------------------------------------------------------------
// Category-specific extensions
// ---------------------------------------------------------------------------

interface FlashAccessory extends AccessoryBase, FujiCompatible {
  category: "flash";
  guideNumber: number;
  ttl: boolean;
  hss: boolean;
  wirelessCommander?: boolean;
  wirelessReceiver?: boolean;
}

interface LensAccessory extends AccessoryBase, FujiCompatible {
  category: "lens-accessory";
  magnificationFactor?: number;
  afRetained?: boolean;
}

interface BatteryAccessory extends AccessoryBase {
  category: "battery";
  compatibleWith?: string[];
  batteryType: BatteryType;
  capacityMah?: number;
  voltage?: number;
}

interface ChargerAccessory extends AccessoryBase {
  category: "charger";
  compatibleWith?: string[];
  batteryType: BatteryType;
  slots?: number;
  usbInput?: boolean;
}

interface BatteryGripAccessory extends AccessoryBase, FujiCompatible {
  category: "battery-grip";
  batteryType: BatteryType;
  batteryCount?: number;
  verticalControls?: boolean;
}

interface AdapterAccessory extends AccessoryBase {
  category: "adapter";
  compatibleWith?: string[];
  sourceMount: AdapterMount;
  targetMount: Mount;
  afSupported?: boolean;
  apertureControl?: boolean;
}

interface TripodAccessory extends AccessoryBase {
  category: "tripod" | "monopod";
  maxLoad?: number;
  maxHeight?: number;
  foldedLength?: number;
  legSections?: number;
  material?: TripodMaterial;
}

interface HeadAccessory extends AccessoryBase {
  category: "tripod-head";
  headType: HeadType;
  maxLoad?: number;
  plateType?: PlateType;
}

interface FilterAccessory extends AccessoryBase {
  category: "filter";
  filterThread?: number;
  filterType: FilterType;
}

interface LightingAccessory extends AccessoryBase {
  category: "lighting";
  colorTemp?: number;
  cri?: number;
  lumens?: number;
}

interface BagAccessory extends AccessoryBase {
  category: "bag";
  capacityLiters?: number;
  bagType?: BagType;
}

interface StorageAccessory extends AccessoryBase {
  category: "storage";
  storageType: StorageType;
  speedMBps?: number;
  capacityGB?: number;
}

interface RemoteAccessory extends AccessoryBase {
  category: "remote";
  compatibleWith?: string[];
  connectionType: ConnectionType;
  intervalometer?: boolean;
}

interface AudioAccessory extends AccessoryBase {
  category: "audio";
  compatibleWith?: string[];
  micPattern?: MicPattern;
  connectionType?: ConnectionType;
}

/** Strap material */
type StrapMaterial = "nylon" | "leather" | "neoprene" | "paracord" | "silk";

interface StrapAccessory extends AccessoryBase {
  category: "strap";
  strapType: StrapType;
  length?: number;
  material?: StrapMaterial;
}

interface PlateAccessory extends AccessoryBase {
  category: "plate";
  plateType?: PlateType;
  arcaCompatible?: boolean;
}

interface PowerBankAccessory extends AccessoryBase {
  category: "power-bank";
  capacityMah: number;
  outputWatts?: number;
  usbPD?: boolean;
}

// ---------------------------------------------------------------------------
// Generic — categories with no extra fields
// ---------------------------------------------------------------------------

interface GenericAccessory extends AccessoryBase {
  category:
    | "hand-grip"
    | "body-accessory"
    | "cooling"
    | "astro-gear"
    | "protection";
  compatibleWith?: string[];
}

// ---------------------------------------------------------------------------
// Discriminated union — narrows by category
// ---------------------------------------------------------------------------

type Accessory =
  | FlashAccessory
  | LensAccessory
  | BatteryAccessory
  | ChargerAccessory
  | BatteryGripAccessory
  | AdapterAccessory
  | TripodAccessory
  | HeadAccessory
  | FilterAccessory
  | LightingAccessory
  | BagAccessory
  | StorageAccessory
  | RemoteAccessory
  | AudioAccessory
  | StrapAccessory
  | PlateAccessory
  | PowerBankAccessory
  | GenericAccessory;

type AccessoryCategory = Accessory["category"];

export type {
  Accessory,
  AccessoryCategory,
  AccessoryBase,
  FujiCompatible,
  FlashAccessory,
  LensAccessory,
  BatteryAccessory,
  ChargerAccessory,
  BatteryGripAccessory,
  AdapterAccessory,
  TripodAccessory,
  HeadAccessory,
  FilterAccessory,
  LightingAccessory,
  BagAccessory,
  StorageAccessory,
  RemoteAccessory,
  AudioAccessory,
  StrapAccessory,
  PlateAccessory,
  PowerBankAccessory,
  GenericAccessory,
  AdapterMount,
  HeadType,
  PlateType,
  FilterType,
  BagType,
  StrapType,
  ConnectionType,
  MicPattern,
  TripodMaterial,
  StrapMaterial,
};
