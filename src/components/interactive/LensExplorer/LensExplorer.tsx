import { useState, useMemo, useCallback } from "react";
import { useSort } from "../../../hooks/useSort";
import { useUrlFilters } from "../../../hooks/useUrlFilters";
import { toSlug } from "../../../utils/slug";
import type { ExplorerLens, LensExplorerProps, LensSortKey } from "./constants";
import {
  FL_RANGES,
  OQ_RANGES,
  PRICE_RANGES,
  INITIAL_PAGE_SIZE,
} from "./constants";
import { LensFilters } from "./LensFilters";
import { LensResults } from "./LensResults";
import styles from "./LensExplorer.module.css";

function passesBooleanFilter(
  filter: string,
  value: boolean | undefined,
): boolean {
  if (filter === "yes") return !!value;
  if (filter === "no") return !value;
  return true;
}

function passesStatusFilter(
  filter: string,
  isDiscontinued: boolean | undefined,
): boolean {
  if (filter === "available") return !isDiscontinued;
  if (filter === "discontinued") return !!isDiscontinued;
  return true;
}

function passesFlFilter(lens: ExplorerLens, fl: string): boolean {
  if (!fl) return true;
  const [min, max] = FL_RANGES[fl];
  return lens.focalLengthMax >= min && lens.focalLengthMin <= max;
}

function passesThreadFilter(
  filterThread: number | null | undefined,
  thread: string,
): boolean {
  if (!thread) return true;
  if (thread === "none") return filterThread == null;
  return filterThread === Number(thread);
}

function passesOqFilter(
  oq: number | null | undefined,
  filter: string,
): boolean {
  if (!filter) return true;
  if (filter === "not-scored") return oq == null;
  const [min, max] = OQ_RANGES[filter];
  return oq != null && oq >= min && oq <= max;
}

function passesRangeFilter(
  value: number,
  filter: string,
  ranges: Record<string, [number, number]>,
): boolean {
  if (!filter) return true;
  const [min, max] = ranges[filter];
  return value >= min && value <= max;
}

function passesExactFilter(value: string, filter: string): boolean {
  return !filter || value === filter;
}

function passesMaxFilter(value: number, filter: string): boolean {
  if (!filter) return true;
  return value <= parseFloat(filter);
}

function passesSearchFilter(text: string, query: string): boolean {
  if (!query) return true;
  return text.toLowerCase().includes(query.toLowerCase());
}

function matchesLensFilters(
  lens: ExplorerLens,
  f: Record<string, string>,
): boolean {
  return (
    passesExactFilter(lens.mount, f.mount) &&
    passesExactFilter(lens.type, f.type) &&
    passesExactFilter(lens.brand, f.brand) &&
    passesBooleanFilter(f.ois, lens.hasOis) &&
    passesBooleanFilter(f.wr, lens.isWeatherSealed) &&
    passesBooleanFilter(f.af, !!lens.afMotor) &&
    passesStatusFilter(f.status, lens.isDiscontinued) &&
    passesFlFilter(lens, f.fl) &&
    passesMaxFilter(lens.maxAperture, f.aperture) &&
    passesThreadFilter(lens.filterThread, f.thread) &&
    passesOqFilter(lens.opticalQuality, f.oq) &&
    passesRangeFilter(lens.price, f.price, PRICE_RANGES) &&
    passesSearchFilter(`${lens.brand} ${lens.model}`, f.q)
  );
}

const FILTER_KEYS = [
  "q",
  "mount",
  "type",
  "brand",
  "ois",
  "wr",
  "af",
  "status",
  "fl",
  "aperture",
  "thread",
  "oq",
  "price",
] as const;

function LensExplorer({ lenses }: LensExplorerProps) {
  const {
    values: f,
    set,
    clear: clearFilters,
    hasFilters,
  } = useUrlFilters(FILTER_KEYS);

  const slugMap = useMemo(
    () =>
      new Map(
        lenses.map((l) => [
          `${l.brand}-${l.model}`,
          toSlug(`${l.brand} ${l.model}`),
        ]),
      ),
    [lenses],
  );

  const brands = useMemo(() => {
    const pool = f.mount ? lenses.filter((l) => l.mount === f.mount) : lenses;
    return [...new Set(pool.map((l) => l.brand))].sort();
  }, [lenses, f.mount]);

  const filtered = useMemo(
    () => lenses.filter((lens) => matchesLensFilters(lens, f)),
    [lenses, f],
  );

  const availableFirst = useCallback(
    (a: ExplorerLens, b: ExplorerLens) =>
      Number(a.isDiscontinued ?? false) - Number(b.isDiscontinued ?? false),
    [],
  );
  const { sorted, sortKey, sortDirection, toggleSort } = useSort<
    ExplorerLens,
    LensSortKey
  >(filtered, "focalLengthMin", "asc", availableFirst);

  function handleMountChange(value: string): void {
    set("mount", value);
    if (f.brand) {
      const brandExistsInMount = lenses.some(
        (l) => l.brand === f.brand && (!value || l.mount === value),
      );
      if (!brandExistsInMount) set("brand", "");
    }
  }

  const [showAll, setShowAll] = useState(false);

  return (
    <div>
      <div className={styles.hero}>
        <h1 className={styles.heroTitle}>Lens Explorer</h1>
        <p className={styles.heroSub}>
          {sorted.length} / {lenses.length} Fujifilm-compatible lenses
        </p>
      </div>

      <LensFilters
        search={f.q}
        setSearch={(v) => set("q", v)}
        mount={f.mount}
        onMountChange={handleMountChange}
        type={f.type}
        setType={(v) => set("type", v)}
        brand={f.brand}
        setBrand={(v) => set("brand", v)}
        ois={f.ois}
        setOis={(v) => set("ois", v)}
        wr={f.wr}
        setWr={(v) => set("wr", v)}
        af={f.af}
        setAf={(v) => set("af", v)}
        discontinued={f.status}
        setDiscontinued={(v) => set("status", v)}
        fl={f.fl}
        setFl={(v) => set("fl", v)}
        maxAp={f.aperture}
        setMaxAp={(v) => set("aperture", v)}
        filterThread={f.thread}
        setFilterThread={(v) => set("thread", v)}
        oqRange={f.oq}
        setOqRange={(v) => set("oq", v)}
        priceRange={f.price}
        setPriceRange={(v) => set("price", v)}
        brands={brands}
        hasFilters={hasFilters}
        clearFilters={clearFilters}
        sortKey={sortKey}
        sortDirection={sortDirection}
        toggleSort={toggleSort}
      />

      {sorted.length === 0 ? (
        <p className={styles.emptyState}>
          No lenses match the current filters.
        </p>
      ) : (
        <>
          <LensResults
            sorted={
              showAll || hasFilters
                ? sorted
                : sorted.slice(0, INITIAL_PAGE_SIZE)
            }
            slugMap={slugMap}
            sortKey={sortKey}
            sortDirection={sortDirection}
            toggleSort={toggleSort}
          />
          {!showAll && !hasFilters && sorted.length > INITIAL_PAGE_SIZE && (
            <button
              type="button"
              className={styles.showAllButton}
              onClick={() => setShowAll(true)}
            >
              Show all {sorted.length} lenses
            </button>
          )}
        </>
      )}
    </div>
  );
}

export default LensExplorer;
