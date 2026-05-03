import { formatFL } from "../../../utils/formatting";
import { toSlug } from "../../../utils/slug";
import { MarkPips, FieldVal } from "../shared/MarkPips";
import { fmtIso } from "./helpers";
import type { EnrichedLens } from "./types";
import type { GenreState } from "./useGenreState";
import styles from "./GenreGuide.module.css";

interface GenreCardsProps {
  state: GenreState;
  enrichedLenses: EnrichedLens[];
}

function GenreCards({ state, enrichedLenses }: GenreCardsProps) {
  const { isNightscape, isLandscape, isArchitecture, isPortrait, isStreet } =
    state;

  return (
    <div className={styles.cards}>
      {enrichedLenses.map((el) => {
        const slug = toSlug(`${el.lens.brand} ${el.lens.model}`);
        return (
          <div
            key={`${el.lens.brand}-${el.lens.model}`}
            className={styles.card}
          >
            <div className={styles.cardTop}>
              <MarkPips mark={el.mark} />
              <span className={styles.cardPrice}>~${el.lens.price}</span>
            </div>
            <div className={styles.cardName}>
              <a className={styles.lensLink} href={`/lenses/${slug}`}>
                {el.lens.brand} {el.lens.model}
              </a>
            </div>
            <div className={styles.cardSpecs}>
              <span>f/{el.lens.maxAperture}</span>
              <span>
                {formatFL(el.lens.focalLengthMin, el.lens.focalLengthMax)}
              </span>
              {isNightscape && el.rule500 != null && <span>{el.rule500}s</span>}
              {(isNightscape ||
                (!isLandscape &&
                  !isArchitecture &&
                  !isPortrait &&
                  !isStreet)) &&
                el.idealIso != null && <span>ISO {fmtIso(el.idealIso)}</span>}
              {isNightscape && (
                <>
                  <span>
                    Coma <FieldVal value={el.lens.coma} />
                  </span>
                  <span>
                    Astig <FieldVal value={el.lens.astigmatism} />
                  </span>
                </>
              )}
              {isLandscape && (
                <>
                  <span>
                    CornerS <FieldVal value={el.lens.cornerStopped} />
                  </span>
                  <span>
                    CenterS <FieldVal value={el.lens.centerStopped} />
                  </span>
                </>
              )}
              {isArchitecture && (
                <>
                  <span>
                    CornerS <FieldVal value={el.lens.cornerStopped} />
                  </span>
                  <span>
                    Dist <FieldVal value={el.lens.distortion} />
                  </span>
                  <span>
                    LatCA <FieldVal value={el.lens.lateralCA} />
                  </span>
                </>
              )}
              {isPortrait && (
                <>
                  <span>
                    Bokeh <FieldVal value={el.lens.bokeh} />
                  </span>
                  <span>
                    CenterWO <FieldVal value={el.lens.centerWideOpen} />
                  </span>
                  <span>
                    LoCA <FieldVal value={el.lens.longitudinalCA} />
                  </span>
                </>
              )}
              {isStreet && (
                <>
                  <span>
                    CenterS <FieldVal value={el.lens.centerStopped} />
                  </span>
                  <span>
                    Coma <FieldVal value={el.lens.coma} />
                  </span>
                  <span>
                    Flare <FieldVal value={el.lens.flareResistance} />
                  </span>
                </>
              )}
              <span>{el.lens.weight}g</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export { GenreCards };
