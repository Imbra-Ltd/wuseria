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

export type { Mount, Brand, CardType, CardSpeedClass };
