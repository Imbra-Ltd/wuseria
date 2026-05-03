import { describe, it, expect } from "vitest";
import type { Lens } from "../types/lens";
import type { Genre } from "../types/genre";
import { lenses } from "../data/lenses";
import { makeLens } from "../test/factories";
import { pickGenreFields } from "./pickGenreFields";
import {
  computeGenreMark,
  computeAllGenreMarks,
  computeOpticalQuality,
  toMark,
  apertureScore,
  weightScore,
  magnificationScore,
  resolveField,
  opticalFieldCount,
  genreFormulas,
  getGenreMark,
  isEditorialPick,
  lensesForGenre,
  isGenre,
} from "./scoring";

function findLens(model: string): Lens {
  const lens = lenses.find((l) => l.model === model);
  if (!lens) throw new Error(`Lens not found: ${model}`);
  return lens;
}

// =============================================================================
// toMark — 0-2 to 1-5 mapping
// =============================================================================

describe("toMark", () => {
  it("maps 0-2 scale to 1-5 in 0.5 steps", () => {
    expect(toMark(0)).toBe(1);
    expect(toMark(0.25)).toBe(1.5);
    expect(toMark(0.5)).toBe(2);
    expect(toMark(0.75)).toBe(2.5);
    expect(toMark(1.0)).toBe(3);
    expect(toMark(1.25)).toBe(3.5);
    expect(toMark(1.5)).toBe(4);
    expect(toMark(1.75)).toBe(4.5);
    expect(toMark(2.0)).toBe(5);
  });

  it("clamps to 1-5 range", () => {
    expect(toMark(-1)).toBe(1);
    expect(toMark(3)).toBe(5);
  });
});

// =============================================================================
// Physical property scores
// =============================================================================

describe("apertureScore", () => {
  it("scores aperture on 0-2 scale", () => {
    expect(apertureScore(1.2)).toBe(2.0);
    expect(apertureScore(1.4)).toBe(2.0);
    expect(apertureScore(1.8)).toBe(1.5);
    expect(apertureScore(2.0)).toBe(1.5);
    expect(apertureScore(2.8)).toBe(1.0);
    expect(apertureScore(4.0)).toBe(0.5);
    expect(apertureScore(4.5)).toBe(0.0);
    expect(apertureScore(5.6)).toBe(0.0);
  });
});

describe("weightScore", () => {
  it("scores weight on 0-2 scale", () => {
    expect(weightScore(100)).toBe(2.0);
    expect(weightScore(199)).toBe(2.0);
    expect(weightScore(200)).toBe(1.5);
    expect(weightScore(400)).toBe(1.5);
    expect(weightScore(500)).toBe(1.0);
    expect(weightScore(700)).toBe(1.0);
    expect(weightScore(900)).toBe(0.5);
    expect(weightScore(1000)).toBe(0.5);
    expect(weightScore(1200)).toBe(0.0);
  });
});

describe("magnificationScore", () => {
  it("scores magnification on 0-2 scale", () => {
    expect(magnificationScore(1.0)).toBe(2.0);
    expect(magnificationScore(0.5)).toBe(1.5);
    expect(magnificationScore(0.33)).toBe(1.0);
    expect(magnificationScore(0.25)).toBe(1.0);
    expect(magnificationScore(0.2)).toBe(0.5);
    expect(magnificationScore(0.15)).toBe(0.5);
    expect(magnificationScore(0.1)).toBe(0.0);
    expect(magnificationScore(0.06)).toBe(0.0);
  });
});

// =============================================================================
// resolveField
// =============================================================================

describe("resolveField", () => {
  const lens = findLens("XF 56mm f/1.2 R LM WR");

  it("returns optical fields directly", () => {
    expect(resolveField(lens, "centerStopped")).toBe(2.0);
    expect(resolveField(lens, "bokeh")).toBe(2.0);
  });

  it("computes aperture score from maxAperture", () => {
    expect(resolveField(lens, "_apertureScore")).toBe(2.0);
  });

  it("computes weight score from weight", () => {
    expect(resolveField(lens, "_weightScore")).toBe(1.0);
  });

  it("computes magnification score from maxMagnification", () => {
    expect(resolveField(lens, "_magnificationScore")).toBe(0.0);
  });

  it("returns undefined for missing optical fields", () => {
    const sparse = makeLens({
      brand: "Fujifilm",
      model: "Sparse",
      centerStopped: 2.0,
    });
    expect(resolveField(sparse, "bokeh")).toBeUndefined();
  });
});

// =============================================================================
// opticalFieldCount
// =============================================================================

