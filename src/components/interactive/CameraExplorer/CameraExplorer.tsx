import { useState, useMemo, useCallback } from "react";
import type { Camera } from "../../../types/camera";
import { useSort } from "../../../hooks/useSort";
import type { CameraSortKey } from "./constants";
import { YEAR_RANGES, PRICE_RANGES } from "./constants";
import { CameraFilters } from "./CameraFilters";
import { CameraResults } from "./CameraResults";
import styles from "./CameraExplorer.module.css";

interface CameraExplorerProps {
  cameras: Camera[];
}

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
      const seriesExistsInMount = cameras.some((c) => c.series === series && (!value || c.mount === value));
      if (!seriesExistsInMount) setSeries("");
    }
  }

  const hasFilters = !!(search || mount || series || yearRange || sensorType || formFactor || discontinued || ibis || wr || videoSpec || priceRange);

  function clearFilters(): void {
    setSearch(""); setMount(""); setSeries(""); setYearRange(""); setSensorType("");
    setFormFactor(""); setDiscontinued(""); setIbis(""); setWr(""); setVideoSpec(""); setPriceRange("");
  }

  return (
    <div>
      <div className={styles.hero}>
        <h1 className={styles.heroTitle}>Camera Explorer</h1>
        <p className={styles.heroSub}>{sorted.length} / {cameras.length} Fujifilm cameras</p>
      </div>

      <CameraFilters
        search={search} setSearch={setSearch} mount={mount} onMountChange={handleMountChange}
        series={series} setSeries={setSeries} yearRange={yearRange} setYearRange={setYearRange}
        sensorType={sensorType} setSensorType={setSensorType} ibis={ibis} setIbis={setIbis}
        wr={wr} setWr={setWr} formFactor={formFactor} setFormFactor={setFormFactor}
        discontinued={discontinued} setDiscontinued={setDiscontinued}
        videoSpec={videoSpec} setVideoSpec={setVideoSpec} priceRange={priceRange} setPriceRange={setPriceRange}
        seriesOptions={seriesOptions} sensorOptions={sensorOptions}
        hasFilters={hasFilters} clearFilters={clearFilters}
      />

      {sorted.length === 0 ? (
        <p className={styles.emptyState}>No cameras match the current filters.</p>
      ) : (
        <CameraResults sorted={sorted} sortKey={sortKey} sortDirection={sortDirection} toggleSort={toggleSort} />
      )}

      <p className={styles.footnote}>
        All prices are approximate USD estimates.
      </p>
    </div>
  );
}

export default CameraExplorer;
