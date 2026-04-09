import type { Mount } from "./lens";

/** Accessory category */
type AccessoryCategory =
  | "flash"
  | "battery-grip"
  | "hand-grip"
  | "power"
  | "lens-accessory"
  | "adapter"
  | "remote"
  | "audio"
  | "body-accessory"
  | "cooling";

/** Compatibility target — camera model, lens model, mount, or battery type */
type CompatTarget = string;

interface Accessory {
  // Identity
  brand: string;
  model: string;
  category: AccessoryCategory;
  year?: number;
  discontinued?: boolean;
  description: string;

  // Compatibility
  compatibleWith: CompatTarget[];
  mount?: Mount;

  // Physical
  weight?: number;
  weatherSealed?: boolean;

  // Flash-specific
  guideNumber?: number;
  ttl?: boolean;
  hss?: boolean;
  wirelessCommander?: boolean;
  wirelessReceiver?: boolean;

  // Teleconverter/extension-specific
  magnificationFactor?: number;
  afRetained?: boolean;

  // Power-specific
  batteryType?: string;
  batteryCount?: number;

  // Price
  price: number;

  // Links
  officialUrl?: string;
}

export type { Accessory, AccessoryCategory, CompatTarget };
