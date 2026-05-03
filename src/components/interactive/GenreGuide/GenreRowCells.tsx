import type { Genre } from "../../../types/genre";
import { FieldVal } from "../shared/MarkPips";
import { fmtIso } from "./helpers";
import type { EnrichedLens } from "./types";
import styles from "./GenreGuide.module.css";

function dotClass(value: boolean | undefined): string {
  return value ? styles.dotOn : styles.dotOff;
}

function formatSweetSpot(aperture: number | undefined): string {
  return aperture ? `f/${aperture}` : "\u2013";
}

interface GenreRowCellsProps {
  el: EnrichedLens;
  genre: Genre;
}

function GenreRowCells({
  el,
  genre,
}: GenreRowCellsProps): React.JSX.Element | null {
  switch (genre) {
    case "nightscape":
      return (
        <>
          <td>{el.effectiveFl}mm</td>
          <td>
            <FieldVal value={el.lens.coma} />
          </td>
          <td>
            <FieldVal value={el.lens.astigmatism} />
          </td>
          <td>f/{el.lens.maxAperture}</td>
          <td>{el.rule500}s</td>
          <td>{fmtIso(el.idealIso)}</td>
        </>
      );
    case "landscape":
      return (
        <>
          <td>{el.effectiveFl}mm</td>
          <td>
            <FieldVal value={el.lens.cornerStopped} />
          </td>
          <td>
            <FieldVal value={el.lens.centerStopped} />
          </td>
          <td>{formatSweetSpot(el.lens.sweetSpotAperture)}</td>
          <td>{fmtIso(el.idealIso)}</td>
        </>
      );
    case "architecture":
      return (
        <>
          <td>{el.effectiveFl}mm</td>
          <td>
            <FieldVal value={el.lens.cornerStopped} />
          </td>
          <td>
            <FieldVal value={el.lens.centerStopped} />
          </td>
          <td>
            <FieldVal value={el.lens.distortion} />
          </td>
          <td>{formatSweetSpot(el.lens.sweetSpotAperture)}</td>
          <td>{fmtIso(el.idealIso)}</td>
          <td>
            <span className={dotClass(el.lens.isWeatherSealed)} />
          </td>
        </>
      );
    case "portrait":
      return (
        <>
          <td>{el.effectiveFl}mm</td>
          <td>
            <FieldVal value={el.lens.bokeh} />
          </td>
          <td>
            <FieldVal value={el.lens.centerWideOpen} />
          </td>
          <td>f/{el.lens.maxAperture}</td>
          <td>{fmtIso(el.idealIso)}</td>
          <td>
            <span className={dotClass(el.lens.hasOis)} />
          </td>
        </>
      );
    case "street":
      return (
        <>
          <td>{el.effectiveFl}mm</td>
          <td>
            <FieldVal value={el.lens.centerStopped} />
          </td>
          <td>f/{el.lens.maxAperture}</td>
          <td>{fmtIso(el.idealIso)}</td>
          <td>
            <span className={dotClass(el.lens.hasOis)} />
          </td>
          <td>
            <span className={dotClass(el.lens.isWeatherSealed)} />
          </td>
          <td>{el.lens.weight}g</td>
        </>
      );
    case "travel":
      return (
        <>
          <td>{el.effectiveFl}mm</td>
          <td>
            <FieldVal value={el.lens.centerStopped} />
          </td>
          <td>{el.lens.weight}g</td>
          <td>{fmtIso(el.idealIso)}</td>
          <td>
            <span className={dotClass(el.lens.hasOis)} />
          </td>
          <td>
            <span className={dotClass(el.lens.isWeatherSealed)} />
          </td>
        </>
      );
    case "sport":
      return (
        <>
          <td>{el.effectiveFl}mm</td>
          <td>
            <FieldVal value={el.lens.centerWideOpen} />
          </td>
          <td>f/{el.lens.maxAperture}</td>
          <td>{fmtIso(el.idealIso)}</td>
          <td>
            <span className={dotClass(el.lens.hasOis)} />
          </td>
          <td>
            <span className={dotClass(el.lens.isWeatherSealed)} />
          </td>
          <td>{el.lens.weight}g</td>
        </>
      );
    case "wildlife":
      return (
        <>
          <td>{el.effectiveFl}mm</td>
          <td>
            <FieldVal value={el.lens.centerWideOpen} />
          </td>
          <td>
            <FieldVal value={el.lens.centerStopped} />
          </td>
          <td>f/{el.lens.maxAperture}</td>
          <td>{fmtIso(el.idealIso)}</td>
          <td>
            <span className={dotClass(el.lens.hasOis)} />
          </td>
          <td>
            <span className={dotClass(el.lens.isWeatherSealed)} />
          </td>
          <td>{el.lens.weight}g</td>
        </>
      );
    case "macro":
      return (
        <>
          <td>{el.effectiveFl}mm</td>
          <td>
            <FieldVal value={el.lens.centerStopped} />
          </td>
          <td>
            {el.lens.maxMagnification
              ? `${el.lens.maxMagnification}x`
              : "\u2013"}
          </td>
          <td>{fmtIso(el.idealIso)}</td>
          <td>
            <span className={dotClass(el.lens.isWeatherSealed)} />
          </td>
        </>
      );
    default:
      return null;
  }
}

export { GenreRowCells };
