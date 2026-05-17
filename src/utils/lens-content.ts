import type { Lens } from "../types/lens";
import type { Genre } from "../types/genre";
import { genreConfigs } from "../data/genres";
import {
  genreFormulas,
  computeOpticalQuality,
  OPTICAL_FIELDS,
  resolveField,
  type OpticalField,
  type ScoringField,
} from "./scoring";
import { toSlug } from "./slug";

// =============================================================================
// TYPES
// =============================================================================

interface GenreTier {
  label: string;
  genres: string[];
}

interface Summary {
  verdict: string;
  genreTiers: GenreTier[];
  strengths: string[];
  weaknesses: string[];
}

interface OpticalClusters {
  sharpness: FieldAssessment[];
  aberrations: FieldAssessment[];
  rendering: FieldAssessment[];
  distortion: FieldAssessment[];
}

interface FieldAssessment {
  field: string;
  phrase: string;
  isStrength: boolean;
}

interface GenreFitEntry {
  genre: Genre;
  name: string;
  mark: number;
  verdict: string;
  primary: FieldAssessment[];
  secondary: FieldAssessment[];
}

interface Alternative {
  brand: string;
  model: string;
  slug: string;
}

interface ContentSpine {
  summary: Summary;
  opticalClusters: OpticalClusters | null;
  genreFit: GenreFitEntry[];
  alternatives: Alternative[];
  metaDescription: string;
}

// =============================================================================
// PHRASE TABLES — score (0–2) → natural-language fragment
// =============================================================================

const FIELD_PHRASES: Record<OpticalField, Record<number, string>> = {
  centerWideOpen: {
    0: "very soft center performance wide open",
    0.5: "below-average center sharpness wide open",
    1: "acceptable center sharpness wide open",
    1.5: "good center sharpness wide open",
    2: "excellent center sharpness wide open",
  },
  cornerWideOpen: {
    0: "very soft corners wide open",
    0.5: "noticeably soft corners wide open",
    1: "acceptable corner sharpness wide open",
    1.5: "good corner performance wide open",
    2: "impressive corner sharpness even wide open",
  },
  centerStopped: {
    0: "disappointing center resolution stopped down",
    0.5: "below-average center resolution stopped down",
    1: "adequate center resolution stopped down",
    1.5: "good center resolution stopped down",
    2: "outstanding center resolution stopped down",
  },
  cornerStopped: {
    0: "poor corner-to-corner sharpness stopped down",
    0.5: "below-average corner sharpness stopped down",
    1: "acceptable corner sharpness stopped down",
    1.5: "good corner-to-corner sharpness stopped down",
    2: "excellent corner-to-corner sharpness stopped down",
  },
  longitudinalCA: {
    0: "heavy longitudinal CA (purple/green fringing on bokeh highlights)",
    0.5: "noticeable longitudinal CA on high-contrast edges",
    1: "moderate longitudinal CA, correctable in post",
    1.5: "well-controlled longitudinal CA",
    2: "virtually no longitudinal chromatic aberration",
  },
  lateralCA: {
    0: "strong lateral CA (color fringing toward frame edges)",
    0.5: "noticeable lateral CA toward the corners",
    1: "moderate lateral CA, auto-corrected by most software",
    1.5: "well-controlled lateral CA",
    2: "negligible lateral chromatic aberration",
  },
  coma: {
    0: "severe coma (point lights smear into wings at corners)",
    0.5: "noticeable coma in the corners wide open",
    1: "moderate coma at the extreme corners",
    1.5: "well-controlled coma",
    2: "negligible coma — point lights stay tight to the corners",
  },
  astigmatism: {
    0: "significant astigmatism affecting point-source rendering",
    0.5: "noticeable astigmatism in the corners",
    1: "moderate astigmatism",
    1.5: "well-controlled astigmatism",
    2: "negligible astigmatism",
  },
  sphericalAberration: {
    0: "strong spherical aberration reducing contrast wide open",
    0.5: "noticeable spherical aberration wide open",
    1: "moderate spherical aberration",
    1.5: "well-corrected spherical aberration",
    2: "excellent spherical aberration correction",
  },
  distortion: {
    0: "heavy distortion requiring software correction",
    0.5: "noticeable distortion visible in architectural subjects",
    1: "moderate distortion, handled by camera profiles",
    1.5: "minimal distortion",
    2: "negligible distortion — straight lines stay straight",
  },
  vignettingWideOpen: {
    0: "heavy vignetting wide open (2+ stops in corners)",
    0.5: "noticeable vignetting wide open",
    1: "moderate vignetting wide open, typical for the aperture class",
    1.5: "mild vignetting wide open",
    2: "minimal vignetting even wide open",
  },
  vignettingStopped: {
    0: "persistent vignetting even stopped down",
    0.5: "above-average residual vignetting stopped down",
    1: "moderate residual vignetting stopped down",
    1.5: "vignetting clears well when stopped down",
    2: "vignetting essentially gone by f/5.6",
  },
  bokeh: {
    0: "harsh, busy bokeh with distracting patterns",
    0.5: "below-average bokeh quality",
    1: "acceptable bokeh rendering",
    1.5: "smooth, pleasant bokeh",
    2: "exceptionally smooth, creamy bokeh",
  },
  flareResistance: {
    0: "poor flare resistance — ghosting and veiling flare with backlight",
    0.5: "below-average flare resistance",
    1: "acceptable flare resistance with modern coatings",
    1.5: "good flare resistance",
    2: "excellent flare resistance — backlit scenes handled confidently",
  },
};

