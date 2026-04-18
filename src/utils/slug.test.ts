import { describe, it, expect } from "vitest";
import { toSlug } from "./slug";

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