describe("opticalFieldCount", () => {
  it("counts populated optical fields", () => {
    const lens = findLens("XF 56mm f/1.2 R LM WR");
    expect(opticalFieldCount(lens)).toBe(14);
  });

  it("returns 0 for unscored lens", () => {
    const lens = makeLens({ brand: "Fujifilm", model: "Empty" });
    expect(opticalFieldCount(lens)).toBe(0);
  });
});

// =============================================================================
// computeGenreMark
// =============================================================================

describe("computeGenreMark", () => {
  it("returns null for unscored lens", () => {
    const lens = makeLens({ brand: "Fujifilm", model: "Empty" });
    expect(computeGenreMark(lens, "landscape")).toBeNull();
  });

  it("returns null when primary field is missing", () => {
    const lens = makeLens({
      brand: "Fujifilm",
      model: "NoBokeh",
      centerStopped: 2.0,
      cornerStopped: 1.5,
      centerWideOpen: 2.0,
      astigmatism: 2.0,
      coma: 2.0,
      longitudinalCA: 2.0,
      lateralCA: 2.0,
      // bokeh missing — required for portrait
    });
    expect(computeGenreMark(lens, "portrait")).toBeNull();
  });

  it("returns null when fewer than 7 optical fields", () => {
    const lens = makeLens({
      brand: "Fujifilm",
      model: "Sparse",
      centerStopped: 2.0,
      cornerStopped: 2.0,
      centerWideOpen: 2.0,
      astigmatism: 2.0,
      coma: 2.0,
      lateralCA: 2.0,
      // Only 6 fields
    });
    expect(computeGenreMark(lens, "landscape")).toBeNull();
  });

  it("computes mark 5 for perfect lens (landscape)", () => {
    const result = computeGenreMark(
      findLens("XF 56mm f/1.2 R LM WR"),
      "landscape",
    );
    expect(result).not.toBeNull();
    expect(result!.mark).toBe(5);
    expect(result!.floor).toBe(2);
  });

  it("floors mark by worst primary field", () => {
    // XF 14mm f/2.8: cornerStopped=1, centerStopped=2 → floor=1
    const result = computeGenreMark(findLens("XF 14mm f/2.8 R"), "landscape");
    expect(result).not.toBeNull();
    expect(result!.floor).toBe(1);
    expect(result!.mark).toBe(3);
  });

  it("includes derived fields in scoring", () => {
    // Street uses _apertureScore as primary
    const result = computeGenreMark(
      findLens("XF 56mm f/1.2 R LM WR"),
      "street",
    );
    expect(result).not.toBeNull();
    expect(result!.mark).toBe(5);
  });

  it("uses magnificationScore for macro genre", () => {
    // XF 80mm f/2.8 Macro: mag=1.0 → magnificationScore=2.0
    const result = computeGenreMark(
      findLens("XF 80mm f/2.8 R LM OIS WR Macro"),
      "macro",
    );
    expect(result).not.toBeNull();
    expect(result!.mark).toBe(5);
  });

  it("gates non-macro lenses in macro genre", () => {
    // XF 56mm f/1.2 R LM WR: mag=0.09 → magnificationScore=0 → floor=0 → mark=1
    const result = computeGenreMark(findLens("XF 56mm f/1.2 R LM WR"), "macro");
    expect(result).not.toBeNull();
    expect(result!.mark).toBe(1);
    expect(result!.floor).toBe(0);
  });
});

// =============================================================================
// computeAllGenreMarks
// =============================================================================

describe("computeAllGenreMarks", () => {
  it("computes marks for all qualifying genres", () => {
    const marks = computeAllGenreMarks(findLens("XF 56mm f/1.2 R LM WR"));
    expect(Object.keys(marks).length).toBeGreaterThan(0);
    expect(marks.landscape).toBe(5);
    expect(marks.street).toBe(5);
    expect(marks.macro).toBe(1); // low magnification
  });

  it("returns empty object for unscored lens", () => {
    const lens = makeLens({ brand: "Fujifilm", model: "Empty" });
    const marks = computeAllGenreMarks(lens);
    expect(Object.keys(marks).length).toBe(0);
  });
});

// =============================================================================
// Snapshot: known lenses produce expected marks
// =============================================================================

