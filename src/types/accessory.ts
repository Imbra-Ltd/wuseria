import type { Mount } from "./lens";
import type { Genre } from "./genre";

/** Accessory category — Fujifilm-specific */
type FujiAccessoryCategory =
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

/** Accessory category — genre gear (universal, affiliate-driven) */
type GenreGearCategory =
  | "tripod"
  | "tripod-head"
  | "monopod"
  | "bag"
  | "strap"
  | "filter"
  | "lighting"
  | "light-modifier"
  | "reflector"
  | "memory-card"
  | "external-storage"
  | "tethering"
  | "monitor"
  | "color-checker"
  | "star-tracker"
  | "lens-heater"
  | "rain-cover"
  | "cleaning";

type AccessoryCategory = FujiAccessoryCategory | GenreGearCategory;

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

  // Genre relevance — which genres recommend this accessory
  genres?: Genre[];

  // Compatibility
  compatibleWith?: CompatTarget[];
  mount?: Mount;
  universal?: boolean;

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

  // Filter-specific
  filterSize?: number;
  filterType?: string;

  // Tripod-specific
  maxLoad?: number;
  foldedLength?: number;

  // Price
  price: number;

  // Links
  officialUrl?: string;
}

export type {
  Accessory,
  AccessoryCategory,
  FujiAccessoryCategory,
  GenreGearCategory,
  CompatTarget,
};
