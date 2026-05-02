import type { ScoredGenre } from "../../../types/genre";
import { evScenes, genreEvLabels } from "../../../data/genres";
import type { SortKey } from "./types";

function sceneLabel(genre: ScoredGenre, sceneEv: number): string {
  if (genre === "nightscape") {
    return evScenes.find((s) => s.ev === sceneEv)?.short ?? "";
  }
  return (
    genreEvLabels[genre]?.[sceneEv] ??
    evScenes.find((s) => s.ev === sceneEv)?.short ??
    ""
  );
}

function evHeaderLabel(genre: ScoredGenre, sceneEv: number): string {
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
  return sortBy === key ? (sortAsc ? "\u2191" : "\u2193") : "\u2195";
}

export { sceneLabel, evHeaderLabel, fmtIso, sortIndicator };
