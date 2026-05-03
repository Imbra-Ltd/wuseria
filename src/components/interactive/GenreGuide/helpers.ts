import type { Genre } from "../../../types/genre";
import { evScenes, genreEvLabels } from "../../../data/genres";
import type { SortKey } from "./types";

function sceneLabel(genre: Genre, sceneEv: number): string {
  if (genre === "nightscape") {
    return evScenes.find((s) => s.ev === sceneEv)?.short ?? "";
  }
  return (
    genreEvLabels[genre]?.[sceneEv] ??
    evScenes.find((s) => s.ev === sceneEv)?.short ??
    ""
  );
}

function evHeaderLabel(genre: Genre, sceneEv: number): string {
  return (
    genreEvLabels[genre]?.[sceneEv] ??
    evScenes.find((s) => s.ev === sceneEv)?.short ??
    ""
  );
}

function fmtIso(v: number | null): string {
  if (v == null) return "\u2013";
  if (v > 99999) return ">100K";
  return v.toLocaleString();
}

function sortIndicator(
  sortBy: SortKey,
  sortAsc: boolean,
  key: SortKey,
): string {
  if (sortBy !== key) return "\u2195";
  return sortAsc ? "\u2191" : "\u2193";
}

function viabilityClass(
  isViable: boolean,
  isMarginal: boolean,
  styles: Record<string, string>,
): string {
  if (isViable) return styles.matrixViable;
  if (isMarginal) return styles.matrixMarginal;
  return styles.matrixOver;
}

function landscapeCatClass(
  t: number,
  frozenThreshold: number,
  silkThreshold: number,
  styles: Record<string, string>,
): string {
  if (t <= frozenThreshold) return styles.lsStatic;
  if (t <= silkThreshold) return styles.lsSilk;
  return styles.lsDramatic;
}

export {
  sceneLabel,
  evHeaderLabel,
  fmtIso,
  sortIndicator,
  viabilityClass,
  landscapeCatClass,
};
