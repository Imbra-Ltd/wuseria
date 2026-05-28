// Minimal lenses.ts-shaped fixture for brandkit tests.
// Exercises: inline officialUrl, multiline officialUrl, a Tokina hyphen
// URL (for normalize_url), a brand with no officialUrl (must be skipped),
// and stored physical fields (for the #779 diff).
export const lenses = [
  {
    brand: "Tokina",
    model: "atx-m 23mm f/1.4 X",
    type: "prime",
    opticalElements: 11,
    opticalGroups: 10,
    weight: 276,
    diameter: 65,
    length: 72,
    filterThread: 52,
    maxMagnification: 0.1,
    apertureBlades: 9,
    minFocusDistance: 300,
    officialUrl: "https://tokinalens.com/product/atx-m-23mm-f1-4-x/",
  },
  {
    brand: "Tokina",
    model: "atx-m 33mm f/1.4 X",
    type: "prime",
    weight: 285,
    officialUrl: "https://tokinalens.com/product/atx-m-33mm-f1-4-x/",
  },
  {
    brand: "Sigma",
    model: "30mm f/1.4 DC DN | C",
    type: "prime",
    weight: 265,
    officialUrl: "https://www.sigma-global.com/en/lenses/c019_30_14/",
  },
  {
    brand: "Tokina",
    model: "Lens Without URL 50mm f/2",
    type: "prime",
    weight: 200,
  },
];