// What each genre demands (SEO-rich descriptions)
const GENRE_PRIORITIES: Record<Genre, string> = {
  nightscape:
    "coma control, astigmatism correction, and a fast aperture for short star exposures",
  landscape:
    "corner-to-corner sharpness at stopped-down apertures and good flare resistance",
  architecture:
    "geometric precision with minimal distortion and even corner sharpness",
  portrait:
    "smooth bokeh and critical center sharpness wide open for subject isolation",
  street:
    "sharp stopped-down performance and a fast enough aperture for low light",
  travel: "balanced image quality in a lightweight package",
  sport:
    "sharp wide-open center performance to freeze action at fast shutter speeds",
  wildlife: "center sharpness across apertures for distant subjects",
  macro:
    "stopped-down center sharpness and high magnification for close-up detail",
};

// =============================================================================
// HELPERS
// =============================================================================

function fieldPhrase(field: OpticalField, score: number): string {
  const phrases = FIELD_PHRASES[field];
  if (score >= 2) return phrases[2];
  if (score >= 1.5) return phrases[1.5];
  if (score >= 1) return phrases[1];
  if (score >= 0.5) return phrases[0.5];
  return phrases[0];
}

function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function cropFactor(mount: string): number {
  return mount === "GFX" ? 0.79 : 1.5;
}

function equivFl(fl: number, mount: string): number {
  return Math.round(fl * cropFactor(mount));
}

function flCategory(equivMm: number): string {
  if (equivMm <= 24) return "ultra-wide";
  if (equivMm <= 35) return "wide-angle";
  if (equivMm <= 60) return "standard";
  if (equivMm <= 105) return "short telephoto";
  if (equivMm <= 200) return "telephoto";
  return "super-telephoto";
}

function verdictAdjective(oq: number): string {
  if (oq >= 1.8) return "an outstanding";
  if (oq >= 1.5) return "a strong";
  if (oq >= 1) return "a solid";
  if (oq >= 0.5) return "a mixed";
  return "a compromised";
}

function isDerived(field: ScoringField): boolean {
  return field.startsWith("_");
}

/** Human-readable label for an optical field. */
function fieldLabel(field: OpticalField): string {
  const labels: Record<OpticalField, string> = {
    centerWideOpen: "Center sharpness (wide open)",
    cornerWideOpen: "Corner sharpness (wide open)",
    centerStopped: "Center sharpness (stopped down)",
    cornerStopped: "Corner sharpness (stopped down)",
    longitudinalCA: "Longitudinal CA",
    lateralCA: "Lateral CA",
    coma: "Coma",
    astigmatism: "Astigmatism",
    sphericalAberration: "Spherical aberration",
    distortion: "Distortion",
    vignettingWideOpen: "Vignetting (wide open)",
    vignettingStopped: "Vignetting (stopped down)",
    bokeh: "Bokeh",
    flareResistance: "Flare resistance",
  };
  return labels[field];
}

