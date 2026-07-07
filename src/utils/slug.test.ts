import { describe, it, expect } from "vitest";
import { toSlug, toDataSlug } from "./slug";

describe("toSlug", () => {
  it("lowercases and hyphenates", () => {
    expect(toSlug("XF 23mm f/1.4")).toBe("xf-23mm-f1-4");
  });

  it("removes slashes", () => {
    expect(toSlug("f/2.8")).toBe("f2-8");
  });

  it("collapses multiple special chars", () => {
    expect(toSlug("XF  16mm  f/1.4  R  WR")).toBe("xf-16mm-f1-4-r-wr");
  });

  it("strips leading and trailing hyphens", () => {
    expect(toSlug(" -hello- ")).toBe("hello");
  });

  it("handles brand + model", () => {
    expect(toSlug("Fujifilm XF 56mm f/1.2 R")).toBe("fujifilm-xf-56mm-f1-2-r");
  });
});

describe("toDataSlug", () => {
  it("applies the ADR-056 brand override for Carl Zeiss", () => {
    expect(toDataSlug("Carl Zeiss", "Touit 32mm f/1.8")).toBe(
      "zeiss-touit-32mm-f1-8",
    );
  });

  it("matches toSlug(brand + model) for brands without an override", () => {
    expect(toDataSlug("Fujifilm", "XF 56mm f/1.2 R")).toBe(
      toSlug("Fujifilm XF 56mm f/1.2 R"),
    );
  });
});
