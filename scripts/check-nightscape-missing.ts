import { lenses } from "../src/data/lenses";

const scored = lenses.filter((l) => (l as Record<string, unknown>).centerStopped != null);
const nightscape = scored.filter((l) => {
  const marks = (l as Record<string, unknown>).genreMarks as Record<string, number> | undefined;
  return marks?.nightscape != null;
});
const missing = scored.filter((l) => {
  const marks = (l as Record<string, unknown>).genreMarks as Record<string, number> | undefined;
  return marks?.nightscape == null;
});

console.log("Scored: " + scored.length);
console.log("Has nightscape mark: " + nightscape.length);
console.log("Missing nightscape: " + missing.length);
console.log("");
console.log("=== Missing nightscape (why?) ===");
for (const l of missing) {
  const a = l as Record<string, unknown>;
  const coma = a.coma;
  const astig = a.astigmatism;
  const reasons: string[] = [];
  if (coma == null) reasons.push("coma");
  if (astig == null) reasons.push("astigmatism");
  console.log(
    String(a.brand).padEnd(12) +
    String(a.model).padEnd(42) +
    "missing: " + (reasons.length > 0 ? reasons.join(", ") : "unknown")
  );
}
