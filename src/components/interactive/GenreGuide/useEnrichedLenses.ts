import { useMemo } from "react";
import type { GenreLens } from "./types";
import { getGenreMark, isEditorialPick } from "../../../utils/scoring";
import { astroExposure, handheldExposure } from "./exposure";
import type { EnrichedLens } from "./types";
import type { GenreState } from "./useGenreState";
import type { SortKey } from "./types";

type LensGetter = (el: EnrichedLens) => number;

const SORT_GETTERS: Record<string, LensGetter> = {
  mark: (el) => el.mark,
  idealIso: (el) => el.idealIso ?? 99999,
  weight: (el) => el.lens.weight,
  price: (el) => el.lens.price,
  fl: (el) => el.lens.focalLengthMin,
  aperture: (el) => el.lens.maxAperture,
  rule500: (el) => el.rule500 ?? 0,
  coma: (el) => el.lens.coma ?? -1,
  astigmatism: (el) => el.lens.astigmatism ?? -1,
  wr: (el) => (el.lens.isWeatherSealed ? 1 : 0),
  ois: (el) => (el.lens.hasOis ? 1 : 0),
  cornerStopped: (el) => el.lens.cornerStopped ?? -1,
  centerStopped: (el) => el.lens.centerStopped ?? -1,
  centerWideOpen: (el) => el.lens.centerWideOpen ?? -1,
  distortion: (el) => el.lens.distortion ?? -1,
  flareResistance: (el) => el.lens.flareResistance ?? -1,
  bokeh: (el) => el.lens.bokeh ?? -1,
  longitudinalCA: (el) => el.lens.longitudinalCA ?? -1,
  lateralCA: (el) => el.lens.lateralCA ?? -1,
  magnification: (el) => el.lens.maxMagnification ?? 0,
};

function compareLenses(
  a: EnrichedLens,
  b: EnrichedLens,
  sortBy: SortKey,
): number {
  if (sortBy === "brand") return a.lens.brand.localeCompare(b.lens.brand);
  const getter = SORT_GETTERS[sortBy];
  if (!getter) return 0;
  const v = getter(a) - getter(b);
  if (sortBy === "mark" && v === 0) {
    return (a.isPick ? 1 : 0) - (b.isPick ? 1 : 0);
  }
  return v;
}

interface GenreFilters {
  brandFilter: string;
  markFilter: string;
  priceFilter: string;
  weightFilter: string;
  apertureFilter: string;
  comaFilter: string;
  astigFilter: string;
  typeFilter: string;
  wrFilter: string;
  cornerFilter: string;
  distFilter: string;
  flareFilter: string;
  bokehFilter: string;
  locaFilter: string;
  latcaFilter: string;
}

function passesMinFilter(value: number | undefined, filter: string): boolean {
  if (!filter) return true;
  return value != null && value >= Number(filter);
}

function passesMaxFilter(value: number, filter: string): boolean {
  if (!filter) return true;
  return value <= Number(filter);
}

function passesExactFilter(value: string, filter: string): boolean {
  return !filter || value === filter;
}

function passesBooleanFilter(
  value: boolean | undefined,
  filter: string,
): boolean {
  if (filter === "yes") return !!value;
  if (filter === "no") return !value;
  return true;
}

function matchesGenreFilters(el: EnrichedLens, f: GenreFilters): boolean {
  return (
    passesExactFilter(el.lens.brand, f.brandFilter) &&
    passesMinFilter(el.mark, f.markFilter) &&
    passesMaxFilter(el.lens.price, f.priceFilter) &&
    passesMaxFilter(el.lens.weight, f.weightFilter) &&
    passesMaxFilter(el.lens.maxAperture, f.apertureFilter) &&
    passesMinFilter(el.lens.coma, f.comaFilter) &&
    passesMinFilter(el.lens.astigmatism, f.astigFilter) &&
    passesExactFilter(el.lens.type, f.typeFilter) &&
    passesBooleanFilter(el.lens.isWeatherSealed, f.wrFilter) &&
    passesMinFilter(el.lens.cornerStopped, f.cornerFilter) &&
    passesMinFilter(el.lens.distortion, f.distFilter) &&
    passesMinFilter(el.lens.flareResistance, f.flareFilter) &&
    passesMinFilter(el.lens.bokeh, f.bokehFilter) &&
    passesMinFilter(el.lens.longitudinalCA, f.locaFilter) &&
    passesMinFilter(el.lens.lateralCA, f.latcaFilter)
  );
}

function useEnrichedLenses(
  lenses: GenreLens[],
  state: GenreState,
): EnrichedLens[] {
  const {
    genre,
    cropFactor,
    ev,
    iso,
    selectedFl,
    magnification,
    sortBy,
    sortAsc,
    isNightscape,
    FL_RANGES,
    brandFilter,
    markFilter,
    priceFilter,
    weightFilter,
    apertureFilter,
    comaFilter,
    astigFilter,
    typeFilter,
    wrFilter,
    cornerFilter,
    distFilter,
    flareFilter,
    bokehFilter,
    locaFilter,
    latcaFilter,
  } = state;

  return useMemo(() => {
    const enriched: EnrichedLens[] = lenses
      .filter((l) => {
        const mark = getGenreMark(l, genre);
        if (mark == null) return false;
        if (l.isDiscontinued) return false;
        if (cropFactor === 0.79 ? l.mount !== "GFX" : l.mount !== "X")
          return false;
        const range = FL_RANGES[selectedFl];
        if (range) {
          if (l.focalLengthMax < range[0] || l.focalLengthMin > range[1])
            return false;
        }
        return true;
      })
      .map((l) => {
        const mark = getGenreMark(l, genre)!;
        const isPick = isEditorialPick(l, genre);
        const range = FL_RANGES[selectedFl];
        let effectiveFl = l.focalLengthMin;
        if (range && l.type === "zoom") {
          effectiveFl = Math.max(l.focalLengthMin, range[0]);
        }
        const macroMag = genre === "macro" ? magnification : undefined;
        const idealIso = isNightscape
          ? astroExposure(
              { ...l, focalLengthMin: effectiveFl } as GenreLens,
              ev,
              iso,
              cropFactor,
            ).idealIso
          : handheldExposure(l, genre, ev, cropFactor, macroMag).idealIso;
        const rule500 = isNightscape
          ? Math.round(500 / (cropFactor * effectiveFl))
          : null;

        return { lens: l, mark, isPick, idealIso, rule500, effectiveFl };
      });

    enriched.sort((a, b) => {
      const v = compareLenses(a, b, sortBy);
      return sortAsc ? v : -v;
    });

    const filters: GenreFilters = {
      brandFilter,
      markFilter,
      priceFilter,
      weightFilter,
      apertureFilter,
      comaFilter,
      astigFilter,
      typeFilter,
      wrFilter,
      cornerFilter,
      distFilter,
      flareFilter,
      bokehFilter,
      locaFilter,
      latcaFilter,
    };
    return enriched.filter((el) => matchesGenreFilters(el, filters));
  }, [
    lenses,
    genre,
    cropFactor,
    ev,
    iso,
    selectedFl,
    magnification,
    sortBy,
    sortAsc,
    isNightscape,
    brandFilter,
    markFilter,
    priceFilter,
    weightFilter,
    apertureFilter,
    comaFilter,
    astigFilter,
    typeFilter,
    wrFilter,
    cornerFilter,
    distFilter,
    flareFilter,
    bokehFilter,
    locaFilter,
    latcaFilter,
    FL_RANGES,
  ]);
}

export { useEnrichedLenses };
