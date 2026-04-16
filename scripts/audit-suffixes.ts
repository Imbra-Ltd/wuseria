import { lenses } from "../src/data/lenses";

const checks = [
  { suffix: "WR", field: "isWeatherSealed", label: "WR" },
  { suffix: "OIS", field: "hasOis", label: "OIS" },
  { suffix: "LM", field: "afMotor", label: "LM", matchValue: "LM" },
  { suffix: " R ", field: "hasApertureRing", label: "R (aperture ring)" },
];

for (const { suffix, field, label, matchValue } of checks) {
  console.log("=== " + label + " ===");
  let issues = 0;

  for (const l of lenses) {
    const a = l as unknown as Record<string, unknown>;
    const model = String(a.model);
    const brand = String(a.brand);
    if (brand !== "Fujifilm") continue;

    const inModel = model.includes(suffix);
    const fieldVal = matchValue ? a[field] === matchValue : Boolean(a[field]);

    if (inModel && !fieldVal) {
      console.log("  MODEL has " + suffix + " but field missing: " + model);
      issues++;
    }
    if (!inModel && fieldVal && !model.startsWith("MKX")) {
      console.log("  FIELD set but model lacks " + suffix + ": " + model);
      issues++;
    }
  }
  if (issues === 0) console.log("  No issues");
  console.log("");
}
