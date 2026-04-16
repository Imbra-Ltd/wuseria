import { lenses } from "../src/data/lenses";
import { OPTICAL_FIELDS } from "../src/utils/scoring";

const scored = lenses.filter((l) => (l as unknown as Record<string, unknown>).centerStopped != null);

console.log("=== Data Completeness ===");
console.log("Scored: " + scored.length + " / " + lenses.length);
console.log("");

console.log("=== Incomplete lenses ===");
for (const l of scored) {
  const a = l as unknown as Record<string, unknown>;
  const filled = OPTICAL_FIELDS.filter((f) => a[f] != null).length;
  const missing = OPTICAL_FIELDS.filter((f) => a[f] == null).map(String);
  const pct = Math.round((filled / 14) * 100);
  if (filled < 14) {
    console.log(
      String(a.brand).padEnd(12) +
      String(a.model).padEnd(40) +
      filled + "/14 (" + pct + "%)  missing: " + missing.join(", ")
    );
  }
}

console.log("");
const complete = scored.filter((l) => OPTICAL_FIELDS.every((f) => (l as unknown as Record<string, unknown>)[f] != null));
const above10 = scored.filter((l) => OPTICAL_FIELDS.filter((f) => (l as unknown as Record<string, unknown>)[f] != null).length >= 10);
const below10 = scored.filter((l) => OPTICAL_FIELDS.filter((f) => (l as unknown as Record<string, unknown>)[f] != null).length < 10);

console.log("=== Summary ===");
console.log("Complete (14/14): " + complete.length + "/" + scored.length);
console.log("10+ fields:       " + above10.length + "/" + scored.length);
console.log("Below 10 fields:  " + below10.length + "/" + scored.length);
