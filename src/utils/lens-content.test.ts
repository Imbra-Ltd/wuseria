import { describe, it, expect } from "vitest";
import { generateLensContent } from "./lens-content";
import { makeLens } from "../test/factories";

const scoredLens = makeLens({
  brand: "Fujifilm",
  model: "XF 56mm f/1.2 R WR",
  mount: "X",
  focalLengthMin: 56,
  focalLengthMax: 56,
  maxAperture: 1.2,
  weight: 445,
  price: 1200,
  isWeatherSealed: true,
  afMotor: "LM",
  maxMagnification: 0.14,
  centerWideOpen: 2,
  cornerWideOpen: 1.5,
  centerStopped: 2,
  cornerStopped: 2,
  longitudinalCA: 2,
  lateralCA: 2,
  coma: 2,
  astigmatism: 2,
  sphericalAberration: 2,
  distortion: 2,
  vignettingWideOpen: 0.5,
  vignettingStopped: 2,
  bokeh: 2,
  flareResistance: 1.5,
  genreMarks: {
    nightscape: 4.5,
    landscape: 5,
    architecture: 5,
    portrait: 4.5,
    street: 5,
    travel: 3,
    sport: 5,
    wildlife: 5,
    macro: 1,
  },
});

const unscoredLens = makeLens({
  brand: "Fujifilm",
  model: "XF 50mm f/2.0 R WR",
  mount: "X",
  focalLengthMin: 50,
  focalLengthMax: 50,
  maxAperture: 2,
  weight: 300,
  price: 500,
});

const weakLens = makeLens({
  brand: "Fujifilm",
  model: "XF 35mm f/2.0 R WR",
  mount: "X",
  focalLengthMin: 35,
  focalLengthMax: 35,
  maxAperture: 2,
  weight: 170,
  price: 400,
  centerWideOpen: 1,
  cornerWideOpen: 0.5,
  centerStopped: 1.5,
  cornerStopped: 1,
  longitudinalCA: 1,
  lateralCA: 1.5,
  coma: 0.5,
  astigmatism: 1,
  sphericalAberration: 1,
  distortion: 0.5,
  vignettingWideOpen: 0,
  vignettingStopped: 1,
  bokeh: 1,
  flareResistance: 0.5,
  genreMarks: {
    nightscape: 2,
    landscape: 3,
    architecture: 2,
    portrait: 2.5,
    street: 3.5,
    travel: 4,
    sport: 2,
    wildlife: 2,
    macro: 1,
  },
});

const allLenses = [scoredLens, unscoredLens, weakLens];

