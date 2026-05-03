import { useMemo, useCallback } from "react";
import type { Accessory } from "../../../types/accessory";
import { useSort } from "../../../hooks/useSort";
import { useUrlFilters } from "../../../hooks/useUrlFilters";
import { toSlug } from "../../../utils/slug";
import { formatCategory } from "../../../utils/formatting";
import { ChipGroup } from "../shared/ChipGroup";
import { RESET_VALUE, resetValue } from "../shared/constants";
import { MobileSort } from "../shared/MobileSort";
import type { ColumnDef } from "../shared/table";
import {
  makeAlignClasses,
  ariaSortValue,
  sortIndicatorChar,
} from "../shared/table";
import styles from "./AccessoriesExplorer.module.css";

interface AccessoriesExplorerProps {
  accessories: Accessory[];
}

type AccessorySortKey =
  | "category"
  | "brand"
  | "model"
  | "description"
  | "price";

const COLUMNS: ColumnDef<AccessorySortKey>[] = [
  { key: "category", label: "Category", align: "left", width: "14%" },
  { key: "brand", label: "Brand", align: "left", width: "12%" },
  { key: "model", label: "Model", align: "left", width: "24%" },
  { key: "description", label: "Description", align: "left", width: "40%" },
  { key: "price", label: "Price", align: "right", width: "10%" },
];

const ALIGN_CLASSES = makeAlignClasses(styles);

const PRICE_RANGES: Record<string, [number, number]> = {
  "0-250": [0, 250],
  "250-500": [250, 500],
  "500-1000": [500, 1000],
  "1000+": [1000, Infinity],
};

function passesRangeFilter(value: number, filter: string): boolean {
  if (!filter) return true;
  const range = PRICE_RANGES[filter];
  if (!range) return true;
  const [min, max] = range;
  return value >= min && value <= max;
}

function getCompatibleWith(acc: Accessory): string[] {
  if ("compatibleWith" in acc && Array.isArray(acc.compatibleWith)) {
    return acc.compatibleWith as string[];
  }
  return [];
}

function matchesAccessoryFilters(
  acc: Accessory,
  f: Record<string, string>,
): boolean {
  if (f.category && acc.category !== f.category) return false;
  if (f.mount && (!("mount" in acc) || acc.mount !== f.mount)) return false;
  if (f.compatible) {
    const cq = f.compatible.toLowerCase();
    if (!getCompatibleWith(acc).some((c) => c.toLowerCase().includes(cq)))
      return false;
  }
  if (f.status === "available" && acc.isDiscontinued) return false;
  if (f.status === "discontinued" && !acc.isDiscontinued) return false;
  if (!passesRangeFilter(acc.price, f.price)) return false;
  const q = f.q.toLowerCase();
  if (
    q &&
    !`${acc.brand} ${acc.model} ${acc.description}`.toLowerCase().includes(q)
  )
    return false;
  return true;
}

const FILTER_KEYS = [
  "q",
  "category",
  "mount",
  "compatible",
  "status",
  "price",
] as const;

