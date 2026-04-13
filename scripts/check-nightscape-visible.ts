import { lenses } from "../src/data/lenses";

const nightscape = lenses.filter((l) => {
  const marks = (l as Record<string, unknown>).genreMarks as Record<string, number> | undefined;
  return marks?.nightscape != null;
});

const active = nightscape.filter((l) => !l.isDiscontinued);
const discontinued = nightscape.filter((l) => l.isDiscontinued);
const xMount = active.filter((l) => l.mount === "X");
const gfx = active.filter((l) => l.mount === "GFX");

console.log("Total nightscape: " + nightscape.length);
console.log("Active (shown): " + active.length);
console.log("Discontinued (hidden): " + discontinued.length);
console.log("X-mount active: " + xMount.length);
console.log("GFX active: " + gfx.length);
console.log("");
console.log("=== Discontinued (hidden) ===");
discontinued.forEach((l) => console.log("  " + l.brand + " " + l.model));
