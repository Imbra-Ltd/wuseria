import { describe, it, expect } from "vitest";
import { genreConfigs } from "./genres";
import type { ScoredGenre } from "../types/genre";

// =============================================================================
// GENRE CONFIGS
// =============================================================================

const ALL_GENRES: ScoredGenre[] = [
  "nightscape", "landscape", "architecture", "street",
  "travel", "portrait", "sport", "wildlife", "macro",
];

describe("genreConfigs", () => {
  it("has configs for all 9 genres", () => {
    for (const genre of ALL_GENRES) {
      expect(genreConfigs[genre]).toBeDefined();
    }
  });

  it("each config has required fields", () => {
    for (const genre of ALL_GENRES) {
      const config = genreConfigs[genre];
      expect(config.genre).toBe(genre);
      expect(config.name).toBeTruthy();
      expect(config.tagline).toBeTruthy();
      expect(config.description).toBeTruthy();
      expect(config.typicalFl.length).toBeGreaterThanOrEqual(1);
    }
  });
});
