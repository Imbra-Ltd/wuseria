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
      expect(content.opticalClusters!.sharpness).toHaveLength(4);
      expect(content.opticalClusters!.aberrations).toHaveLength(5);
      expect(content.opticalClusters!.rendering).toHaveLength(4);
      expect(content.opticalClusters!.distortion).toHaveLength(1);
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
      expect(content.genreFit).toHaveLength(9);
    });

    it("returns empty for unscored lens", () => {
      const content = generateLensContent(unscoredLens, allLenses);
      expect(content.genreFit).toHaveLength(0);
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
    const altHighOQ = makeLens({
      brand: "Sigma",
      model: "56mm f/1.4 DC DN",
      mount: "X",
      focalLengthMin: 56,
      focalLengthMax: 56,
      maxAperture: 1.4,
      weight: 280,
      price: 480,
      centerWideOpen: 1.5,
      cornerWideOpen: 1.5,
      centerStopped: 1.5,
      cornerStopped: 1.5,
      longitudinalCA: 1.5,
      lateralCA: 1.5,
      coma: 1.5,
      astigmatism: 1.5,
      sphericalAberration: 1.5,
      distortion: 1.5,
      vignettingWideOpen: 1.5,
      vignettingStopped: 1.5,
      bokeh: 1.5,
      flareResistance: 1.5,
    });

    const altLowOQ = makeLens({
      brand: "Viltrox",
      model: "56mm f/1.4 STM",
      mount: "X",
      focalLengthMin: 56,
      focalLengthMax: 56,
      maxAperture: 1.4,
      weight: 260,
      price: 300,
      centerWideOpen: 1,
      cornerWideOpen: 1,
      centerStopped: 1,
      cornerStopped: 1,
      longitudinalCA: 1,
      lateralCA: 1,
      coma: 1,
      astigmatism: 1,
      sphericalAberration: 1,
      distortion: 1,
      vignettingWideOpen: 1,
      vignettingStopped: 1,
      bokeh: 1,
      flareResistance: 1,
    });

    const altZoom = makeLens({
      brand: "Fujifilm",
      model: "XF 50-140mm f/2.8 R LM OIS WR",
      mount: "X",
      type: "zoom",
      focalLengthMin: 50,
      focalLengthMax: 140,
      maxAperture: 2.8,
      weight: 995,
      price: 1600,
      centerWideOpen: 1.5,
      cornerWideOpen: 1.5,
      centerStopped: 1.5,
      cornerStopped: 1.5,
      longitudinalCA: 1.5,
      lateralCA: 1.5,
      coma: 1.5,
      astigmatism: 1.5,
      sphericalAberration: 1.5,
      distortion: 1.5,
      vignettingWideOpen: 1.5,
      vignettingStopped: 1.5,
      bokeh: 1.5,
      flareResistance: 1.5,
    });

    const altUnscored = makeLens({
      brand: "7Artisans",
      model: "55mm f/1.4 II",
      mount: "X",
      focalLengthMin: 55,
      focalLengthMax: 55,
      maxAperture: 1.4,
      weight: 230,
      price: 150,
    });

    const altLenses = [
      scoredLens,
      unscoredLens,
      weakLens,
      altHighOQ,
      altLowOQ,
      altZoom,
      altUnscored,
    ];

    it("shows same-type alternatives first, sorted by OQ", () => {
      const content = generateLensContent(scoredLens, altLenses);
      const slugs = content.alternatives.map((a) => a.slug);
      const highIdx = slugs.findIndex((s) => s.includes("sigma"));
      const lowIdx = slugs.findIndex((s) => s.includes("viltrox"));
      expect(highIdx).toBeLessThan(lowIdx);
    });

    it("limits same-type to 5 and other-type to 3", () => {
      const content = generateLensContent(scoredLens, altLenses);
      expect(content.alternatives.length).toBeLessThanOrEqual(8);
    });

    it("places unscored same-type alternatives after scored", () => {
      const content = generateLensContent(scoredLens, altLenses);
      const slugs = content.alternatives.map((a) => a.slug);
      const scoredIdx = slugs.findIndex((s) => s.includes("sigma"));
      const unscoredIdx = slugs.findIndex((s) => s.includes("xf-50mm"));
      expect(scoredIdx).toBeGreaterThanOrEqual(0);
      expect(unscoredIdx).toBeGreaterThanOrEqual(0);
      expect(scoredIdx).toBeLessThan(unscoredIdx);
    });

    it("includes zooms that cover the focal length as other-type", () => {
      const content = generateLensContent(scoredLens, altLenses);
      const zoom = content.alternatives.find((a) =>
        a.slug.includes("50-140mm"),
      );
      expect(zoom).toBeDefined();
    });

    it("excludes lenses outside ±20% range", () => {
      const content = generateLensContent(scoredLens, altLenses);
      // weakLens at 35mm: |35-56| = 21 > 56*0.2 = 11.2
      const found = content.alternatives.find((a) =>
        a.slug.includes("xf-35mm"),
      );
      expect(found).toBeUndefined();
    });

    it("excludes discontinued lenses", () => {
      const discontinued = makeLens({
        brand: "Fujifilm",
        model: "XF 56mm f/1.2 R",
        mount: "X",
        focalLengthMin: 56,
        focalLengthMax: 56,
        isDiscontinued: true,
      });
      const withDiscontinued = [...altLenses, discontinued];
      const content = generateLensContent(scoredLens, withDiscontinued);
      const found = content.alternatives.find(
        (a) => a.model === "XF 56mm f/1.2 R",
      );
      expect(found).toBeUndefined();
    });

    it("excludes the lens itself", () => {
      const content = generateLensContent(scoredLens, altLenses);
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
