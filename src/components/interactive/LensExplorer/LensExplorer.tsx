import { useState, useMemo } from "react";
import type { Lens } from "../../../types/lens";
import { useSort } from "../../../hooks/useSort";
import { toSlug } from "../../../utils/slug";
import styles from "./LensExplorer.module.css";

interface LensExplorerProps {
  lenses: Lens[];
}

type LensSortKey =
  | "brand"
  | "model"
  | "focalLengthMin"
  | "maxAperture"
  | "hasOis"
  | "isWeatherSealed"
  | "afMotor"
  | "weight"
  | "price";

type ColumnAlign = "left" | "right" | "center";

const COLUMNS: { key: LensSortKey; label: string; align: ColumnAlign }[] = [
  { key: "brand", label: "Brand", align: "left" },
  { key: "model", label: "Model", align: "left" },
  { key: "focalLengthMin", label: "FL", align: "right" },
  { key: "maxAperture", label: "f/", align: "right" },
  { key: "hasOis", label: "OIS", align: "center" },
  { key: "isWeatherSealed", label: "WR", align: "center" },
  { key: "afMotor", label: "AF", align: "center" },
  { key: "weight", label: "Weight", align: "right" },
  { key: "price", label: "~USD", align: "right" },
];

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
      if (af === "yes" && !lens.hasAutofocus) return false;
      if (af === "no" && lens.hasAutofocus) return false;
      if (discontinued === "available" && lens.isDiscontinued) return false;
      if (discontinued === "discontinued" && !lens.isDiscontinued) return false;
      if (fl) {
        const ranges: Record<string, [number, number]> = {
          "0-14": [0, 14],
          "15-23": [15, 23],
          "24-35": [24, 35],
          "36-100": [36, 100],
          "101-300": [101, 300],
          "300+": [300, Infinity],
        };
        const [min, max] = ranges[fl];
        if (lens.focalLengthMax < min || lens.focalLengthMin > max) return false;
      }
      if (q && !`${lens.brand} ${lens.model}`.toLowerCase().includes(q)) return false;
      return true;
    });
  }, [lenses, search, mount, type, brand, ois, wr, af, discontinued, fl]);

  const { sorted, sortKey, sortDirection, toggleSort } = useSort<Lens, LensSortKey>(filtered, "focalLengthMin");

  function resetValue(value: string): string {
    return value === "__all__" ? "" : value;
  }

  function handleMountChange(value: string): void {
    setMount(value);
    if (brand) {
      const brandExistsInMount = lenses.some(
        (l) => l.brand === brand && (!value || l.mount === value),
      );
      if (!brandExistsInMount) setBrand("");
    }
  }

  const hasFilters = search || mount || type || brand || ois || wr || af || discontinued || fl;

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
            <option value="__all__">All brands</option>
            {brands.includes("Fujifilm") && <option value="Fujifilm">Fujifilm</option>}
            {brands.includes("Fujifilm") && <option disabled>───</option>}
            {brands.filter((b) => b !== "Fujifilm").map((b) => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>

          <select className={`${styles.filterSelect} ${fl ? styles.filterActive : ""}`} value={fl} onChange={(e) => setFl(resetValue(e.target.value))} aria-label="Filter by focal length">
            <option value="" hidden>Focal Length</option>
            <option value="__all__">All</option>
            <option value="0-14">&le; 14mm</option>
            <option value="15-23">15-23mm</option>
            <option value="24-35">24-35mm</option>
            <option value="36-100">36-100mm</option>
            <option value="101-300">101-300mm</option>
            <option value="300+">300mm+</option>
          </select>

          <select className={`${styles.filterSelect} ${discontinued ? styles.filterActive : ""}`} value={discontinued} onChange={(e) => setDiscontinued(resetValue(e.target.value))} aria-label="Filter by status">
            <option value="" hidden>Status</option>
            <option value="__all__">All</option>
            <option value="available">Available</option>
            <option value="discontinued">Discontinued</option>
          </select>
        </div>

        <div className={styles.chipRow}>
          <div className={styles.chipGroup}>
            <span className={styles.chipLabel}>Mount</span>
            <button type="button" className={`${styles.chip} ${mount === "" ? styles.chipOn : ""}`} onClick={() => handleMountChange("")}>All</button>
            <button type="button" className={`${styles.chip} ${mount === "X" ? styles.chipOn : ""}`} onClick={() => handleMountChange("X")}>X</button>
            <button type="button" className={`${styles.chip} ${mount === "GFX" ? styles.chipOn : ""}`} onClick={() => handleMountChange("GFX")}>GFX</button>
          </div>

          <div className={styles.chipGroup}>
            <span className={styles.chipLabel}>Type</span>
            <button type="button" className={`${styles.chip} ${type === "" ? styles.chipOn : ""}`} onClick={() => setType("")}>All</button>
            <button type="button" className={`${styles.chip} ${type === "prime" ? styles.chipOn : ""}`} onClick={() => setType("prime")}>Prime</button>
            <button type="button" className={`${styles.chip} ${type === "zoom" ? styles.chipOn : ""}`} onClick={() => setType("zoom")}>Zoom</button>
          </div>

          <div className={styles.chipGroup}>
            <span className={styles.chipLabel}>AF</span>
            <button type="button" className={`${styles.chip} ${af === "" ? styles.chipOn : ""}`} onClick={() => setAf("")}>All</button>
            <button type="button" className={`${styles.chip} ${af === "yes" ? styles.chipOn : ""}`} onClick={() => setAf("yes")}>AF</button>
            <button type="button" className={`${styles.chip} ${af === "no" ? styles.chipOn : ""}`} onClick={() => setAf("no")}>MF</button>
          </div>

          <div className={styles.chipGroup}>
            <span className={styles.chipLabel}>OIS</span>
            <button type="button" className={`${styles.chip} ${ois === "" ? styles.chipOn : ""}`} onClick={() => setOis("")}>All</button>
            <button type="button" className={`${styles.chip} ${ois === "yes" ? styles.chipOn : ""}`} onClick={() => setOis("yes")}>Yes</button>
            <button type="button" className={`${styles.chip} ${ois === "no" ? styles.chipOn : ""}`} onClick={() => setOis("no")}>No</button>
          </div>

          <div className={styles.chipGroup}>
            <span className={styles.chipLabel}>WR</span>
            <button type="button" className={`${styles.chip} ${wr === "" ? styles.chipOn : ""}`} onClick={() => setWr("")}>All</button>
            <button type="button" className={`${styles.chip} ${wr === "yes" ? styles.chipOn : ""}`} onClick={() => setWr("yes")}>Yes</button>
            <button type="button" className={`${styles.chip} ${wr === "no" ? styles.chipOn : ""}`} onClick={() => setWr("no")}>No</button>
          </div>
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
                      className={col.align === "right" ? styles.cellRight : col.align === "center" ? styles.cellCenter : undefined}
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
                      <span className={styles.typeBadge}>{lens.type === "prime" ? "P" : "Z"}</span>
                      <a className={styles.lensLink} href={`/lenses/${toSlug(`${lens.brand} ${lens.model}`)}`}>
                        {lens.model}
                      </a>
                    </td>
                    <td className={styles.cellRight}>{formatFL(lens)}</td>
                    <td className={styles.cellRight}>{lens.maxAperture}</td>
                    <td className={styles.cellCenter}><span className={lens.hasOis ? styles.dotOn : styles.dotOff} /></td>
                    <td className={styles.cellCenter}><span className={lens.isWeatherSealed ? styles.dotOn : styles.dotOff} /></td>
                    <td className={styles.cellCenter}>{lens.afMotor ?? "MF"}</td>
                    <td className={styles.cellRight}>{lens.weight}g</td>
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
                  <a className={styles.lensLink} href={`/lenses/${toSlug(`${lens.brand} ${lens.model}`)}`}>
                    {lens.brand} {lens.model}
                  </a>
                  <span className={styles.cardPrice}>~${lens.price}</span>
                </div>
                <div className={styles.cardSpecs}>
                  <span>{formatFL(lens)}</span>
                  <span>f/{lens.maxAperture}</span>
                  <span>{lens.weight}g</span>
                  <span>{lens.type === "prime" ? "Prime" : "Zoom"}</span>
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
