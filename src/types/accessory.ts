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

interface PowerAccessory extends AccessoryBase {
  category: "power";
  batteryType: string;
  batteryCount?: number;
}

interface SupportAccessory extends AccessoryBase {
  category: "support";
  maxLoad?: number;
  foldedLength?: number;
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

// ---------------------------------------------------------------------------
// Generic — categories with no extra fields
// ---------------------------------------------------------------------------

interface GenericAccessory extends AccessoryBase {
  category:
    | "battery-grip"
    | "hand-grip"
    | "adapter"
    | "remote"
    | "audio"
    | "body-accessory"
    | "cooling"
    | "bag"
    | "storage"
    | "astro-gear"
    | "protection";
}

// ---------------------------------------------------------------------------
// Discriminated union — narrows by category
// ---------------------------------------------------------------------------

type Accessory =
  | FlashAccessory
  | LensAccessory
  | PowerAccessory
  | SupportAccessory
  | FilterAccessory
  | LightingAccessory
  | GenericAccessory;

type AccessoryCategory = Accessory["category"];

export type {
  Accessory,
  AccessoryCategory,
  AccessoryBase,
  FlashAccessory,
  LensAccessory,
  PowerAccessory,
  SupportAccessory,
  FilterAccessory,
  LightingAccessory,
  GenericAccessory,
};
