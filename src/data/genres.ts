import type { ScoredGenre, GenreConfig } from "../types/genre";
import type { EvScene } from "../types/common";

// =============================================================================
// GENRE CONFIGS — ported from prototype GENRE_PARAMS (App.jsx:427-436)
// =============================================================================

const genreConfigs: Record<ScoredGenre, GenreConfig> = {
  astro: {
    genre: "astro",
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
  astro: {
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
    16: "Snow field / bright beach",
    15: "Sunny open landscape",
    14: "Thin overcast",
    13: "Overcast sky",
    12: "Heavy overcast",
    11: "Mountain peaks at golden hour",
    10: "Lake reflection at dusk",
    9: "Coastal cliffs at blue hour",
    8: "Forest ridgeline at late twilight",
    7: "Dark valley / mountain silhouette",
  },
  architecture: {
    12: "Overcast exterior",
    11: "Golden hour / open shade",
    10: "Deep shade / glass atrium",
    9: "Bright interior / skylights",
    8: "Blue hour",
    7: "Indoor daylight",
    6: "Office / lobby",
    5: "Dim church / museum",
    4: "Night exterior",
    3: "Night interior",
  },
  street: {
    8: "Bright overcast city",
    7: "Open shade / cloudy",
    6: "Overcast street",
    5: "Covered market / indoor street",
    4: "Dusk / golden hour",
    3: "Late evening urban",
    2: "Night market / bright signage",
    1: "Lit street at night",
    0: "Night street, neon signs",
    [-1]: "Deep night, single streetlamp",
  },
  travel: {
    14: "Bright beach / snow",
    13: "Sunny open square",
    12: "Hazy sun / open shade",
    11: "Partly cloudy",
    10: "Overcast exterior",
    9: "Covered market / arcade",
    8: "Bright interior / atrium",
    7: "Dim interior / cafe",
    6: "Blue hour / dusk",
    5: "Golden hour street",
  },
  portrait: {
    14: "Bright sun / outdoor midday",
    13: "Slightly overcast",
    12: "Open shade / slight overcast",
    11: "Golden hour",
    10: "Window light",
    9: "Blue hour / shade",
    8: "Overcast exterior",
    7: "Bright interior / studio",
    6: "Indoor natural light",
    5: "Dim interior / candlelight",
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
};

// =============================================================================
// GENRE SCENE FILTER — EV range per genre (App.jsx:1964-1973)
// =============================================================================

const genreSceneFilter: Record<ScoredGenre, (ev: number) => boolean> = {
  astro: (ev) => ev <= 1,
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
// EXPORTS
// =============================================================================

export { genreConfigs, evScenes, genreEvLabels, genreSceneFilter };
