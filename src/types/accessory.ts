import type { Mount } from "./lens";
import type { Genre } from "./genre";

/** Accessory category */
type AccessoryCategory =
  // Fuji-specific
  | "flash"
  | "battery-grip"
  | "hand-grip"
  | "power"
  | "lens-accessory"
  | "adapter"
  | "remote"
  | "audio"
  | "body-accessory"
  | "cooling"
  // Genre gear (universal, affiliate-driven)
  | "support"
  | "bag"
  | "filter"
  | "lighting"
  | "storage"
  | "astro-gear"
  | "protection";

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
  compatibleWith?: string[];
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

  // Support-specific (tripod, monopod)
  maxLoad?: number;
  foldedLength?: number;

  // Price
  price: number;

  // Links
  officialUrl?: string;
}

export type { Accessory, AccessoryCategory };
