import { describe, it, expect } from "vitest";
import { lenses } from "./lenses";
import { OPTICAL_FIELDS, genreFormulas } from "../utils/scoring";

// =============================================================================
// UNIQUENESS
// =============================================================================

describe("lens uniqueness", () => {
  it("no duplicate brand+model combinations", () => {
    const keys = lenses.map((l) => `${l.brand}|${l.model}`);
    const dupes = keys.filter((k, i) => keys.indexOf(k) !== i);
    expect(dupes, `Duplicates: ${dupes.join(", ")}`).toHaveLength(0);
  });
});

// =============================================================================
// REQUIRED FIELDS
// =============================================================================

describe("required fields", () => {
  it("every lens has brand, model, type, mount, focalLengthMin/Max, maxAperture, weight, price", () => {
    for (const l of lenses) {
      const id = `${l.brand} ${l.model}`;
      expect(l.brand, `${id}: brand`).toBeTruthy();
      expect(l.model, `${id}: model`).toBeTruthy();
      expect(l.type, `${id}: type`).toMatch(/^(prime|zoom)$/);
      expect(l.mount, `${id}: mount`).toMatch(/^(X|GFX)$/);
      expect(l.focalLengthMin, `${id}: focalLengthMin`).toBeGreaterThan(0);
      expect(l.focalLengthMax, `${id}: focalLengthMax`).toBeGreaterThanOrEqual(
        l.focalLengthMin,
      );
      expect(l.maxAperture, `${id}: maxAperture`).toBeGreaterThan(0);
      expect(l.weight, `${id}: weight`).toBeGreaterThan(0);
      expect(l.price, `${id}: price`).toBeGreaterThan(0);
    }
  });

  it("zoom lenses have focalLengthMax > focalLengthMin", () => {
    const zooms = lenses.filter((l) => l.type === "zoom");
    for (const l of zooms) {
      expect(
        l.focalLengthMax,
        `${l.brand} ${l.model}: zoom must have max > min`,
      ).toBeGreaterThan(l.focalLengthMin);
    }
  });
});

// =============================================================================
// OPTICAL FIELD RANGES
// =============================================================================

describe("optical field ranges (0-2 scale)", () => {
  const scored = lenses.filter((l) => l.centerStopped != null);

  it("all optical fields are 0-2 in 0.5 steps", () => {
    const valid = [0, 0.5, 1.0, 1.5, 2.0];
    for (const l of scored) {
      const id = `${l.brand} ${l.model}`;
      for (const field of OPTICAL_FIELDS) {
        const value = l[field];
        if (value != null) {
          expect(
            valid,
            `${id}.${field} = ${value} (not a valid 0-2 step)`,
          ).toContain(value);
        }
      }
    }
  });

  it("scored lenses have centerStopped defined", () => {
    for (const l of scored) {
      expect(
        l.centerStopped,
        `${l.brand} ${l.model}: scored but no centerStopped`,
      ).toBeDefined();
    }
  });

  it("scored lenses have at least 7 of 14 optical fields", () => {
    for (const l of scored) {
      const count = OPTICAL_FIELDS.filter((f) => l[f] != null).length;
      expect(
        count,
        `${l.brand} ${l.model}: only ${count}/14 optical fields`,
      ).toBeGreaterThanOrEqual(7);
    }
  });
});

// =============================================================================
// GENRE MARKS
// =============================================================================

describe("genreMarks", () => {
  const withMarks = lenses.filter(
    (l) => l.genreMarks != null && Object.keys(l.genreMarks).length > 0,
  );

  it("at least 50 lenses have genreMarks", () => {
    expect(withMarks.length).toBeGreaterThanOrEqual(50);
  });

  it("all marks are 1-5 in 0.5 steps", () => {
    const valid = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5];
    for (const l of withMarks) {
      const id = `${l.brand} ${l.model}`;
      for (const [genre, mark] of Object.entries(l.genreMarks!)) {
        expect(
          valid,
          `${id}.genreMarks.${genre} = ${mark} (not a valid 1-5 step)`,
        ).toContain(mark);
      }
    }
  });

  it("genreMarks only use valid genre keys", () => {
    const validGenres = Object.keys(genreFormulas);
    for (const l of withMarks) {
      const id = `${l.brand} ${l.model}`;
      for (const genre of Object.keys(l.genreMarks!)) {
        expect(
          validGenres,
          `${id}: unknown genre "${genre}" in genreMarks`,
        ).toContain(genre);
      }
    }
  });

  it("every lens with genreMarks also has optical data", () => {
    for (const l of withMarks) {
      expect(
        l.centerStopped,
        `${l.brand} ${l.model}: has genreMarks but no centerStopped`,
      ).toBeDefined();
    }
  });
});

// =============================================================================
// REVIEW SOURCES
// =============================================================================

describe("reviewSources", () => {
  const withReviews = lenses.filter((l) => l.reviewSources != null);

  it("scored lenses have at least one review source", () => {
    const scored = lenses.filter((l) => l.centerStopped != null);
    for (const l of scored) {
      expect(
        l.reviewSources,
        `${l.brand} ${l.model}: scored but no reviewSources`,
      ).toBeDefined();
    }
  });

  it("review source URLs are valid HTTPS URLs", () => {
    for (const l of withReviews) {
      const id = `${l.brand} ${l.model}`;
      for (const [source, url] of Object.entries(l.reviewSources!)) {
        expect(url, `${id}.reviewSources.${source}: not an HTTPS URL`).toMatch(
          /^https:\/\//,
        );
      }
    }
  });
});

// =============================================================================
// PRICE ROUNDING
// =============================================================================

describe("prices", () => {
  it("all prices are rounded to nearest $250", () => {
    for (const l of lenses) {
      expect(
        l.price % 250,
        `${l.brand} ${l.model}: price ${l.price} not rounded to $250`,
      ).toBe(0);
    }
  });
});
