import {
  ND_OPTIONS,
  FL_CHIPS_X,
  FL_CHIPS_GFX,
  MACRO_MAGNIFICATION_OPTIONS,
} from "../../../data/genres";
import { ChipGroup } from "../shared/ChipGroup";
import type { GenreState } from "./useGenreState";
import styles from "./GenreGuide.module.css";

interface GenreControlsProps {
  state: GenreState;
}

function GenreControls({ state }: GenreControlsProps) {
  const {
    genre,
    iso,
    setIso,
    nd,
    cropFactor,
    setCropFactor,
    selectedFl,
    setSelectedFl,
    magnification,
    setMagnification,
    isNightscape,
    flChips,
    toggleNd,
  } = state;

  return (
    <div className={styles.controls}>
      {/* Mount */}
      <div className={styles.controlGroup}>
        <ChipGroup
          label="Mount"
          value={cropFactor === 1.5 ? "X" : "GFX"}
          onChange={(v) => {
            const c = v === "GFX" ? 0.79 : 1.5;
            setCropFactor(c);
            if (isNightscape) setIso(c === 0.79 ? 3200 : 1600);
            const chips = c === 0.79 ? FL_CHIPS_GFX : FL_CHIPS_X;
            setSelectedFl(chips.default[0].fl);
          }}
          styles={styles}
          options={[
            { label: "X-Mount", value: "X" },
            { label: "GFX", value: "GFX" },
          ]}
        />
      </div>

      {/* FL chips */}
      <div className={styles.controlGroup}>
        <span className={styles.controlLabel}>FL</span>
        <div className={styles.flRow}>
          {flChips.map((chip) => (
            <button
              key={chip.fl}
              type="button"
              className={`${styles.chip} ${selectedFl === chip.fl ? styles.chipOn : ""}`}
              onClick={() => setSelectedFl(chip.fl)}
            >
              {chip.label}
            </button>
          ))}
        </div>
      </div>

      {/* ISO */}
      <div className={styles.controlGroup}>
        <span className={styles.controlLabel}>ISO</span>
        <div className={styles.flRow}>
          {[100, 200, 400, 800, 1600, 3200, 6400].map((v) => (
            <button
              key={v}
              type="button"
              className={`${styles.chip} ${iso === v ? styles.chipOn : ""}`}
              onClick={() => setIso(v)}
            >
              {v}
            </button>
          ))}
        </div>
      </div>

      {/* ND — only for landscape + architecture */}
      {(genre === "landscape" || genre === "architecture") && (
        <div className={styles.controlGroup}>
          <span className={styles.controlLabel}>ND</span>
          <div className={styles.ndRow}>
            {ND_OPTIONS.map((opt) => (
              <button
                key={opt.factor}
                type="button"
                className={`${styles.chip} ${nd.includes(opt.factor) ? styles.chipOn : ""}`}
                onClick={() => toggleNd(opt.factor)}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Magnification — only for macro */}
      {genre === "macro" && (
        <div className={styles.controlGroup}>
          <span className={styles.controlLabel}>Mag</span>
          <div className={styles.flRow}>
            {MACRO_MAGNIFICATION_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                type="button"
                className={`${styles.chip} ${magnification === opt.value ? styles.chipOn : ""}`}
                onClick={() => setMagnification(opt.value)}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export { GenreControls };
