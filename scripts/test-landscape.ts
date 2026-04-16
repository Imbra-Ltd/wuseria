import { lenses } from "../src/data/lenses";

const primary: string[] = ["cornerStopped", "centerStopped"];
const secondary: string[] = ["distortion", "lateralCA", "vignettingStopped", "flareResistance", "astigmatism"];
const W_P = 3;
const W_S = 1;

const allOptical = [
  "centerStopped", "cornerStopped", "centerWideOpen", "cornerWideOpen",
  "astigmatism", "coma", "sphericalAberration", "longitudinalCA",
  "lateralCA", "distortion", "vignettingWideOpen", "vignettingStopped",
  "bokeh", "flareResistance",
];

for (const lens of lenses) {
  const l = lens as unknown as Record<string, unknown>;
  if (l.centerStopped == null) continue;

  const name = String(l.model);

  // Check primaries
  const missingP = primary.find((f) => l[f] == null);
  if (missingP) {
    console.log(name.padEnd(38) + "SKIP: missing " + missingP);
    continue;
  }

  // 50% threshold
  const count = allOptical.filter((f) => l[f] != null).length;
  if (count < 7) {
    console.log(name.padEnd(38) + "SKIP: " + count + "/14 fields");
    continue;
  }

  // Weighted average
  let sumW = 0;
  let sumWV = 0;
  for (const f of primary) {
    sumW += W_P;
    sumWV += W_P * (l[f] as number);
  }
  for (const f of secondary) {
    if (l[f] != null) {
      sumW += W_S;
      sumWV += W_S * (l[f] as number);
    }
  }

  const raw = sumWV / sumW;
  const floor = Math.min(...primary.map((f) => l[f] as number));
  const capped = Math.min(raw, floor);

  // Map 0-2 -> 1-5: 0→1, 0.5→2, 1.0→3, 1.5→4, 2.0→5
  const mark = Math.round(capped * 4) / 4 * 2 + 1;
  const markStep = Math.round(mark * 2) / 2;
  const markFinal = Math.min(5, Math.max(1, markStep));

  const vals = [...primary, ...secondary]
    .map((f) => f.replace("Stopped", "S").replace("WideOpen", "WO").replace("Resistance", "") + "=" + (l[f] ?? "-"))
    .join(" ");

  console.log(
    name.padEnd(38) +
    "mark=" + markFinal +
    "  raw=" + raw.toFixed(2) +
    "  floor=" + floor +
    "  [" + vals + "]"
  );
}