describe("genre mark snapshots", () => {
  const snapshots: Array<{
    model: string;
    genre: Genre;
    mark: number;
  }> = [
    // Landscape
    { model: "XF 56mm f/1.2 R LM WR", genre: "landscape", mark: 5 },
    { model: "XF 200mm f/2.0 R LM OIS WR", genre: "landscape", mark: 5 },
    { model: "XF 90mm f/2.0 R LM WR", genre: "landscape", mark: 4 },
    { model: "XF 14mm f/2.8 R", genre: "landscape", mark: 3 },

    // Architecture
    { model: "XF 56mm f/1.2 R LM WR", genre: "architecture", mark: 5 },
    { model: "XF 90mm f/2.0 R LM WR", genre: "architecture", mark: 4 },
    { model: "XF 8-16mm f/2.8 R LM WR", genre: "architecture", mark: 4 },

    // Portrait
    { model: "XF 200mm f/2.0 R LM OIS WR", genre: "portrait", mark: 5 },
    { model: "XF 90mm f/2.0 R LM WR", genre: "portrait", mark: 4 },
    { model: "XF 80mm f/2.8 R LM OIS WR Macro", genre: "portrait", mark: 4 },

    // Street
    { model: "XF 56mm f/1.2 R LM WR", genre: "street", mark: 5 },
    { model: "XF 33mm f/1.4 R LM WR", genre: "street", mark: 4.5 },
    { model: "XF 23mm f/1.4 R LM WR", genre: "street", mark: 4.5 },

    // Travel
    { model: "XF 16mm f/2.8 R LM WR", genre: "travel", mark: 4.5 },
    { model: "XF 23mm f/2.0 R WR", genre: "travel", mark: 4.5 },
    { model: "XF 200mm f/2.0 R LM OIS WR", genre: "travel", mark: 1 }, // too heavy

    // Sport
    { model: "XF 56mm f/1.2 R LM WR", genre: "sport", mark: 5 },
    { model: "XF 200mm f/2.0 R LM OIS WR", genre: "sport", mark: 5 },
    { model: "XF 90mm f/2.0 R LM WR", genre: "sport", mark: 4.5 },

    // Wildlife
    { model: "XF 56mm f/1.2 R LM WR", genre: "wildlife", mark: 5 },
    { model: "XF 200mm f/2.0 R LM OIS WR", genre: "wildlife", mark: 5 },
    { model: "XF 90mm f/2.0 R LM WR", genre: "wildlife", mark: 5 },

    // Nightscape
    { model: "XF 56mm f/1.2 R LM WR", genre: "nightscape", mark: 4.5 },
    { model: "XF 90mm f/2.0 R LM WR", genre: "nightscape", mark: 4 },
    { model: "12mm f/2", genre: "nightscape", mark: 4 },
    {
      model: "XF 100-400mm f/4.5-5.6 R LM OIS WR",
      genre: "nightscape",
      mark: 1,
    },

    // Macro
    { model: "XF 80mm f/2.8 R LM OIS WR Macro", genre: "macro", mark: 5 },
    { model: "XF 60mm f/2.4 R Macro", genre: "macro", mark: 4 },
    { model: "XF 56mm f/1.2 R LM WR", genre: "macro", mark: 1 },
  ];

  for (const { model, genre, mark } of snapshots) {
    it(`${model} → ${genre} = ${mark}`, () => {
      const lens = findLens(model);
      const result = computeGenreMark(lens, genre);
      expect(result).not.toBeNull();
      expect(result!.mark).toBe(mark);
    });
  }
});

// =============================================================================
// Genre formula coverage
// =============================================================================

describe("genreFormulas", () => {
  it("has formulas for all 9 genres", () => {
    expect(Object.keys(genreFormulas)).toHaveLength(9);
  });

  it("every formula has at least one primary field", () => {
    for (const [genre, formula] of Object.entries(genreFormulas)) {
      expect(
        formula.primary.length,
        `${genre} has no primary fields`,
      ).toBeGreaterThan(0);
    }
  });
});

// =============================================================================
// Lookup helpers (pre-computed genreMarks on Lens)
// =============================================================================

const scored = makeLens({
  brand: "Fujifilm",
  model: "XF 90mm f/2.0 R LM WR",
  genreMarks: { portrait: 5, sport: 3, wildlife: 3 },
  editorialPicks: ["portrait"],
});

const unscored = makeLens({
  brand: "Fujifilm",
  model: "XF 999mm f/99",
});

describe("getGenreMark", () => {
  it("returns mark for a scored genre", () => {
    expect(getGenreMark(scored, "portrait")).toBe(5);
  });

  it("returns null for an unscored genre", () => {
    expect(getGenreMark(scored, "nightscape")).toBeNull();
  });

  it("returns null for a lens with no genreMarks", () => {
    expect(getGenreMark(unscored, "portrait")).toBeNull();
  });
});

describe("isEditorialPick", () => {
  it("returns true for a picked genre", () => {
    expect(isEditorialPick(scored, "portrait")).toBe(true);
  });

  it("returns false for a non-picked genre", () => {
    expect(isEditorialPick(scored, "sport")).toBe(false);
  });
});

