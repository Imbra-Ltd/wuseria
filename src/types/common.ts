// =============================================================================
// MOUNT
// =============================================================================

type Mount = "X" | "GFX";

// =============================================================================
// BRAND
// =============================================================================

type Brand =
  | "Fujifilm"
  | "7Artisans"
  | "AstrHori"
  | "Carl Zeiss"
  | "Handevision"
  | "Irix"
  | "Kamlan"
  | "Kipon"
  | "Lensbaby"
  | "Meike"
  | "Meyer Optik"
  | "Mitakon"
  | "NiSi"
  | "Pergear"
  | "SLR Magic"
  | "Samyang"
  | "Sigma"
  | "Sirui"
  | "TTartisan"
  | "Tamron"
  | "Thingyfy"
  | "Tokina"
  | "Venus Laowa"
  | "Viltrox"
  | "Voigtlander";

// =============================================================================
// FOCAL LENGTH CATEGORY
// =============================================================================

type FlCategory = "ultra-wide" | "wide" | "standard" | "tele" | "super-tele";

// =============================================================================
// EV SCENE — standard photographic EV reference
// =============================================================================

interface EvScene {
  ev: number;
  short: string;
}

// =============================================================================
// STORAGE
// =============================================================================

type MemoryCardType = "SD" | "CFexpress";

type CardSpeedClass = "UHS-I" | "UHS-II" | "UHS-III";

// Extends MemoryCardType with external storage media
type StorageType = MemoryCardType | "SSD" | "HDD";

// =============================================================================
// BATTERY
// =============================================================================

type BatteryType = "NP-W126" | "NP-W126S" | "NP-W235" | "NP-T125";

// =============================================================================
// EXPORTS
// =============================================================================

export type {
  Mount,
  Brand,
  FlCategory,
  EvScene,
  MemoryCardType,
  CardSpeedClass,
  StorageType,
  BatteryType,
};
