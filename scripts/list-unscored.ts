import { lenses } from "../src/data/lenses";

const unscored = lenses.filter(
  (l) => (l as unknown as Record<string, unknown>).centerStopped == null,
);
const scored = lenses.filter(
  (l) => (l as unknown as Record<string, unknown>).centerStopped != null,
);

console.log("Scored: " + scored.length + " / " + lenses.length);
console.log("Unscored: " + unscored.length);
console.log("");

const byBrand: Record<string, string[]> = {};
for (const l of unscored) {
  const a = l as unknown as Record<string, unknown>;
  const b = String(a.brand);
  if (!byBrand[b]) byBrand[b] = [];
  byBrand[b].push(String(a.model));
}

for (const [brand, models] of Object.entries(byBrand).sort()) {
  console.log(brand + " (" + models.length + "):");
  models.forEach((m) => console.log("  " + m));
}
