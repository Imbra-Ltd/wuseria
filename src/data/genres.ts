import type { ScoredGenre, GenreConfig } from "../types/genre";
import type { EvScene } from "../types/common";

// =============================================================================
// GENRE CONFIGS — ported from prototype GENRE_PARAMS (App.jsx:427-436)
// =============================================================================

const genreConfigs: Record<ScoredGenre, GenreConfig> = {
  nightscape: {
    genre: "nightscape",
    name: "Nightscape Photography",
    tagline: "Untracked tripod · Beat the startrails · 500 rule",
    description:
      "Stars, Milky Way, and night landscapes on a fixed tripod. Low coma, low astigmatism, and fast apertures matter most.",
    typicalFl: ["ultra-wide", "wide"],
  },
  landscape: {
    genre: "landscape",
    name: "Landscape Photography",
    tagline: "Tripod · creative exposure control · peak sharpness",
    description:
      "Sharp from corner to corner at the sweet-spot aperture. Resolution and flare resistance count.",
    typicalFl: ["ultra-wide", "wide"],
  },
  architecture: {
    genre: "architecture",
    name: "Architecture Photography",
    tagline: "Tripod · maximize depth of field · sweet spot at f/8",
    description:
      "Geometric precision with minimal distortion and corner-to-corner sharpness at stopped-down apertures.",
    typicalFl: ["ultra-wide", "wide"],
  },
  street: {
    genre: "street",
    name: "Street Photography",
    tagline: "Handheld · capture the moment · 1/FL rule",
    description:
      "Sharp at the sweet spot and fast enough for low light. Stopped-down sharpness and wide aperture matter most.",
    typicalFl: ["wide", "standard"],
  },
  travel: {
    genre: "travel",
    name: "Travel Photography",
    tagline: "Handheld · light and versatile · 1/FL rule",
    description:
      "Versatile coverage in a light kit. Balance between image quality, weight, and focal-length range.",
    typicalFl: ["wide", "standard"],
  },
  portrait: {
    genre: "portrait",
    name: "Portrait Photography",
    tagline: "Handheld · freeze expression · 2x FL rule",
    description:
      "Smooth bokeh, flattering compression, and critical sharpness on the eyes. Subject isolation is key.",
    typicalFl: ["standard", "tele"],
  },
  sport: {
    genre: "sport",
    name: "Sport Photography",
    tagline: "Handheld · freeze motion · 4x FL rule",
    description:
      "Sharp wide open to freeze action at fast shutter speeds. Wide-open center sharpness matters most.",
    typicalFl: ["standard", "tele"],
  },
  wildlife: {
    genre: "wildlife",
    name: "Wildlife Photography",
    tagline: "Handheld · capture behaviour · 4x FL rule",
    description:
      "Sharp both wide open and stopped down for distant subjects. Center sharpness across apertures matters most.",
    typicalFl: ["tele", "super-tele"],
  },
  macro: {
    genre: "macro",
    name: "Macro Photography",
    tagline: "Tripod · maximize magnification · peak sharpness",
    description:
      "Close-up imaging of small subjects. Magnification ratio and center sharpness at stopped-down apertures matter most.",
    typicalFl: ["standard", "tele"],
  },
};

// =============================================================================
// EV SCENES — ported from prototype EV_SCENES (App.jsx:308-336)
// =============================================================================

const evScenes: EvScene[] = [
  { ev: 18, short: "Bright reflections" },
  { ev: 17, short: "White in bright sun" },
  { ev: 16, short: "Sand or snow" },
  { ev: 15, short: "Bright or hazy sun" },
  { ev: 14, short: "Slightly overcast" },
  { ev: 13, short: "Overcast" },
  { ev: 12, short: "Heavy overcast" },
  { ev: 11, short: "Sunset / deep shade" },
  { ev: 10, short: "Just after sunset" },
  { ev: 9, short: "10 min after sunset" },
  { ev: 8, short: "Times Square at night" },
  { ev: 7, short: "Bright street at night" },
  { ev: 6, short: "Night interior (bright)" },
  { ev: 5, short: "Night interior (average)" },
  { ev: 4, short: "Bright street lamps" },
  { ev: 3, short: "Brightly lit night streets" },
  { ev: 2, short: "Typical night streets" },
  { ev: 1, short: "City center" },
  { ev: 0, short: "Bright suburb" },
  { ev: -1, short: "Suburb" },
  { ev: -2, short: "Full moon" },
  { ev: -3, short: "Rural town" },
  { ev: -4, short: "Rural" },
  { ev: -5, short: "Dark rural" },
  { ev: -6, short: "Dark site" },
  { ev: -7, short: "Excellent dark site" },
  { ev: -8, short: "Pristine dark site" },
];

