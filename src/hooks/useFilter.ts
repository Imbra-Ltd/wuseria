import { useState, useMemo } from "react";

type FilterValues<K extends string> = Partial<Record<K, string>>;

interface UseFilterResult<T, K extends string> {
  filtered: T[];
  filters: FilterValues<K>;
  setFilter: (key: K, value: string) => void;
  clearFilters: () => void;
}

function useFilter<T, K extends string & keyof T>(
  items: T[],
  filterKeys: K[],
): UseFilterResult<T, K> {
  const [filters, setFilters] = useState<FilterValues<K>>({});

  const filtered = useMemo(() => {
    return items.filter((item) =>
      filterKeys.every((key) => {
        const filterValue = filters[key];
        if (!filterValue) return true;

        const itemValue = item[key as keyof T];
        if (itemValue == null) return false;

        return String(itemValue) === filterValue;
      }),
    );
  }, [items, filters, filterKeys]);

  function setFilter(key: K, value: string): void {
    setFilters((prev) => {
      const next = { ...prev };
      if (value === "") {
        delete next[key];
      } else {
        next[key] = value;
      }
      return next;
    });
  }

  function clearFilters(): void {
    setFilters({});
  }

  return { filtered, filters, setFilter, clearFilters };
}

export { useFilter };
export type { FilterValues };
