import { useState, useMemo, useCallback } from "react";
import { useSort } from "../../../hooks/useSort";
import { toSlug } from "../../../utils/slug";
import type { ExplorerLens, LensExplorerProps, LensSortKey } from "./constants";
import { FL_RANGES, OQ_RANGES, PRICE_RANGES } from "./constants";
import { LensFilters } from "./LensFilters";
import { LensResults } from "./LensResults";
import styles from "./LensExplorer.module.css";

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
  const [filterThread, setFilterThread] = useState("");
  const [oqRange, setOqRange] = useState("");
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
      if (filterThread === "none" && lens.filterThread != null) return false;
      if (filterThread && filterThread !== "none" && lens.filterThread !== Number(filterThread)) return false;
      if (oqRange === "not-scored") {
        if (lens.opticalQuality != null) return false;
      } else if (oqRange) {
        const [min, max] = OQ_RANGES[oqRange];
        if (lens.opticalQuality == null || lens.opticalQuality < min || lens.opticalQuality > max) return false;
      }
      if (priceRange) {
        const [min, max] = PRICE_RANGES[priceRange];
        if (lens.price < min || lens.price > max) return false;
      }
      if (q && !`${lens.brand} ${lens.model}`.toLowerCase().includes(q)) return false;
      return true;
    });
  }, [lenses, search, mount, type, brand, ois, wr, af, discontinued, fl, maxAp, filterThread, oqRange, priceRange]);

  const availableFirst = useCallback((a: ExplorerLens, b: ExplorerLens) =>
    Number(a.isDiscontinued ?? false) - Number(b.isDiscontinued ?? false), []);
  const { sorted, sortKey, sortDirection, toggleSort } = useSort<ExplorerLens, LensSortKey>(filtered, "focalLengthMin", "asc", availableFirst);

  function handleMountChange(value: string): void {
    setMount(value);
    if (brand) {
      const brandExistsInMount = lenses.some((l) => l.brand === brand && (!value || l.mount === value));
      if (!brandExistsInMount) setBrand("");
    }
  }

  const hasFilters = !!(search || mount || type || brand || ois || wr || af || discontinued || fl || maxAp || filterThread || oqRange || priceRange);

  function clearFilters(): void {
    setSearch(""); setMount(""); setType(""); setBrand(""); setOis(""); setWr("");
    setAf(""); setDiscontinued(""); setFl(""); setMaxAp(""); setFilterThread("");
    setOqRange(""); setPriceRange("");
  }

  return (
    <div>
      <div className={styles.hero}>
        <h1 className={styles.heroTitle}>Lens Explorer</h1>
        <p className={styles.heroSub}>{sorted.length} / {lenses.length} Fujifilm-compatible lenses</p>
      </div>

      <LensFilters
        search={search} setSearch={setSearch} mount={mount} onMountChange={handleMountChange}
        type={type} setType={setType} brand={brand} setBrand={setBrand}
        ois={ois} setOis={setOis} wr={wr} setWr={setWr} af={af} setAf={setAf}
        discontinued={discontinued} setDiscontinued={setDiscontinued}
        fl={fl} setFl={setFl} maxAp={maxAp} setMaxAp={setMaxAp}
        filterThread={filterThread} setFilterThread={setFilterThread}
        oqRange={oqRange} setOqRange={setOqRange} priceRange={priceRange} setPriceRange={setPriceRange}
        brands={brands} hasFilters={hasFilters} clearFilters={clearFilters}
      />

      {sorted.length === 0 ? (
        <p className={styles.emptyState}>No lenses match the current filters.</p>
      ) : (
        <LensResults sorted={sorted} slugMap={slugMap} sortKey={sortKey} sortDirection={sortDirection} toggleSort={toggleSort} />
      )}

      <p className={styles.footnote}>
        All prices are approximate USD estimates.
      </p>
    </div>
  );
}

export default LensExplorer;