// =============================================================================
// GENRE EV LABELS — per-genre overrides (App.jsx:339-424)
// =============================================================================

const genreEvLabels: Partial<Record<ScoredGenre, Record<number, string>>> = {
  nightscape: {
    1: "City center (Bortle 8-9)",
    0: "Bright suburb (Bortle 7)",
    [-1]: "Suburb (Bortle 6)",
    [-2]: "Full moon (any site, ~Bortle 5-6)",
    [-3]: "Rural town (Bortle 5)",
    [-4]: "Rural (Bortle 4)",
    [-5]: "Dark rural (Bortle 3)",
    [-6]: "Dark site (Bortle 2)",
    [-7]: "Excellent dark site (Bortle 1, solar max)",
    [-8]: "Pristine dark site (Bortle 1, solar min)",
  },
  landscape: {
    16: "Snow / bright beach",
    15: "Sunny landscape",
    14: "Thin overcast",
    13: "Overcast sky",
    12: "Heavy overcast",
    11: "Golden hour",
    10: "Dusk / reflection",
    9: "Blue hour",
    8: "Late twilight",
    7: "Dark valley",
  },
  architecture: {
    12: "Overcast exterior",
    11: "Golden hour",
    10: "Deep shade / atrium",
    9: "Bright interior",
    8: "Blue hour",
    7: "Indoor daylight",
    6: "Office / lobby",
    5: "Dim church",
    4: "Night exterior",
    3: "Night interior",
  },
  street: {
    8: "Bright overcast",
    7: "Open shade",
    6: "Overcast street",
    5: "Covered market",
    4: "Dusk / golden hour",
    3: "Late evening",
    2: "Night market",
    1: "Lit street",
    0: "Neon signs",
    [-1]: "Deep night",
  },
  travel: {
    14: "Bright beach / snow",
    13: "Sunny open square",
    12: "Hazy / open shade",
    11: "Partly cloudy",
    10: "Overcast exterior",
    9: "Covered market",
    8: "Bright interior",
    7: "Dim interior / cafe",
    6: "Blue hour / dusk",
    5: "Golden hour street",
  },
  portrait: {
    14: "Bright sun",
    13: "Slightly overcast",
    12: "Open shade",
    11: "Golden hour",
    10: "Window light",
    9: "Blue hour",
    8: "Overcast exterior",
    7: "Studio / interior",
    6: "Natural light",
    5: "Dim / candlelight",
  },
  sport: {
    16: "Bright sun / stadium",
    15: "Sunny outdoor",
    14: "Slightly overcast",
    13: "Overcast outdoor",
    12: "Heavy overcast",
    11: "Golden hour",
    10: "Indoor arena (bright)",
    9: "Indoor arena (average)",
    8: "Indoor gym",
    6: "Dim indoor / swimming",
  },
  wildlife: {
    14: "Bright sun / open field",
    13: "Slightly overcast",
    12: "Open shade",
    11: "Golden hour",
    10: "Sunset",
    9: "Blue hour",
    8: "Forest clearing",
    7: "Dense forest",
    6: "Dusk / low light",
    5: "Near darkness",
  },
  macro: {
    14: "Direct sun",
    13: "Overcast / flash",
    12: "Shade / ring flash",
    11: "Diffused flash",
    10: "Overcast garden",
    9: "Shaded foliage",
    8: "Deep shade / forest",
    7: "Indoor window",
    6: "Dim natural light",
    5: "Aquarium / tank",
  },
};

// =============================================================================
// GENRE SCENE FILTER — EV range per genre (App.jsx:1964-1973)
// =============================================================================

const genreSceneFilter: Record<ScoredGenre, (ev: number) => boolean> = {
  nightscape: (ev) => ev <= 1,
  landscape: (ev) => ev >= 7 && ev <= 16,
  architecture: (ev) => ev >= 3 && ev <= 12,
  street: (ev) => ev >= -1 && ev <= 8,
  travel: (ev) => ev >= 5 && ev <= 14,
  portrait: (ev) => ev >= 5 && ev <= 14,
  sport: (ev) => ev >= 6 && ev <= 16,
  wildlife: (ev) => ev >= 5 && ev <= 14,
  macro: (ev) => ev >= 5 && ev <= 14,
};

// =============================================================================
// MACRO MAGNIFICATION OPTIONS
// =============================================================================

const MACRO_MAGNIFICATION_OPTIONS = [
  { label: "0.25×", value: 0.25 },
  { label: "0.5×", value: 0.5 },
  { label: "1.0×", value: 1.0 },
  { label: "1.4×", value: 1.4 },
  { label: "2.0×", value: 2.0 },
];

