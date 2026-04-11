import { lenses } from "../src/data/lenses";

const genre = process.argv[2] || "landscape";

const genres: Record<string, { primary: string[]; secondary: string[] }> = {
  landscape: {
    primary: ["cornerStopped", "centerStopped"],
    secondary: ["distortion", "lateralCA", "longitudinalCA", "vignettingStopped", "flareResistance", "astigmatism", "coma"],
  },
  portrait: {
    primary: ["bokeh", "centerWideOpen"],
    secondary: ["longitudinalCA", "sphericalAberration", "vignettingWideOpen"],
  },
  architecture: {
    primary: ["cornerStopped", "centerStopped", "distortion"],
    secondary: ["lateralCA", "vignettingStopped", "flareResistance"],
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
  "centerStopped", "cornerStopped", "centerWideOpen", "cornerWideOpen",
  "astigmatism", "coma", "sphericalAberration", "longitudinalCA",
  "lateralCA", "distortion", "vignettingWideOpen", "vignettingStopped",
  "bokeh", "flareResistance",
];

console.log(genre.toUpperCase());
console.log("Primary (w=" + W_P + "): " + config.primary.join(", "));
console.log("Secondary (w=" + W_S + "): " + config.secondary.join(", "));
console.log("");

for (const lens of lenses) {
  const l = lens as Record<string, unknown>;
  if (l.centerStopped == null) continue;

  const name = String(l.model);

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

  // Map 0-2 -> 1-5 (integer steps)
  const markFinal = Math.min(5, Math.max(1, Math.round(capped * 2 + 1)));

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
    "mark=" + markFinal +
    "  raw=" + raw.toFixed(2) +
    "  floor=" + floor +
    "  [" + vals + "]"
  );
}
