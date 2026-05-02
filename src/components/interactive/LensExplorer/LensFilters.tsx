import { ChipGroup } from "../shared/ChipGroup";
import { MobileSort } from "../shared/MobileSort";
import { RESET_VALUE, resetValue } from "../shared/constants";
import type { LensSortKey } from "./constants";
import { APERTURE_OPTIONS, COLUMNS, FILTER_THREAD_OPTIONS } from "./constants";
import styles from "./LensExplorer.module.css";

interface LensFiltersProps {
  search: string;
  setSearch: (v: string) => void;
  mount: string;
  onMountChange: (v: string) => void;
  type: string;
  setType: (v: string) => void;
  brand: string;
  setBrand: (v: string) => void;
  ois: string;
  setOis: (v: string) => void;
  wr: string;
  setWr: (v: string) => void;
  af: string;
  setAf: (v: string) => void;
  discontinued: string;
  setDiscontinued: (v: string) => void;
  fl: string;
  setFl: (v: string) => void;
  maxAp: string;
  setMaxAp: (v: string) => void;
  filterThread: string;
  setFilterThread: (v: string) => void;
  oqRange: string;
  setOqRange: (v: string) => void;
  priceRange: string;
  setPriceRange: (v: string) => void;
  brands: string[];
  hasFilters: boolean;
  clearFilters: () => void;
  sortKey: LensSortKey;
  sortDirection: "asc" | "desc";
  toggleSort: (key: LensSortKey) => void;
}

function LensFilters(props: LensFiltersProps) {
  const {
    search,
    setSearch,
    mount,
    onMountChange,
    type,
    setType,
    brand,
    setBrand,
    ois,
    setOis,
    wr,
    setWr,
    af,
    setAf,
    discontinued,
    setDiscontinued,
    fl,
    setFl,
    maxAp,
    setMaxAp,
    filterThread,
    setFilterThread,
    oqRange,
    setOqRange,
    priceRange,
    setPriceRange,
    brands,
    hasFilters,
    clearFilters,
    sortKey,
    sortDirection,
    toggleSort,
  } = props;

  return (
    <div className={styles.filters}>
      <div className={styles.filterTop}>
        <input
          className={styles.searchInput}
          type="text"
          placeholder="Search model..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Search by model name"
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
        <select
          autoComplete="off"
          className={`${styles.filterSelect} ${brand ? styles.filterActive : ""}`}
          value={brand}
          onChange={(e) => setBrand(resetValue(e.target.value))}
          aria-label="Filter by brand"
        >
          <option value="" hidden>
            Brand
          </option>
          <option value={RESET_VALUE}>All brands</option>
          {brands.includes("Fujifilm") && (
            <option value="Fujifilm">Fujifilm</option>
          )}
          {brands.includes("Fujifilm") && <option disabled>───</option>}
          {brands
            .filter((b) => b !== "Fujifilm")
            .map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
        </select>

        <select
          autoComplete="off"
          className={`${styles.filterSelect} ${fl ? styles.filterActive : ""}`}
          value={fl}
          onChange={(e) => setFl(resetValue(e.target.value))}
          aria-label="Filter by focal length"
        >
          <option value="" hidden>
            Focal Length
          </option>
          <option value={RESET_VALUE}>All</option>
          <option value="0-14">&le; 14mm</option>
          <option value="15-23">15-23mm</option>
          <option value="24-35">24-35mm</option>
          <option value="36-100">36-100mm</option>
          <option value="101-300">101-300mm</option>
          <option value="300+">300mm+</option>
        </select>

        <select
          autoComplete="off"
          className={`${styles.filterSelect} ${maxAp ? styles.filterActive : ""}`}
          value={maxAp}
          onChange={(e) => setMaxAp(resetValue(e.target.value))}
          aria-label="Filter by aperture"
        >
          <option value="" hidden>
            Aperture
          </option>
          <option value={RESET_VALUE}>All</option>
          {APERTURE_OPTIONS.map((ap) => (
            <option key={ap} value={ap}>
              f/{ap} or faster
            </option>
          ))}
        </select>

        <select
          autoComplete="off"
          className={`${styles.filterSelect} ${filterThread ? styles.filterActive : ""}`}
          value={filterThread}
          onChange={(e) => setFilterThread(resetValue(e.target.value))}
          aria-label="Filter by filter thread"
        >
          <option value="" hidden>
            {"\u03A6"} Thread
          </option>
          <option value={RESET_VALUE}>All</option>
          <option value="none">None</option>
          {FILTER_THREAD_OPTIONS.filter((t) => t !== "none").map((t) => (
            <option key={t} value={t}>
              {"\u03A6"}
              {t}mm
            </option>
          ))}
        </select>

        <select
          autoComplete="off"
          className={`${styles.filterSelect} ${oqRange ? styles.filterActive : ""}`}
          value={oqRange}
          onChange={(e) => setOqRange(resetValue(e.target.value))}
          aria-label="Filter by optical quality"
        >
          <option value="" hidden>
            Optical Quality
          </option>
          <option value={RESET_VALUE}>All</option>
          <option value="1.5+">1.5+ (Excellent)</option>
          <option value="1.0-1.4">1.0 – 1.4 (Good)</option>
          <option value="0.5-0.9">0.5 – 0.9 (Average)</option>
          <option value="0-0.4">0 – 0.4 (Below avg)</option>
          <option value="not-scored">Not scored</option>
        </select>

        <select
          autoComplete="off"
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
          <option value="1000-2000">$1,000 - $2,000</option>
          <option value="2000+">$2,000+</option>
        </select>
      </div>

      <div className={styles.chipRow}>
        <ChipGroup
          label="Mount"
          value={mount}
          onChange={onMountChange}
          styles={styles}
          options={[
            { label: "All", value: "" },
            { label: "X", value: "X" },
            { label: "GFX", value: "GFX" },
          ]}
        />
        <ChipGroup
          label="Type"
          value={type}
          onChange={setType}
          styles={styles}
          options={[
            { label: "All", value: "" },
            { label: "Prime", value: "prime" },
            { label: "Zoom", value: "zoom" },
          ]}
        />
        <ChipGroup
          label="AF"
          value={af}
          onChange={setAf}
          styles={styles}
          options={[
            { label: "All", value: "" },
            { label: "AF", value: "yes" },
            { label: "MF", value: "no" },
          ]}
        />
        <ChipGroup
          label="OIS"
          value={ois}
          onChange={setOis}
          styles={styles}
          options={[
            { label: "All", value: "" },
            { label: "Yes", value: "yes" },
            { label: "No", value: "no" },
          ]}
        />
        <ChipGroup
          label="WR"
          value={wr}
          onChange={setWr}
          styles={styles}
          options={[
            { label: "All", value: "" },
            { label: "Yes", value: "yes" },
            { label: "No", value: "no" },
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
  );
}

export { LensFilters };