// =============================================================================
// ND FILTER OPTIONS
// =============================================================================

const ND_OPTIONS = [
  { label: "ND2", factor: 2 },
  { label: "ND4", factor: 4 },
  { label: "ND8", factor: 8 },
  { label: "ND64", factor: 64 },
  { label: "ND1000", factor: 1000 },
];

// =============================================================================
// FL CHIPS — per-genre focal-length presets
// =============================================================================

// APS-C (X-mount, crop 1.5)
const FL_CHIPS_X: Record<string, { label: string; fl: number }[]> = {
  default: [
    { label: "Ultra-wide", fl: 12 },
    { label: "Wide", fl: 24 },
    { label: "Standard", fl: 50 },
    { label: "Tele", fl: 135 },
    { label: "Super-tele", fl: 300 },
  ],
  portrait: [
    { label: "Group", fl: 15 },
    { label: "Indoor", fl: 33 },
    { label: "Outdoor", fl: 57 },
  ],
  sportWildlife: [
    { label: "Standard", fl: 50 },
    { label: "Tele", fl: 135 },
    { label: "Super-tele", fl: 300 },
  ],
  macro: [
    { label: "Standard", fl: 50 },
    { label: "Tele", fl: 90 },
    { label: "Long macro", fl: 200 },
  ],
};

// GFX (medium format, crop 0.79)
const FL_CHIPS_GFX: Record<string, { label: string; fl: number }[]> = {
  default: [
    { label: "Ultra-wide", fl: 23 },
    { label: "Wide", fl: 35 },
    { label: "Standard", fl: 63 },
    { label: "Tele", fl: 200 },
    { label: "Super-tele", fl: 500 },
  ],
  portrait: [
    { label: "Group", fl: 23 },
    { label: "Indoor", fl: 55 },
    { label: "Outdoor", fl: 80 },
  ],
  sportWildlife: [
    { label: "Standard", fl: 63 },
    { label: "Tele", fl: 200 },
    { label: "Super-tele", fl: 500 },
  ],
  macro: [
    { label: "Standard", fl: 63 },
    { label: "Tele", fl: 120 },
    { label: "Long macro", fl: 200 },
  ],
};

// =============================================================================
// FL RANGES — lens must overlap the range to show
// =============================================================================

// APS-C: Ultra-wide 6-15mm, Wide 16-27mm, Standard 28-56mm, Tele 57-150mm, Super-tele 151+
const FL_RANGES_X: Record<number, [number, number]> = {
  12:  [6, 15],      // Ultra-wide
  15:  [12, 24],     // Portrait group
  24:  [16, 27],     // Wide
  33:  [24, 45],     // Portrait indoor
  50:  [28, 56],     // Standard
  57:  [40, 75],     // Portrait outdoor
  90:  [57, 150],    // Tele / macro tele
  135: [57, 150],    // Tele
  200: [100, 300],   // Long macro
  300: [151, 600],   // Super-tele
};

// GFX: Ultra-wide 14-30mm, Wide 31-45mm, Standard 46-90mm, Tele 91-250mm, Super-tele 251+
const FL_RANGES_GFX: Record<number, [number, number]> = {
  23:  [14, 30],     // Ultra-wide
  35:  [31, 45],     // Wide
  55:  [31, 60],     // Portrait indoor
  63:  [46, 90],     // Standard
  80:  [50, 100],    // Portrait outdoor
  120: [91, 250],    // Tele / macro tele
  200: [91, 250],    // Tele
  500: [251, 600],   // Super-tele
};

// =============================================================================
// GENRE DEFAULTS — initial EV, ISO, FL per genre
// =============================================================================

const GENRE_DEFAULTS: Record<ScoredGenre, { ev: number; iso: number; fl: number }> = {
  nightscape:   { ev: -7, iso: 3200, fl: 12 },
  landscape:    { ev: 9,  iso: 100,  fl: 24 },
  architecture: { ev: 7,  iso: 200,  fl: 12 },
  street:       { ev: 2,  iso: 6400, fl: 24 },
  travel:       { ev: 6,  iso: 400,  fl: 24 },
  portrait:     { ev: 7,  iso: 200,  fl: 50 },
  sport:        { ev: 8,  iso: 800,  fl: 135 },
  wildlife:     { ev: 10, iso: 3200, fl: 300 },
  macro:        { ev: 10, iso: 200,  fl: 90 },
};

// =============================================================================
// GENRE EQUIPMENT — recommended gear per genre
// =============================================================================

