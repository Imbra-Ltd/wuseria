import { useMemo } from "react";
import type { Lens } from "../../../types/lens";
import { getGenreMark, isEditorialPick } from "../../../utils/scoring";
import { astroExposure, handheldExposure } from "./exposure";
import type { EnrichedLens } from "./types";
import type { GenreState } from "./useGenreState";

function useEnrichedLenses(lenses: Lens[], state: GenreState): EnrichedLens[] {
  const {
    genre, cropFactor, ev, iso, selectedFl, magnification,
    sortBy, sortAsc, isNightscape, FL_RANGES,
    brandFilter, markFilter, priceFilter, weightFilter,
    apertureFilter, comaFilter, astigFilter, typeFilter,
    wrFilter, cornerFilter, distFilter, flareFilter,
    bokehFilter, locaFilter, latcaFilter,
  } = state;

  return useMemo(() => {
    const enriched: EnrichedLens[] = lenses
      .filter((l) => {
        const mark = getGenreMark(l, genre);
        if (mark == null) return false;
        if (l.isDiscontinued) return false;
        if (cropFactor === 0.79 ? l.mount !== "GFX" : l.mount !== "X") return false;
        const range = FL_RANGES[selectedFl];
        if (range) {
          if (l.focalLengthMax < range[0] || l.focalLengthMin > range[1]) return false;
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
        const idealIso = isNightscape
          ? astroExposure({ ...l, focalLengthMin: effectiveFl } as Lens, ev, iso, cropFactor).idealIso
          : handheldExposure(l, genre, ev, cropFactor, genre === "macro" ? magnification : undefined).idealIso;
        const rule500 = isNightscape
          ? Math.round(500 / (cropFactor * effectiveFl))
          : null;

        return { lens: l, mark, isPick, idealIso, rule500, effectiveFl };
      });

    enriched.sort((a, b) => {
      let v = 0;
      switch (sortBy) {
        case "mark":
          v = a.mark - b.mark;
          if (v === 0) v = (a.isPick ? 1 : 0) - (b.isPick ? 1 : 0);
          break;

        case "brand": v = a.lens.brand.localeCompare(b.lens.brand); break;
        case "idealIso": v = (a.idealIso ?? 99999) - (b.idealIso ?? 99999); break;
        case "weight": v = a.lens.weight - b.lens.weight; break;
        case "price": v = a.lens.price - b.lens.price; break;
        case "fl": v = a.lens.focalLengthMin - b.lens.focalLengthMin; break;
        case "aperture": v = a.lens.maxAperture - b.lens.maxAperture; break;
        case "rule500": v = (a.rule500 ?? 0) - (b.rule500 ?? 0); break;
        case "coma": v = (a.lens.coma ?? -1) - (b.lens.coma ?? -1); break;
        case "astigmatism": v = (a.lens.astigmatism ?? -1) - (b.lens.astigmatism ?? -1); break;
        case "wr": v = (a.lens.isWeatherSealed ? 1 : 0) - (b.lens.isWeatherSealed ? 1 : 0); break;
        case "ois": v = (a.lens.hasOis ? 1 : 0) - (b.lens.hasOis ? 1 : 0); break;
        case "cornerStopped": v = (a.lens.cornerStopped ?? -1) - (b.lens.cornerStopped ?? -1); break;
        case "centerStopped": v = (a.lens.centerStopped ?? -1) - (b.lens.centerStopped ?? -1); break;
        case "centerWideOpen": v = (a.lens.centerWideOpen ?? -1) - (b.lens.centerWideOpen ?? -1); break;
        case "distortion": v = (a.lens.distortion ?? -1) - (b.lens.distortion ?? -1); break;
        case "flareResistance": v = (a.lens.flareResistance ?? -1) - (b.lens.flareResistance ?? -1); break;
        case "bokeh": v = (a.lens.bokeh ?? -1) - (b.lens.bokeh ?? -1); break;
        case "longitudinalCA": v = (a.lens.longitudinalCA ?? -1) - (b.lens.longitudinalCA ?? -1); break;
        case "lateralCA": v = (a.lens.lateralCA ?? -1) - (b.lens.lateralCA ?? -1); break;
        case "magnification": v = (a.lens.maxMagnification ?? 0) - (b.lens.maxMagnification ?? 0); break;
      }
      return sortAsc ? v : -v;
    });

    return enriched.filter((el) => {
      if (brandFilter && el.lens.brand !== brandFilter) return false;
      if (markFilter && el.mark < Number(markFilter)) return false;
      if (priceFilter && el.lens.price > Number(priceFilter)) return false;
      if (weightFilter && el.lens.weight > Number(weightFilter)) return false;
      if (apertureFilter && el.lens.maxAperture > Number(apertureFilter)) return false;
      if (comaFilter && (el.lens.coma == null || el.lens.coma < Number(comaFilter))) return false;
      if (astigFilter && (el.lens.astigmatism == null || el.lens.astigmatism < Number(astigFilter))) return false;
      if (typeFilter && el.lens.type !== typeFilter) return false;
      if (wrFilter === "yes" && !el.lens.isWeatherSealed) return false;
      if (wrFilter === "no" && el.lens.isWeatherSealed) return false;
      if (cornerFilter && (el.lens.cornerStopped == null || el.lens.cornerStopped < Number(cornerFilter))) return false;
      if (distFilter && (el.lens.distortion == null || el.lens.distortion < Number(distFilter))) return false;
      if (flareFilter && (el.lens.flareResistance == null || el.lens.flareResistance < Number(flareFilter))) return false;
      if (bokehFilter && (el.lens.bokeh == null || el.lens.bokeh < Number(bokehFilter))) return false;
      if (locaFilter && (el.lens.longitudinalCA == null || el.lens.longitudinalCA < Number(locaFilter))) return false;
      if (latcaFilter && (el.lens.lateralCA == null || el.lens.lateralCA < Number(latcaFilter))) return false;
      return true;
    });
  }, [lenses, genre, cropFactor, ev, iso, selectedFl, magnification, sortBy, sortAsc, isNightscape, brandFilter, markFilter, priceFilter, weightFilter, apertureFilter, comaFilter, astigFilter, typeFilter, wrFilter, cornerFilter, distFilter, flareFilter, bokehFilter, locaFilter, latcaFilter, FL_RANGES]);
}

export { useEnrichedLenses };
