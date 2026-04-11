import { describe, it, expect } from "vitest";
import type { Lens } from "../types/lens";
import {
  getGenreMark,
  isEditorialPick,
  lensesForGenre,
  isScoredGenre,
} from "./scoring";

// =============================================================================
// TEST FIXTURES
// =============================================================================

function makeLens(
  overrides: Partial<Lens> & Pick<Lens, "brand" | "model">,
): Lens {
  return {
    type: "prime",
    mount: "X",
    focalLengthMin: 35,
    focalLengthMax: 35,
    maxAperture: 1.4,
    weight: 200,
    price: 600,
    ...overrides,
  };
}

const scored = makeLens({
  brand: "Fujifilm",
  model: "XF 90mm f/2.0",
  genreMarks: { portrait: 5, sport: 3, wildlife: 3 },
  editorialPicks: ["portrait"],
});

const unscored = makeLens({
  brand: "Fujifilm",
  model: "XF 999mm f/99",
});

const xf16 = makeLens({
  brand: "Fujifilm",
  model: "XF 16mm f/1.4",
  genreMarks: { astro: 4, street: 4, portrait: 3 },
  editorialPicks: ["astro", "street"],
});

const xf23 = makeLens({
  brand: "Fujifilm",
  model: "XF 23mm f/1.4",
  genreMarks: { astro: 4, street: 4, portrait: 3 },
});

// =============================================================================
// getGenreMark
// =============================================================================

describe("getGenreMark", () => {
  it("returns mark for a scored genre", () => {
    expect(getGenreMark(scored, "portrait")).toBe(5);
    expect(getGenreMark(scored, "sport")).toBe(3);
  });

  it("returns null for an unscored genre", () => {
    expect(getGenreMark(scored, "astro")).toBeNull();
  });

  it("returns null for a lens with no genreMarks", () => {
    expect(getGenreMark(unscored, "portrait")).toBeNull();
  });
});

// =============================================================================
// isEditorialPick
// =============================================================================

describe("isEditorialPick", () => {
  it("returns true for a picked genre", () => {
    expect(isEditorialPick(scored, "portrait")).toBe(true);
  });

  it("returns false for a non-picked genre", () => {
    expect(isEditorialPick(scored, "sport")).toBe(false);
  });

  it("returns false for a lens with no picks", () => {
    expect(isEditorialPick(unscored, "portrait")).toBe(false);
  });
});

// =============================================================================
// lensesForGenre
// =============================================================================

describe("lensesForGenre", () => {
  const allLenses = [scored, unscored, xf16, xf23];

  it("returns only lenses scored for the genre", () => {
    const results = lensesForGenre(allLenses, "portrait");
    expect(results).toHaveLength(3);
    expect(results.find((l) => l === unscored)).toBeUndefined();
  });

  it("sorts by mark descending", () => {
    const results = lensesForGenre(allLenses, "portrait");
    expect(results[0]).toBe(scored);
    for (let i = 1; i < results.length; i++) {
      expect(results[i - 1].genreMarks!.portrait!).toBeGreaterThanOrEqual(
        results[i].genreMarks!.portrait!,
      );
    }
  });

  it("returns empty array when no lenses match", () => {
    expect(lensesForGenre(allLenses, "landscape")).toHaveLength(0);
  });
});

// =============================================================================
// isScoredGenre
// =============================================================================

describe("isScoredGenre", () => {
  it("returns true for all 8 scored genres", () => {
    const genres = [
      "astro", "landscape", "architecture", "street",
      "travel", "portrait", "sport", "wildlife",
    ] as const;
    for (const g of genres) {
      expect(isScoredGenre(g)).toBe(true);
    }
  });

  it("returns false for macro", () => {
    expect(isScoredGenre("macro")).toBe(false);
  });
});
