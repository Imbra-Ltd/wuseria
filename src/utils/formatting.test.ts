import { describe, it, expect } from "vitest";
import { formatShutter, formatFL, formatCategory } from "./formatting";

describe("formatShutter", () => {
  it("formats hours", () => {
    expect(formatShutter(3600)).toBe("1h");
    expect(formatShutter(7200)).toBe("2h");
  });

  it("formats minutes", () => {
    expect(formatShutter(60)).toBe("1m");
    expect(formatShutter(300)).toBe("5m");
  });

  it("formats whole seconds", () => {
    expect(formatShutter(1)).toBe("1s");
    expect(formatShutter(30)).toBe("30s");
  });

  it("formats fractions", () => {
    expect(formatShutter(1 / 250)).toBe("1/250");
    expect(formatShutter(1 / 60)).toBe("1/60");
    expect(formatShutter(1 / 4000)).toBe("1/4000");
  });

  it("rounds to nearest whole second", () => {
    expect(formatShutter(1.4)).toBe("1s");
    expect(formatShutter(29.7)).toBe("30s");
  });

  it("rounds fractional denominators", () => {
    expect(formatShutter(0.008)).toBe("1/125");
  });
});

describe("formatFL", () => {
  it("formats prime (min === max)", () => {
    expect(formatFL(23, 23)).toBe("23mm");
  });

  it("formats zoom (min !== max)", () => {
    expect(formatFL(18, 55)).toBe("18-55mm");
  });
});

describe("formatCategory", () => {
  it("formats known categories", () => {
    expect(formatCategory("battery-grip")).toBe("Battery Grip");
    expect(formatCategory("lens-accessory")).toBe("Lens Accessory");
    expect(formatCategory("body-accessory")).toBe("Body Accessory");
    expect(formatCategory("flash")).toBe("Flash");
  });

  it("returns unknown categories as-is", () => {
    expect(formatCategory("unknown")).toBe("unknown");
  });
});
