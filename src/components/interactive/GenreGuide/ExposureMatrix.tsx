import {
  MATRIX_FL_COLS_X,
  MATRIX_FL_COLS_GFX,
  MATRIX_APERTURES,
} from "../../../data/genres";
import { viabilityClass } from "./helpers";
import styles from "./GenreGuide.module.css";

interface ExposureMatrixProps {
  cropFactor: number;
  iso: number;
  ev: number;
  selectedFl: number;
}

function ExposureMatrix({
  cropFactor,
  iso,
  ev,
  selectedFl,
}: ExposureMatrixProps) {
  const MATRIX_FL_COLS =
    cropFactor === 0.79 ? MATRIX_FL_COLS_GFX : MATRIX_FL_COLS_X;
  const fallback =
    cropFactor === 0.79 ? MATRIX_FL_COLS_GFX[23] : MATRIX_FL_COLS_X[12];
  const cols = MATRIX_FL_COLS[selectedFl] || fallback;

  return (
    <div className={styles.matrix}>
      <div className={styles.matrixTitle}>
        EV Matrix · Tripod · Rule of 500 · Untracked · Capture the stars
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
            {MATRIX_APERTURES.map((ap) => (
              <tr key={ap}>
                <td className={styles.matrixRowHead}>{ap}</td>
                {cols.map((fl) => {
                  const maxT = Math.round(500 / (cropFactor * fl));
                  const needed = Math.round(
                    (ap * ap * 100) / (maxT * Math.pow(2, ev)),
                  );
                  const viable = needed <= iso;
                  const marginal = !viable && needed <= iso * 2;
                  const label =
                    maxT >= 60 ? `${Math.round(maxT / 60)}m` : `${maxT}s`;
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
        <span className={styles.matrixViableText}>●</span> within ISO{" "}
        <span className={styles.matrixMarginalText}>●</span> within 1 stop{" "}
        <span className={styles.matrixOverText}>●</span> needs more ISO
      </div>
      <p className={styles.matrixExplain}>
        Max exposure before star trails = 500 / (crop x FL). Each cell shows the
        longest untracked exposure at that aperture and focal length. Green
        means your selected ISO is enough. Amber means you are within one stop —
        recoverable with exposure push and noise reduction. Red means the
        exposure does not gather enough light at this ISO.
      </p>
    </div>
  );
}

export { ExposureMatrix };
export type { ExposureMatrixProps };
