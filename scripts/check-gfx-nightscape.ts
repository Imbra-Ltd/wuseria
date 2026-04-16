import { lenses } from "../src/data/lenses";

const gfxScored = lenses.filter(
  (l) => l.mount === "GFX" && (l as unknown as Record<string, unknown>).centerStopped != null
);

console.log("GFX scored: " + gfxScored.length);
console.log("");

for (const l of gfxScored) {
  const a = l as unknown as Record<string, unknown>;
  const marks = a.genreMarks as Record<string, number> | undefined;
  const coma = a.coma;
  const astig = a.astigmatism;
  const aperture = a.maxAperture;
  console.log(
    String(a.model).padEnd(40) +
    "nightscape=" + (marks?.nightscape ?? "NONE").toString().padEnd(6) +
    "coma=" + String(coma ?? "?").padEnd(5) +
    "astig=" + String(astig ?? "?").padEnd(5) +
    "f/" + aperture
  );
}
