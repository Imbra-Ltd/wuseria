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
// STORAGE
// =============================================================================

type CardType = "SD" | "CFexpress";

type CardSpeedClass = "UHS-I" | "UHS-II" | "UHS-III";

// Extends CardType with external storage media
type StorageType = CardType | "SSD" | "HDD";

// =============================================================================
// BATTERY
// =============================================================================

type BatteryType = "NP-W126" | "NP-W126S" | "NP-W235" | "NP-T125";

// =============================================================================
// EXPORTS
// =============================================================================

export type { Mount, Brand, CardType, CardSpeedClass, StorageType, BatteryType };
