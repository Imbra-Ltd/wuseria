import { useState, useMemo, useCallback } from "react";
import type { Camera } from "../../../types/camera";
import { useSort } from "../../../hooks/useSort";
import { toSlug } from "../../../utils/slug";
import { ChipGroup } from "../shared/ChipGroup";
import { RESET_VALUE, resetValue } from "../shared/constants";
import styles from "./CameraExplorer.module.css";

interface CameraExplorerProps {
  cameras: Camera[];
}

type CameraSortKey =
  | "model"
  | "year"
  | "megapixels"
  | "sensor"
  | "hasIbis"
  | "isWeatherSealed"
  | "mechanicalBurstFps"
  | "videoSpec"
  | "batteryLife"
  | "weight"
  | "price";

type ColumnAlign = "left" | "right" | "center";

const COLUMNS: { key: CameraSortKey; label: string; align: ColumnAlign }[] = [
  { key: "model", label: "Model", align: "left" },
  { key: "year", label: "Year", align: "right" },
  { key: "megapixels", label: "MP", align: "right" },
  { key: "sensor", label: "Sensor", align: "left" },
  { key: "hasIbis", label: "IBIS", align: "center" },
  { key: "isWeatherSealed", label: "WR", align: "center" },
  { key: "mechanicalBurstFps", label: "FPS", align: "right" },
  { key: "videoSpec", label: "Video", align: "center" },
  { key: "batteryLife", label: "Battery", align: "right" },
  { key: "weight", label: "Weight", align: "right" },
  { key: "price", label: "Price", align: "right" },
];

const ALIGN_CLASSES: Record<ColumnAlign, string | undefined> = {
  left: undefined,
  right: styles.cellRight,
  center: styles.cellCenter,
};

const YEAR_RANGES: Record<string, [number, number]> = {
  "2022+": [2022, Infinity],
  "2019-2021": [2019, 2021],
  "2016-2018": [2016, 2018],
  "2012-2015": [2012, 2015],
};

const VIDEO_OPTIONS = ["8K", "6.2K", "4K", "1080p"];

const PRICE_RANGES: Record<string, [number, number]> = {
  "0-500": [0, 500],
  "500-1000": [500, 1000],
  "1000-2000": [1000, 2000],
  "2000-4000": [2000, 4000],
  "4000+": [4000, Infinity],
};

