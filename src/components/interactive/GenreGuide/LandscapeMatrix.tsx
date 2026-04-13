import { MATRIX_FL_COLS_X, MATRIX_FL_COLS_GFX, MATRIX_APERTURES } from "../../../data/genres";
import styles from "./GenreGuide.module.css";

interface LandscapeMatrixProps {
  cropFactor: number;
  iso: number;
  ev: number;
  nd: number[];
  selectedFl: number;
}

function formatShutter(seconds: number): string {
  if (seconds >= 3600) return `${Math.round(seconds / 3600)}h`;
  if (seconds >= 60) return `${Math.round(seconds / 60)}m`;
  if (seconds >= 1) return `${Math.round(seconds)}s`;
  const denom = Math.round(1 / seconds);
  return `1/${denom}`;
}

function LandscapeMatrix({ cropFactor, iso, ev, nd, selectedFl }: LandscapeMatrixProps) {
  const MATRIX_FL_COLS = cropFactor === 0.79 ? MATRIX_FL_COLS_GFX : MATRIX_FL_COLS_X;
  const fallback = cropFactor === 0.79 ? MATRIX_FL_COLS_GFX[23] : MATRIX_FL_COLS_X[12];
  const cols = MATRIX_FL_COLS[selectedFl] || fallback;
  const ndFactor = nd.reduce((acc, f) => acc * f, 1);
  const ndLabel = ndFactor > 1 ? ` · ND${ndFactor.toLocaleString()}` : "";
  const apertures = MATRIX_APERTURES;

  return (
    <div className={styles.matrix}>
      <div className={styles.matrixTitle}>
        EV Matrix · ISO {iso}{ndLabel} · tripod · {cropFactor === 0.79 ? "diffraction f/16+" : "diffraction f/11+"}
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
                    const cat = t < 1 ? "static" : t <= 30 ? "silk" : "dramatic";
                    const cls = cat === "static"
                      ? styles.lsStatic
                      : cat === "silk"
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
        <span className={styles.lsStaticText}>●</span> static{" "}
        <span className={styles.lsSilkText}>●</span> silk (1–30s){" "}
        <span className={styles.lsDramaticText}>●</span> dramatic (&gt;30s)
      </div>
      <p className={styles.matrixExplain}>
        Each cell shows the shutter speed at that aperture. Blue freezes motion.
        Green gives silky water and cloud streaks. Teal creates dramatic long
        exposures where moving objects disappear.
      </p>
    </div>
  );
}

export { LandscapeMatrix };
export type { LandscapeMatrixProps };