describe("generateLensContent", () => {
  describe("summary", () => {
    it("generates verdict for scored lens", () => {
      const content = generateLensContent(scoredLens, allLenses);
      expect(content.summary.verdict).toContain("outstanding");
      expect(content.summary.verdict).toContain("84mm equivalent");
    });

    it("generates verdict for unscored lens", () => {
      const content = generateLensContent(unscoredLens, allLenses);
      expect(content.summary.verdict).toContain("XF 50mm f/2.0 R WR");
      expect(content.summary.verdict).toContain("75mm equivalent");
    });

    it("generates genre tiers", () => {
      const content = generateLensContent(scoredLens, allLenses);
      expect(content.summary.genreTiers.length).toBeGreaterThan(0);
      const excellent = content.summary.genreTiers.find(
        (t) => t.label === "Excellent for",
      );
      expect(excellent).toBeDefined();
      expect(excellent!.genres).toContain("Landscape");
    });

    it("generates strengths at cluster level", () => {
      const content = generateLensContent(scoredLens, allLenses);
      expect(content.summary.strengths).toContain(
        "Excellent sharpness at all apertures",
      );
      expect(content.summary.strengths).toContain(
        "Weather-sealed construction",
      );
    });

    it("lists weaknesses from low-scoring fields", () => {
      const content = generateLensContent(scoredLens, allLenses);
      const vignetting = content.summary.weaknesses.find((w) =>
        w.toLowerCase().includes("vignetting"),
      );
      expect(vignetting).toBeDefined();
    });
  });

  describe("optical clusters", () => {
    it("returns clusters for scored lens", () => {
      const content = generateLensContent(scoredLens, allLenses);
      expect(content.opticalClusters).not.toBeNull();
      expect(content.opticalClusters!.sharpness.length).toBe(4);
      expect(content.opticalClusters!.aberrations.length).toBe(5);
      expect(content.opticalClusters!.rendering.length).toBe(4);
      expect(content.opticalClusters!.distortion.length).toBe(1);
    });

    it("returns null for unscored lens", () => {
      const content = generateLensContent(unscoredLens, allLenses);
      expect(content.opticalClusters).toBeNull();
    });

    it("marks high scores as strengths", () => {
      const content = generateLensContent(scoredLens, allLenses);
      const center = content.opticalClusters!.sharpness[0];
      expect(center.isStrength).toBe(true);
    });

    it("marks low scores as weaknesses", () => {
      const content = generateLensContent(scoredLens, allLenses);
      const vignetting = content.opticalClusters!.rendering.find(
        (a) => a.field === "Vignetting (wide open)",
      );
      expect(vignetting).toBeDefined();
      expect(vignetting!.isStrength).toBe(false);
    });
  });

  describe("genre fit", () => {
    it("returns entries for scored lens", () => {
      const content = generateLensContent(scoredLens, allLenses);
      expect(content.genreFit.length).toBe(9);
    });

    it("returns empty for unscored lens", () => {
      const content = generateLensContent(unscoredLens, allLenses);
      expect(content.genreFit.length).toBe(0);
    });

    it("follows canonical genre order", () => {
      const content = generateLensContent(scoredLens, allLenses);
      const genres = content.genreFit.map((g) => g.genre);
      expect(genres[0]).toBe("nightscape");
      expect(genres[8]).toBe("macro");
    });

    it("separates primary and secondary fields", () => {
      const content = generateLensContent(scoredLens, allLenses);
      const portrait = content.genreFit.find((g) => g.genre === "portrait")!;
      expect(portrait.primary.length).toBeGreaterThan(0);
      expect(portrait.secondary.length).toBeGreaterThan(0);
    });
  });

  describe("alternatives", () => {
    it("finds alternatives in same mount", () => {
      const content = generateLensContent(scoredLens, allLenses);
      expect(content.alternatives.length).toBeGreaterThan(0);
      expect(content.alternatives[0].slug).toContain("fujifilm-xf-50mm");
    });

    it("excludes the lens itself", () => {
      const content = generateLensContent(scoredLens, allLenses);
      const self = content.alternatives.find(
        (a) => a.model === scoredLens.model,
      );
      expect(self).toBeUndefined();
    });
  });

  describe("weak lens coverage", () => {
    it("generates verdict with lower adjective", () => {
      const content = generateLensContent(weakLens, allLenses);
      expect(content.summary.verdict).toContain("solid");
    });

    it("includes genre tiers for all levels", () => {
      const content = generateLensContent(weakLens, allLenses);
      const avoid = content.summary.genreTiers.find(
        (t) => t.label === "Avoid for",
      );
      const adequate = content.summary.genreTiers.find(
        (t) => t.label === "Adequate for",
      );
      expect(avoid).toBeDefined();
      expect(adequate).toBeDefined();
    });

    it("generates weaknesses from low fields", () => {
      const content = generateLensContent(weakLens, allLenses);
      expect(content.summary.weaknesses.length).toBeGreaterThan(0);
    });

    it("genre fit includes weak and adequate entries", () => {
      const content = generateLensContent(weakLens, allLenses);
      const macro = content.genreFit.find((g) => g.genre === "macro")!;
      expect(macro.mark).toBe(1);
      const street = content.genreFit.find((g) => g.genre === "street")!;
      expect(street.mark).toBe(3.5);
    });
  });

  describe("meta description", () => {
    it("generates SEO description", () => {
      const content = generateLensContent(scoredLens, allLenses);
      expect(content.metaDescription).toContain("Fujifilm XF 56mm f/1.2 R WR");
      expect(content.metaDescription).toContain("Outstanding");
    });
  });
});