const GENRE_EQUIPMENT: Record<string, string[]> = {
  nightscape:   ["Star tracker", "Sturdy tripod", "Lens heater", "Dew shield", "Light pollution filter", "External power bank", "Remote intervalometer", "Bahtinov mask", "Spare batteries", "Red light headlamp"],
  landscape:    ["Sturdy tripod", "Ball head", "L-bracket", "Remote shutter", "Filter set (CPL & ND)", "Graduated ND filter", "Rain cover", "Spare batteries", "Fast memory cards", "Outdoor camera backpack"],
  architecture: ["Sturdy tripod", "Geared tripod head", "L-bracket", "Remote shutter", "Tethering cable", "Field monitor", "Filter set (CPL & Graduated ND)", "Anti-reflective lens cover", "Color checker", "Power bank"],
  street:       ["Thumb grip", "Compact bag", "Quick-adjust sling strap", "Mini travel tripod", "Flash (Compact)", "Filter set (ND, CPL & Black Mist)", "Fast memory cards", "Spare batteries", "Soft shutter release button", "Rain cover"],
  travel:       ["Travel tripod", "Adjustable sling strap", "Travel camera backpack", "L-bracket", "Filter set (ND & Polarizer)", "Anti-reflection hood", "Remote shutter", "Fast memory cards", "Spare batteries", "Portable SSD"],
  portrait:     ["Tripod", "Speedlight", "Flash trigger", "Light stand", "Constant light", "Light modifiers", "Reflector", "Tethering cable", "Color checker", "Remote shutter"],
  sport:        ["Monopod", "Battery grip", "Dual harness", "Teleconverter", "Remote trigger", "Fast memory cards", "Spare batteries", "Rain cover", "Power bank", "Camera gear bag"],
  wildlife:     ["Gimbal head", "Tripod/Monopod", "Teleconverter", "Beanbag", "Shoulder sling strap", "Lens covers", "Fast memory cards", "Spare batteries", "Power bank", "Wildlife backpack"],
  macro:        ["Sturdy tripod", "Macro rail", "Ring flash", "Diffuser", "Extension tubes", "Remote shutter", "Reflector", "Focus stacking software", "Spare batteries", "Macro shooting tent"],
};

// =============================================================================
// NIGHTSCAPE ISO BY EV — suggested ISO per EV for nightscape, balanced at f/2.8
// =============================================================================

const NIGHTSCAPE_ISO_BY_EV: Record<number, number> = {
  1: 100, 0: 200, [-1]: 200, [-2]: 400, [-3]: 400,
  [-4]: 800, [-5]: 1600, [-6]: 1600, [-7]: 3200, [-8]: 6400,
};

// =============================================================================
// EXPOSURE MATRIX CONSTANTS — focal lengths and apertures for nightscape grid
// =============================================================================

// APS-C matrix FL columns (keyed by FL chip value)
const MATRIX_FL_COLS_X: Record<number, number[]> = {
  12:  [8, 10, 12, 14],
  15:  [12, 15, 18, 23],
  24:  [16, 18, 23, 27],
  33:  [24, 33, 35, 50],
  50:  [33, 35, 50, 56],
  57:  [40, 50, 57, 75],
  90:  [60, 80, 90, 100],
  135: [60, 80, 90, 100, 135],
  200: [100, 135, 200, 300],
  300: [150, 200, 300, 400],
};

// GFX matrix FL columns (keyed by FL chip value)
const MATRIX_FL_COLS_GFX: Record<number, number[]> = {
  23:  [20, 23, 30, 35],
  35:  [32, 35, 45, 50],
  55:  [35, 45, 55, 63],
  63:  [45, 55, 63, 80],
  80:  [55, 63, 80, 100],
  120: [80, 100, 120, 200],
  200: [100, 120, 200, 250],
  500: [250, 500],
};

const MATRIX_APERTURES = [1.0, 1.4, 2.0, 2.8, 4.0, 5.6, 8, 11];

// =============================================================================
// EXPORTS
// =============================================================================

export {
  genreConfigs,
  evScenes,
  genreEvLabels,
  genreSceneFilter,
  MACRO_MAGNIFICATION_OPTIONS,
  ND_OPTIONS,
  FL_CHIPS_X,
  FL_CHIPS_GFX,
  FL_RANGES_X,
  FL_RANGES_GFX,
  GENRE_DEFAULTS,
  GENRE_EQUIPMENT,
  NIGHTSCAPE_ISO_BY_EV,
  MATRIX_FL_COLS_X,
  MATRIX_FL_COLS_GFX,
  MATRIX_APERTURES,
};
