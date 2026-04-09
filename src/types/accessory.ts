import type { Mount, Brand, BatteryType, StorageType } from "./common";
import type { Genre } from "./genre";

// =============================================================================
// STRING LITERAL UNIONS
// =============================================================================

// Mount systems beyond Fujifilm (for adapter sourceMount)
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

type BagType = "backpack" | "sling" | "shoulder" | "holster" | "rolling";

type StrapType = "neck" | "sling" | "wrist" | "harness";

type StrapMaterial = "nylon" | "leather" | "neoprene" | "paracord" | "silk";

type ConnectionType = "wired-2.5mm" | "wired-usb" | "bluetooth" | "radio" | "wifi";

type MicPattern = "stereo" | "shotgun" | "omni" | "cardioid";

type TripodMaterial = "carbon-fiber" | "aluminum" | "basalt";

// =============================================================================
// FUJI COMPATIBLE MIXIN
// =============================================================================

interface FujiCompatible {
  mount?: Mount;
  compatibleWith?: string[];
  isWeatherSealed?: boolean;
}

// =============================================================================
// BASE — fields that apply to every accessory
// =============================================================================

interface AccessoryBase {
  brand: Brand;
  model: string;
  year?: number;
  isDiscontinued?: boolean;
  description: string;
  genres?: Genre[];
  weight?: number;
  price: number;
  officialUrl?: string;
}

// =============================================================================
// CATEGORY-SPECIFIC EXTENSIONS
// =============================================================================

interface FlashAccessory extends AccessoryBase, FujiCompatible {
  category: "flash";
  guideNumber: number;
  hasTtl: boolean;
  hasHss: boolean;
  isWirelessCommander?: boolean;
  isWirelessReceiver?: boolean;
}

interface LensAccessory extends AccessoryBase, FujiCompatible {
  category: "lens-accessory";

  // e.g. 1.4 for a 1.4x teleconverter
  magnificationFactor?: number;

  isAfRetained?: boolean;
}

interface BatteryAccessory extends AccessoryBase {
  category: "battery";
  compatibleWith?: string[];
  batteryType: BatteryType;

  // mAh
  capacityMah?: number;

  // Volts
  voltage?: number;
}

interface ChargerAccessory extends AccessoryBase {
  category: "charger";
  compatibleWith?: string[];
  batteryType: BatteryType;
  slots?: number;
  hasUsbInput?: boolean;
}

interface BatteryGripAccessory extends AccessoryBase, FujiCompatible {
  category: "battery-grip";
  batteryType: BatteryType;
  batteryCount?: number;
  hasVerticalControls?: boolean;
}

interface AdapterAccessory extends AccessoryBase {
  category: "adapter";
  compatibleWith?: string[];
  sourceMount: AdapterMount;
  targetMount: Mount;
  isAfSupported?: boolean;
  hasApertureControl?: boolean;
}

interface TripodAccessory extends AccessoryBase {
  category: "tripod" | "monopod";

  // kg
  maxLoad?: number;

  // mm
  maxHeight?: number;

  // mm
  foldedLength?: number;

  legSections?: number;
  material?: TripodMaterial;
}

interface HeadAccessory extends AccessoryBase {
  category: "tripod-head";
  headType: HeadType;

  // kg
  maxLoad?: number;

  plateType?: PlateType;
}

interface FilterAccessory extends AccessoryBase {
  category: "filter";

  // mm, matches lens filterThread
  filterThread?: number;

  filterType: FilterType;
}

interface LightingAccessory extends AccessoryBase {
  category: "lighting";

  // Kelvin
  colorTemp?: number;

  // Color Rendering Index, 0–100
  cri?: number;

  lumens?: number;
}

interface BagAccessory extends AccessoryBase {
  category: "bag";

  // Liters
  capacityLiters?: number;

  bagType?: BagType;
}

interface StorageAccessory extends AccessoryBase {
  category: "storage";
  storageType: StorageType;

  // MB/s write speed
  speedMBps?: number;

  capacityGB?: number;
}

interface RemoteAccessory extends AccessoryBase {
  category: "remote";
  compatibleWith?: string[];
  connectionType: ConnectionType;
  hasIntervalometer?: boolean;
}

interface AudioAccessory extends AccessoryBase {
  category: "audio";
  compatibleWith?: string[];
  micPattern?: MicPattern;
  connectionType?: ConnectionType;
}

interface StrapAccessory extends AccessoryBase {
  category: "strap";
  strapType: StrapType;

  // mm
  length?: number;

  material?: StrapMaterial;
}

interface PlateAccessory extends AccessoryBase {
  category: "plate";
  plateType?: PlateType;
  isArcaCompatible?: boolean;
}

interface PowerBankAccessory extends AccessoryBase {
  category: "power-bank";
  capacityMah: number;

  // Watts
  outputWatts?: number;

  hasUsbPD?: boolean;
}

// =============================================================================
// GENERIC — categories with no extra fields
// =============================================================================

interface GenericAccessory extends AccessoryBase {
  category:
    | "hand-grip"
    | "body-accessory"
    | "cooling"
    | "astro-gear"
    | "protection";
  compatibleWith?: string[];
}

// =============================================================================
// DISCRIMINATED UNION
// =============================================================================

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

// =============================================================================
// EXPORTS
// =============================================================================

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
  StrapMaterial,
  ConnectionType,
  MicPattern,
  TripodMaterial,
};
