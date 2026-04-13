import styles from "./GenreGuide.module.css";

// =============================================================================
// PROPS
// =============================================================================

interface LandscapeMatrixProps {
  cropFactor: number;
  iso: number;
  ev: number;
  nd: number[];
}

// =============================================================================
// CONSTANTS
// =============================================================================

// Skip f/16 on APS-C (diffraction), include it only for GFX
const APERTURES_APSC = [2.8, 4, 5.6, 8, 11];
const APERTURES_GFX = [2.8, 4, 5.6, 8, 11, 16];

// Diffraction thresholds: f/11 on APS-C, f/16 on GFX
function isDiffraction(ap: number, cropFactor: number): boolean {
  if (cropFactor === 0.79) return ap >= 16;
  return ap >= 11;
}

// =============================================================================
// SHUTTER SPEED FORMATTING
// =============================================================================

function formatShutter(seconds: number): string {
  if (seconds >= 3600) return `${Math.round(seconds / 3600)}h`;
  if (seconds >= 60) return `${Math.round(seconds / 60)}m`;
  if (seconds >= 1) return `${Math.round(seconds)}s`;
  // Sub-second: show as fraction
  const denom = Math.round(1 / seconds);
  return `1/${denom}`;
}

// =============================================================================
// SHUTTER SPEED CATEGORY
// =============================================================================

type ShutterCategory = "static" | "silk" | "dramatic";

function shutterCategory(seconds: number): ShutterCategory {
  if (seconds < 1) return "static";
  if (seconds <= 30) return "silk";
  return "dramatic";
}

// =============================================================================
// COMPONENT
// =============================================================================

function LandscapeMatrix({ cropFactor, iso, ev, nd }: LandscapeMatrixProps) {
  const apertures = cropFactor === 0.79 ? APERTURES_GFX : APERTURES_APSC;
  const ndFactor = nd.reduce((acc, f) => acc * f, 1);
  const ndLabel = ndFactor > 1 ? ndFactor : 1;

  return (
    <div className={styles.matrix}>
      <div className={styles.matrixTitle}>
        Shutter speed matrix · ISO {iso} · ND{ndLabel} · EV {ev} · tripod
      </div>
      <div className={styles.matrixScroll}>
        <table className={styles.matrixTable}>
          <thead>
            <tr>
              <th className={styles.matrixCorner}>f/</th>
              <th className={styles.matrixColHead}>Shutter</th>
            </tr>
          </thead>
          <tbody>
            {apertures.map((ap) => {
              const t = ((ap * ap * 100) / (iso * Math.pow(2, ev))) * (ndFactor > 0 ? ndFactor : 1);
              const cat = shutterCategory(t);
              const diffraction = isDiffraction(ap, cropFactor);

              const cellClass =
                cat === "static"
                  ? styles.lsStatic
                  : cat === "silk"
                    ? styles.lsSilk
                    : styles.lsDramatic;

              return (
                <tr key={ap}>
                  <td className={styles.matrixRowHead}>
                    {ap}
                    {diffraction && <span className={styles.lsDiffWarn}> &#9888;</span>}
                  </td>
                  <td className={`${styles.matrixCell} ${cellClass}`}>
                    {formatShutter(t)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div className={styles.matrixLegend}>
        <span className={styles.lsStaticText}>&#9679;</span> static{" "}
        <span className={styles.lsSilkText}>&#9679;</span> silk (1&#8211;30s){" "}
        <span className={styles.lsDramaticText}>&#9679;</span> dramatic (&gt;30s){" "}
        <span className={styles.lsDiffWarn}>&#9888;</span> diffraction
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
