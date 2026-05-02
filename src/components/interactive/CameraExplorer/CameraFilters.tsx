import { ChipGroup } from "../shared/ChipGroup";
import { MobileSort } from "../shared/MobileSort";
import { RESET_VALUE, resetValue } from "../shared/constants";
import type { CameraSortKey } from "./constants";
import { COLUMNS, YEAR_RANGES, VIDEO_OPTIONS } from "./constants";
import styles from "./CameraExplorer.module.css";

interface CameraFiltersProps {
  search: string;
  setSearch: (v: string) => void;
  mount: string;
  onMountChange: (v: string) => void;
  series: string;
  setSeries: (v: string) => void;
  yearRange: string;
  setYearRange: (v: string) => void;
  sensorType: string;
  setSensorType: (v: string) => void;
  ibis: string;
  setIbis: (v: string) => void;
  wr: string;
  setWr: (v: string) => void;
  formFactor: string;
  setFormFactor: (v: string) => void;
  discontinued: string;
  setDiscontinued: (v: string) => void;
  videoSpec: string;
  setVideoSpec: (v: string) => void;
  priceRange: string;
  setPriceRange: (v: string) => void;
  seriesOptions: string[];
  sensorOptions: string[];
  hasFilters: boolean;
  clearFilters: () => void;
  sortKey: CameraSortKey;
  sortDirection: "asc" | "desc";
  toggleSort: (key: CameraSortKey) => void;
}

function CameraFilters(props: CameraFiltersProps) {
  const {
    search,
    setSearch,
    mount,
    onMountChange,
    series,
    setSeries,
    yearRange,
    setYearRange,
    sensorType,
    setSensorType,
    ibis,
    setIbis,
    wr,
    setWr,
    formFactor,
    setFormFactor,
    discontinued,
    setDiscontinued,
    videoSpec,
    setVideoSpec,
    priceRange,
    setPriceRange,
    seriesOptions,
    sensorOptions,
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
          className={`${styles.filterSelect} ${formFactor ? styles.filterActive : ""}`}
          value={formFactor}
          onChange={(e) => setFormFactor(resetValue(e.target.value))}
          aria-label="Filter by body style"
        >
          <option value="" hidden>
            Body
          </option>
          <option value={RESET_VALUE}>All</option>
          <option value="standard">Standard</option>
          <option value="pro-grip">Pro grip</option>
          <option value="rangefinder">Rangefinder</option>
          <option value="compact">Compact</option>
        </select>

        <select
          autoComplete="off"
          className={`${styles.filterSelect} ${series ? styles.filterActive : ""}`}
          value={series}
          onChange={(e) => setSeries(resetValue(e.target.value))}
          aria-label="Filter by series"
        >
          <option value="" hidden>
            Series
          </option>
          <option value={RESET_VALUE}>All series</option>
          {seriesOptions.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>

        <select
          autoComplete="off"
          className={`${styles.filterSelect} ${yearRange ? styles.filterActive : ""}`}
          value={yearRange}
          onChange={(e) => setYearRange(resetValue(e.target.value))}
          aria-label="Filter by year"
        >
          <option value="" hidden>
            Year
          </option>
          <option value={RESET_VALUE}>All</option>
          {Object.keys(YEAR_RANGES).map((key) => (
            <option key={key} value={key}>
              {key}
            </option>
          ))}
        </select>

        <select
          autoComplete="off"
          className={`${styles.filterSelect} ${sensorType ? styles.filterActive : ""}`}
          value={sensorType}
          onChange={(e) => setSensorType(resetValue(e.target.value))}
          aria-label="Filter by sensor"
        >
          <option value="" hidden>
            Sensor
          </option>
          <option value={RESET_VALUE}>All</option>
          {sensorOptions.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>

        <select
          autoComplete="off"
          className={`${styles.filterSelect} ${videoSpec ? styles.filterActive : ""}`}
          value={videoSpec}
          onChange={(e) => setVideoSpec(resetValue(e.target.value))}
          aria-label="Filter by video"
        >
          <option value="" hidden>
            Video
          </option>
          <option value={RESET_VALUE}>All</option>
          {VIDEO_OPTIONS.map((v) => (
            <option key={v} value={v}>
              {v}+
            </option>
          ))}
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
          <option value="0-500">Under $500</option>
          <option value="500-1000">$500 - $1,000</option>
          <option value="1000-2000">$1,000 - $2,000</option>
          <option value="2000-4000">$2,000 - $4,000</option>
          <option value="4000+">$4,000+</option>
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
          label="IBIS"
          value={ibis}
          onChange={setIbis}
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

export { CameraFilters };
