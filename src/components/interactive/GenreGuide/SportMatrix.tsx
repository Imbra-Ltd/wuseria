import {
  MATRIX_FL_COLS_X,
  MATRIX_FL_COLS_GFX,
  MATRIX_APERTURES,
} from "../../../data/genres";
import { viabilityClass } from "./helpers";
import styles from "./GenreGuide.module.css";

interface SportMatrixProps {
  cropFactor: number;
  iso: number;
  ev: number;
  selectedFl: number;
  genre: "sport" | "wildlife";
}

function SportMatrix({
  cropFactor,
  iso,
  ev,
  selectedFl,
  genre,
}: SportMatrixProps) {
  const MATRIX_FL_COLS =
    cropFactor === 0.79 ? MATRIX_FL_COLS_GFX : MATRIX_FL_COLS_X;
  const fallback =
    cropFactor === 0.79 ? MATRIX_FL_COLS_GFX[63] : MATRIX_FL_COLS_X[135];
  const cols = MATRIX_FL_COLS[selectedFl] || fallback;
  const apertures = MATRIX_APERTURES.filter((ap) => ap <= 11);

  return (
    <div className={styles.matrix}>
      <div className={styles.matrixTitle}>
        EV Matrix · Tripod/Monopod · 1/4×FL rule ·{" "}
        {genre === "wildlife" ? "Capture the wild" : "Capture the action"}
      </div>
      <div className={styles.matrixScroll}>
        <table className={styles.matrixTable}>
          <thead>
            <tr>
              <th className={styles.matrixCorner}>f/</th>
              {cols.map((fl) => (
                <th key={fl} className={styles.matrixColHead}>
                  {fl}mm
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {apertures.map((ap) => (
              <tr key={ap}>
                <td className={styles.matrixRowHead}>{ap}</td>
                {cols.map((fl) => {
                  // 4× FL rule: min shutter = 1/(4 × crop × FL)
                  const minS = 1 / (4 * cropFactor * fl);
                  const t = (ap * ap * 100) / (iso * Math.pow(2, ev));
                  const viable = t <= minS;
                  const marginal = !viable && t <= minS * 2;
                  const label =
                    minS >= 1
                      ? `${Math.round(minS)}s`
                      : `1/${Math.round(1 / minS)}`;
                  const cls = viabilityClass(viable, marginal, styles);
                  return (
                    <td key={fl} className={`${styles.matrixCell} ${cls}`}>
                      {label}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className={styles.matrixLegend}>
        <span className={styles.matrixViableText}>●</span> fast enough{" "}
        <span className={styles.matrixMarginalText}>●</span> 1 stop slow{" "}
        <span className={styles.matrixOverText}>●</span> too slow
      </div>
      <p className={styles.matrixExplain}>
        {genre === "wildlife"
          ? "Each cell shows the minimum shutter speed to freeze fast-moving subjects like birds in flight. Green means your settings freeze motion. Amber is borderline — slight blur on wings and fast movement."
          : "Each cell shows the minimum shutter speed to freeze action at that focal length. Green means your settings freeze motion. Amber is borderline — slight blur on fast movement."}
      </p>
    </div>
  );
}

export { SportMatrix };
export type { SportMatrixProps };
