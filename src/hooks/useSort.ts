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

function useSort<T, K extends string & keyof T>(
  items: T[],
  defaultKey: K,
  defaultDirection: SortDirection = "asc",
): UseSortResult<T, K> {
  const [sort, setSort] = useState<SortState<K>>({
    key: defaultKey,
    direction: defaultDirection,
  });

  const sorted = useMemo(() => {
    const copy = [...items];
    copy.sort((a, b) => {
      const aVal = a[sort.key as keyof T];
      const bVal = b[sort.key as keyof T];

      if (aVal == null && bVal == null) return 0;
      if (aVal == null) return 1;
      if (bVal == null) return -1;

      if (typeof aVal === "string" && typeof bVal === "string") {
        const cmp = aVal.localeCompare(bVal);
        return sort.direction === "asc" ? cmp : -cmp;
      }

      if (typeof aVal === "number" && typeof bVal === "number") {
        return sort.direction === "asc" ? aVal - bVal : bVal - aVal;
      }

      return 0;
    });
    return copy;
  }, [items, sort.key, sort.direction]);

  function toggleSort(key: K): void {
    setSort((prev) => ({
      key,
      direction: prev.key === key && prev.direction === "asc" ? "desc" : "asc",
    }));
  }

  return { sorted, sortKey: sort.key, sortDirection: sort.direction, toggleSort };
}

export { useSort };
export type { SortDirection };
