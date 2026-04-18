import type { ScoredGenre } from "../../../types/genre";
import type { SortKey } from "./types";

type ColumnDef = [SortKey, string, boolean?];

function getColumnDefs(genre: ScoredGenre): ColumnDef[] {
  const common: ColumnDef[] = [
    ["mark", "Mark"],
    ["pick", ""],
    ["brand", "Brand"],
    ["fl", "Model"],
    ["fl", "FL"],
  ];

  const genreColumns: Record<string, ColumnDef[]> = {
    nightscape: [
      ...common,
      ["coma", "Coma", true],
      ["astigmatism", "Astig", true],
      ["aperture", "f/", true],
      ["rule500", "Rule 500"],
      ["idealIso", "Ideal ISO"],
      ["wr", "WR"],
      ["price", "Price"],
    ],
    landscape: [
      ...common,
      ["cornerStopped", "CornerS", true],
      ["centerStopped", "CenterS", true],
      ["aperture", "Sweet"],
      ["idealIso", "Ideal ISO"],
      ["wr", "WR"],
      ["price", "Price"],
    ],
    architecture: [
      ...common,
      ["cornerStopped", "CornerS", true],
      ["centerStopped", "CenterS", true],
      ["distortion", "Distor", true],
      ["aperture", "Sweet"],
      ["idealIso", "Ideal ISO"],
      ["wr", "WR"],
      ["price", "Price"],
    ],
    portrait: [
      ...common,
      ["bokeh", "Bokeh", true],
      ["centerWideOpen", "CenterWO", true],
      ["aperture", "f/"],
      ["idealIso", "Ideal ISO"],
      ["ois", "OIS"],
      ["price", "Price"],
    ],
    street: [
      ...common,
      ["centerStopped", "CenterS", true],
      ["aperture", "f/", true],
      ["idealIso", "Ideal ISO"],
      ["ois", "OIS"],
      ["wr", "WR"],
      ["weight", "Weight"],
      ["price", "Price"],
    ],
    travel: [
      ...common,
      ["centerStopped", "CenterS", true],
      ["weight", "Weight", true],
      ["idealIso", "Ideal ISO"],
      ["ois", "OIS"],
      ["wr", "WR"],
      ["price", "Price"],
    ],
    sport: [
      ...common,
      ["centerWideOpen", "CenterWO", true],
      ["aperture", "f/"],
      ["idealIso", "Ideal ISO"],
      ["ois", "OIS"],
      ["wr", "WR"],
      ["weight", "Weight"],
      ["price", "Price"],
    ],
    wildlife: [
      ...common,
      ["centerWideOpen", "CenterWO", true],
      ["centerStopped", "CenterS", true],
      ["aperture", "f/"],
      ["idealIso", "Ideal ISO"],
      ["ois", "OIS"],
      ["wr", "WR"],
      ["weight", "Weight"],
      ["price", "Price"],
    ],
    macro: [
      ...common,
      ["centerStopped", "CenterS", true],
      ["magnification", "Mag", true],
      ["idealIso", "Ideal ISO"],
      ["wr", "WR"],
      ["price", "Price"],
    ],
  };

  return genreColumns[genre] ?? [
    ["mark", "Mark"],
    ["pick", ""],
    ["brand", "Brand"],
    ["fl", "Model"],
    ["idealIso", "Ideal ISO"],
    ["weight", "Weight"],
    ["price", "Price"],
  ];
}

export { getColumnDefs };
export type { ColumnDef };
