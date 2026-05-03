import { useMemo, useCallback } from "react";
import { useSort } from "../../../hooks/useSort";
import { useUrlFilters } from "../../../hooks/useUrlFilters";
import type { CameraSortKey } from "./constants";
import { YEAR_RANGES, PRICE_RANGES } from "./constants";
import { CameraFilters } from "./CameraFilters";
import { CameraResults } from "./CameraResults";
import type { ExplorerCamera } from "./types";
import styles from "./CameraExplorer.module.css";

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
  f: Record<string, string>,
): boolean {
  return (
    passesExactFilter(cam.mount, f.mount) &&
    passesExactFilter(cam.series, f.series) &&
    passesRangeFilter(cam.year, f.year, YEAR_RANGES) &&
    passesExactFilter(cam.sensor, f.sensor) &&
    passesExactFilter(cam.formFactor, f.form) &&
    passesBooleanFilter(f.ibis, cam.hasIbis) &&
    passesBooleanFilter(f.wr, cam.isWeatherSealed) &&
    passesStatusFilter(f.status, cam.isDiscontinued) &&
    passesExactFilter(cam.videoSpec, f.video) &&
    passesRangeFilter(cam.price, f.price, PRICE_RANGES) &&
    (!f.q || cam.model.toLowerCase().includes(f.q.toLowerCase()))
  );
}

interface CameraExplorerProps {
  cameras: ExplorerCamera[];
}

const FILTER_KEYS = [
  "q",
  "mount",
  "series",
  "year",
  "sensor",
  "form",
  "ibis",
  "wr",
  "status",
  "video",
  "price",
] as const;

function CameraExplorer({ cameras }: CameraExplorerProps) {
  const {
    values: f,
    set,
    clear: clearFilters,
    hasFilters,
  } = useUrlFilters(FILTER_KEYS);

  const seriesOptions = useMemo(() => {
    const pool = f.mount ? cameras.filter((c) => c.mount === f.mount) : cameras;
    return [...new Set(pool.map((c) => c.series))].sort();
  }, [cameras, f.mount]);

  const sensorOptions = useMemo(() => {
    const pool = f.mount ? cameras.filter((c) => c.mount === f.mount) : cameras;
    return [...new Set(pool.map((c) => c.sensor))].sort();
  }, [cameras, f.mount]);

  const filtered = useMemo(
    () => cameras.filter((cam) => matchesCameraFilters(cam, f)),
    [cameras, f],
  );

  const availableFirst = useCallback(
    (a: ExplorerCamera, b: ExplorerCamera) =>
      Number(a.isDiscontinued ?? false) - Number(b.isDiscontinued ?? false),
    [],
  );
  const descFirst = useMemo(
    () => new Set<CameraSortKey>(["hasIbis", "isWeatherSealed"]),
    [],
  );
  const { sorted, sortKey, sortDirection, toggleSort } = useSort<
    ExplorerCamera,
    CameraSortKey
  >(filtered, "year", "asc", availableFirst, descFirst);

  function handleMountChange(value: string): void {
    set("mount", value);
    if (f.series) {
      const seriesExistsInMount = cameras.some(
        (c) => c.series === f.series && (!value || c.mount === value),
      );
      if (!seriesExistsInMount) set("series", "");
    }
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
        search={f.q}
        setSearch={(v) => set("q", v)}
        mount={f.mount}
        onMountChange={handleMountChange}
        series={f.series}
        setSeries={(v) => set("series", v)}
        yearRange={f.year}
        setYearRange={(v) => set("year", v)}
        sensorType={f.sensor}
        setSensorType={(v) => set("sensor", v)}
        ibis={f.ibis}
        setIbis={(v) => set("ibis", v)}
        wr={f.wr}
        setWr={(v) => set("wr", v)}
        formFactor={f.form}
        setFormFactor={(v) => set("form", v)}
        discontinued={f.status}
        setDiscontinued={(v) => set("status", v)}
        videoSpec={f.video}
        setVideoSpec={(v) => set("video", v)}
        priceRange={f.price}
        setPriceRange={(v) => set("price", v)}
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
