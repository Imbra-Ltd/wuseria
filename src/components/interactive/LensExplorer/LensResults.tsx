import { formatFL } from "../../../utils/formatting";
import { makeAlignClasses } from "../shared/table";
import type { ExplorerLens, LensSortKey } from "./constants";
import { COLUMNS } from "./constants";
import styles from "./LensExplorer.module.css";

const ALIGN_CLASSES = makeAlignClasses(styles);

interface LensResultsProps {
  sorted: ExplorerLens[];
  slugMap: Map<string, string>;
  sortKey: LensSortKey;
  sortDirection: "asc" | "desc";
  toggleSort: (key: LensSortKey) => void;
}

function LensResults({ sorted, slugMap, sortKey, sortDirection, toggleSort }: LensResultsProps) {
  return (
    <>
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              {COLUMNS.map((col) => (
                <th key={col.key} className={ALIGN_CLASSES[col.align]} onClick={() => toggleSort(col.key)}
                  aria-sort={sortKey === col.key ? (sortDirection === "asc" ? "ascending" : "descending") : "none"}>
                  {col.label}
                  <span className={styles.sortIndicator}>
                    {sortKey === col.key ? (sortDirection === "asc" ? "\u2191" : "\u2193") : "\u2195"}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((lens) => (
              <tr key={`${lens.brand}-${lens.model}`} className={lens.isDiscontinued ? styles.rowDiscontinued : undefined}>
                <td>{lens.brand}</td>
                <td><a className={styles.lensLink} href={`/lenses/${slugMap.get(`${lens.brand}-${lens.model}`)}`}>{lens.model}</a></td>
                <td>{lens.year ?? ""}</td>
                <td className={styles.cellRight}>{formatFL(lens.focalLengthMin, lens.focalLengthMax)}</td>
                <td className={styles.cellRight}>{lens.maxAperture}</td>
                <td className={styles.cellRight}>{lens.filterThread ?? "\u2013"}</td>
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

      <div className={styles.cards}>
        {sorted.map((lens) => (
          <div key={`${lens.brand}-${lens.model}`} className={`${styles.card} ${lens.isDiscontinued ? styles.cardDiscontinued : ""}`}>
            <div className={styles.cardHeader}>
              <a className={styles.lensLink} href={`/lenses/${slugMap.get(`${lens.brand}-${lens.model}`)}`}>{lens.brand} {lens.model}</a>
              <span className={styles.cardPrice}>~${lens.price}</span>
            </div>
            <div className={styles.cardSpecs}>
              {lens.year && <span>{lens.year}</span>}
              <span>{lens.weight}g</span>
              {lens.opticalQuality != null && <span>OQ {lens.opticalQuality.toFixed(1)}</span>}
              {lens.filterThread && <span>{"\u03A6"}{lens.filterThread}mm</span>}
            </div>
            <div className={styles.cardBadges}>
              <span className={styles.badge}>{lens.mount}</span>
              <span className={styles.badge}>{lens.type === "prime" ? "Prime" : "Zoom"}</span>
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
  );
}

export { LensResults };
