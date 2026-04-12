import { describe, it, expect } from "vitest";
import { genreConfigs } from "./genres";
import type { ScoredGenre } from "../types/genre";

// =============================================================================
// GENRE CONFIGS
// =============================================================================

describe("genreConfigs", () => {
  const expectedGenres: ScoredGenre[] = [
    "astro",
    "landscape",
    "architecture",
    "street",
    "travel",
    "portrait",
    "sport",
    "wildlife",
  ];

  it("has configs for all 8 scored genres", () => {
    for (const genre of expectedGenres) {
      expect(genreConfigs[genre]).toBeDefined();
    }
  });

  it("each config has required fields", () => {
    for (const genre of expectedGenres) {
      const config = genreConfigs[genre];
      expect(config.genre).toBe(genre);
      expect(config.name).toBeTruthy();
      expect(config.tagline).toBeTruthy();
      expect(config.description).toBeTruthy();
      expect(config.typicalFl.length).toBeGreaterThanOrEqual(1);
    }
  });
});