function CameraExplorer({ cameras }: CameraExplorerProps) {
  const [search, setSearch] = useState("");
  const [mount, setMount] = useState("");
  const [series, setSeries] = useState("");
  const [yearRange, setYearRange] = useState("");
  const [sensorType, setSensorType] = useState("");
  const [ibis, setIbis] = useState("");
  const [wr, setWr] = useState("");
  const [formFactor, setFormFactor] = useState("");
  const [discontinued, setDiscontinued] = useState("");
  const [videoSpec, setVideoSpec] = useState("");
  const [priceRange, setPriceRange] = useState("");

  const seriesOptions = useMemo(() => {
    const pool = mount ? cameras.filter((c) => c.mount === mount) : cameras;
    return [...new Set(pool.map((c) => c.series))].sort();
  }, [cameras, mount]);

  const sensorOptions = useMemo(() => {
    const pool = mount ? cameras.filter((c) => c.mount === mount) : cameras;
    return [...new Set(pool.map((c) => c.sensor))].sort();
  }, [cameras, mount]);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return cameras.filter((cam) => {
      if (mount && cam.mount !== mount) return false;
      if (series && cam.series !== series) return false;
      if (yearRange) {
        const [min, max] = YEAR_RANGES[yearRange];
        if (cam.year < min || cam.year > max) return false;
      }
      if (sensorType && cam.sensor !== sensorType) return false;
      if (formFactor && cam.formFactor !== formFactor) return false;
      if (ibis === "yes" && !cam.hasIbis) return false;
      if (ibis === "no" && cam.hasIbis) return false;
      if (wr === "yes" && !cam.isWeatherSealed) return false;
      if (wr === "no" && cam.isWeatherSealed) return false;
      if (discontinued === "available" && cam.isDiscontinued) return false;
      if (discontinued === "discontinued" && !cam.isDiscontinued) return false;
      if (videoSpec && cam.videoSpec !== videoSpec) return false;
      if (priceRange) {
        const [min, max] = PRICE_RANGES[priceRange];
        if (cam.price < min || cam.price > max) return false;
      }
      if (q && !cam.model.toLowerCase().includes(q)) return false;
      return true;
    });
  }, [cameras, search, mount, series, yearRange, sensorType, formFactor, discontinued, ibis, wr, videoSpec, priceRange]);

  const availableFirst = useCallback((a: Camera, b: Camera) =>
    Number(a.isDiscontinued ?? false) - Number(b.isDiscontinued ?? false), []);
  const { sorted, sortKey, sortDirection, toggleSort } = useSort<Camera, CameraSortKey>(filtered, "year", "asc", availableFirst);

  function handleMountChange(value: string): void {
    setMount(value);
    if (series) {
      const seriesExistsInMount = cameras.some(
        (c) => c.series === series && (!value || c.mount === value),
      );
      if (!seriesExistsInMount) setSeries("");
    }
  }

  const hasFilters = search || mount || series || yearRange || sensorType || formFactor || discontinued || ibis || wr || videoSpec || priceRange;

  function clearFilters(): void {
    setSearch("");
    setMount("");
    setSeries("");
    setYearRange("");
    setSensorType("");
    setFormFactor("");
    setDiscontinued("");
    setIbis("");
    setWr("");
    setVideoSpec("");
    setPriceRange("");
  }

  return (
    <div>
      <div className={styles.hero}>
        <h1 className={styles.heroTitle}>Camera Explorer</h1>
        <p className={styles.heroSub}>{sorted.length} / {cameras.length} Fujifilm cameras</p>
      </div>
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
          <select autoComplete="off" className={`${styles.filterSelect} ${formFactor ? styles.filterActive : ""}`} value={formFactor} onChange={(e) => setFormFactor(resetValue(e.target.value))} aria-label="Filter by body style">
            <option value="" hidden>Body</option>
            <option value={RESET_VALUE}>All</option>
            <option value="standard">Standard</option>
            <option value="pro-grip">Pro grip</option>
            <option value="rangefinder">Rangefinder</option>
            <option value="compact">Compact</option>
          </select>

          <select autoComplete="off" className={`${styles.filterSelect} ${series ? styles.filterActive : ""}`} value={series} onChange={(e) => setSeries(resetValue(e.target.value))} aria-label="Filter by series">
            <option value="" hidden>Series</option>
            <option value={RESET_VALUE}>All series</option>
            {seriesOptions.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>

          <select autoComplete="off" className={`${styles.filterSelect} ${yearRange ? styles.filterActive : ""}`} value={yearRange} onChange={(e) => setYearRange(resetValue(e.target.value))} aria-label="Filter by year">
            <option value="" hidden>Year</option>
            <option value={RESET_VALUE}>All</option>
            {Object.keys(YEAR_RANGES).map((key) => (
              <option key={key} value={key}>{key}</option>
            ))}
          </select>

          <select autoComplete="off" className={`${styles.filterSelect} ${sensorType ? styles.filterActive : ""}`} value={sensorType} onChange={(e) => setSensorType(resetValue(e.target.value))} aria-label="Filter by sensor">
            <option value="" hidden>Sensor</option>
            <option value={RESET_VALUE}>All</option>
            {sensorOptions.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>

          <select autoComplete="off" className={`${styles.filterSelect} ${videoSpec ? styles.filterActive : ""}`} value={videoSpec} onChange={(e) => setVideoSpec(resetValue(e.target.value))} aria-label="Filter by video">
            <option value="" hidden>Video</option>
            <option value={RESET_VALUE}>All</option>
            {VIDEO_OPTIONS.map((v) => (
              <option key={v} value={v}>{v}+</option>
            ))}
          </select>

          <select autoComplete="off" className={`${styles.filterSelect} ${priceRange ? styles.filterActive : ""}`} value={priceRange} onChange={(e) => setPriceRange(resetValue(e.target.value))} aria-label="Filter by price">
            <option value="" hidden>Price</option>
            <option value={RESET_VALUE}>All</option>
            <option value="0-500">Under $500</option>
            <option value="500-1000">$500 - $1,000</option>
            <option value="1000-2000">$1,000 - $2,000</option>
            <option value="2000-4000">$2,000 - $4,000</option>
            <option value="4000+">$4,000+</option>
          </select>
        </div>

        <div className={styles.chipRow}>
          <ChipGroup label="Mount" value={mount} onChange={handleMountChange} styles={styles} options={[
            { label: "All", value: "" }, { label: "X", value: "X" }, { label: "GFX", value: "GFX" },
          ]} />
          <ChipGroup label="IBIS" value={ibis} onChange={setIbis} styles={styles} options={[
            { label: "All", value: "" }, { label: "Yes", value: "yes" }, { label: "No", value: "no" },
          ]} />
          <ChipGroup label="WR" value={wr} onChange={setWr} styles={styles} options={[
            { label: "All", value: "" }, { label: "Yes", value: "yes" }, { label: "No", value: "no" },
          ]} />
          <ChipGroup label="Status" value={discontinued} onChange={setDiscontinued} styles={styles} options={[
            { label: "All", value: "" }, { label: "Available", value: "available" }, { label: "Discontinued", value: "discontinued" },
          ]} />
        </div>
      </div>

      {sorted.length === 0 ? (
        <p className={styles.emptyState}>No cameras match the current filters.</p>
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
                      onClick={() => toggleSort(col.key)}
                      aria-sort={
                        sortKey === col.key
                          ? sortDirection === "asc" ? "ascending" : "descending"
                          : "none"
                      }
                    >
                      {col.label}
                      <span className={styles.sortIndicator}>
                        {sortKey === col.key
                          ? (sortDirection === "asc" ? "\u2191" : "\u2193")
                          : "\u2195"}
                      </span>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {sorted.map((cam) => (
                  <tr key={`${cam.series}-${cam.model}`} className={cam.isDiscontinued ? styles.rowDiscontinued : undefined}>
                    <td>
                      <a className={styles.lensLink} href={`/cameras/${toSlug(cam.model)}`}>{cam.model}</a>
                    </td>
                    <td className={styles.cellRight}>{cam.year}</td>
                    <td className={styles.cellRight}>{cam.megapixels}</td>
                    <td>{cam.sensor}</td>
                    <td className={styles.cellCenter}><span className={cam.hasIbis ? styles.dotOn : styles.dotOff} /></td>
                    <td className={styles.cellCenter}><span className={cam.isWeatherSealed ? styles.dotOn : styles.dotOff} /></td>
                    <td className={styles.cellRight}>{cam.mechanicalBurstFps ?? "\u2013"}</td>
                    <td className={styles.cellCenter}>{cam.videoSpec}</td>
                    <td className={styles.cellRight}>{cam.batteryLife ?? "\u2013"}</td>
                    <td className={styles.cellRight}>{cam.weight}g</td>
                    <td className={styles.cellRight}>~${cam.price}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Cards — mobile */}
          <div className={styles.cards}>
            {sorted.map((cam) => (
              <div key={`${cam.series}-${cam.model}`} className={`${styles.card} ${cam.isDiscontinued ? styles.cardDiscontinued : ""}`}>
                <div className={styles.cardHeader}>
                  <a className={styles.lensLink} href={`/cameras/${toSlug(cam.model)}`}>{cam.model}</a>
                  <span className={styles.cardPrice}>~${cam.price}</span>
                </div>
                <div className={styles.cardSpecs}>
                  <span>{cam.year}</span>
                  <span>{cam.megapixels}MP</span>
                  <span>{cam.sensor}</span>
                  <span>{cam.videoSpec}</span>
                  {cam.mechanicalBurstFps && <span>{cam.mechanicalBurstFps}fps</span>}
                  {cam.batteryLife && <span>{cam.batteryLife} shots</span>}
                  <span>{cam.weight}g</span>
                </div>
                <div className={styles.cardBadges}>
                  {cam.hasIbis && <span className={styles.badge}>IBIS</span>}
                  {cam.isWeatherSealed && <span className={styles.badge}>WR</span>}
                  {cam.isDiscontinued && <span className={styles.badge}>Discontinued</span>}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      <p className={styles.footnote}>
        All prices are approximate USD estimates.
        See <a href="/trade-deals">Trade Deals</a> for current market rates.
      </p>
    </div>
  );
}

export default CameraExplorer;
