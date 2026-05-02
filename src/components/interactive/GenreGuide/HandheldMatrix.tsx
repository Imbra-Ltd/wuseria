import {
  MATRIX_FL_COLS_X,
  MATRIX_FL_COLS_GFX,
  MATRIX_APERTURES,
} from "../../../data/genres";
import styles from "./GenreGuide.module.css";

interface HandheldMatrixProps {
  cropFactor: number;
  iso: number;
  ev: number;
  selectedFl: number;
  genre: "street" | "travel" | "portrait" | "macro";
  magnification?: number;
}

function HandheldMatrix({
  cropFactor,
  iso,
  ev,
  selectedFl,
  genre,
  magnification = 1.0,
}: HandheldMatrixProps) {
  const MATRIX_FL_COLS =
    cropFactor === 0.79 ? MATRIX_FL_COLS_GFX : MATRIX_FL_COLS_X;
  const fallback =
    cropFactor === 0.79 ? MATRIX_FL_COLS_GFX[23] : MATRIX_FL_COLS_X[12];
  const cols = MATRIX_FL_COLS[selectedFl] || fallback;
  const apertures = MATRIX_APERTURES;

  // Min shutter speed by genre:
  // Portrait: 2× FL rule (freeze expression)
  // Macro: 1/(FL × (1+mag) × crop) — magnification extends effective FL
  // Street/Travel: reciprocal rule adjusted for megapixels
  function minShutter(fl: number): number {
    if (genre === "portrait") return 1 / (2 * cropFactor * fl);
    if (genre === "macro") return 1 / (fl * (1 + magnification) * cropFactor);
    return 1 / (cropFactor * fl);
  }

  const titles: Record<string, string> = {
    portrait: "1/2×FL rule · Capture the emotion",
    street: "1/FL rule · Capture the moment",
    travel: "1/FL rule · Capture the story",
    macro: `1/${1 + magnification}×FL rule · Capture the detail`,
  };

  return (
    <div className={styles.matrix}>
      <div className={styles.matrixTitle}>
        EV Matrix · Handheld · {titles[genre]}
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
                  const minS = minShutter(fl);
                  const needed = Math.round(
                    (ap * ap * 100) / (minS * Math.pow(2, ev)),
                  );
                  const viable = needed <= iso;
                  const marginal = !viable && needed <= iso * 2;
                  const label =
                    minS >= 1
                      ? `${Math.round(minS)}s`
                      : `1/${Math.round(1 / minS)}`;
                  const cls = viable
                    ? styles.matrixViable
                    : marginal
                      ? styles.matrixMarginal
                      : styles.matrixOver;
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
        Each cell shows the minimum shutter speed to avoid camera shake at that
        focal length. Green means your ISO is enough. Amber means recoverable
        with exposure push and noise reduction.
      </p>
    </div>
  );
}

export { HandheldMatrix };
export type { HandheldMatrixProps };
