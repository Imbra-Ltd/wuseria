import { useState, useMemo, useCallback } from "react";
import type { Lens } from "../../../types/lens";
import { useSort } from "../../../hooks/useSort";
import { toSlug } from "../../../utils/slug";
import { ChipGroup } from "../shared/ChipGroup";
import { RESET_VALUE, resetValue } from "../shared/constants";
import styles from "./LensExplorer.module.css";

interface ExplorerLens extends Lens {
  opticalQuality?: number | null;
}

interface LensExplorerProps {
  lenses: ExplorerLens[];
}

type LensSortKey =
  | "brand"
  | "model"
  | "year"
  | "focalLengthMin"
  | "maxAperture"
  | "hasOis"
  | "isWeatherSealed"
  | "afMotor"
  | "weight"
  | "opticalQuality"
  | "price";

type ColumnAlign = "left" | "right" | "center";

const COLUMNS: { key: LensSortKey; label: string; align: ColumnAlign }[] = [
  { key: "brand", label: "Brand", align: "left" },
  { key: "model", label: "Model", align: "left" },
  { key: "year", label: "Year", align: "left" },
  { key: "focalLengthMin", label: "FL", align: "right" },
  { key: "maxAperture", label: "f/", align: "right" },
  { key: "hasOis", label: "OIS", align: "center" },
  { key: "isWeatherSealed", label: "WR", align: "center" },
  { key: "afMotor", label: "AF", align: "center" },
  { key: "weight", label: "Weight", align: "right" },
  { key: "opticalQuality", label: "OQ", align: "right" },
  { key: "price", label: "Price", align: "right" },
];

const APERTURE_OPTIONS = ["0.95", "1.0", "1.2", "1.4", "1.8", "2.0", "2.8", "3.5", "4.0", "4.5", "5.6", "6.3", "8.0"];

const FL_RANGES: Record<string, [number, number]> = {
  "0-14": [0, 14],
  "15-23": [15, 23],
  "24-35": [24, 35],
  "36-100": [36, 100],
  "101-300": [101, 300],
  "300+": [300, Infinity],
};

const PRICE_RANGES: Record<string, [number, number]> = {
  "0-250": [0, 250],
  "250-500": [250, 500],
  "500-1000": [500, 1000],
  "1000-2000": [1000, 2000],
  "2000+": [2000, Infinity],
};

const ALIGN_CLASSES: Record<ColumnAlign, string | undefined> = {
  left: undefined,
  right: styles.cellRight,
  center: styles.cellCenter,
};

function formatFL(lens: Lens): string {
  if (lens.focalLengthMin === lens.focalLengthMax) {
    return `${lens.focalLengthMin}mm`;
  }
  return `${lens.focalLengthMin}-${lens.focalLengthMax}mm`;
}

