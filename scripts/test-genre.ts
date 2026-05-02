import { lenses } from "../src/data/lenses";

const genre = process.argv[2] || "landscape";

const genres: Record<string, { primary: string[]; secondary: string[] }> = {
  nightscape: {
    primary: ["coma", "astigmatism", "_apertureScore"],
    secondary: [
      "lateralCA",
      "centerWideOpen",
      "cornerWideOpen",
      "longitudinalCA",
      "vignettingWideOpen",
      "sphericalAberration",
    ],
  },
  landscape: {
    primary: ["cornerStopped", "centerStopped"],
    secondary: [
      "distortion",
      "lateralCA",
      "longitudinalCA",
      "vignettingStopped",
      "flareResistance",
      "astigmatism",
      "coma",
    ],
  },
  travel: {
    primary: ["centerStopped", "_weightScore"],
    secondary: ["_apertureScore", "flareResistance", "longitudinalCA"],
  },
  street: {
    primary: ["centerStopped", "_apertureScore"],
    secondary: ["centerWideOpen", "flareResistance", "longitudinalCA", "coma"],
  },
  portrait: {
    primary: ["bokeh", "centerWideOpen"],
    secondary: ["longitudinalCA", "sphericalAberration", "vignettingWideOpen"],
  },
  wildlife: {
    primary: ["centerWideOpen", "centerStopped"],
    secondary: ["_apertureScore", "longitudinalCA", "lateralCA"],
  },
  sport: {
    primary: ["centerWideOpen"],
    secondary: ["_apertureScore", "longitudinalCA", "lateralCA"],
  },
  architecture: {
    primary: ["cornerStopped", "centerStopped", "distortion"],
    secondary: ["lateralCA", "vignettingStopped", "flareResistance"],
  },
  macro: {
    primary: ["centerStopped", "_magnificationScore"],
    secondary: [
      "distortion",
      "lateralCA",
      "longitudinalCA",
      "sphericalAberration",
      "bokeh",
    ],
  },
};

const config = genres[genre];
if (!config) {
  console.error("Unknown genre: " + genre);
  console.error("Available: " + Object.keys(genres).join(", "));
  process.exit(1);
}

const W_P = 3;
const W_S = 1;

const allOptical = [
  "centerStopped",
  "cornerStopped",
  "centerWideOpen",
  "cornerWideOpen",
  "astigmatism",
  "coma",
  "sphericalAberration",
  "longitudinalCA",
  "lateralCA",
  "distortion",
  "vignettingWideOpen",
  "vignettingStopped",
  "bokeh",
  "flareResistance",
];

console.log(genre.toUpperCase());
console.log("Primary (w=" + W_P + "): " + config.primary.join(", "));
console.log("Secondary (w=" + W_S + "): " + config.secondary.join(", "));
console.log("");

function weightScore(grams: number): number {
  if (grams < 200) return 2.0;
  if (grams <= 400) return 1.5;
  if (grams <= 700) return 1.0;
  if (grams <= 1000) return 0.5;
  return 0.0;
}

function apertureScore(maxAp: number): number {
  if (maxAp <= 1.4) return 2.0;
  if (maxAp <= 2.0) return 1.5;
  if (maxAp <= 2.8) return 1.0;
  if (maxAp <= 4.0) return 0.5;
  return 0.0;
}

function magnificationScore(mag: number): number {
  if (mag >= 1.0) return 2.0;
  if (mag >= 0.5) return 1.5;
  if (mag >= 0.25) return 1.0;
  if (mag >= 0.15) return 0.5;
  return 0.0;
}

function focusDistanceScore(mfd: number): number {
  if (mfd <= 150) return 2.0;
  if (mfd <= 250) return 1.5;
  if (mfd <= 400) return 1.0;
  if (mfd <= 700) return 0.5;
  return 0.0;
}

for (const lens of lenses) {
  const l = lens as unknown as Record<string, unknown>;
  if (l.centerStopped == null) continue;

  const name = String(l.model);

  // Compute derived scores
  if (
    config.primary.includes("_apertureScore") ||
    config.secondary.includes("_apertureScore")
  ) {
    (l as unknown as Record<string, unknown>)._apertureScore = apertureScore(
      l.maxAperture as number,
    );
  }
  if (
    config.primary.includes("_weightScore") ||
    config.secondary.includes("_weightScore")
  ) {
    (l as unknown as Record<string, unknown>)._weightScore = weightScore(
      l.weight as number,
    );
  }
  if (
    config.primary.includes("_magnificationScore") ||
    config.secondary.includes("_magnificationScore")
  ) {
    const mag = l.maxMagnification as number | undefined;
    if (mag != null)
      (l as unknown as Record<string, unknown>)._magnificationScore =
        magnificationScore(mag);
  }
  if (
    config.primary.includes("_focusDistanceScore") ||
    config.secondary.includes("_focusDistanceScore")
  ) {
    const mfd = l.minFocusDistance as number | undefined;
    if (mfd != null)
      (l as unknown as Record<string, unknown>)._focusDistanceScore =
        focusDistanceScore(mfd);
  }

  // Check primaries
  const missingP = config.primary.find((f) => l[f] == null);
  if (missingP) {
    console.log(name.padEnd(40) + "SKIP: missing " + missingP);
    continue;
  }

  // 50% threshold
  const count = allOptical.filter((f) => l[f] != null).length;
  if (count < 7) {
    console.log(name.padEnd(40) + "SKIP: " + count + "/14 fields");
    continue;
  }

  // Weighted average
  let sumW = 0;
  let sumWV = 0;
  for (const f of config.primary) {
    sumW += W_P;
    sumWV += W_P * (l[f] as number);
  }
  for (const f of config.secondary) {
    if (l[f] != null) {
      sumW += W_S;
      sumWV += W_S * (l[f] as number);
    }
  }

  const raw = sumWV / sumW;
  const floor = Math.min(...config.primary.map((f) => l[f] as number));
  const capped = Math.min(raw, floor);

  // Map 0-2 -> 1-5 (0.5 steps)
  const markFinal = Math.min(5, Math.max(1, Math.round(capped * 4) / 2 + 1));

  const vals = [...config.primary, ...config.secondary]
    .map((f) => {
      const short = f
        .replace("Stopped", "S")
        .replace("WideOpen", "WO")
        .replace("Resistance", "")
        .replace("longitudinal", "lo")
        .replace("lateral", "lat")
        .replace("astigmatism", "astig")
        .replace("vignetting", "vig")
        .replace("distortion", "dist")
        .replace("flare", "flare")
        .replace("center", "c")
        .replace("corner", "cr");
      return short + "=" + (l[f] ?? "-");
    })
    .join(" ");

  console.log(
    name.padEnd(40) +
      "mark=" +
      markFinal +
      "  raw=" +
      raw.toFixed(2) +
      "  floor=" +
      floor +
      "  [" +
      vals +
      "]",
  );
}
