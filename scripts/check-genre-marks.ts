import { lenses } from "../src/data/lenses";
import type { ScoredGenre } from "../src/types/genre";

const genres: ScoredGenre[] = [
  "nightscape", "landscape", "architecture", "street",
  "travel", "portrait", "sport", "wildlife", "macro",
];

for (const g of genres) {
  const count = lenses.filter((l) => l.genreMarks?.[g] != null).length;
  console.log(g.padEnd(15) + count + " lenses");
}

console.log("");
console.log("Total with any genreMarks: " + lenses.filter((l) => l.genreMarks != null && Object.keys(l.genreMarks).length > 0).length);
console.log("Total lenses: " + lenses.length);
