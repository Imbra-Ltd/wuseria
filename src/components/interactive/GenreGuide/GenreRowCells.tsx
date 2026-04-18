import type { ScoredGenre } from "../../../types/genre";
import { FieldVal } from "../shared/MarkPips";
import { fmtIso } from "./helpers";
import type { EnrichedLens } from "./types";
import styles from "./GenreGuide.module.css";

interface GenreRowCellsProps {
  el: EnrichedLens;
  genre: ScoredGenre;
}

function GenreRowCells({ el, genre }: GenreRowCellsProps): React.JSX.Element | null {
  if (genre === "nightscape") return (
    <>
      <td>{el.effectiveFl}mm</td>
      <td><FieldVal value={el.lens.coma} /></td>
      <td><FieldVal value={el.lens.astigmatism} /></td>
      <td>f/{el.lens.maxAperture}</td>
      <td>{el.rule500}s</td>
      <td>{fmtIso(el.idealIso)}</td>
    </>
  );
  if (genre === "landscape") return (
    <>
      <td>{el.effectiveFl}mm</td>
      <td><FieldVal value={el.lens.cornerStopped} /></td>
      <td><FieldVal value={el.lens.centerStopped} /></td>
      <td>{el.lens.sweetSpotAperture ? `f/${el.lens.sweetSpotAperture}` : "\u2013"}</td>
      <td>{fmtIso(el.idealIso)}</td>
    </>
  );
  if (genre === "architecture") return (
    <>
      <td>{el.effectiveFl}mm</td>
      <td><FieldVal value={el.lens.cornerStopped} /></td>
      <td><FieldVal value={el.lens.centerStopped} /></td>
      <td><FieldVal value={el.lens.distortion} /></td>
      <td>{el.lens.sweetSpotAperture ? `f/${el.lens.sweetSpotAperture}` : "\u2013"}</td>
      <td>{fmtIso(el.idealIso)}</td>
      <td><span className={el.lens.isWeatherSealed ? styles.dotOn : styles.dotOff} /></td>
    </>
  );
  if (genre === "portrait") return (
    <>
      <td>{el.effectiveFl}mm</td>
      <td><FieldVal value={el.lens.bokeh} /></td>
      <td><FieldVal value={el.lens.centerWideOpen} /></td>
      <td>f/{el.lens.maxAperture}</td>
      <td>{fmtIso(el.idealIso)}</td>
      <td><span className={el.lens.hasOis ? styles.dotOn : styles.dotOff} /></td>
    </>
  );
  if (genre === "street") return (
    <>
      <td>{el.effectiveFl}mm</td>
      <td><FieldVal value={el.lens.centerStopped} /></td>
      <td>f/{el.lens.maxAperture}</td>
      <td>{fmtIso(el.idealIso)}</td>
      <td><span className={el.lens.hasOis ? styles.dotOn : styles.dotOff} /></td>
      <td><span className={el.lens.isWeatherSealed ? styles.dotOn : styles.dotOff} /></td>
      <td>{el.lens.weight}g</td>
    </>
  );
  if (genre === "travel") return (
    <>
      <td>{el.effectiveFl}mm</td>
      <td><FieldVal value={el.lens.centerStopped} /></td>
      <td>{el.lens.weight}g</td>
      <td>{fmtIso(el.idealIso)}</td>
      <td><span className={el.lens.hasOis ? styles.dotOn : styles.dotOff} /></td>
      <td><span className={el.lens.isWeatherSealed ? styles.dotOn : styles.dotOff} /></td>
    </>
  );
  if (genre === "sport") return (
    <>
      <td>{el.effectiveFl}mm</td>
      <td><FieldVal value={el.lens.centerWideOpen} /></td>
      <td>f/{el.lens.maxAperture}</td>
      <td>{fmtIso(el.idealIso)}</td>
      <td><span className={el.lens.hasOis ? styles.dotOn : styles.dotOff} /></td>
      <td><span className={el.lens.isWeatherSealed ? styles.dotOn : styles.dotOff} /></td>
      <td>{el.lens.weight}g</td>
    </>
  );
  if (genre === "wildlife") return (
    <>
      <td>{el.effectiveFl}mm</td>
      <td><FieldVal value={el.lens.centerWideOpen} /></td>
      <td><FieldVal value={el.lens.centerStopped} /></td>
      <td>f/{el.lens.maxAperture}</td>
      <td>{fmtIso(el.idealIso)}</td>
      <td><span className={el.lens.hasOis ? styles.dotOn : styles.dotOff} /></td>
      <td><span className={el.lens.isWeatherSealed ? styles.dotOn : styles.dotOff} /></td>
      <td>{el.lens.weight}g</td>
    </>
  );
  if (genre === "macro") return (
    <>
      <td>{el.effectiveFl}mm</td>
      <td><FieldVal value={el.lens.centerStopped} /></td>
      <td>{el.lens.maxMagnification ? `${el.lens.maxMagnification}x` : "\u2013"}</td>
      <td>{fmtIso(el.idealIso)}</td>
      <td><span className={el.lens.isWeatherSealed ? styles.dotOn : styles.dotOff} /></td>
    </>
  );
  return null;
}

export { GenreRowCells };