function LensExplorer({ lenses }: LensExplorerProps) {
  const [search, setSearch] = useState("");
  const [mount, setMount] = useState("");
  const [type, setType] = useState("");
  const [brand, setBrand] = useState("");
  const [ois, setOis] = useState("");
  const [wr, setWr] = useState("");
  const [af, setAf] = useState("");
  const [discontinued, setDiscontinued] = useState("");
  const [fl, setFl] = useState("");
  const [maxAp, setMaxAp] = useState("");
  const [priceRange, setPriceRange] = useState("");

  const slugMap = useMemo(
    () => new Map(lenses.map((l) => [`${l.brand}-${l.model}`, toSlug(`${l.brand} ${l.model}`)])),
    [lenses],
  );

  const brands = useMemo(() => {
    const pool = mount ? lenses.filter((l) => l.mount === mount) : lenses;
    return [...new Set(pool.map((l) => l.brand))].sort();
  }, [lenses, mount]);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return lenses.filter((lens) => {
      if (mount && lens.mount !== mount) return false;
      if (type && lens.type !== type) return false;
      if (brand && lens.brand !== brand) return false;
      if (ois === "yes" && !lens.hasOis) return false;
      if (ois === "no" && lens.hasOis) return false;
      if (wr === "yes" && !lens.isWeatherSealed) return false;
      if (wr === "no" && lens.isWeatherSealed) return false;
      if (af === "yes" && !lens.afMotor) return false;
      if (af === "no" && lens.afMotor) return false;
      if (discontinued === "available" && lens.isDiscontinued) return false;
      if (discontinued === "discontinued" && !lens.isDiscontinued) return false;
      if (fl) {
        const [min, max] = FL_RANGES[fl];
        if (lens.focalLengthMax < min || lens.focalLengthMin > max) return false;
      }
      if (maxAp && lens.maxAperture > parseFloat(maxAp)) return false;
      if (priceRange) {
        const [min, max] = PRICE_RANGES[priceRange];
        if (lens.price < min || lens.price > max) return false;
      }
      if (q && !`${lens.brand} ${lens.model}`.toLowerCase().includes(q)) return false;
      return true;
    });
  }, [lenses, search, mount, type, brand, ois, wr, af, discontinued, fl, maxAp, priceRange]);

  const availableFirst = useCallback((a: ExplorerLens, b: ExplorerLens) =>
    Number(a.isDiscontinued ?? false) - Number(b.isDiscontinued ?? false), []);
  const { sorted, sortKey, sortDirection, toggleSort } = useSort<ExplorerLens, LensSortKey>(filtered, "focalLengthMin", "asc", availableFirst);

  function handleMountChange(value: string): void {
    setMount(value);
    if (brand) {
      const brandExistsInMount = lenses.some(
        (l) => l.brand === brand && (!value || l.mount === value),
      );
      if (!brandExistsInMount) setBrand("");
    }
  }

  const hasFilters = search || mount || type || brand || ois || wr || af || discontinued || fl || maxAp || priceRange;

  function clearFilters(): void {
    setSearch("");
    setMount("");
    setType("");
    setBrand("");
    setOis("");
    setWr("");
    setAf("");
    setDiscontinued("");
    setFl("");
    setMaxAp("");
    setPriceRange("");
  }

  return (
    <div>
      <div className={styles.hero}>
        <h1 className={styles.heroTitle}>Lens Explorer</h1>
        <p className={styles.heroSub}>{sorted.length} / {lenses.length} Fujifilm-compatible lenses</p>
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
          <select className={`${styles.filterSelect} ${brand ? styles.filterActive : ""}`} value={brand} onChange={(e) => setBrand(resetValue(e.target.value))} aria-label="Filter by brand">
            <option value="" hidden>Brand</option>
            <option value={RESET_VALUE}>All brands</option>
            {brands.includes("Fujifilm") && <option value="Fujifilm">Fujifilm</option>}
            {brands.includes("Fujifilm") && <option disabled>───</option>}
            {brands.filter((b) => b !== "Fujifilm").map((b) => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>

          <select className={`${styles.filterSelect} ${fl ? styles.filterActive : ""}`} value={fl} onChange={(e) => setFl(resetValue(e.target.value))} aria-label="Filter by focal length">
            <option value="" hidden>Focal Length</option>
            <option value={RESET_VALUE}>All</option>
            <option value="0-14">&le; 14mm</option>
            <option value="15-23">15-23mm</option>
            <option value="24-35">24-35mm</option>
            <option value="36-100">36-100mm</option>
            <option value="101-300">101-300mm</option>
            <option value="300+">300mm+</option>
          </select>

          <select className={`${styles.filterSelect} ${maxAp ? styles.filterActive : ""}`} value={maxAp} onChange={(e) => setMaxAp(resetValue(e.target.value))} aria-label="Filter by aperture">
            <option value="" hidden>Aperture</option>
            <option value={RESET_VALUE}>All</option>
            {APERTURE_OPTIONS.map((ap) => (
              <option key={ap} value={ap}>f/{ap} or faster</option>
            ))}
          </select>

          <select className={`${styles.filterSelect} ${priceRange ? styles.filterActive : ""}`} value={priceRange} onChange={(e) => setPriceRange(resetValue(e.target.value))} aria-label="Filter by price">
            <option value="" hidden>Price</option>
            <option value={RESET_VALUE}>All</option>
            <option value="0-250">Under $250</option>
            <option value="250-500">$250 - $500</option>
            <option value="500-1000">$500 - $1,000</option>
            <option value="1000-2000">$1,000 - $2,000</option>
            <option value="2000+">$2,000+</option>
          </select>

        </div>

        <div className={styles.chipRow}>
          <ChipGroup label="Mount" value={mount} onChange={handleMountChange} styles={styles} options={[
            { label: "All", value: "" }, { label: "X", value: "X" }, { label: "GFX", value: "GFX" },
          ]} />
          <ChipGroup label="Type" value={type} onChange={setType} styles={styles} options={[
            { label: "All", value: "" }, { label: "Prime", value: "prime" }, { label: "Zoom", value: "zoom" },
          ]} />
          <ChipGroup label="AF" value={af} onChange={setAf} styles={styles} options={[
            { label: "All", value: "" }, { label: "AF", value: "yes" }, { label: "MF", value: "no" },
          ]} />
          <ChipGroup label="OIS" value={ois} onChange={setOis} styles={styles} options={[
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
        <p className={styles.emptyState}>No lenses match the current filters.</p>
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
                {sorted.map((lens) => (
                  <tr key={`${lens.brand}-${lens.model}`} className={lens.isDiscontinued ? styles.rowDiscontinued : undefined}>
                    <td>{lens.brand}</td>
                    <td>
                      <a className={styles.lensLink} href={`/lenses/${slugMap.get(`${lens.brand}-${lens.model}`)}`}>
                        {lens.model}
                      </a>
                    </td>
                    <td>{lens.year ?? ""}</td>
                    <td className={styles.cellRight}>{formatFL(lens)}</td>
                    <td className={styles.cellRight}>{lens.maxAperture}</td>
                    <td className={styles.cellCenter}><span className={lens.hasOis ? styles.dotOn : styles.dotOff} /></td>
                    <td className={styles.cellCenter}><span className={lens.isWeatherSealed ? styles.dotOn : styles.dotOff} /></td>
                    <td className={styles.cellCenter}>{lens.afMotor ?? "MF"}</td>
                    <td className={styles.cellRight}>{lens.weight}g</td>
                    <td className={styles.cellRight}>{lens.opticalQuality != null ? lens.opticalQuality.toFixed(1) : "\u2013"}</td>
                    <td className={styles.cellRight}>~${lens.price}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Cards — mobile */}
          <div className={styles.cards}>
            {sorted.map((lens) => (
              <div key={`${lens.brand}-${lens.model}`} className={`${styles.card} ${lens.isDiscontinued ? styles.cardDiscontinued : ""}`}>
                <div className={styles.cardHeader}>
                  <a className={styles.lensLink} href={`/lenses/${slugMap.get(`${lens.brand}-${lens.model}`)}`}>
                    {lens.brand} {lens.model}
                  </a>
                  <span className={styles.cardPrice}>~${lens.price}</span>
                </div>
                <div className={styles.cardSpecs}>
                  <span>f/{lens.maxAperture}</span>
                  <span>{lens.weight}g</span>
                  {lens.filterThread != null && <span>{"\u03A6"}{lens.filterThread}</span>}
                  {lens.opticalQuality != null && <span>OQ {lens.opticalQuality.toFixed(1)}</span>}
                  {lens.year && <span>{lens.year}</span>}
                </div>
                <div className={styles.cardBadges}>
                  {lens.hasOis && <span className={styles.badge}>OIS</span>}
                  {lens.isWeatherSealed && <span className={styles.badge}>WR</span>}
                  {lens.afMotor && <span className={styles.badge}>{lens.afMotor}</span>}
                  {!lens.afMotor && <span className={styles.badge}>MF</span>}
                  {lens.isDiscontinued && <span className={styles.badge}>Discontinued</span>}
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

export default LensExplorer;
