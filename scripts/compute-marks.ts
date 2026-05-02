import { lenses } from "../src/data/lenses";
import { computeAllGenreMarks } from "../src/utils/scoring";
import type { ScoredGenre } from "../src/types/genre";
import * as fs from "fs";

const GENRES: ScoredGenre[] = [
  "nightscape",
  "landscape",
  "architecture",
  "portrait",
  "street",
  "travel",
  "sport",
  "wildlife",
  "macro",
];

const mode = process.argv[2] || "print";

// Compute marks for all scored lenses
const results: Array<{
  brand: string;
  model: string;
  marks: Partial<Record<ScoredGenre, number>>;
}> = [];

for (const lens of lenses) {
  if (lens.centerStopped == null) continue;
  const marks = computeAllGenreMarks(lens);
  if (Object.keys(marks).length > 0) {
    results.push({ brand: lens.brand, model: lens.model, marks });
  }
}

if (mode === "print") {
  // Print summary
  console.log("Scored lenses: " + results.length);
  console.log("");

  for (const { brand, model, marks } of results) {
    const markStr = GENRES.filter((g) => marks[g] != null)
      .map((g) => g.slice(0, 4) + "=" + marks[g])
      .join(" ");
    console.log((brand + " " + model).padEnd(45) + markStr);
  }
} else if (mode === "patch") {
  // Patch lenses.ts with genreMarks
  const filePath = "src/data/lenses.ts";
  let content = fs.readFileSync(filePath, "utf-8");
  let patchCount = 0;

  for (const { model, marks } of results) {
    // Build genreMarks object string
    const entries = GENRES.filter((g) => marks[g] != null).map(
      (g) => `${g}: ${marks[g]}`,
    );
    const marksStr = "genreMarks: { " + entries.join(", ") + " },";

    // Find the lens in the file by model
    // Look for the model string and then find the right place to insert
    const modelEscaped = model.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const modelRegex = new RegExp(`model: "${modelEscaped}",`);
    const match = content.match(modelRegex);
    if (!match || match.index == null) {
      console.error("Could not find model: " + model);
      continue;
    }

    // Check if genreMarks already exists for this lens
    // Find the next lens entry (next "brand:" or end of array)
    const afterModel = content.indexOf(match[0], match.index) + match[0].length;
    const nextBrand = content.indexOf("\n    brand:", afterModel);
    const lensBlock =
      nextBrand > 0
        ? content.slice(afterModel, nextBrand)
        : content.slice(afterModel, afterModel + 2000);

    if (lensBlock.includes("genreMarks:")) {
      // Replace existing genreMarks
      const oldMarksRegex = /genreMarks: \{[^}]+\},/;
      const oldMatch = lensBlock.match(oldMarksRegex);
      if (oldMatch && oldMatch.index != null) {
        const absPos = afterModel + oldMatch.index;
        content =
          content.slice(0, absPos) +
          marksStr +
          content.slice(absPos + oldMatch[0].length);
        patchCount++;
      }
    } else {
      // Insert before reviewSources or officialUrl
      const insertTargets = ["reviewSources:", "officialUrl:"];
      let insertPos = -1;
      for (const target of insertTargets) {
        const idx = lensBlock.indexOf(target);
        if (idx >= 0) {
          insertPos = afterModel + idx;
          break;
        }
      }

      if (insertPos > 0) {
        // Find the indentation
        const lineStart = content.lastIndexOf("\n", insertPos) + 1;
        const indent =
          content.slice(lineStart, insertPos).match(/^\s*/)?.[0] || "    ";
        content =
          content.slice(0, insertPos) +
          marksStr +
          "\n" +
          indent +
          content.slice(insertPos);
        patchCount++;
      } else {
        console.error("Could not find insert point for: " + model);
      }
    }
  }

  fs.writeFileSync(filePath, content, "utf-8");
  console.log("Patched " + patchCount + " lenses with genreMarks");
}
