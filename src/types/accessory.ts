import type { Mount } from "./lens";
import type { Genre } from "./genre";

// ---------------------------------------------------------------------------
// Base — shared fields on every accessory
// ---------------------------------------------------------------------------

interface AccessoryBase {
  brand: string;
  model: string;
  year?: number;
  discontinued?: boolean;
  description: string;
  genres?: Genre[];
  compatibleWith?: string[];
  mount?: Mount;
  universal?: boolean;
  weight?: number;
  weatherSealed?: boolean;
  price: number;
  officialUrl?: string;
}

// ---------------------------------------------------------------------------
// Category-specific extensions
// ---------------------------------------------------------------------------

interface FlashAccessory extends AccessoryBase {
  category: "flash";
  guideNumber: number;
  ttl: boolean;
  hss: boolean;
  wirelessCommander?: boolean;
  wirelessReceiver?: boolean;
}

interface LensAccessory extends AccessoryBase {
  category: "lens-accessory";
  magnificationFactor?: number;
  afRetained?: boolean;
}

interface BatteryAccessory extends AccessoryBase {
  category: "battery";
  batteryType: string;
  capacity?: number;
  voltage?: number;
}

interface ChargerAccessory extends AccessoryBase {
  category: "charger";
  batteryType: string;
  slots?: number;
  usbInput?: boolean;
}

interface BatteryGripAccessory extends AccessoryBase {
  category: "battery-grip";
  batteryType: string;
  batteryCount?: number;
  verticalControls?: boolean;
}

interface AdapterAccessory extends AccessoryBase {
  category: "adapter";
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
  connectionType: string;
  intervalometer?: boolean;
}

interface AudioAccessory extends AccessoryBase {
  category: "audio";
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
