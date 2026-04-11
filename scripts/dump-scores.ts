import { lenses } from "../src/data/lenses";

const fields = [
  "centerStopped", "cornerStopped", "centerWideOpen", "cornerWideOpen",
  "astigmatism", "coma", "sphericalAberration",
  "longitudinalCA", "lateralCA", "distortion",
  "vignettingWideOpen", "vignettingStopped",
  "bokeh", "flareResistance",
];

const scored = lenses
  .filter((l) => (l as Record<string, unknown>).centerStopped != null)
  .sort((a, b) => a.focalLengthMin - b.focalLengthMin);

for (const l of scored) {
  const lens = l as Record<string, unknown>;
  process.stdout.write(`\n### ${lens.model}\n\n`);
  process.stdout.write(`| Field | Score |\n`);
  process.stdout.write(`|-------|-------|\n`);
  process.stdout.write(`| sweetSpotAperture | f/${lens.sweetSpotAperture} |\n`);
  for (const f of fields) {
    const v = lens[f];
    process.stdout.write(`| ${f} | ${v ?? "—"} |\n`);
  }
  const rs = lens.reviewSources as Record<string, string> | undefined;
  if (rs) {
    process.stdout.write(`\nSources: ${Object.keys(rs).join(", ")}\n`);
  }
}
