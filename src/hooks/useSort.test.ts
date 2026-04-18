import { describe, it, expect } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useSort } from "./useSort";

interface Item {
  name: string;
  price: number;
  year: number;
}

const items: Item[] = [
  { name: "Bravo", price: 300, year: 2020 },
  { name: "Alpha", price: 100, year: 2022 },
  { name: "Charlie", price: 200, year: 2021 },
];

describe("useSort", () => {
  it("sorts by default key ascending", () => {
    const { result } = renderHook(() => useSort(items, "name"));
    expect(result.current.sorted.map((i) => i.name)).toEqual(["Alpha", "Bravo", "Charlie"]);
    expect(result.current.sortKey).toBe("name");
    expect(result.current.sortDirection).toBe("asc");
  });

  it("sorts numbers ascending", () => {
    const { result } = renderHook(() => useSort(items, "price"));
    expect(result.current.sorted.map((i) => i.price)).toEqual([100, 200, 300]);
  });

  it("toggles to descending on same key", () => {
    const { result } = renderHook(() => useSort(items, "price"));
    act(() => result.current.toggleSort("price"));
    expect(result.current.sortDirection).toBe("desc");
    expect(result.current.sorted.map((i) => i.price)).toEqual([300, 200, 100]);
  });

  it("switches key and resets to ascending", () => {
    type K = "name" | "price" | "year";
    const { result } = renderHook(() => useSort<Item, K>(items, "price"));
    act(() => result.current.toggleSort("price")); // desc
    act(() => result.current.toggleSort("name")); // new key → asc
    expect(result.current.sortKey).toBe("name");
    expect(result.current.sortDirection).toBe("asc");
  });

  it("applies stable prefix sort", () => {
    const withDiscontinued = [
      { name: "B", price: 1, year: 2020, disc: true },
      { name: "A", price: 2, year: 2021, disc: false },
      { name: "C", price: 3, year: 2022, disc: false },
    ];
    const prefix = (a: typeof withDiscontinued[0], b: typeof withDiscontinued[0]) =>
      Number(a.disc) - Number(b.disc);
    const { result } = renderHook(() => useSort(withDiscontinued, "name", "asc", prefix));
    expect(result.current.sorted.map((i) => i.name)).toEqual(["A", "C", "B"]);
  });

  it("handles null values by sorting them last", () => {
    const withNulls = [
      { name: "A", price: null as unknown as number, year: 2020 },
      { name: "B", price: 100, year: 2021 },
    ];
    const { result } = renderHook(() => useSort(withNulls, "price"));
    expect(result.current.sorted.map((i) => i.name)).toEqual(["B", "A"]);
  });
});
