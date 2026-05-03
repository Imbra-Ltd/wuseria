import { useState, useMemo } from "react";

type SortDirection = "asc" | "desc";

interface SortState<K extends string> {
  key: K;
  direction: SortDirection;
}

interface UseSortResult<T, K extends string> {
  sorted: T[];
  sortKey: K;
  sortDirection: SortDirection;
  toggleSort: (key: K) => void;
}

function compareValues(aVal: unknown, bVal: unknown): number {
  if (aVal == null && bVal == null) return 0;
  if (aVal == null) return 1;
  if (bVal == null) return -1;
  if (typeof aVal === "string" && typeof bVal === "string") {
    return aVal.localeCompare(bVal);
  }
  if (typeof aVal === "boolean" && typeof bVal === "boolean") {
    return Number(aVal) - Number(bVal);
  }
  if (typeof aVal === "number" && typeof bVal === "number") {
    return aVal - bVal;
  }
  return 0;
}

function useSort<T, K extends string & keyof T>(
  items: T[],
  defaultKey: K,
  defaultDirection: SortDirection = "asc",
  stablePrefix?: (a: T, b: T) => number,
): UseSortResult<T, K> {
  const [sort, setSort] = useState<SortState<K>>({
    key: defaultKey,
    direction: defaultDirection,
  });

  const sorted = useMemo(() => {
    const copy = [...items];
    copy.sort((a, b) => {
      // Stable prefix sort (e.g. available before discontinued)
      if (stablePrefix) {
        const pre = stablePrefix(a, b);
        if (pre !== 0) return pre;
      }

      const aVal = a[sort.key as keyof T];
      const bVal = b[sort.key as keyof T];

      // Nulls always last, regardless of direction
      if (aVal == null && bVal == null) return 0;
      if (aVal == null) return 1;
      if (bVal == null) return -1;

      const cmp = compareValues(aVal, bVal);
      return sort.direction === "asc" ? cmp : -cmp;
    });
    return copy;
  }, [items, sort.key, sort.direction, stablePrefix]);

  function toggleSort(key: K): void {
    setSort((prev) => ({
      key,
      direction: prev.key === key && prev.direction === "asc" ? "desc" : "asc",
    }));
  }

  return {
    sorted,
    sortKey: sort.key,
    sortDirection: sort.direction,
    toggleSort,
  };
}

export { useSort };
export type { SortDirection };
