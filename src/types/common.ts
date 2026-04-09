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

/** Memory card type — used by Camera and StorageAccessory */
type CardType = "SD" | "CFexpress";

/** SD card speed class */
type CardSpeedClass = "UHS-I" | "UHS-II" | "UHS-III";

/** Storage media type — extends CardType with external storage */
type StorageType = CardType | "SSD" | "HDD";

/** Battery model — Fujifilm X and GFX systems */
type BatteryType = "NP-W126" | "NP-W126S" | "NP-W235" | "NP-T125";

export type { Mount, Brand, CardType, CardSpeedClass, StorageType, BatteryType };
