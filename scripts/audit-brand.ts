import { lenses } from "../src/data/lenses";

const brand = process.argv[2];

// Fields grouped by source
const givenFields = [
  // Optical specs (from manufacturer)
  "apertureBlades",
  "hasCircularAperture",
  "maxMagnification",
  "minFocusDistance",
  // Build (from manufacturer/reviews)
  "afMotor",
  "hasApertureRing",
  "isApertureClickless",
  "hasFocusRing",
  "isFocusByWire",
  "hasDistanceScale",
  "hasRotatingFront",
  "hasTripodMount",
  // Physical (from manufacturer)
  "diameter",
  "length",
  "filterThread",
];

const calculatedFields = [
  "sweetSpotAperture",
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
  "genreMarks",
  "reviewSources",
];

function countField(brandLenses: typeof lenses, field: string): number {
  return brandLenses.filter(
    (l) => (l as Record<string, unknown>)[field] != null,
  ).length;
}

function printFieldTable(
  brandLenses: typeof lenses,
  fields: string[],
  label: string,
): void {
  console.log(`\n${label}:`);
  console.log("Field                | Pop     | Miss");
  console.log("---------------------|---------|-----");
  for (const field of fields) {
    const count = countField(brandLenses, field);
    const missing = brandLenses.length - count;
    const status = missing === 0 ? " DONE" : "";
    console.log(
      `${field.padEnd(21)}| ${String(count).padStart(3)}/${brandLenses.length} | ${String(missing).padStart(3)}${status}`,
    );
  }
}

function printPerLens(brandLenses: typeof lenses): void {
  console.log("\nPER-LENS GIVEN FIELDS:");
  console.log("---");
  for (const l of brandLenses) {
    const missing = givenFields.filter(
      (f) => (l as Record<string, unknown>)[f] == null,
    );
    if (missing.length === 0) {
      console.log(`${l.model}: COMPLETE`);
    } else {
      console.log(`${l.model}: missing ${missing.join(", ")}`);
    }
  }
}

function auditBrand(brandName: string): void {
  const brandLenses = lenses.filter((l) => l.brand === brandName);
  if (brandLenses.length === 0) {
    console.log(`No lenses found for brand: ${brandName}`);
    return;
  }

  console.log(`\n${brandName}: ${brandLenses.length} lenses`);
  console.log("=".repeat(60));
  printFieldTable(brandLenses, givenFields, "GIVEN FIELDS (from specs)");
  printFieldTable(
    brandLenses,
    calculatedFields,
    "CALCULATED FIELDS (from scoring/reviews)",
  );
  printPerLens(brandLenses);
}

if (brand) {
  auditBrand(brand);
} else {
  // All brands summary
  const brands = [...new Set(lenses.map((l) => l.brand))].sort();
  console.log("GIVEN FIELDS COVERAGE BY BRAND\n");
  console.log("Brand                | Lenses | Given%  | Missing");
  console.log("---------------------|--------|---------|--------");
  for (const b of brands) {
    const bl = lenses.filter((l) => l.brand === b);
    const totalSlots = bl.length * givenFields.length;
    const filled = bl.reduce((sum, l) => {
      return (
        sum +
        givenFields.filter((f) => (l as Record<string, unknown>)[f] != null)
          .length
      );
    }, 0);
    const pct = ((filled / totalSlots) * 100).toFixed(0);
    const missing = totalSlots - filled;
    const status = missing === 0 ? " DONE" : "";
    console.log(
      `${b.padEnd(21)}| ${String(bl.length).padStart(4)}   | ${pct.padStart(4)}%   | ${String(missing).padStart(4)}${status}`,
    );
  }
}
