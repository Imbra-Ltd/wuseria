import { MATRIX_FL_COLS_X, MATRIX_FL_COLS_GFX, MATRIX_APERTURES } from "../../../data/genres";
import { formatShutter } from "../../../utils/formatting";
import styles from "./GenreGuide.module.css";

interface ArchitectureMatrixProps {
  cropFactor: number;
  iso: number;
  ev: number;
  nd: number[];
  selectedFl: number;
}

function ArchitectureMatrix({ cropFactor, iso, ev, nd, selectedFl }: ArchitectureMatrixProps) {
  const MATRIX_FL_COLS = cropFactor === 0.79 ? MATRIX_FL_COLS_GFX : MATRIX_FL_COLS_X;
  const fallback = cropFactor === 0.79 ? MATRIX_FL_COLS_GFX[23] : MATRIX_FL_COLS_X[12];
  const cols = MATRIX_FL_COLS[selectedFl] || fallback;
  const ndFactor = nd.reduce((acc, f) => acc * f, 1);
  const apertures = MATRIX_APERTURES;

  return (
    <div className={styles.matrix}>
      <div className={styles.matrixTitle}>
        EV Matrix · Tripod · Maximize depth of field · Capture perfect pixel to pixel
      </div>
      <div className={styles.matrixScroll}>
        <table className={styles.matrixTable}>
          <thead>
            <tr>
              <th className={styles.matrixCorner}>f/</th>
              {cols.map((fl) => (
                <th key={fl} className={styles.matrixColHead}>{fl}mm</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {apertures.map((ap) => {
              return (
                <tr key={ap}>
                  <td className={styles.matrixRowHead}>
                    {ap}
                  </td>
                  {cols.map((fl) => {
                    const t = ((ap * ap * 100) / (iso * Math.pow(2, ev))) * ndFactor;
                    // Architecture: frozen (≤1/60s), blur (≤30s), vanish (>30s)
                    const cat = t <= 1 / 60 ? "frozen" : t <= 30 ? "blur" : "vanish";
                    const cls = cat === "frozen"
                      ? styles.lsStatic
                      : cat === "blur"
                        ? styles.lsSilk
                        : styles.lsDramatic;
                    return (
                      <td key={fl} className={`${styles.matrixCell} ${cls}`}>
                        {formatShutter(t)}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div className={styles.matrixLegend}>
        <span className={styles.lsStaticText}>●</span> people frozen{" "}
        <span className={styles.lsSilkText}>●</span> people blur{" "}
        <span className={styles.lsDramaticText}>●</span> people vanish
      </div>
      <p className={styles.matrixExplain}>
        Each cell shows the shutter speed at that aperture. Blue freezes
        people sharply. Amber blurs movement. Teal makes people disappear
        from long exposures — ideal for empty architecture shots.
      </p>
    </div>
  );
}

export { ArchitectureMatrix };
export type { ArchitectureMatrixProps };
