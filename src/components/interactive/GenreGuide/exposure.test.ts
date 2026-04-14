import { describe, it, expect } from "vitest";
import type { Lens } from "../../../types/lens";
import { astroExposure, handheldExposure } from "./exposure";

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

const xf16 = makeLens({
  brand: "Fujifilm",
  model: "XF 16mm f/1.4",
  focalLengthMin: 16,
  focalLengthMax: 16,
  maxAperture: 1.4,
});

const xf90 = makeLens({
  brand: "Fujifilm",
  model: "XF 90mm f/2.0",
  focalLengthMin: 90,
  focalLengthMax: 90,
  maxAperture: 2.0,
});

const xf23 = makeLens({
  brand: "Fujifilm",
  model: "XF 23mm f/1.4",
  focalLengthMin: 23,
  focalLengthMax: 23,
  maxAperture: 1.4,
});

// =============================================================================
// astroExposure
// =============================================================================

describe("astroExposure", () => {
  it("computes rule-of-500 max exposure", () => {
    const result = astroExposure(xf16, -7, 1600, 1.5);
    expect(result.maxT).toBeCloseTo(500 / (1.5 * 16), 2);
  });

  it("computes ideal ISO for Milky Way scenario (EV -7)", () => {
    const result = astroExposure(xf16, -7, 1600, 1.5);
    expect(result.idealIso).toBe(
      Math.round((1.4 * 1.4 * 100) / ((500 / (1.5 * 16)) * Math.pow(2, -7))),
    );
  });

  it("ratio = actT / maxT", () => {
    const result = astroExposure(xf16, -7, 1600, 1.5);
    expect(result.ratio).toBeCloseTo(result.actT / result.maxT, 6);
  });

  it("GFX crop gives longer max exposure and lower ideal ISO", () => {
    const x = astroExposure(xf16, -7, 1600, 1.5);
    const gfx = astroExposure(xf16, -7, 1600, 0.79);
    expect(gfx.maxT).toBeGreaterThan(x.maxT);
    expect(gfx.idealIso).toBeLessThan(x.idealIso);
  });
});

// =============================================================================
// handheldExposure
// =============================================================================

describe("handheldExposure", () => {
  it("street uses reciprocal rule: 1/(crop × FL)", () => {
    const result = handheldExposure(xf23, "street", 2, 1.5);
    const expected = 1 / (1.5 * 23);
    expect(result.minShutter).toBeCloseTo(expected, 6);
  });

  it("portrait uses 2x FL rule", () => {
    const result = handheldExposure(xf90, "portrait", 10, 1.5);
    expect(result.minShutter).toBeCloseTo(1 / (2 * 1.5 * 90), 6);
  });

  it("macro uses magnification-adjusted rule", () => {
    const result = handheldExposure(xf90, "macro", 10, 1.5, 1.0);
    expect(result.minShutter).toBeCloseTo(1 / (90 * 2 * 1.5), 6);
  });

  it("macro at 0.5x magnification", () => {
    const result = handheldExposure(xf90, "macro", 10, 1.5, 0.5);
    expect(result.minShutter).toBeCloseTo(1 / (90 * 1.5 * 1.5), 6);
  });

  it("sport uses 4x FL rule", () => {
    const result = handheldExposure(xf90, "sport", 13, 1.5);
    expect(result.minShutter).toBeCloseTo(1 / (4 * 1.5 * 90), 6);
  });

  it("wildlife uses same 4x FL rule as sport", () => {
    const s = handheldExposure(xf90, "sport", 9, 1.5);
    const w = handheldExposure(xf90, "wildlife", 9, 1.5);
    expect(w.minShutter).toBe(s.minShutter);
  });

  it("computes ideal ISO at widest aperture", () => {
    const result = handheldExposure(xf23, "street", 2, 1.5);
    const expectedIso = Math.round(
      (1.4 * 1.4 * 100) / (result.minShutter * Math.pow(2, 2)),
    );
    expect(result.idealIso).toBe(expectedIso);
  });
});
