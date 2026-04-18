import { toSlug } from "../../../utils/slug";
import { MarkPips, PickStar } from "../shared/MarkPips";
import type { EnrichedLens } from "./types";
import type { GenreState } from "./useGenreState";
import { sortIndicator } from "./helpers";
import { getColumnDefs } from "./genreColumns";
import { GenreRowCells } from "./GenreRowCells";
import styles from "./GenreGuide.module.css";

interface GenreTableProps {
  state: GenreState;
  enrichedLenses: EnrichedLens[];
}

function GenreTable({ state, enrichedLenses }: GenreTableProps) {
  const { genre, sortBy, sortAsc, handleSort, isNightscape, isLandscape } = state;
  const columns = getColumnDefs(genre);

  return (
    <div className={styles.tableWrap}>
      <table className={styles.table}>
        <thead>
          <tr>
            {columns.map(([key, label, primary]) => (
              <th
                key={`${key}-${label}`}
                className={`${key === "pick" ? styles.cellCenter : ""} ${primary ? styles.primaryCol : ""}`}
              >
                {key === "pick" || key === "wr" || key === "ois" ? (
                  label
                ) : (
                  <button type="button" className={styles.sortButton} onClick={() => handleSort(key)}>
                    {label}
                    <span className={styles.sortIndicator}>{sortIndicator(sortBy, sortAsc, key)}</span>
                  </button>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {enrichedLenses.map((el) => (
            <tr key={`${el.lens.brand}-${el.lens.model}`}>
              <td><MarkPips mark={el.mark} /></td>
              <td className={styles.cellCenter}><PickStar isPick={el.isPick} /></td>
              <td>{el.lens.brand}</td>
              <td><a className={styles.lensLink} href={`/lenses/${toSlug(`${el.lens.brand} ${el.lens.model}`)}`}>{el.lens.model}</a></td>
              <GenreRowCells el={el} genre={genre} />
              {(isNightscape || isLandscape) && (
                <td><span className={el.lens.isWeatherSealed ? styles.dotOn : styles.dotOff} /></td>
              )}
              <td>~${el.lens.price}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export { GenreTable };
