import { lenses } from "../src/data/lenses";

const scored = lenses.filter(
  (l) => (l as unknown as Record<string, unknown>).centerStopped != null,
);
const missingMag = scored.filter(
  (l) => (l as unknown as Record<string, unknown>).maxMagnification == null,
);
const missingMfd = scored.filter(
  (l) => (l as unknown as Record<string, unknown>).minFocusDistance == null,
);

console.log("Scored lenses: " + scored.length);
console.log("Missing maxMagnification: " + missingMag.length);
console.log("Missing minFocusDistance: " + missingMfd.length);
console.log("");

if (missingMag.length > 0) {
  console.log("=== Missing maxMagnification ===");
  for (const l of missingMag) {
    const a = l as unknown as Record<string, unknown>;
    console.log("  " + a.brand + " " + a.model);
  }
}
console.log("");
if (missingMfd.length > 0) {
  console.log("=== Missing minFocusDistance ===");
  for (const l of missingMfd) {
    const a = l as unknown as Record<string, unknown>;
    console.log("  " + a.brand + " " + a.model);
  }
}

console.log("=== All scored lenses mag/mfd ===");
for (const l of scored) {
  const a = l as unknown as Record<string, unknown>;
  const mag = a.maxMagnification as number;
  const mfd = a.minFocusDistance as number;
  console.log(
    String(a.model).padEnd(40) +
      "mag=" +
      String(mag).padEnd(6) +
      " mfd=" +
      String(mfd).padEnd(6) +
      " magScore=" +
      (mag >= 1.0
        ? "2.0"
        : mag >= 0.5
          ? "1.5"
          : mag >= 0.25
            ? "1.0"
            : mag >= 0.15
              ? "0.5"
              : "0.0"),
  );
}
