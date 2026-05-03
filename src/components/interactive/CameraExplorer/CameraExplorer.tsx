import { useState, useMemo, useCallback } from "react";
import { useSort } from "../../../hooks/useSort";
import type { CameraSortKey } from "./constants";
import { YEAR_RANGES, PRICE_RANGES } from "./constants";
import { CameraFilters } from "./CameraFilters";
import { CameraResults } from "./CameraResults";
import type { ExplorerCamera } from "./types";
import styles from "./CameraExplorer.module.css";

interface CameraFilterValues {
  search: string;
  mount: string;
  series: string;
  yearRange: string;
  sensorType: string;
  formFactor: string;
  ibis: string;
  wr: string;
  discontinued: string;
  videoSpec: string;
  priceRange: string;
}

function passesBooleanFilter(
  filter: string,
  value: boolean | undefined,
): boolean {
  if (filter === "yes") return !!value;
  if (filter === "no") return !value;
  return true;
}

function passesRangeFilter(
  value: number,
  filter: string,
  ranges: Record<string, [number, number]>,
): boolean {
  if (!filter) return true;
  const range = ranges[filter];
  if (!range) return true;
  const [min, max] = range;
  return value >= min && value <= max;
}

function passesExactFilter(value: string, filter: string): boolean {
  return !filter || value === filter;
}

function passesStatusFilter(
  filter: string,
  isDiscontinued: boolean | undefined,
): boolean {
  if (filter === "available") return !isDiscontinued;
  if (filter === "discontinued") return !!isDiscontinued;
  return true;
}

function matchesCameraFilters(
  cam: ExplorerCamera,
  f: CameraFilterValues,
): boolean {
  return (
    passesExactFilter(cam.mount, f.mount) &&
    passesExactFilter(cam.series, f.series) &&
    passesRangeFilter(cam.year, f.yearRange, YEAR_RANGES) &&
    passesExactFilter(cam.sensor, f.sensorType) &&
    passesExactFilter(cam.formFactor, f.formFactor) &&
    passesBooleanFilter(f.ibis, cam.hasIbis) &&
    passesBooleanFilter(f.wr, cam.isWeatherSealed) &&
    passesStatusFilter(f.discontinued, cam.isDiscontinued) &&
    passesExactFilter(cam.videoSpec, f.videoSpec) &&
    passesRangeFilter(cam.price, f.priceRange, PRICE_RANGES) &&
    (!f.search || cam.model.toLowerCase().includes(f.search.toLowerCase()))
  );
}

interface CameraExplorerProps {
  cameras: ExplorerCamera[];
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
    const f: CameraFilterValues = {
      search,
      mount,
      series,
      yearRange,
      sensorType,
      formFactor,
      ibis,
      wr,
      discontinued,
      videoSpec,
      priceRange,
    };
    return cameras.filter((cam) => matchesCameraFilters(cam, f));
  }, [
    cameras,
    search,
    mount,
    series,
    yearRange,
    sensorType,
    formFactor,
    discontinued,
    ibis,
    wr,
    videoSpec,
    priceRange,
  ]);

  const availableFirst = useCallback(
    (a: ExplorerCamera, b: ExplorerCamera) =>
      Number(a.isDiscontinued ?? false) - Number(b.isDiscontinued ?? false),
    [],
  );
  const { sorted, sortKey, sortDirection, toggleSort } = useSort<
    ExplorerCamera,
    CameraSortKey
  >(filtered, "year", "asc", availableFirst);

  function handleMountChange(value: string): void {
    setMount(value);
    if (series) {
      const seriesExistsInMount = cameras.some(
        (c) => c.series === series && (!value || c.mount === value),
      );
      if (!seriesExistsInMount) setSeries("");
    }
  }

  const hasFilters = !!(
    search ||
    mount ||
    series ||
    yearRange ||
    sensorType ||
    formFactor ||
    discontinued ||
    ibis ||
    wr ||
    videoSpec ||
    priceRange
  );

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
        <p className={styles.heroSub}>
          {sorted.length} / {cameras.length} Fujifilm cameras
        </p>
      </div>

      <CameraFilters
        search={search}
        setSearch={setSearch}
        mount={mount}
        onMountChange={handleMountChange}
        series={series}
        setSeries={setSeries}
        yearRange={yearRange}
        setYearRange={setYearRange}
        sensorType={sensorType}
        setSensorType={setSensorType}
        ibis={ibis}
        setIbis={setIbis}
        wr={wr}
        setWr={setWr}
        formFactor={formFactor}
        setFormFactor={setFormFactor}
        discontinued={discontinued}
        setDiscontinued={setDiscontinued}
        videoSpec={videoSpec}
        setVideoSpec={setVideoSpec}
        priceRange={priceRange}
        setPriceRange={setPriceRange}
        seriesOptions={seriesOptions}
        sensorOptions={sensorOptions}
        hasFilters={hasFilters}
        clearFilters={clearFilters}
        sortKey={sortKey}
        sortDirection={sortDirection}
        toggleSort={toggleSort}
      />

      {sorted.length === 0 ? (
        <p className={styles.emptyState}>
          No cameras match the current filters.
        </p>
      ) : (
        <CameraResults
          sorted={sorted}
          sortKey={sortKey}
          sortDirection={sortDirection}
          toggleSort={toggleSort}
        />
      )}
    </div>
  );
}

export default CameraExplorer;
