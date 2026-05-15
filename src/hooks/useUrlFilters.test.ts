import { describe, it, expect, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useUrlFilters } from "./useUrlFilters";

const KEYS = ["type", "mount", "ois"] as const;

describe("useUrlFilters", () => {
  beforeEach(() => {
    globalThis.history.replaceState(null, "", globalThis.location.pathname);
  });

  it("initializes all keys to empty string", () => {
    const { result } = renderHook(() => useUrlFilters(KEYS));
    expect(result.current.values).toEqual({ type: "", mount: "", ois: "" });
    expect(result.current.hasFilters).toBe(false);
  });

  it("reads initial values from URL params", () => {
    globalThis.history.replaceState(null, "", "?type=prime&ois=yes");
    const { result } = renderHook(() => useUrlFilters(KEYS));
    expect(result.current.values.type).toBe("prime");
    expect(result.current.values.ois).toBe("yes");
    expect(result.current.values.mount).toBe("");
    expect(result.current.hasFilters).toBe(true);
  });

  it("set updates a single filter value", () => {
    const { result } = renderHook(() => useUrlFilters(KEYS));
    act(() => result.current.set("type", "zoom"));
    expect(result.current.values.type).toBe("zoom");
    expect(result.current.hasFilters).toBe(true);
  });

  it("set syncs to URL", () => {
    const { result } = renderHook(() => useUrlFilters(KEYS));
    act(() => result.current.set("mount", "GFX"));
    expect(globalThis.location.search).toContain("mount=GFX");
  });

  it("clear resets all values to empty", () => {
    const { result } = renderHook(() => useUrlFilters(KEYS));
    act(() => result.current.set("type", "prime"));
    act(() => result.current.set("ois", "yes"));
    act(() => result.current.clear());
    expect(result.current.values).toEqual({ type: "", mount: "", ois: "" });
    expect(result.current.hasFilters).toBe(false);
  });

  it("clear removes URL params", () => {
    const { result } = renderHook(() => useUrlFilters(KEYS));
    act(() => result.current.set("type", "prime"));
    act(() => result.current.clear());
    expect(globalThis.location.search).toBe("");
  });

  it("ignores URL params not in keys", () => {
    globalThis.history.replaceState(null, "", "?type=prime&unknown=foo");
    const { result } = renderHook(() => useUrlFilters(KEYS));
    expect(result.current.values).toEqual({
      type: "prime",
      mount: "",
      ois: "",
    });
  });
});