// =============================================================================
// CLUSTER FIELD GROUPS
// =============================================================================

const SHARPNESS_FIELDS: OpticalField[] = [
  "centerWideOpen",
  "cornerWideOpen",
  "centerStopped",
  "cornerStopped",
];
const ABERRATION_FIELDS: OpticalField[] = [
  "longitudinalCA",
  "lateralCA",
  "coma",
  "astigmatism",
  "sphericalAberration",
];

function clusterAverage(lens: Lens, fields: OpticalField[]): number | null {
  const vals = fields.map((f) => lens[f]).filter((v): v is number => v != null);
  if (vals.length === 0) return null;
  return vals.reduce((a, b) => a + b, 0) / vals.length;
}

// =============================================================================
// SUMMARY
// =============================================================================

function generateVerdict(lens: Lens): string {
  const oq = computeOpticalQuality(lens);
  const equiv = equivFl(lens.focalLengthMin, lens.mount);
  const category = flCategory(equiv);

  if (oq != null) {
    return (
      `The ${lens.brand} ${lens.model} is ${verdictAdjective(oq)} optical performer — ` +
      `a ${category} ${lens.type} (${equiv}mm equivalent) ` +
      `with f/${lens.maxAperture} maximum aperture.`
    );
  }

  const flDesc =
    lens.type === "zoom"
      ? `${lens.focalLengthMin}-${lens.focalLengthMax}mm`
      : `${lens.focalLengthMin}mm`;
  return (
    `The ${lens.brand} ${lens.model} is a ${flDesc} ${category} ${lens.type} ` +
    `(${equiv}mm equivalent) with f/${lens.maxAperture} maximum aperture.`
  );
}

const TIER_LABELS = ["Excellent for", "Adequate for", "Avoid for"] as const;

function tierForMark(mark: number): string {
  if (mark >= 4) return TIER_LABELS[0];
  if (mark >= 2.5) return TIER_LABELS[1];
  return TIER_LABELS[2];
}

function generateGenreTiers(lens: Lens): GenreTier[] {
  if (!lens.genreMarks) return [];

  const groups: Record<string, string[]> = {};
  const genreOrder = Object.keys(genreConfigs) as Genre[];

  for (const genre of genreOrder) {
    const mark = lens.genreMarks[genre];
    if (mark == null) continue;
    const name = genreConfigs[genre].name.replace(" Photography", "");
    const tier = tierForMark(mark);
    if (!groups[tier]) groups[tier] = [];
    groups[tier].push(name);
  }

  return TIER_LABELS.filter((l) => groups[l]).map((l) => ({
    label: l,
    genres: groups[l],
  }));
}

function clusterStrength(
  lens: Lens,
  fields: OpticalField[],
  high: string,
  low: string,
): string | null {
  const avg = clusterAverage(lens, fields);
  if (avg == null || avg < 1.5) return null;
  return avg >= 1.8 ? high : low;
}

function generateStrengths(lens: Lens): string[] {
  const strengths: string[] = [];

  const sharp = clusterStrength(
    lens,
    SHARPNESS_FIELDS,
    "Excellent sharpness at all apertures",
    "Good overall sharpness",
  );
  if (sharp) strengths.push(sharp);

  const aber = clusterStrength(
    lens,
    ABERRATION_FIELDS,
    "Negligible optical aberrations",
    "Well-controlled aberrations",
  );
  if (aber) strengths.push(aber);

  if (lens.bokeh != null && lens.bokeh >= 1.5) {
    strengths.push(
      lens.bokeh >= 2 ? "Exceptionally smooth bokeh" : "Smooth, pleasant bokeh",
    );
  }
  if (lens.flareResistance != null && lens.flareResistance >= 1.5) {
    strengths.push("Good flare resistance");
  }
  if (lens.distortion != null && lens.distortion >= 1.5) {
    strengths.push("Negligible distortion");
  }
  if (lens.isWeatherSealed) strengths.push("Weather-sealed construction");
  if (lens.afMotor === "LM") strengths.push("Fast linear motor autofocus");
  if (lens.hasOis) strengths.push("Built-in optical stabilization");

  return strengths;
}

