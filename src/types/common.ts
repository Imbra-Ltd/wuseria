/** Fujifilm lens/camera mount system */
type Mount = "X" | "GFX";

/** Known brands across lenses, cameras, and accessories */
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

type CardType = "SD" | "CFexpress";

type CardSpeedClass = "UHS-I" | "UHS-II" | "UHS-III";

/** Extends CardType with external storage media */
type StorageType = CardType | "SSD" | "HDD";

type BatteryType = "NP-W126" | "NP-W126S" | "NP-W235" | "NP-T125";

export type { Mount, Brand, CardType, CardSpeedClass, StorageType, BatteryType };