describe("lensesForGenre", () => {
  const xf16 = makeLens({
    brand: "Fujifilm",
    model: "XF 16mm f/1.4",
    genreMarks: { portrait: 3 },
  });

  it("returns only scored lenses, sorted by mark desc", () => {
    const results = lensesForGenre([scored, unscored, xf16], "portrait");
    expect(results).toHaveLength(2);
    expect(results[0]).toBe(scored);
    expect(results[1]).toBe(xf16);
  });
});

describe("isGenre", () => {
  it("returns true for all 9 genres", () => {
    const genres: Genre[] = [
      "nightscape",
      "landscape",
      "architecture",
      "street",
      "travel",
      "portrait",
      "sport",
      "wildlife",
      "macro",
    ];
    for (const g of genres) {
      expect(isGenre(g)).toBe(true);
    }
  });
});

// =============================================================================
// pickGenreFields
// =============================================================================

describe("pickGenreFields", () => {
  it("picks only genre-relevant fields from a full Lens", () => {
    const lens = findLens("XF 56mm f/1.2 R LM WR");
    const picked = pickGenreFields(lens);
    expect(picked.brand).toBe(lens.brand);
    expect(picked.model).toBe(lens.model);
    expect(picked.mount).toBe(lens.mount);
    expect(picked.weight).toBe(lens.weight);
    expect(picked.price).toBe(lens.price);
    expect(picked.genreMarks).toBe(lens.genreMarks);
    expect(picked.centerStopped).toBe(lens.centerStopped);
    // Should NOT contain fields outside GenreLens
    expect("officialUrl" in picked).toBe(false);
    expect("reviewSources" in picked).toBe(false);
  });
});

// =============================================================================
// computeOpticalQuality
// =============================================================================

describe("computeOpticalQuality", () => {
  it("returns null for unscored lens (fewer than 7 fields)", () => {
    const lens = makeLens({ brand: "Fujifilm", model: "Empty" });
    expect(computeOpticalQuality(lens)).toBeNull();
  });

  it("returns null when exactly 6 optical fields (below threshold)", () => {
    const lens = makeLens({
      brand: "Fujifilm",
      model: "Sparse",
      centerStopped: 2.0,
      cornerStopped: 1.5,
      centerWideOpen: 2.0,
      astigmatism: 1.5,
      coma: 1.0,
      lateralCA: 1.5,
    });
    expect(computeOpticalQuality(lens)).toBeNull();
  });

  it("returns a number when 7+ optical fields are present", () => {
    const lens = makeLens({
      brand: "Fujifilm",
      model: "Scored",
      centerStopped: 2.0,
      cornerStopped: 1.5,
      centerWideOpen: 2.0,
      astigmatism: 1.5,
      coma: 1.0,
      lateralCA: 1.5,
      longitudinalCA: 1.5,
    });
    const result = computeOpticalQuality(lens);
    expect(result).not.toBeNull();
    expect(result).toBeGreaterThanOrEqual(0);
    expect(result).toBeLessThanOrEqual(2);
  });

  it("returns max score (2.0) for a perfect lens", () => {
    const lens = makeLens({
      brand: "Fujifilm",
      model: "Perfect",
      centerStopped: 2.0,
      cornerStopped: 2.0,
      centerWideOpen: 2.0,
      cornerWideOpen: 2.0,
      astigmatism: 2.0,
      coma: 2.0,
      sphericalAberration: 2.0,
      longitudinalCA: 2.0,
      lateralCA: 2.0,
      distortion: 2.0,
      vignettingWideOpen: 2.0,
      vignettingStopped: 2.0,
      bokeh: 2.0,
      flareResistance: 2.0,
    });
    expect(computeOpticalQuality(lens)).toBe(2.0);
  });

  it("matches known lens score from data", () => {
    const lens = findLens("XF 56mm f/1.2 R LM WR");
    const result = computeOpticalQuality(lens);
    expect(result).not.toBeNull();
    expect(result).toBeGreaterThan(1.5);
  });

  it("result is rounded to one decimal", () => {
    const lens = makeLens({
      brand: "Fujifilm",
      model: "Mixed",
      centerStopped: 2.0,
      cornerStopped: 1.0,
      centerWideOpen: 1.5,
      astigmatism: 2.0,
      coma: 0.5,
      lateralCA: 1.0,
      longitudinalCA: 1.5,
      distortion: 1.0,
    });
    const result = computeOpticalQuality(lens);
    expect(result).not.toBeNull();
    const decimalPart = result!.toString().split(".")[1];
    expect(!decimalPart || decimalPart.length <= 1).toBe(true);
  });
});
