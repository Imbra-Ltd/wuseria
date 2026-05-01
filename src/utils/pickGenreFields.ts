import type { Lens } from "../types/lens";
import type { GenreLens } from "../components/interactive/GenreGuide/types";

function pickGenreFields(l: Lens): GenreLens {
  return {
    brand: l.brand,
    model: l.model,
    mount: l.mount,
    type: l.type,
    focalLengthMin: l.focalLengthMin,
    focalLengthMax: l.focalLengthMax,
    maxAperture: l.maxAperture,
    sweetSpotAperture: l.sweetSpotAperture,
    maxMagnification: l.maxMagnification,
    hasOis: l.hasOis,
    isWeatherSealed: l.isWeatherSealed,
    isDiscontinued: l.isDiscontinued,
    weight: l.weight,
    price: l.price,
    genreMarks: l.genreMarks,
    editorialPicks: l.editorialPicks,
    centerStopped: l.centerStopped,
    cornerStopped: l.cornerStopped,
    centerWideOpen: l.centerWideOpen,
    astigmatism: l.astigmatism,
    coma: l.coma,
    longitudinalCA: l.longitudinalCA,
    lateralCA: l.lateralCA,
    distortion: l.distortion,
    bokeh: l.bokeh,
    flareResistance: l.flareResistance,
  };
}

export { pickGenreFields };
