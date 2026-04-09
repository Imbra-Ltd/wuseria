import type { Mount } from "./lens";
import type { Genre } from "./genre";

// ---------------------------------------------------------------------------
// Base — truly universal fields that apply to every accessory
// ---------------------------------------------------------------------------

interface AccessoryBase {
  brand: string;
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

interface FlashAccessory extends AccessoryBase {
  category: "flash";
  mount?: Mount;
  compatibleWith?: string[];
  weatherSealed?: boolean;
  guideNumber: number;
  ttl: boolean;
  hss: boolean;
  wirelessCommander?: boolean;
  wirelessReceiver?: boolean;
}

interface LensAccessory extends AccessoryBase {
  category: "lens-accessory";
  mount?: Mount;
  compatibleWith?: string[];
  weatherSealed?: boolean;
  magnificationFactor?: number;
  afRetained?: boolean;
}

interface BatteryAccessory extends AccessoryBase {
  category: "battery";
  compatibleWith?: string[];
  batteryType: string;
  capacity?: number;
  voltage?: number;
}

interface ChargerAccessory extends AccessoryBase {
  category: "charger";
  compatibleWith?: string[];
  batteryType: string;
  slots?: number;
  usbInput?: boolean;
}

interface BatteryGripAccessory extends AccessoryBase {
  category: "battery-grip";
  mount?: Mount;
  compatibleWith?: string[];
  weatherSealed?: boolean;
  batteryType: string;
  batteryCount?: number;
  verticalControls?: boolean;
}

interface AdapterAccessory extends AccessoryBase {
  category: "adapter";
  compatibleWith?: string[];
  sourceMount: string;
  targetMount: string;
  afSupported?: boolean;
  apertureControl?: boolean;
}

interface TripodAccessory extends AccessoryBase {
  category: "tripod" | "monopod";
  maxLoad?: number;
  maxHeight?: number;
  foldedLength?: number;
  legSections?: number;
  material?: string;
}

interface HeadAccessory extends AccessoryBase {
  category: "tripod-head";
  headType: string;
  maxLoad?: number;
  plateType?: string;
}

interface FilterAccessory extends AccessoryBase {
  category: "filter";
  filterSize?: number;
  filterType: string;
}

interface LightingAccessory extends AccessoryBase {
  category: "lighting";
  colorTemp?: number;
  cri?: number;
  lumens?: number;
}

interface BagAccessory extends AccessoryBase {
  category: "bag";
  capacity?: number;
  bagType?: string;
}

interface StorageAccessory extends AccessoryBase {
  category: "storage";
  storageType: string;
  speed?: number;
  capacityGB?: number;
}

interface RemoteAccessory extends AccessoryBase {
  category: "remote";
  compatibleWith?: string[];
  connectionType: string;
  intervalometer?: boolean;
}

interface AudioAccessory extends AccessoryBase {
  category: "audio";
  compatibleWith?: string[];
  micPattern?: string;
  connectionType?: string;
}

interface StrapAccessory extends AccessoryBase {
  category: "strap";
  strapType: string;
  length?: number;
  material?: string;
}

interface PlateAccessory extends AccessoryBase {
  category: "plate";
  plateType?: string;
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
};
