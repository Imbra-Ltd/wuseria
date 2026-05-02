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

  const filtered = useMemo(() => {
    const q = f.q.toLowerCase();
    return lenses.filter((lens) => {
      if (f.mount && lens.mount !== f.mount) return false;
      if (f.type && lens.type !== f.type) return false;
      if (f.brand && lens.brand !== f.brand) return false;
      if (f.ois === "yes" && !lens.hasOis) return false;
      if (f.ois === "no" && lens.hasOis) return false;
      if (f.wr === "yes" && !lens.isWeatherSealed) return false;
      if (f.wr === "no" && lens.isWeatherSealed) return false;
      if (f.af === "yes" && !lens.afMotor) return false;
      if (f.af === "no" && lens.afMotor) return false;
      if (f.status === "available" && lens.isDiscontinued) return false;
      if (f.status === "discontinued" && !lens.isDiscontinued) return false;
      if (f.fl) {
        const [min, max] = FL_RANGES[f.fl];
        if (lens.focalLengthMax < min || lens.focalLengthMin > max)
          return false;
      }
      if (f.aperture && lens.maxAperture > parseFloat(f.aperture)) return false;
      if (f.thread === "none" && lens.filterThread != null) return false;
      if (
        f.thread &&
        f.thread !== "none" &&
        lens.filterThread !== Number(f.thread)
      )
        return false;
      if (f.oq === "not-scored") {
        if (lens.opticalQuality != null) return false;
      } else if (f.oq) {
        const [min, max] = OQ_RANGES[f.oq];
        if (
          lens.opticalQuality == null ||
          lens.opticalQuality < min ||
          lens.opticalQuality > max
        )
          return false;
      }
      if (f.price) {
        const [min, max] = PRICE_RANGES[f.price];
        if (lens.price < min || lens.price > max) return false;
      }
      if (q && !`${lens.brand} ${lens.model}`.toLowerCase().includes(q))
        return false;
      return true;
    });
  }, [lenses, f]);

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