function generateWeaknesses(lens: Lens): string[] {
  const weaknesses: string[] = [];

  for (const field of OPTICAL_FIELDS) {
    const val = lens[field];
    if (val != null && val <= 0.5) {
      weaknesses.push(capitalize(fieldPhrase(field, val)));
    }
  }
  if (
    lens.maxMagnification != null &&
    lens.maxMagnification < 0.15 &&
    !lens.isTiltShift
  ) {
    weaknesses.push(
      `Low macro capability (${lens.maxMagnification}x magnification)`,
    );
  }
  if (!lens.hasOis && lens.focalLengthMax >= 50) {
    weaknesses.push("No built-in optical stabilization");
  }

  return weaknesses;
}

function generateSummary(lens: Lens): Summary {
  return {
    verdict: generateVerdict(lens),
    genreTiers: generateGenreTiers(lens),
    strengths: generateStrengths(lens),
    weaknesses: generateWeaknesses(lens),
  };
}

// =============================================================================
// OPTICAL QUALITY CLUSTERS
// =============================================================================

const RENDERING_FIELDS: OpticalField[] = [
  "bokeh",
  "vignettingWideOpen",
  "vignettingStopped",
  "flareResistance",
];

function assessCluster(lens: Lens, fields: OpticalField[]): FieldAssessment[] {
  return fields
    .map((f) => {
      const val = lens[f];
      if (val == null) return null;
      return {
        field: fieldLabel(f),
        phrase: capitalize(fieldPhrase(f, val)),
        isStrength: val >= 1.5,
      };
    })
    .filter((a): a is FieldAssessment => a != null);
}

function generateOpticalClusters(lens: Lens): OpticalClusters | null {
  const hasAny = OPTICAL_FIELDS.some((f) => lens[f] != null);
  if (!hasAny) return null;

  return {
    sharpness: assessCluster(lens, SHARPNESS_FIELDS),
    aberrations: assessCluster(lens, ABERRATION_FIELDS),
    rendering: assessCluster(lens, RENDERING_FIELDS),
    distortion: assessCluster(lens, ["distortion"]),
  };
}

// =============================================================================
// GENRE FIT
// =============================================================================

function derivedPhrase(
  lens: Lens,
  field: ScoringField,
  isStrength: boolean,
): string {
  if (field === "_apertureScore") {
    return isStrength
      ? `Fast f/${lens.maxAperture} aperture`
      : `Slow f/${lens.maxAperture} aperture`;
  }
  if (field === "_weightScore") {
    return isStrength
      ? `Lightweight at ${lens.weight}g`
      : `Heavy at ${lens.weight}g`;
  }
  if (field === "_magnificationScore" && lens.maxMagnification != null) {
    return isStrength
      ? `${lens.maxMagnification}x magnification`
      : `Low magnification (${lens.maxMagnification}x)`;
  }
  return "No data";
}

function assessField(lens: Lens, field: ScoringField): FieldAssessment | null {
  const val = resolveField(lens, field);
  if (val == null) return null;

  const isStrength = val >= 1.5;

  if (isDerived(field)) {
    return {
      field: field.slice(1),
      phrase: derivedPhrase(lens, field, isStrength),
      isStrength,
    };
  }

  const optField = field as OpticalField;
  return {
    field: fieldLabel(optField),
    phrase: capitalize(fieldPhrase(optField, val)),
    isStrength,
  };
}

