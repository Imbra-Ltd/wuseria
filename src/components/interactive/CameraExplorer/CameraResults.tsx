import type { ExplorerCamera } from "./types";
import { toSlug } from "../../../utils/slug";
import { makeAlignClasses } from "../shared/table";
import type { CameraSortKey } from "./constants";
import { COLUMNS } from "./constants";
import styles from "./CameraExplorer.module.css";

const ALIGN_CLASSES = makeAlignClasses(styles);

interface CameraResultsProps {
  sorted: ExplorerCamera[];
  sortKey: CameraSortKey;
  sortDirection: "asc" | "desc";
  toggleSort: (key: CameraSortKey) => void;
}

function CameraResults({ sorted, sortKey, sortDirection, toggleSort }: CameraResultsProps) {
  return (
    <>
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              {COLUMNS.map((col) => (
                <th key={col.key} className={ALIGN_CLASSES[col.align]}
                  aria-sort={sortKey === col.key ? (sortDirection === "asc" ? "ascending" : "descending") : "none"}>
                  <button type="button" className={styles.sortButton} onClick={() => toggleSort(col.key)}>
                    {col.label}
                    <span className={styles.sortIndicator}>
                      {sortKey === col.key ? (sortDirection === "asc" ? "\u2191" : "\u2193") : "\u2195"}
                    </span>
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((cam) => (
              <tr key={`${cam.series}-${cam.model}`} className={cam.isDiscontinued ? styles.rowDiscontinued : undefined}>
                <td><a className={styles.lensLink} href={`/cameras/${toSlug(cam.model)}`}>{cam.model}</a></td>
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
  );
}

export { CameraResults };