function AccessoriesExplorer({ accessories }: AccessoriesExplorerProps) {
  const {
    values: f,
    set,
    clear: clearFilters,
    hasFilters,
  } = useUrlFilters(FILTER_KEYS);

  const categories = useMemo(() => {
    const cats = [...new Set(accessories.map((a) => a.category))].sort();
    return cats;
  }, [accessories]);

  const filtered = useMemo(
    () => accessories.filter((acc) => matchesAccessoryFilters(acc, f)),
    [accessories, f],
  );

  const availableFirst = useCallback(
    (a: Accessory, b: Accessory) =>
      Number(a.isDiscontinued ?? false) - Number(b.isDiscontinued ?? false),
    [],
  );
  const { sorted, sortKey, sortDirection, toggleSort } = useSort<
    Accessory,
    AccessorySortKey
  >(filtered, "category", "asc", availableFirst);

  return (
    <div>
      <div className={styles.hero}>
        <h1 className={styles.heroTitle}>Accessories</h1>
        <p className={styles.heroSub}>
          {sorted.length} / {accessories.length} Fujifilm accessories
        </p>
      </div>

      <div className={styles.filters}>
        <div className={styles.filterTop}>
          <input
            className={styles.searchInput}
            type="text"
            placeholder="Search accessories..."
            value={f.q}
            onChange={(e) => set("q", e.target.value)}
            aria-label="Search accessories"
          />
          {hasFilters && (
            <button
              className={styles.clearButton}
              onClick={clearFilters}
              type="button"
              aria-label="Clear all filters"
            >
              &#x2715; Clear
            </button>
          )}
        </div>

        <div className={styles.filterRow}>
          <input
            className={`${styles.searchInput} ${f.compatible ? styles.filterActive : ""}`}
            type="text"
            placeholder="Compatible with... (e.g. X-T5)"
            value={f.compatible}
            onChange={(e) => set("compatible", e.target.value)}
            aria-label="Filter by compatible model"
          />

          <select
            className={`${styles.filterSelect} ${f.category ? styles.filterActive : ""}`}
            value={f.category}
            onChange={(e) => set("category", resetValue(e.target.value))}
            aria-label="Filter by category"
          >
            <option value="" hidden>
              Category
            </option>
            <option value={RESET_VALUE}>All categories</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {formatCategory(c)}
              </option>
            ))}
          </select>

          <select
            className={`${styles.filterSelect} ${f.price ? styles.filterActive : ""}`}
            value={f.price}
            onChange={(e) => set("price", resetValue(e.target.value))}
            aria-label="Filter by price"
          >
            <option value="" hidden>
              Price
            </option>
            <option value={RESET_VALUE}>All</option>
            <option value="0-250">Under $250</option>
            <option value="250-500">$250 - $500</option>
            <option value="500-1000">$500 - $1,000</option>
            <option value="1000+">$1,000+</option>
          </select>
        </div>

        <div className={styles.chipRow}>
          <ChipGroup
            label="Mount"
            value={f.mount}
            onChange={(v) => set("mount", v)}
            styles={styles}
            options={[
              { label: "All", value: "" },
              { label: "X", value: "X" },
              { label: "GFX", value: "GFX" },
            ]}
          />
          <ChipGroup
            label="Status"
            value={f.status}
            onChange={(v) => set("status", v)}
            styles={styles}
            options={[
              { label: "All", value: "" },
              { label: "Available", value: "available" },
              { label: "Discontinued", value: "discontinued" },
            ]}
          />
        </div>

        <MobileSort
          columns={COLUMNS}
          sortKey={sortKey}
          sortDirection={sortDirection}
          toggleSort={toggleSort}
          styles={styles}
        />
      </div>

      {sorted.length === 0 ? (
        <p className={styles.emptyState}>
          No accessories match the current filters.
        </p>
      ) : (
        <>
          {/* Table — desktop */}
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <colgroup>
                {COLUMNS.map((col) => (
                  <col key={col.key} style={{ width: col.width }} />
                ))}
              </colgroup>
              <thead>
                <tr>
                  {COLUMNS.map((col) => (
                    <th
                      key={col.key}
                      className={ALIGN_CLASSES[col.align]}
                      aria-sort={ariaSortValue(col.key, sortKey, sortDirection)}
                    >
                      <button
                        type="button"
                        className={styles.sortButton}
                        onClick={() => toggleSort(col.key)}
                      >
                        {col.label}
                        <span className={styles.sortIndicator}>
                          {sortIndicatorChar(col.key, sortKey, sortDirection)}
                        </span>
                      </button>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {sorted.map((acc) => {
                  const slug = toSlug(`${acc.brand} ${acc.model}`);
                  return (
                    <tr
                      key={`${acc.brand}-${acc.model}`}
                      className={
                        acc.isDiscontinued ? styles.rowDiscontinued : undefined
                      }
                    >
                      <td>
                        <span className={styles.categoryBadge}>
                          {formatCategory(acc.category)}
                        </span>
                      </td>
                      <td>{acc.brand}</td>
                      <td className={styles.modelCell}>
                        <a
                          className={styles.lensLink}
                          href={`/accessories/${slug}`}
                        >
                          {acc.model}
                        </a>
                      </td>
                      <td className={styles.descriptionCell}>
                        {acc.description}
                        {"compatibleWith" in acc &&
                          Array.isArray(acc.compatibleWith) && (
                            <div className={styles.compatBadges}>
                              {(acc.compatibleWith as string[]).map((c) => (
                                <span key={c} className={styles.compatBadge}>
                                  {c}
                                </span>
                              ))}
                            </div>
                          )}
                      </td>
                      <td className={styles.cellRight}>~${acc.price}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Cards — mobile */}
          <div className={styles.cards}>
            {sorted.map((acc) => {
              const slug = toSlug(`${acc.brand} ${acc.model}`);
              return (
                <div
                  key={`${acc.brand}-${acc.model}`}
                  className={`${styles.card} ${acc.isDiscontinued ? styles.cardDiscontinued : ""}`}
                >
                  <div className={styles.cardHeader}>
                    <a
                      className={styles.lensLink}
                      href={`/accessories/${slug}`}
                    >
                      {acc.brand} {acc.model}
                    </a>
                    <span className={styles.cardPrice}>~${acc.price}</span>
                  </div>
                  <p className={styles.cardDescription}>{acc.description}</p>
                  <div className={styles.cardBadges}>
                    <span className={styles.badge}>
                      {formatCategory(acc.category)}
                    </span>
                    {"mount" in acc && acc.mount && (
                      <span className={styles.badge}>{acc.mount}</span>
                    )}
                    {acc.isDiscontinued && (
                      <span className={styles.badge}>Discontinued</span>
                    )}
                  </div>
                  {"compatibleWith" in acc &&
                    Array.isArray(acc.compatibleWith) && (
                      <div className={styles.compatBadges}>
                        {(acc.compatibleWith as string[]).map((c) => (
                          <span key={c} className={styles.compatBadge}>
                            {c}
                          </span>
                        ))}
                      </div>
                    )}
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

export default AccessoriesExplorer;