function generateGenreFit(lens: Lens): GenreFitEntry[] {
  if (!lens.genreMarks) return [];

  const entries: GenreFitEntry[] = [];

  for (const [genre, mark] of Object.entries(lens.genreMarks) as [
    Genre,
    number,
  ][]) {
    const config = genreConfigs[genre];
    const formula = genreFormulas[genre];

    // Verdict — states what the genre needs, no judgment (score speaks)
    const verdict = `${config.name} prioritizes ${GENRE_PRIORITIES[genre]}.`;

    // Assess primary and secondary fields separately
    const primary = formula.primary
      .map((f) => assessField(lens, f))
      .filter((a): a is FieldAssessment => a != null);

    const secondary = formula.secondary
      .map((f) => assessField(lens, f))
      .filter((a): a is FieldAssessment => a != null);

    entries.push({
      genre,
      name: config.name,
      mark,
      verdict,
      primary,
      secondary,
    });
  }

  // Fixed genre order matching site navigation
  const genreOrder = Object.keys(genreConfigs) as Genre[];
  entries.sort(
    (a, b) => genreOrder.indexOf(a.genre) - genreOrder.indexOf(b.genre),
  );
  return entries;
}

// =============================================================================
// ALTERNATIVES
// =============================================================================

function sortByOQ(a: Lens, b: Lens): number {
  const oqA = computeOpticalQuality(a);
  const oqB = computeOpticalQuality(b);
  if (oqA == null && oqB == null) return 0;
  if (oqA == null) return 1;
  if (oqB == null) return -1;
  return oqB - oqA;
}

function findAlternatives(lens: Lens, allLenses: Lens[]): Alternative[] {
  const mid = (lens.focalLengthMin + lens.focalLengthMax) / 2;
  const isSameType = (other: Lens): boolean => other.type === lens.type;

  const candidates = allLenses.filter((other) => {
    if (other.model === lens.model || other.mount !== lens.mount) return false;
    if (other.isDiscontinued) return false;
    // Must cover the lens FL or be within ±20%
    const margin = mid * 0.2;
    const coversFL = other.focalLengthMin <= mid && other.focalLengthMax >= mid;
    const nearFL =
      Math.abs(other.focalLengthMin - mid) <= margin ||
      Math.abs(other.focalLengthMax - mid) <= margin;
    if (!coversFL && !nearFL) return false;
    // Reject superzooms (>4x range) — they're not direct alternatives
    const zoomRatio = other.focalLengthMax / other.focalLengthMin;
    if (zoomRatio > 4) return false;
    return true;
  });

  // Same type first (up to 5), then other type (up to 3)
  const sameType = candidates.filter(isSameType).sort(sortByOQ).slice(0, 5);
  const otherType = candidates
    .filter((c) => !isSameType(c))
    .sort(sortByOQ)
    .slice(0, 3);

  return [...sameType, ...otherType].map((other) => ({
    brand: other.brand,
    model: other.model,
    slug: toSlug(`${other.brand} ${other.model}`),
  }));
}

// =============================================================================
// META DESCRIPTION
// =============================================================================

function generateMetaDescription(lens: Lens): string {
  const oq = computeOpticalQuality(lens);
  const topGenre = lens.genreMarks
    ? (Object.entries(lens.genreMarks) as [Genre, number][]).sort(
        (a, b) => b[1] - a[1],
      )[0]
    : null;

  const parts = [
    `Is the ${lens.brand} ${lens.model} right for your photography?`,
  ];
  if (oq != null) {
    let adj = "Mixed";
    if (oq >= 1.8) adj = "Outstanding";
    else if (oq >= 1.5) adj = "Strong";
    else if (oq >= 1) adj = "Solid";
    parts.push(`${adj} optics.`);
  }
  if (topGenre) {
    parts.push(
      `${topGenre[1]}/5 for ${genreConfigs[topGenre[0]].name.toLowerCase()}.`,
    );
  }
  parts.push("Specs, optical scores, and alternatives.");
  return parts.join(" ");
}

// =============================================================================
// MAIN
// =============================================================================

function generateLensContent(lens: Lens, allLenses: Lens[]): ContentSpine {
  return {
    summary: generateSummary(lens),
    opticalClusters: generateOpticalClusters(lens),
    genreFit: generateGenreFit(lens),
    alternatives: findAlternatives(lens, allLenses),
    metaDescription: generateMetaDescription(lens),
  };
}

// =============================================================================
// EXPORTS
// =============================================================================

export { generateLensContent };
export type {
  ContentSpine,
  GenreFitEntry,
  FieldAssessment,
  Alternative,
  Summary,
  OpticalClusters,
};
