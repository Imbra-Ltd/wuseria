import { useState, useMemo, useCallback } from "react";
import type { Accessory, AccessoryCategory } from "../../../types/accessory";
import { useSort } from "../../../hooks/useSort";
import { toSlug } from "../../../utils/slug";
import { ChipGroup } from "../shared/ChipGroup";
import { RESET_VALUE, resetValue } from "../shared/constants";
import { MobileSort } from "../shared/MobileSort";
import type { ColumnAlign } from "../shared/table";
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

const COLUMNS: { key: AccessorySortKey; label: string; align: ColumnAlign }[] =
  [
    { key: "category", label: "Category", align: "left" },
    { key: "brand", label: "Brand", align: "left" },
    { key: "model", label: "Model", align: "left" },
    { key: "description", label: "Description", align: "left" },
    { key: "price", label: "Price", align: "right" },
  ];

const ALIGN_CLASSES = makeAlignClasses(styles);

const CATEGORY_LABELS: Record<string, string> = {
  flash: "Flash",
  "battery-grip": "Battery Grip",
  "hand-grip": "Hand Grip",
  battery: "Battery",
  charger: "Charger",
  "lens-accessory": "Lens Accessory",
  adapter: "Adapter",
  remote: "Remote",
  audio: "Audio",
  cooling: "Cooling",
  "body-accessory": "Body Accessory",
};

function formatCategory(category: AccessoryCategory): string {
  return CATEGORY_LABELS[category] ?? category;
}

const PRICE_RANGES: Record<string, [number, number]> = {
  "0-250": [0, 250],
  "250-500": [250, 500],
  "500-1000": [500, 1000],
  "1000+": [1000, Infinity],
};

interface AccessoryFilterValues {
  search: string;
  category: string;
  mount: string;
  compatible: string;
  discontinued: string;
  priceRange: string;
}

function passesRangeFilter(value: number, filter: string): boolean {
  if (!filter) return true;
  const [min, max] = PRICE_RANGES[filter];
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
  f: AccessoryFilterValues,
): boolean {
  if (f.category && acc.category !== f.category) return false;
  if (f.mount && (!("mount" in acc) || acc.mount !== f.mount)) return false;
  if (f.compatible) {
    const cq = f.compatible.toLowerCase();
    if (!getCompatibleWith(acc).some((c) => c.toLowerCase().includes(cq)))
      return false;
  }
  if (f.discontinued === "available" && acc.isDiscontinued) return false;
  if (f.discontinued === "discontinued" && !acc.isDiscontinued) return false;
  if (!passesRangeFilter(acc.price, f.priceRange)) return false;
  const q = f.search.toLowerCase();
  if (
    q &&
    !`${acc.brand} ${acc.model} ${acc.description}`.toLowerCase().includes(q)
  )
    return false;
  return true;
}

function AccessoriesExplorer({ accessories }: AccessoriesExplorerProps) {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [mount, setMount] = useState("");
  const [compatible, setCompatible] = useState("");
  const [discontinued, setDiscontinued] = useState("");
  const [priceRange, setPriceRange] = useState("");

  const categories = useMemo(() => {
    const cats = [...new Set(accessories.map((a) => a.category))].sort();
    return cats;
  }, [accessories]);

  const filtered = useMemo(() => {
    const f: AccessoryFilterValues = {
      search,
      category,
      mount,
      compatible,
      discontinued,
      priceRange,
    };
    return accessories.filter((acc) => matchesAccessoryFilters(acc, f));
  }, [
    accessories,
    search,
    category,
    mount,
    compatible,
    discontinued,
    priceRange,
  ]);

  const availableFirst = useCallback(
    (a: Accessory, b: Accessory) =>
      Number(a.isDiscontinued ?? false) - Number(b.isDiscontinued ?? false),
    [],
  );
  const { sorted, sortKey, sortDirection, toggleSort } = useSort<
    Accessory,
    AccessorySortKey
  >(filtered, "category", "asc", availableFirst);

  const hasFilters =
    search || category || mount || compatible || discontinued || priceRange;

  function clearFilters(): void {
    setSearch("");
    setCategory("");
    setMount("");
    setCompatible("");
    setDiscontinued("");
    setPriceRange("");
  }

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
            value={search}
            onChange={(e) => setSearch(e.target.value)}
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
            className={`${styles.searchInput} ${compatible ? styles.filterActive : ""}`}
            type="text"
            placeholder="Compatible with... (e.g. X-T5)"
            value={compatible}
            onChange={(e) => setCompatible(e.target.value)}
            aria-label="Filter by compatible model"
          />

          <select
            className={`${styles.filterSelect} ${category ? styles.filterActive : ""}`}
            value={category}
            onChange={(e) => setCategory(resetValue(e.target.value))}
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
            className={`${styles.filterSelect} ${priceRange ? styles.filterActive : ""}`}
            value={priceRange}
            onChange={(e) => setPriceRange(resetValue(e.target.value))}
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
            value={mount}
            onChange={setMount}
            styles={styles}
            options={[
              { label: "All", value: "" },
              { label: "X", value: "X" },
              { label: "GFX", value: "GFX" },
            ]}
          />
          <ChipGroup
            label="Status"
            value={discontinued}
            onChange={setDiscontinued}
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
