import type { MtfData } from "../types/mtf";

const mtfReadings: Record<string, MtfData> = {
  "sigma-12mm-f1-4-dc-dn-c": {
    source: "https://www.sigma-global.com/en/lenses/c025_12_14/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.89, M: 0.89 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.88, M: 0.88 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.88, M: 0.87 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.88, M: 0.86 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.87, M: 0.84 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.86, M: 0.83 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.85, M: 0.81 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.97, M: 0.96 },
              30: { S: 0.81, M: 0.79 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.75, M: 0.78 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.94, M: 0.95 },
              30: { S: 0.68, M: 0.74 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.93, M: 0.91 },
              30: { S: 0.67, M: 0.62 },
            },
          },
        ],
      },
    ],
  },
  "sigma-15mm-f1-4-dc-dn-c": {
    source: "https://www.sigma-global.com/en/lenses/c026_15_14/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.86, M: 0.86 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.86, M: 0.86 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.86, M: 0.86 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.86, M: 0.85 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.86, M: 0.84 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.97, M: 0.96 },
              30: { S: 0.84, M: 0.82 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.82, M: 0.8 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.78, M: 0.77 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.95, M: 0.96 },
              30: { S: 0.74, M: 0.72 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.93, M: 0.95 },
              30: { S: 0.69, M: 0.68 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.93, M: 0.92 },
              30: { S: 0.68, M: 0.59 },
            },
          },
        ],
      },
    ],
  },
  "sigma-16mm-f1-4-dc-dn-c": {
    source: "https://www.sigma-global.com/en/lenses/c017_16_14/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.81, M: 0.79 },
            },
          },
          {
            position: 2.5,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.82, M: 0.79 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.82, M: 0.77 },
            },
          },
          {
            position: 7.5,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.78, M: 0.74 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.93, M: 0.95 },
              30: { S: 0.68, M: 0.72 },
            },
          },
          {
            position: 12.5,
            samples: {
              10: { S: 0.83, M: 0.93 },
              30: { S: 0.59, M: 0.64 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.71, M: 0.89 },
              30: { S: 0.5, M: 0.56 },
            },
          },
        ],
      },
    ],
  },
  "sigma-23mm-f1-4-dc-dn-c": {
    source: "https://www.sigma-global.com/en/lenses/c023_23_14/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.85, M: 0.85 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.84, M: 0.83 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.83, M: 0.82 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.81, M: 0.8 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.78, M: 0.8 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.96, M: 0.97 },
              30: { S: 0.76, M: 0.8 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.96, M: 0.97 },
              30: { S: 0.76, M: 0.81 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.96, M: 0.97 },
              30: { S: 0.78, M: 0.81 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.95, M: 0.96 },
              30: { S: 0.75, M: 0.79 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.91, M: 0.95 },
              30: { S: 0.62, M: 0.77 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.82, M: 0.92 },
              30: { S: 0.43, M: 0.68 },
            },
          },
        ],
      },
    ],
  },
  "sigma-56mm-f1-4-dc-dn-c": {
    source: "https://www.sigma-global.com/en/lenses/c018_56_14/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.86, M: 0.86 },
            },
          },
          {
            position: 2.5,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.87, M: 0.87 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.86, M: 0.86 },
            },
          },
          {
            position: 7.5,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.81, M: 0.85 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.8, M: 0.86 },
            },
          },
          {
            position: 12.5,
            samples: {
              10: { S: 0.91, M: 0.95 },
              30: { S: 0.61, M: 0.74 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.72, M: 0.93 },
              30: { S: 0.36, M: 0.61 },
            },
          },
        ],
      },
    ],
  },
  "sigma-10-18mm-f2-8-dc-dn-c": {
    source: "https://www.sigma-global.com/en/lenses/c023_10_28/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        focalLength: 10,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.93, M: 0.93 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.92, M: 0.92 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.92, M: 0.9 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.91, M: 0.88 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.88, M: 0.87 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.86, M: 0.85 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.97, M: 0.96 },
              30: { S: 0.87, M: 0.82 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.97, M: 0.95 },
              30: { S: 0.88, M: 0.76 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.97, M: 0.94 },
              30: { S: 0.87, M: 0.73 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.97, M: 0.93 },
              30: { S: 0.85, M: 0.7 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.96, M: 0.91 },
              30: { S: 0.78, M: 0.6 },
            },
          },
        ],
      },
      {
        aperture: "f/2.8",
        focalLength: 18,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: null, M: null },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.91, M: 0.9 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.91, M: 0.88 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.9, M: 0.86 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.9, M: 0.86 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.97, M: 0.96 },
              30: { S: 0.89, M: 0.85 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.97, M: 0.96 },
              30: { S: 0.86, M: 0.84 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.96, M: 0.95 },
              30: { S: 0.81, M: 0.78 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.94, M: 0.93 },
              30: { S: 0.71, M: 0.68 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.92, M: 0.91 },
              30: { S: 0.59, M: 0.56 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.86, M: 0.87 },
              30: { S: 0.43, M: 0.43 },
            },
          },
        ],
      },
    ],
  },
  "sigma-16-300mm-f3-5-6-7-dc-os-c": {
    source: "https://www.sigma-global.com/en/lenses/c025_16_300/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/3.5",
        focalLength: 16,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.86, M: 0.86 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.85, M: 0.78 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.96, M: 0.94 },
              30: { S: 0.84, M: 0.73 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.96, M: 0.93 },
              30: { S: 0.83, M: 0.67 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.96, M: 0.93 },
              30: { S: 0.84, M: 0.66 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.96, M: 0.93 },
              30: { S: 0.84, M: 0.65 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.96, M: 0.91 },
              30: { S: 0.82, M: 0.6 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.95, M: 0.88 },
              30: { S: 0.78, M: 0.54 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.94, M: 0.85 },
              30: { S: 0.74, M: 0.46 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.92, M: 0.81 },
              30: { S: 0.69, M: 0.37 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.9, M: 0.74 },
              30: { S: 0.64, M: 0.45 },
            },
          },
        ],
      },
      {
        aperture: "f/3.5",
        focalLength: 300,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.84, M: 0.84 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.95, M: 0.94 },
              30: { S: 0.83, M: 0.76 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.95, M: 0.92 },
              30: { S: 0.81, M: 0.71 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.94, M: 0.89 },
              30: { S: 0.79, M: 0.63 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.93, M: 0.88 },
              30: { S: 0.76, M: 0.55 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.92, M: 0.85 },
              30: { S: 0.72, M: 0.48 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.91, M: 0.83 },
              30: { S: 0.69, M: 0.46 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.9, M: 0.81 },
              30: { S: 0.67, M: 0.44 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.9, M: 0.77 },
              30: { S: 0.67, M: 0.42 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.9, M: 0.75 },
              30: { S: 0.67, M: 0.41 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.89, M: 0.67 },
              30: { S: 0.67, M: 0.41 },
            },
          },
        ],
      },
    ],
  },
  "sigma-17-40mm-f1-8-dc-art": {
    source: "https://www.sigma-global.com/en/lenses/a025_17_40/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.8",
        focalLength: 17,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.94, M: 0.94 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.94, M: 0.92 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.93, M: 0.9 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.92, M: 0.87 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.92, M: 0.87 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.9, M: 0.87 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.98, M: 0.96 },
              30: { S: 0.87, M: 0.8 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.96, M: 0.95 },
              30: { S: 0.81, M: 0.71 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.92, M: 0.94 },
              30: { S: 0.69, M: 0.66 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.86, M: 0.93 },
              30: { S: 0.56, M: 0.56 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.8, M: 0.89 },
              30: { S: 0.52, M: 0.5 },
            },
          },
        ],
      },
      {
        aperture: "f/1.8",
        focalLength: 40,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.91, M: 0.91 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.91, M: 0.89 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.9, M: 0.86 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.9, M: 0.84 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.89, M: 0.83 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.87, M: 0.81 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.86, M: 0.82 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.98, M: 0.96 },
              30: { S: 0.85, M: 0.81 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.97, M: 0.95 },
              30: { S: 0.84, M: 0.77 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.97, M: 0.94 },
              30: { S: 0.84, M: 0.72 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.96, M: 0.92 },
              30: { S: 0.82, M: 0.65 },
            },
          },
        ],
      },
    ],
  },
  "sigma-18-50mm-f2-8-dc-dn-c": {
    source: "https://www.sigma-global.com/en/lenses/c021_18_50/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        focalLength: 18,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.86, M: 0.86 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.97, M: 0.96 },
              30: { S: 0.84, M: 0.83 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.96, M: 0.95 },
              30: { S: 0.83, M: 0.79 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.96, M: 0.94 },
              30: { S: 0.81, M: 0.75 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.95, M: 0.93 },
              30: { S: 0.78, M: 0.73 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.95, M: 0.92 },
              30: { S: 0.75, M: 0.69 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.94, M: 0.92 },
              30: { S: 0.73, M: 0.67 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.94, M: 0.91 },
              30: { S: 0.72, M: 0.65 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.94, M: 0.9 },
              30: { S: 0.73, M: 0.62 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.93, M: 0.88 },
              30: { S: 0.74, M: 0.59 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.92, M: 0.84 },
              30: { S: 0.73, M: 0.5 },
            },
          },
        ],
      },
      {
        aperture: "f/2.8",
        focalLength: 50,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.87, M: 0.87 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.97, M: 0.96 },
              30: { S: 0.87, M: 0.86 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.97, M: 0.96 },
              30: { S: 0.88, M: 0.85 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.97, M: 0.96 },
              30: { S: 0.87, M: 0.82 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.97, M: 0.96 },
              30: { S: 0.85, M: 0.8 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.96, M: 0.95 },
              30: { S: 0.82, M: 0.75 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.95, M: 0.94 },
              30: { S: 0.78, M: 0.71 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.73, M: 0.68 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.91, M: 0.92 },
              30: { S: 0.68, M: 0.62 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.89, M: 0.9 },
              30: { S: 0.64, M: 0.55 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.91, M: 0.86 },
              30: { S: 0.68, M: 0.46 },
            },
          },
        ],
      },
    ],
  },
  "sigma-100-400mm-f5-6-3-dg-dn-os-c": {
    source: "https://www.sigma-global.com/en/lenses/c020_100_400/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/5",
        focalLength: 100,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.79, M: 0.79 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.79, M: 0.79 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.79, M: 0.79 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.79, M: 0.79 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.79, M: 0.78 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.79, M: 0.78 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.95, M: 0.94 },
              30: { S: 0.8, M: 0.77 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.95, M: 0.94 },
              30: { S: 0.8, M: 0.77 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.95, M: 0.93 },
              30: { S: 0.8, M: 0.76 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.94, M: 0.93 },
              30: { S: 0.8, M: 0.75 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.94, M: 0.92 },
              30: { S: 0.79, M: 0.72 },
            },
          },
        ],
      },
      {
        aperture: "f/5",
        focalLength: 400,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.84, M: 0.84 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.84, M: 0.84 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.84, M: 0.82 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.95, M: 0.94 },
              30: { S: 0.84, M: 0.81 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.95, M: 0.94 },
              30: { S: 0.83, M: 0.8 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.95, M: 0.94 },
              30: { S: 0.83, M: 0.78 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.95, M: 0.93 },
              30: { S: 0.83, M: 0.76 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.95, M: 0.93 },
              30: { S: 0.82, M: 0.75 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.95, M: 0.92 },
              30: { S: 0.82, M: 0.72 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.95, M: 0.92 },
              30: { S: 0.82, M: 0.7 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.95, M: 0.91 },
              30: { S: 0.82, M: 0.68 },
            },
          },
        ],
      },
    ],
  },

  "samyang-100mm-f2-8-ed-umc-macro": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=154",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.92, M: 0.92 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.9, M: 0.9 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.97, M: 0.96 },
              30: { S: 0.88, M: 0.82 },
            },
          },
          {
            position: 15,
            samples: {
              10: { S: 0.98, M: 0.95 },
              30: { S: 0.9, M: 0.8 },
            },
          },
          {
            position: 20,
            samples: {
              10: { S: 0.95, M: 0.94 },
              30: { S: 0.77, M: 0.67 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.98, M: 0.97 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.95, M: 0.95 },
            },
          },
          {
            position: 15,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.93, M: 0.9 },
            },
          },
          {
            position: 20,
            samples: {
              10: { S: 0.99, M: 0.95 },
              30: { S: 0.95, M: 0.78 },
            },
          },
        ],
      },
    ],
  },
  "samyang-10mm-f2-8-ed-as-ncs-cs": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=343",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.98, M: 0.97 },
            },
          },
          {
            position: 2,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.97, M: 0.97 },
            },
          },
          {
            position: 4,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.97, M: 0.85 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.97, M: 0.81 },
            },
          },
          {
            position: 8,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.97, M: 0.78 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.99, M: 0.96 },
              30: { S: 0.95, M: 0.74 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.89, M: 0.67 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.74, M: 0.54 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 2,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.97, M: 0.97 },
            },
          },
          {
            position: 4,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.99, M: 0.94 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.99, M: 0.89 },
            },
          },
          {
            position: 8,
            samples: {
              10: { S: 0.99, M: 0.97 },
              30: { S: 0.99, M: 0.83 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.99, M: 0.96 },
              30: { S: 0.99, M: 0.76 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.99, M: 0.94 },
              30: { S: 0.98, M: 0.67 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.99, M: 0.89 },
              30: { S: 0.98, M: 0.57 },
            },
          },
        ],
      },
    ],
  },
  "samyang-12mm-f2-0-ncs-cs": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=351",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.91, M: 0.91 },
            },
          },
          {
            position: 2,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.91, M: 0.88 },
            },
          },
          {
            position: 4,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.91, M: 0.82 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.98, M: 0.95 },
              30: { S: 0.91, M: 0.74 },
            },
          },
          {
            position: 8,
            samples: {
              10: { S: 0.98, M: 0.94 },
              30: { S: 0.88, M: 0.67 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.97, M: 0.95 },
              30: { S: 0.76, M: 0.66 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.92, M: 0.91 },
              30: { S: 0.6, M: 0.56 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.77, M: 0.76 },
              30: { S: 0.47, M: 0.26 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.97, M: 0.98 },
            },
          },
          {
            position: 2,
            samples: {
              10: { S: 1, M: 0.98 },
              30: { S: 0.99, M: 0.97 },
            },
          },
          {
            position: 4,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.99, M: 0.94 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.98, M: 0.99 },
              30: { S: 0.96, M: 0.87 },
            },
          },
          {
            position: 8,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.94, M: 0.79 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.98, M: 0.99 },
              30: { S: 0.94, M: 0.72 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.95, M: 0.56 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.98, M: 0.74 },
              30: { S: 0.97, M: 0.23 },
            },
          },
        ],
      },
    ],
  },
  "samyang-12mm-f2-8-ed-as-ncs-fish-eye": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=190",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.98, M: 0.97 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.96, M: 0.88 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.98, M: 0.96 },
              30: { S: 0.93, M: 0.93 },
            },
          },
          {
            position: 15,
            samples: {
              10: { S: 0.97, M: 0.96 },
              30: { S: 0.82, M: 0.82 },
            },
          },
          {
            position: 20,
            samples: {
              10: { S: 0.94, M: 0.93 },
              30: { S: 0.71, M: 0.46 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.92, M: 0.92 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.99, M: 0.96 },
              30: { S: 0.75, M: 0.75 },
            },
          },
          {
            position: 15,
            samples: {
              10: { S: 0.99, M: 0.92 },
              30: { S: 0.98, M: 0.52 },
            },
          },
          {
            position: 20,
            samples: {
              10: { S: 0.98, M: 0.86 },
              30: { S: 0.91, M: 0.44 },
            },
          },
        ],
      },
    ],
  },
  "samyang-135mm-f2-0-ed-umc": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=167",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.98, M: 0.99 },
              30: { S: 0.93, M: 0.93 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 0.98, M: 0.99 },
              30: { S: 0.93, M: 0.92 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.93, M: 0.92 },
            },
          },
          {
            position: 15,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.91, M: 0.91 },
            },
          },
          {
            position: 20,
            samples: {
              10: { S: 0.97, M: 0.98 },
              30: { S: 0.82, M: 0.87 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.94, M: 0.93 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.94, M: 0.94 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.94, M: 0.92 },
            },
          },
          {
            position: 15,
            samples: {
              10: { S: 0.98, M: 0.99 },
              30: { S: 0.91, M: 0.91 },
            },
          },
          {
            position: 20,
            samples: {
              10: { S: 0.97, M: 0.98 },
              30: { S: 0.83, M: 0.87 },
            },
          },
        ],
      },
    ],
  },
  "samyang-14mm-f2-8-ed-as-if-umc": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=148",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.96, M: 0.96 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 0.99, M: 0.97 },
              30: { S: 0.94, M: 0.78 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.99, M: 0.97 },
              30: { S: 0.94, M: 0.82 },
            },
          },
          {
            position: 15,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.93, M: 0.9 },
            },
          },
          {
            position: 20,
            samples: {
              10: { S: 0.95, M: 0.97 },
              30: { S: 0.7, M: 0.81 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.97, M: 0.96 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.94, M: 0.94 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.92, M: 0.92 },
            },
          },
          {
            position: 15,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.89, M: 0.89 },
            },
          },
          {
            position: 20,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.93, M: 0.93 },
            },
          },
        ],
      },
    ],
  },
  "samyang-16mm-f2-0-ed-as-umc-cs": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=354",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.97, M: 0.98 },
            },
          },
          {
            position: 2,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.97, M: 0.98 },
            },
          },
          {
            position: 4,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.96, M: 0.95 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.95, M: 0.95 },
            },
          },
          {
            position: 8,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.9, M: 0.91 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.96, M: 0.97 },
              30: { S: 0.82, M: 0.8 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.92, M: 0.96 },
              30: { S: 0.68, M: 0.75 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.85, M: 0.95 },
              30: { S: 0.56, M: 0.67 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 2,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 4,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.98, M: 0.96 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 8,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.99, M: 0.97 },
              30: { S: 0.98, M: 0.85 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.99, M: 0.97 },
              30: { S: 0.98, M: 0.79 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.99, M: 0.95 },
              30: { S: 0.99, M: 0.67 },
            },
          },
        ],
      },
    ],
  },
  "samyang-20mm-f1-8-ed-as-umc": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=161",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.95, M: 0.94 },
              30: { S: 0.75, M: 0.75 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.71, M: 0.64 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.94, M: 0.92 },
              30: { S: 0.68, M: 0.62 },
            },
          },
          {
            position: 15,
            samples: {
              10: { S: 0.89, M: 0.92 },
              30: { S: 0.57, M: 0.61 },
            },
          },
          {
            position: 20,
            samples: {
              10: { S: 0.61, M: 0.78 },
              30: { S: 0.34, M: 0.4 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.97, M: 0.96 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 0.99, M: 1 },
              30: { S: 0.99, M: 0.82 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.95, M: 0.64 },
            },
          },
          {
            position: 15,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.92, M: 0.57 },
            },
          },
          {
            position: 20,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.92, M: 0.42 },
            },
          },
        ],
      },
    ],
  },
  "samyang-21mm-f1-4-ed-as-umc-cs": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=378",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.98, M: 0.99 },
              30: { S: 0.89, M: 0.88 },
            },
          },
          {
            position: 2,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.9, M: 0.89 },
            },
          },
          {
            position: 4,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.91, M: 0.89 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.9, M: 0.88 },
            },
          },
          {
            position: 8,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.89, M: 0.86 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.87, M: 0.87 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.86, M: 0.86 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.83, M: 0.83 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 2,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.98, M: 0.97 },
            },
          },
          {
            position: 4,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.98, M: 0.96 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.98, M: 0.95 },
            },
          },
          {
            position: 8,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.98, M: 0.93 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.98, M: 0.9 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.99, M: 0.97 },
              30: { S: 0.98, M: 0.87 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.99, M: 0.97 },
              30: { S: 0.98, M: 0.87 },
            },
          },
        ],
      },
    ],
  },
  "samyang-300mm-f6-3-ed-umc-cs-reflex": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=170",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/6.3",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.98, M: 0.99 },
              30: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 2,
            samples: {
              10: { S: 0.98, M: 0.99 },
              30: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 4,
            samples: {
              10: { S: 0.98, M: 0.99 },
              30: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.98, M: 0.99 },
              30: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 8,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.97, M: 0.97 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 1 },
              30: { S: 0.99, M: 0.99 },
            },
          },
          {
            position: 2,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.99, M: 0.99 },
            },
          },
          {
            position: 4,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.99, M: 0.99 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.99, M: 0.99 },
            },
          },
          {
            position: 8,
            samples: {
              10: { S: 0.99, M: 1 },
              30: { S: 0.99, M: 0.99 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.99, M: 1 },
              30: { S: 0.99, M: 0.99 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 1, M: 1 },
              30: { S: 0.99, M: 0.99 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 1, M: 1 },
              30: { S: 0.99, M: 0.98 },
            },
          },
        ],
      },
    ],
  },
  "samyang-35mm-f1-2-ed-as-umc-cs": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=381",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.2",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.87, M: 0.87 },
            },
          },
          {
            position: 2,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.87, M: 0.84 },
            },
          },
          {
            position: 4,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.86, M: 0.83 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.84, M: 0.85 },
            },
          },
          {
            position: 8,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.82, M: 0.85 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.97, M: 0.96 },
              30: { S: 0.82, M: 0.8 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.97, M: 0.95 },
              30: { S: 0.82, M: 0.81 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.96, M: 0.93 },
              30: { S: 0.77, M: 0.73 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 2,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 4,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.98, M: 0.97 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.97, M: 0.97 },
            },
          },
          {
            position: 8,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.95, M: 0.94 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.95, M: 0.94 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.95, M: 0.94 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.97, M: 0.95 },
            },
          },
        ],
      },
    ],
  },
  "samyang-35mm-f1-4-as-umc": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=159",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.91, M: 0.91 },
              30: { S: 0.71, M: 0.71 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 0.92, M: 0.93 },
              30: { S: 0.71, M: 0.71 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.74, M: 0.74 },
            },
          },
          {
            position: 15,
            samples: {
              10: { S: 0.92, M: 0.91 },
              30: { S: 0.71, M: 0.71 },
            },
          },
          {
            position: 20,
            samples: {
              10: { S: 0.76, M: 0.87 },
              30: { S: 0.46, M: 0.58 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.98, M: 0.99 },
              30: { S: 0.91, M: 0.9 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.92, M: 0.85 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.99, M: 0.96 },
              30: { S: 0.96, M: 0.95 },
            },
          },
          {
            position: 15,
            samples: {
              10: { S: 0.99, M: 0.96 },
              30: { S: 0.97, M: 0.72 },
            },
          },
          {
            position: 20,
            samples: {
              10: { S: 0.99, M: 0.94 },
              30: { S: 0.92, M: 0.71 },
            },
          },
        ],
      },
    ],
  },
  "samyang-50mm-f1-2-as-umc-cs": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=384",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.2",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.81, M: 0.8 },
            },
          },
          {
            position: 2,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.81, M: 0.76 },
            },
          },
          {
            position: 4,
            samples: {
              10: { S: 0.96, M: 0.95 },
              30: { S: 0.8, M: 0.75 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.96, M: 0.95 },
              30: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 8,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.76, M: 0.76 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.8, M: 0.81 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.95, M: 0.96 },
              30: { S: 0.81, M: 0.78 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.93, M: 0.94 },
              30: { S: 0.73, M: 0.74 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.98, M: 0.99 },
              30: { S: 0.97, M: 0.96 },
            },
          },
          {
            position: 2,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.97, M: 0.93 },
            },
          },
          {
            position: 4,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.97, M: 0.92 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.97, M: 0.93 },
            },
          },
          {
            position: 8,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.98, M: 0.95 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.98, M: 0.91 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.97, M: 0.85 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.99, M: 0.96 },
              30: { S: 0.97, M: 0.82 },
            },
          },
        ],
      },
    ],
  },
  "samyang-50mm-f1-4-as-umc": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=155",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.9, M: 0.9 },
              30: { S: 0.73, M: 0.74 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 0.91, M: 0.91 },
              30: { S: 0.66, M: 0.55 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.92, M: 0.85 },
              30: { S: 0.49, M: 0.42 },
            },
          },
          {
            position: 15,
            samples: {
              10: { S: 0.96, M: 0.86 },
              30: { S: 0.55, M: 0.47 },
            },
          },
          {
            position: 20,
            samples: {
              10: { S: 0.75, M: 0.91 },
              30: { S: 0.5, M: 0.54 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.93, M: 0.92 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.97, M: 0.88 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.96, M: 0.88 },
            },
          },
          {
            position: 15,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.94, M: 0.81 },
            },
          },
          {
            position: 20,
            samples: {
              10: { S: 0.99, M: 0.89 },
              30: { S: 0.94, M: 0.48 },
            },
          },
        ],
      },
    ],
  },
  "samyang-85mm-f1-4-as-if-umc": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=149",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.9, M: 0.9 },
              30: { S: 0.69, M: 0.69 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 0.91, M: 0.9 },
              30: { S: 0.69, M: 0.66 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.91, M: 0.92 },
              30: { S: 0.62, M: 0.64 },
            },
          },
          {
            position: 15,
            samples: {
              10: { S: 0.91, M: 0.94 },
              30: { S: 0.56, M: 0.6 },
            },
          },
          {
            position: 20,
            samples: {
              10: { S: 0.84, M: 0.93 },
              30: { S: 0.55, M: 0.57 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 1 },
              30: { S: 0.95, M: 0.95 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 1, M: 0.99 },
              30: { S: 0.96, M: 0.91 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 1, M: 1 },
              30: { S: 0.97, M: 0.96 },
            },
          },
          {
            position: 15,
            samples: {
              10: { S: 0.99, M: 0.96 },
              30: { S: 0.96, M: 0.73 },
            },
          },
          {
            position: 20,
            samples: {
              10: { S: 0.99, M: 0.94 },
              30: { S: 0.96, M: 0.63 },
            },
          },
        ],
      },
    ],
  },
  "samyang-8mm-f2-8-ed-as-if-umc-fisheye": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=339",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.93, M: 0.93 },
            },
          },
          {
            position: 2,
            samples: {
              10: { S: 0.98, M: 0.99 },
              30: { S: 0.95, M: 0.92 },
            },
          },
          {
            position: 4,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.94, M: 0.9 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.97, M: 0.98 },
              30: { S: 0.89, M: 0.9 },
            },
          },
          {
            position: 8,
            samples: {
              10: { S: 0.96, M: 0.97 },
              30: { S: 0.81, M: 0.84 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.95, M: 0.96 },
              30: { S: 0.73, M: 0.79 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.93, M: 0.95 },
              30: { S: 0.65, M: 0.73 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.91, M: 0.94 },
              30: { S: 0.61, M: 0.66 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.99, M: 0.98 },
            },
          },
          {
            position: 2,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.99, M: 0.96 },
            },
          },
          {
            position: 4,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.99, M: 0.94 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.99, M: 0.91 },
            },
          },
          {
            position: 8,
            samples: {
              10: { S: 0.99, M: 0.97 },
              30: { S: 0.98, M: 0.87 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.99, M: 0.97 },
              30: { S: 0.98, M: 0.82 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.99, M: 0.96 },
              30: { S: 0.98, M: 0.77 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 1, M: 0.95 },
              30: { S: 0.97, M: 0.69 },
            },
          },
        ],
      },
    ],
  },
  "samyang-8mm-f3-5-aspherical-if-mc-fish-eye": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=335",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/3.5",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.94, M: 0.93 },
              30: { S: 0.75, M: 0.76 },
            },
          },
          {
            position: 2,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.77, M: 0.75 },
            },
          },
          {
            position: 4,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.78, M: 0.75 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.79, M: 0.74 },
            },
          },
          {
            position: 8,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.77, M: 0.7 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.72, M: 0.73 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.92, M: 0.89 },
              30: { S: 0.65, M: 0.5 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.9, M: 0.9 },
              30: { S: 0.6, M: 0.47 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.94, M: 0.95 },
            },
          },
          {
            position: 2,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.96, M: 0.93 },
            },
          },
          {
            position: 4,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.98, M: 0.9 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.99, M: 0.97 },
              30: { S: 0.99, M: 0.83 },
            },
          },
          {
            position: 8,
            samples: {
              10: { S: 0.99, M: 0.95 },
              30: { S: 0.98, M: 0.73 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.98, M: 0.94 },
              30: { S: 0.93, M: 0.61 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.97, M: 0.9 },
              30: { S: 0.88, M: 0.5 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.97, M: 0.86 },
              30: { S: 0.87, M: 0.42 },
            },
          },
        ],
      },
    ],
  },
  "samyang-af-12mm-f2-0": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=466",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.0",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.91, M: 0.91 },
            },
          },
          {
            position: 3,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.91, M: 0.91 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.98, M: 0.96 },
              30: { S: 0.88, M: 0.88 },
            },
          },
          {
            position: 9,
            samples: {
              10: { S: 0.98, M: 0.96 },
              30: { S: 0.83, M: 0.68 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.9, M: 0.91 },
              30: { S: 0.67, M: 0.67 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.75, M: 0.75 },
              30: { S: 0.46, M: 0.24 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 1, M: 0.99 },
              30: { S: 1, M: 0.99 },
            },
          },
          {
            position: 3,
            samples: {
              10: { S: 1, M: 0.99 },
              30: { S: 1, M: 0.93 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 1, M: 0.98 },
              30: { S: 0.99, M: 0.86 },
            },
          },
          {
            position: 9,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.97, M: 0.77 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 1, M: 0.6 },
              30: { S: 0.99, M: 0.09 },
            },
          },
        ],
      },
    ],
  },
  "samyang-af-75mm-f1-8": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=470",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.98, M: 0.97 },
              30: { S: 0.87, M: 0.86 },
            },
          },
          {
            position: 3,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.84, M: 0.84 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.79, M: 0.8 },
            },
          },
          {
            position: 9,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.73, M: 0.74 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.89, M: 0.92 },
              30: { S: 0.68, M: 0.69 },
            },
          },
          {
            position: 14.5,
            samples: {
              10: { S: 0.84, M: 0.93 },
              30: { S: 0.66, M: 0.66 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.97, M: 0.96 },
            },
          },
          {
            position: 3,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.97, M: 0.97 },
            },
          },
          {
            position: 6,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.98, M: 0.96 },
            },
          },
          {
            position: 9,
            samples: {
              10: { S: 0.99, M: 1 },
              30: { S: 0.99, M: 0.95 },
            },
          },
          {
            position: 12,
            samples: {
              10: { S: 0.99, M: 1 },
              30: { S: 0.99, M: 0.93 },
            },
          },
          {
            position: 14.5,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.98, M: 0.91 },
            },
          },
        ],
      },
    ],
  },
  "samyang-tiltshift-24mm-f3-5-ed-as-umc": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=162",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/3.5",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.95, M: 0.94 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 0.98, M: 0.99 },
              30: { S: 0.93, M: 0.93 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.98, M: 0.98 },
              30: { S: 0.86, M: 0.77 },
            },
          },
          {
            position: 15,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.69, M: 0.68 },
            },
          },
          {
            position: 20,
            samples: {
              10: { S: 0.87, M: 0.94 },
              30: { S: 0.54, M: 0.67 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.97, M: 0.98 },
            },
          },
          {
            position: 5,
            samples: {
              10: { S: 0.99, M: 1 },
              30: { S: 0.97, M: 0.94 },
            },
          },
          {
            position: 10,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.96, M: 0.97 },
            },
          },
          {
            position: 15,
            samples: {
              10: { S: 0.99, M: 0.99 },
              30: { S: 0.96, M: 0.78 },
            },
          },
          {
            position: 20,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.94, M: 0.79 },
            },
          },
        ],
      },
    ],
  },
  "tokina-atx-m-11-18mm-f2-8-x": {
    source: "https://tokinalens.com/product/atx_m_11_18mm_f2_8_x/",
    mtfType: "measured",
    charts: [
      {
        aperture: "f/2.8 @ 11mm",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: null, M: null },
              30: { S: 0.99, M: null },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: null, M: 0.96 },
              30: { S: 0.98, M: null },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: null, M: 0.9 },
              30: { S: 0.94, M: null },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: null, M: 0.89 },
              30: { S: 0.88, M: null },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 1, M: 0.89 },
              30: { S: 0.84, M: null },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 1, M: 0.97 },
              30: { S: 0.83, M: null },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 1, M: 0.95 },
              30: { S: 0.85, M: null },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 1, M: 0.92 },
              30: { S: 0.84, M: 0.59 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.98, M: 0.91 },
              30: { S: 0.76, M: 0.54 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.93, M: 0.88 },
              30: { S: 0.6, M: 0.48 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.82, M: 0.86 },
              30: { S: 0.43, M: 0.39 },
            },
          },
        ],
      },
      {
        aperture: "f/2.8 @ 18mm",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: null, M: null },
              30: { S: 0.93, M: null },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: null, M: null },
              30: { S: 0.91, M: null },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: null, M: 1 },
              30: { S: 0.88, M: 0.82 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 1, M: 0.99 },
              30: { S: 0.83, M: 0.79 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 1, M: 0.99 },
              30: { S: 0.79, M: 0.78 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.99, M: 0.98 },
              30: { S: 0.74, M: null },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.98, M: 0.96 },
              30: { S: 0.66, M: null },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.95, M: 0.93 },
              30: { S: 0.55, M: null },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.91, M: 0.9 },
              30: { S: 0.49, M: null },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.83, M: 0.88 },
              30: { S: 0.48, M: null },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.74, M: null },
              30: { S: 0.43, M: null },
            },
          },
        ],
      },
    ],
  },
  "tokina-atx-m-33mm-f1-4-x": {
    source: "https://tokinalens.com/product/atx_m_33mm_f1_4_x/",
    mtfType: "measured",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: null, M: 0.92 },
              30: { S: null, M: 0.71 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.69, M: 0.69 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.91, M: 0.9 },
              30: { S: 0.68, M: 0.65 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.91, M: 0.94 },
              30: { S: 0.69, M: 0.65 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.91, M: 0.9 },
              30: { S: 0.7, M: 0.59 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.9, M: 0.87 },
              30: { S: 0.67, M: 0.52 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.87, M: 0.87 },
              30: { S: 0.58, M: 0.49 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.86, M: 0.84 },
              30: { S: 0.51, M: 0.45 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.86, M: 0.81 },
              30: { S: 0.55, M: 0.41 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.86, M: 0.78 },
              30: { S: 0.58, M: 0.49 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: null, M: null },
              30: { S: null, M: 0.51 },
            },
          },
        ],
      },
    ],
  },
  "tokina-atx-m-56mm-f1-4-x": {
    source: "https://tokinalens.com/product/atx_m_56mm_f1_4_x/",
    mtfType: "measured",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: null, M: 0.91 },
              30: { S: null, M: 0.69 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.91, M: 0.9 },
              30: { S: 0.68, M: 0.67 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.89, M: 0.88 },
              30: { S: 0.66, M: null },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.91, M: null },
              30: { S: 0.64, M: 0.57 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.88, M: null },
              30: { S: 0.62, M: 0.58 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: null, M: 0.86 },
              30: { S: 0.62, M: 0.59 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.87, M: 0.85 },
              30: { S: 0.58, M: null },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.82, M: 0.86 },
              30: { S: 0.49, M: 0.54 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.76, M: null },
              30: { S: 0.44, M: 0.55 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.75, M: null },
              30: { S: 0.59, M: 0.55 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: null, M: null },
              30: { S: 0.45, M: 0.27 },
            },
          },
        ],
      },
    ],
  },
  "viltrox-af-75mm-f1-2-pro": {
    source: "https://viltrox.com/products/75mm-f12-xf-lens",
    mtfType: "measured",
    charts: [
      {
        aperture: "f/1.2",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.94 },
              30: { S: null, M: null },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.99, M: 0.94 },
              30: { S: null, M: null },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.99, M: 0.95 },
              30: { S: null, M: null },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.99, M: null },
              30: { S: 0.93, M: null },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.99, M: 0.94 },
              30: { S: 0.9, M: null },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.98, M: 0.9 },
              30: { S: null, M: null },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.98, M: null },
              30: { S: 0.88, M: 0.84 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.97, M: null },
              30: { S: 0.88, M: 0.82 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.98, M: null },
              30: { S: 0.88, M: null },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.97, M: null },
              30: { S: 0.87, M: 0.81 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 1, M: null },
              30: { S: 0.85, M: null },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-gf-100-200mm-f5-6-r-lm-ois-wr": {
    source:
      "https://fujifilm-x.com/en-us/products/lenses/gf100-200mmf56-r-lm-ois-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/5.6",
        focalLength: 100,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.95, M: 0.95 },
              20: { S: 0.92, M: 0.92 },
              40: { S: 0.78, M: 0.78 },
            },
          },
          {
            position: 2.69,
            samples: {
              10: { S: 0.95, M: 0.95 },
              20: { S: 0.91, M: 0.91 },
              40: { S: 0.76, M: 0.75 },
            },
          },
          {
            position: 5.38,
            samples: {
              10: { S: 0.94, M: 0.94 },
              20: { S: 0.91, M: 0.91 },
              40: { S: 0.76, M: 0.74 },
            },
          },
          {
            position: 8.07,
            samples: {
              10: { S: 0.95, M: 0.95 },
              20: { S: 0.91, M: 0.92 },
              40: { S: 0.75, M: 0.75 },
            },
          },
          {
            position: 10.76,
            samples: {
              10: { S: 0.94, M: 0.94 },
              20: { S: 0.91, M: 0.92 },
              40: { S: 0.74, M: 0.76 },
            },
          },
          {
            position: 13.45,
            samples: {
              10: { S: 0.94, M: 0.94 },
              20: { S: 0.91, M: 0.91 },
              40: { S: 0.75, M: 0.76 },
            },
          },
          {
            position: 16.14,
            samples: {
              10: { S: 0.95, M: 0.94 },
              20: { S: 0.91, M: 0.89 },
              40: { S: 0.77, M: 0.74 },
            },
          },
          {
            position: 18.83,
            samples: {
              10: { S: 0.94, M: 0.93 },
              20: { S: 0.91, M: 0.87 },
              40: { S: 0.79, M: 0.7 },
            },
          },
          {
            position: 21.52,
            samples: {
              10: { S: 0.93, M: 0.92 },
              20: { S: 0.88, M: 0.87 },
              40: { S: 0.76, M: 0.69 },
            },
          },
          {
            position: 24.21,
            samples: {
              10: { S: 0.9, M: 0.92 },
              20: { S: 0.78, M: 0.84 },
              40: { S: 0.55, M: 0.63 },
            },
          },
          {
            position: 26.9,
            samples: {
              10: { S: 0.83, M: 0.85 },
              20: { S: 0.58, M: 0.64 },
              40: { S: 0.22, M: 0.36 },
            },
          },
        ],
      },
      {
        aperture: "f/5.6",
        focalLength: 200,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.98, M: 0.98 },
              20: { S: 0.93, M: 0.93 },
              40: { S: 0.83, M: 0.83 },
            },
          },
          {
            position: 2.69,
            samples: {
              10: { S: 0.97, M: 0.97 },
              20: { S: 0.92, M: 0.9 },
              40: { S: 0.8, M: 0.76 },
            },
          },
          {
            position: 5.38,
            samples: {
              10: { S: 0.96, M: 0.94 },
              20: { S: 0.9, M: 0.86 },
              40: { S: 0.75, M: 0.69 },
            },
          },
          {
            position: 8.07,
            samples: {
              10: { S: 0.95, M: 0.91 },
              20: { S: 0.88, M: 0.8 },
              40: { S: 0.69, M: 0.63 },
            },
          },
          {
            position: 10.76,
            samples: {
              10: { S: 0.94, M: 0.88 },
              20: { S: 0.85, M: 0.73 },
              40: { S: 0.62, M: 0.56 },
            },
          },
          {
            position: 13.45,
            samples: {
              10: { S: 0.93, M: 0.84 },
              20: { S: 0.81, M: 0.67 },
              40: { S: 0.56, M: 0.49 },
            },
          },
          {
            position: 16.14,
            samples: {
              10: { S: 0.91, M: 0.83 },
              20: { S: 0.78, M: 0.64 },
              40: { S: 0.51, M: 0.42 },
            },
          },
          {
            position: 18.83,
            samples: {
              10: { S: 0.9, M: 0.83 },
              20: { S: 0.75, M: 0.65 },
              40: { S: 0.48, M: 0.41 },
            },
          },
          {
            position: 21.52,
            samples: {
              10: { S: 0.89, M: 0.83 },
              20: { S: 0.74, M: 0.7 },
              40: { S: 0.5, M: 0.44 },
            },
          },
          {
            position: 24.21,
            samples: {
              10: { S: 0.88, M: 0.84 },
              20: { S: 0.75, M: 0.74 },
              40: { S: 0.54, M: 0.44 },
            },
          },
          {
            position: 26.9,
            samples: {
              10: { S: 0.89, M: 0.84 },
              20: { S: 0.76, M: 0.73 },
              40: { S: 0.58, M: 0.38 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-gf-110mm-f2-0-r-lm-wr": {
    source: "https://fujifilm-x.com/en-us/products/lenses/gf110mmf2-r-lm-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.0",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.93, M: 0.93 },
              20: { S: 0.94, M: 0.94 },
              40: { S: 0.89, M: 0.89 },
            },
          },
          {
            position: 2.69,
            samples: {
              15: { S: 0.93, M: 0.93 },
              20: { S: 0.93, M: 0.93 },
              40: { S: 0.88, M: 0.88 },
            },
          },
          {
            position: 5.38,
            samples: {
              15: { S: 0.93, M: 0.93 },
              20: { S: 0.94, M: 0.94 },
              40: { S: 0.89, M: 0.88 },
            },
          },
          {
            position: 8.07,
            samples: {
              15: { S: 0.93, M: 0.93 },
              20: { S: 0.94, M: 0.94 },
              40: { S: 0.89, M: 0.87 },
            },
          },
          {
            position: 10.76,
            samples: {
              15: { S: 0.93, M: 0.93 },
              20: { S: 0.93, M: 0.93 },
              40: { S: 0.87, M: 0.86 },
            },
          },
          {
            position: 13.45,
            samples: {
              15: { S: 0.93, M: 0.93 },
              20: { S: 0.92, M: 0.93 },
              40: { S: 0.82, M: 0.85 },
            },
          },
          {
            position: 16.14,
            samples: {
              15: { S: 0.92, M: 0.92 },
              20: { S: 0.9, M: 0.92 },
              40: { S: 0.75, M: 0.84 },
            },
          },
          {
            position: 18.83,
            samples: {
              15: { S: 0.91, M: 0.92 },
              20: { S: 0.86, M: 0.92 },
              40: { S: 0.67, M: 0.81 },
            },
          },
          {
            position: 21.52,
            samples: {
              15: { S: 0.88, M: 0.92 },
              20: { S: 0.77, M: 0.9 },
              40: { S: 0.63, M: 0.75 },
            },
          },
          {
            position: 24.21,
            samples: {
              15: { S: 0.81, M: 0.91 },
              20: { S: 0.65, M: 0.87 },
              40: { S: 0.55, M: 0.7 },
            },
          },
          {
            position: 26.9,
            samples: {
              15: { S: 0.66, M: 0.9 },
              20: { S: 0.47, M: 0.83 },
              40: { S: 0.36, M: 0.59 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-gf-110mm-f5-6-ts-macro": {
    source: "https://fujifilm-x.com/en-us/products/lenses/gf110mmf56-ts-macro/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/5.6",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.93, M: 0.93 },
              20: { S: 0.99, M: 0.99 },
              40: { S: 0.96, M: 0.96 },
            },
          },
          {
            position: 2.69,
            samples: {
              10: { S: 0.93, M: 0.93 },
              20: { S: 0.98, M: 0.99 },
              40: { S: 0.96, M: 0.96 },
            },
          },
          {
            position: 5.38,
            samples: {
              10: { S: 0.93, M: 0.93 },
              20: { S: 0.98, M: 0.99 },
              40: { S: 0.95, M: 0.96 },
            },
          },
          {
            position: 8.07,
            samples: {
              10: { S: 0.93, M: 0.93 },
              20: { S: 0.98, M: 0.99 },
              40: { S: 0.95, M: 0.96 },
            },
          },
          {
            position: 10.76,
            samples: {
              10: { S: 0.93, M: 0.93 },
              20: { S: 0.98, M: 0.99 },
              40: { S: 0.93, M: 0.96 },
            },
          },
          {
            position: 13.45,
            samples: {
              10: { S: 0.92, M: 0.93 },
              20: { S: 0.97, M: 0.99 },
              40: { S: 0.9, M: 0.96 },
            },
          },
          {
            position: 16.14,
            samples: {
              10: { S: 0.92, M: 0.93 },
              20: { S: 0.97, M: 0.99 },
              40: { S: 0.88, M: 0.95 },
            },
          },
          {
            position: 18.83,
            samples: {
              10: { S: 0.92, M: 0.93 },
              20: { S: 0.96, M: 0.98 },
              40: { S: 0.85, M: 0.95 },
            },
          },
          {
            position: 21.52,
            samples: {
              10: { S: 0.92, M: 0.93 },
              20: { S: 0.95, M: 0.98 },
              40: { S: 0.83, M: 0.92 },
            },
          },
          {
            position: 24.21,
            samples: {
              10: { S: 0.92, M: 0.93 },
              20: { S: 0.95, M: 0.97 },
              40: { S: 0.81, M: 0.9 },
            },
          },
          {
            position: 26.9,
            samples: {
              10: { S: 0.92, M: 0.93 },
              20: { S: 0.94, M: 0.97 },
              40: { S: 0.79, M: 0.88 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-gf-120mm-f4-r-lm-ois-wr-macro": {
    source:
      "https://fujifilm-x.com/en-us/products/lenses/gf120mmf4-r-lm-ois-wr-macro/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.92, M: 0.92 },
              20: { S: 0.92, M: 0.92 },
              40: { S: 0.84, M: 0.84 },
            },
          },
          {
            position: 2.69,
            samples: {
              15: { S: 0.92, M: 0.92 },
              20: { S: 0.92, M: 0.92 },
              40: { S: 0.83, M: 0.83 },
            },
          },
          {
            position: 5.38,
            samples: {
              15: { S: 0.92, M: 0.92 },
              20: { S: 0.92, M: 0.92 },
              40: { S: 0.82, M: 0.82 },
            },
          },
          {
            position: 8.07,
            samples: {
              15: { S: 0.92, M: 0.92 },
              20: { S: 0.91, M: 0.91 },
              40: { S: 0.81, M: 0.83 },
            },
          },
          {
            position: 10.76,
            samples: {
              15: { S: 0.92, M: 0.92 },
              20: { S: 0.91, M: 0.92 },
              40: { S: 0.8, M: 0.83 },
            },
          },
          {
            position: 13.45,
            samples: {
              15: { S: 0.92, M: 0.92 },
              20: { S: 0.9, M: 0.92 },
              40: { S: 0.78, M: 0.83 },
            },
          },
          {
            position: 16.14,
            samples: {
              15: { S: 0.92, M: 0.92 },
              20: { S: 0.9, M: 0.92 },
              40: { S: 0.75, M: 0.84 },
            },
          },
          {
            position: 18.83,
            samples: {
              15: { S: 0.91, M: 0.91 },
              20: { S: 0.89, M: 0.92 },
              40: { S: 0.71, M: 0.84 },
            },
          },
          {
            position: 21.52,
            samples: {
              15: { S: 0.91, M: 0.92 },
              20: { S: 0.88, M: 0.92 },
              40: { S: 0.67, M: 0.83 },
            },
          },
          {
            position: 24.21,
            samples: {
              15: { S: 0.91, M: 0.92 },
              20: { S: 0.86, M: 0.92 },
              40: { S: 0.64, M: 0.83 },
            },
          },
          {
            position: 26.9,
            samples: {
              15: { S: 0.91, M: 0.92 },
              20: { S: 0.86, M: 0.91 },
              40: { S: 0.63, M: 0.8 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-gf-20-35mm-f4-r-wr": {
    source: "https://fujifilm-x.com/en-us/products/lenses/gf20-35mmf4-r-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/4",
        focalLength: 20,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 1, M: 1 },
              20: { S: 0.92, M: 0.92 },
              40: { S: 0.9, M: 0.9 },
            },
          },
          {
            position: 2.69,
            samples: {
              10: { S: 1, M: 1 },
              20: { S: 0.91, M: 0.91 },
              40: { S: 0.9, M: 0.89 },
            },
          },
          {
            position: 5.38,
            samples: {
              10: { S: 1, M: 1 },
              20: { S: 0.91, M: 0.9 },
              40: { S: 0.89, M: 0.84 },
            },
          },
          {
            position: 8.07,
            samples: {
              10: { S: 1, M: 0.99 },
              20: { S: 0.9, M: 0.88 },
              40: { S: 0.86, M: 0.79 },
            },
          },
          {
            position: 10.76,
            samples: {
              10: { S: 1, M: 0.99 },
              20: { S: 0.9, M: 0.87 },
              40: { S: 0.83, M: 0.74 },
            },
          },
          {
            position: 13.45,
            samples: {
              10: { S: 1, M: 0.98 },
              20: { S: 0.89, M: 0.85 },
              40: { S: 0.81, M: 0.69 },
            },
          },
          {
            position: 16.14,
            samples: {
              10: { S: 1, M: 0.99 },
              20: { S: 0.9, M: 0.87 },
              40: { S: 0.83, M: 0.75 },
            },
          },
          {
            position: 18.83,
            samples: {
              10: { S: 0.99, M: 0.99 },
              20: { S: 0.89, M: 0.88 },
              40: { S: 0.83, M: 0.77 },
            },
          },
          {
            position: 21.52,
            samples: {
              10: { S: 0.98, M: 0.99 },
              20: { S: 0.86, M: 0.88 },
              40: { S: 0.74, M: 0.79 },
            },
          },
          {
            position: 24.21,
            samples: {
              10: { S: 0.97, M: 0.99 },
              20: { S: 0.81, M: 0.86 },
              40: { S: 0.64, M: 0.71 },
            },
          },
          {
            position: 26.9,
            samples: {
              10: { S: 0.97, M: 0.96 },
              20: { S: 0.8, M: 0.78 },
              40: { S: 0.61, M: 0.52 },
            },
          },
        ],
      },
      {
        aperture: "f/4",
        focalLength: 35,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.98, M: 0.98 },
              20: { S: 0.97, M: 0.97 },
              40: { S: 0.93, M: 0.93 },
            },
          },
          {
            position: 2.69,
            samples: {
              10: { S: 0.98, M: 0.98 },
              20: { S: 0.96, M: 0.94 },
              40: { S: 0.89, M: 0.82 },
            },
          },
          {
            position: 5.38,
            samples: {
              10: { S: 0.98, M: 0.97 },
              20: { S: 0.95, M: 0.93 },
              40: { S: 0.85, M: 0.79 },
            },
          },
          {
            position: 8.07,
            samples: {
              10: { S: 0.98, M: 0.98 },
              20: { S: 0.96, M: 0.97 },
              40: { S: 0.87, M: 0.9 },
            },
          },
          {
            position: 10.76,
            samples: {
              10: { S: 0.98, M: 0.98 },
              20: { S: 0.96, M: 0.95 },
              40: { S: 0.89, M: 0.86 },
            },
          },
          {
            position: 13.45,
            samples: {
              10: { S: 0.98, M: 0.97 },
              20: { S: 0.95, M: 0.91 },
              40: { S: 0.85, M: 0.73 },
            },
          },
          {
            position: 16.14,
            samples: {
              10: { S: 0.98, M: 0.96 },
              20: { S: 0.94, M: 0.9 },
              40: { S: 0.79, M: 0.72 },
            },
          },
          {
            position: 18.83,
            samples: {
              10: { S: 0.98, M: 0.97 },
              20: { S: 0.93, M: 0.9 },
              40: { S: 0.75, M: 0.74 },
            },
          },
          {
            position: 21.52,
            samples: {
              10: { S: 0.97, M: 0.96 },
              20: { S: 0.91, M: 0.89 },
              40: { S: 0.71, M: 0.69 },
            },
          },
          {
            position: 24.21,
            samples: {
              10: { S: 0.97, M: 0.95 },
              20: { S: 0.89, M: 0.85 },
              40: { S: 0.68, M: 0.6 },
            },
          },
          {
            position: 26.9,
            samples: {
              10: { S: 0.96, M: 0.92 },
              20: { S: 0.87, M: 0.77 },
              40: { S: 0.63, M: 0.53 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-gf-250mm-f4-r-lm-ois-wr": {
    source:
      "https://fujifilm-x.com/en-us/products/lenses/gf250mmf4-r-lm-ois-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.94, M: 0.94 },
              20: { S: 0.94, M: 0.94 },
              40: { S: 0.93, M: 0.93 },
            },
          },
          {
            position: 2.69,
            samples: {
              15: { S: 0.94, M: 0.94 },
              20: { S: 0.94, M: 0.94 },
              40: { S: 0.93, M: 0.93 },
            },
          },
          {
            position: 5.38,
            samples: {
              15: { S: 0.93, M: 0.93 },
              20: { S: 0.93, M: 0.93 },
              40: { S: 0.92, M: 0.9 },
            },
          },
          {
            position: 8.07,
            samples: {
              15: { S: 0.93, M: 0.93 },
              20: { S: 0.93, M: 0.93 },
              40: { S: 0.91, M: 0.87 },
            },
          },
          {
            position: 10.76,
            samples: {
              15: { S: 0.93, M: 0.92 },
              20: { S: 0.93, M: 0.92 },
              40: { S: 0.9, M: 0.85 },
            },
          },
          {
            position: 13.45,
            samples: {
              15: { S: 0.93, M: 0.91 },
              20: { S: 0.93, M: 0.91 },
              40: { S: 0.89, M: 0.83 },
            },
          },
          {
            position: 16.14,
            samples: {
              15: { S: 0.93, M: 0.91 },
              20: { S: 0.93, M: 0.91 },
              40: { S: 0.88, M: 0.81 },
            },
          },
          {
            position: 18.83,
            samples: {
              15: { S: 0.92, M: 0.9 },
              20: { S: 0.92, M: 0.9 },
              40: { S: 0.87, M: 0.79 },
            },
          },
          {
            position: 21.52,
            samples: {
              15: { S: 0.92, M: 0.9 },
              20: { S: 0.92, M: 0.9 },
              40: { S: 0.86, M: 0.79 },
            },
          },
          {
            position: 24.21,
            samples: {
              15: { S: 0.92, M: 0.9 },
              20: { S: 0.92, M: 0.9 },
              40: { S: 0.84, M: 0.8 },
            },
          },
          {
            position: 26.9,
            samples: {
              15: { S: 0.9, M: 0.9 },
              20: { S: 0.9, M: 0.9 },
              40: { S: 0.8, M: 0.8 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-gf-30mm-f3-5-r-wr": {
    source: "https://fujifilm-x.com/en-us/products/lenses/gf30mmf35-r-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/3.5",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.97, M: 0.97 },
              20: { S: 0.95, M: 0.95 },
            },
          },
          {
            position: 2.69,
            samples: {
              10: { S: null, M: null },
              20: { S: 0.94, M: 0.94 },
            },
          },
          {
            position: 5.38,
            samples: {
              10: { S: 0.97, M: 0.96 },
              20: { S: 0.94, M: 0.93 },
            },
          },
          {
            position: 8.07,
            samples: {
              10: { S: 0.96, M: 0.96 },
              20: { S: 0.94, M: 0.93 },
            },
          },
          {
            position: 10.76,
            samples: {
              10: { S: 0.96, M: 0.96 },
              20: { S: 0.92, M: 0.93 },
            },
          },
          {
            position: 13.45,
            samples: {
              10: { S: 0.95, M: 0.95 },
              20: { S: 0.91, M: 0.93 },
            },
          },
          {
            position: 16.14,
            samples: {
              10: { S: 0.94, M: 0.94 },
              20: { S: 0.87, M: 0.93 },
            },
          },
          {
            position: 18.83,
            samples: {
              10: { S: 0.92, M: 0.92 },
              20: { S: 0.81, M: 0.92 },
            },
          },
          {
            position: 21.52,
            samples: {
              10: { S: 0.89, M: 0.89 },
              20: { S: 0.74, M: 0.9 },
            },
          },
          {
            position: 24.21,
            samples: {
              10: { S: 0.85, M: 0.85 },
              20: { S: 0.67, M: 0.88 },
            },
          },
          {
            position: 26.9,
            samples: {
              10: { S: 0.82, M: 0.82 },
              20: { S: 0.6, M: 0.85 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-gf-30mm-f5-6-ts": {
    source: "https://fujifilm-x.com/en-us/products/lenses/gf30mmf56-ts/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/5.6",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.99 },
              20: { S: 0.98, M: 0.98 },
              40: { S: 0.95, M: 0.95 },
            },
          },
          {
            position: 2.69,
            samples: {
              10: { S: 0.99, M: 0.99 },
              20: { S: 0.98, M: 0.97 },
              40: { S: 0.95, M: 0.92 },
            },
          },
          {
            position: 5.38,
            samples: {
              10: { S: 1, M: 0.99 },
              20: { S: 0.98, M: 0.96 },
              40: { S: 0.94, M: 0.87 },
            },
          },
          {
            position: 8.07,
            samples: {
              10: { S: 0.99, M: 0.99 },
              20: { S: 0.97, M: 0.95 },
              40: { S: 0.9, M: 0.84 },
            },
          },
          {
            position: 10.76,
            samples: {
              10: { S: 0.99, M: 0.98 },
              20: { S: 0.95, M: 0.94 },
              40: { S: 0.84, M: 0.82 },
            },
          },
          {
            position: 13.45,
            samples: {
              10: { S: 0.98, M: 0.98 },
              20: { S: 0.94, M: 0.93 },
              40: { S: 0.77, M: 0.8 },
            },
          },
          {
            position: 16.14,
            samples: {
              10: { S: 0.98, M: 0.99 },
              20: { S: 0.94, M: 0.95 },
              40: { S: 0.78, M: 0.85 },
            },
          },
          {
            position: 18.83,
            samples: {
              10: { S: 0.99, M: 0.99 },
              20: { S: 0.95, M: 0.95 },
              40: { S: 0.84, M: 0.84 },
            },
          },
          {
            position: 21.52,
            samples: {
              10: { S: 0.99, M: 0.98 },
              20: { S: 0.95, M: 0.92 },
              40: { S: 0.85, M: 0.76 },
            },
          },
          {
            position: 24.21,
            samples: {
              10: { S: 0.97, M: 0.97 },
              20: { S: 0.92, M: 0.9 },
              40: { S: 0.74, M: 0.72 },
            },
          },
          {
            position: 26.9,
            samples: {
              10: { S: 0.95, M: 0.98 },
              20: { S: 0.84, M: 0.92 },
              40: { S: 0.64, M: 0.75 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-gf-32-64mm-f4-r-lm-wr": {
    source: "https://fujifilm-x.com/en-us/products/lenses/gf32-64mmf4-r-lm-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/4",
        focalLength: 32,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.94, M: 0.94 },
              20: { S: 0.92, M: 0.92 },
              45: { S: 0.87, M: 0.87 },
            },
          },
          {
            position: 2.69,
            samples: {
              15: { S: 0.94, M: 0.94 },
              20: { S: 0.92, M: 0.9 },
              45: { S: 0.87, M: 0.82 },
            },
          },
          {
            position: 5.38,
            samples: {
              15: { S: 0.94, M: 0.92 },
              20: { S: 0.91, M: 0.87 },
              45: { S: 0.86, M: 0.73 },
            },
          },
          {
            position: 8.07,
            samples: {
              15: { S: 0.94, M: 0.92 },
              20: { S: 0.92, M: 0.85 },
              45: { S: 0.87, M: 0.71 },
            },
          },
          {
            position: 10.76,
            samples: {
              15: { S: 0.94, M: 0.91 },
              20: { S: 0.92, M: 0.82 },
              45: { S: 0.89, M: 0.72 },
            },
          },
          {
            position: 13.45,
            samples: {
              15: { S: 0.94, M: 0.89 },
              20: { S: 0.93, M: 0.79 },
              45: { S: 0.91, M: 0.69 },
            },
          },
          {
            position: 16.14,
            samples: {
              15: { S: 0.94, M: 0.87 },
              20: { S: 0.93, M: 0.75 },
              45: { S: 0.91, M: 0.63 },
            },
          },
          {
            position: 18.83,
            samples: {
              15: { S: 0.93, M: 0.84 },
              20: { S: 0.91, M: 0.71 },
              45: { S: 0.84, M: 0.54 },
            },
          },
          {
            position: 21.52,
            samples: {
              15: { S: 0.92, M: 0.83 },
              20: { S: 0.87, M: 0.73 },
              45: { S: 0.71, M: 0.52 },
            },
          },
          {
            position: 24.21,
            samples: {
              15: { S: 0.91, M: 0.81 },
              20: { S: 0.83, M: 0.76 },
              45: { S: 0.64, M: 0.5 },
            },
          },
          {
            position: 26.9,
            samples: {
              15: { S: 0.92, M: 0.77 },
              20: { S: 0.86, M: 0.57 },
              45: { S: 0.71, M: 0.25 },
            },
          },
        ],
      },
      {
        aperture: "f/4",
        focalLength: 64,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.96, M: 0.96 },
              20: { S: 0.94, M: 0.94 },
              45: { S: 0.9, M: 0.9 },
            },
          },
          {
            position: 2.69,
            samples: {
              15: { S: 0.96, M: 0.96 },
              20: { S: 0.94, M: 0.94 },
              45: { S: 0.89, M: 0.87 },
            },
          },
          {
            position: 5.38,
            samples: {
              15: { S: 0.96, M: 0.96 },
              20: { S: 0.94, M: 0.92 },
              45: { S: 0.87, M: 0.82 },
            },
          },
          {
            position: 8.07,
            samples: {
              15: { S: 0.96, M: 0.96 },
              20: { S: 0.93, M: 0.9 },
              45: { S: 0.85, M: 0.76 },
            },
          },
          {
            position: 10.76,
            samples: {
              15: { S: 0.96, M: 0.94 },
              20: { S: 0.93, M: 0.89 },
              45: { S: 0.82, M: 0.74 },
            },
          },
          {
            position: 13.45,
            samples: {
              15: { S: 0.95, M: 0.94 },
              20: { S: 0.92, M: 0.9 },
              45: { S: 0.79, M: 0.73 },
            },
          },
          {
            position: 16.14,
            samples: {
              15: { S: 0.95, M: 0.95 },
              20: { S: 0.91, M: 0.91 },
              45: { S: 0.76, M: 0.77 },
            },
          },
          {
            position: 18.83,
            samples: {
              15: { S: 0.95, M: 0.95 },
              20: { S: 0.89, M: 0.92 },
              45: { S: 0.71, M: 0.79 },
            },
          },
          {
            position: 21.52,
            samples: {
              15: { S: 0.94, M: 0.95 },
              20: { S: 0.87, M: 0.91 },
              45: { S: 0.62, M: 0.76 },
            },
          },
          {
            position: 24.21,
            samples: {
              15: { S: 0.93, M: 0.94 },
              20: { S: 0.82, M: 0.88 },
              45: { S: 0.53, M: 0.66 },
            },
          },
          {
            position: 26.9,
            samples: {
              15: { S: 0.91, M: 0.93 },
              20: { S: 0.79, M: 0.82 },
              45: { S: 0.46, M: 0.51 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-gf-35-70mm-f4-5-5-6-wr": {
    source: "https://fujifilm-x.com/en-us/products/lenses/gf35-70mmf45-56-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/4.5",
        focalLength: 35,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.99 },
              20: { S: 0.94, M: 0.94 },
              40: { S: 0.8, M: 0.8 },
            },
          },
          {
            position: 2.69,
            samples: {
              10: { S: 0.99, M: 0.99 },
              20: { S: 0.93, M: 0.93 },
              40: { S: 0.77, M: 0.79 },
            },
          },
          {
            position: 5.38,
            samples: {
              10: { S: 0.98, M: 0.97 },
              20: { S: 0.91, M: 0.89 },
              40: { S: 0.73, M: 0.76 },
            },
          },
          {
            position: 8.07,
            samples: {
              10: { S: 0.96, M: 0.94 },
              20: { S: 0.85, M: 0.83 },
              40: { S: 0.69, M: 0.72 },
            },
          },
          {
            position: 10.76,
            samples: {
              10: { S: 0.93, M: 0.94 },
              20: { S: 0.79, M: 0.81 },
              40: { S: 0.67, M: 0.69 },
            },
          },
          {
            position: 13.45,
            samples: {
              10: { S: 0.9, M: 0.94 },
              20: { S: 0.75, M: 0.8 },
              40: { S: 0.64, M: 0.64 },
            },
          },
          {
            position: 16.14,
            samples: {
              10: { S: 0.86, M: 0.93 },
              20: { S: 0.71, M: 0.79 },
              40: { S: 0.59, M: 0.6 },
            },
          },
          {
            position: 18.83,
            samples: {
              10: { S: 0.8, M: 0.92 },
              20: { S: 0.66, M: 0.76 },
              40: { S: 0.54, M: 0.57 },
            },
          },
          {
            position: 21.52,
            samples: {
              10: { S: 0.72, M: 0.92 },
              20: { S: 0.58, M: 0.77 },
              40: { S: 0.46, M: 0.55 },
            },
          },
          {
            position: 24.21,
            samples: {
              10: { S: 0.61, M: 0.91 },
              20: { S: 0.48, M: 0.72 },
              40: { S: 0.38, M: 0.47 },
            },
          },
          {
            position: 26.9,
            samples: {
              10: { S: 0.54, M: 0.84 },
              20: { S: 0.4, M: 0.49 },
              40: { S: 0.27, M: 0.26 },
            },
          },
        ],
      },
      {
        aperture: "f/4.5",
        focalLength: 70,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 1, M: 1 },
              20: { S: 1, M: 1 },
              40: { S: 1, M: 1 },
            },
          },
          {
            position: 2.69,
            samples: {
              10: { S: null, M: null },
              20: { S: 1, M: 1 },
              40: { S: 0.99, M: 0.98 },
            },
          },
          {
            position: 5.38,
            samples: {
              10: { S: 1, M: 1 },
              20: { S: 1, M: 0.99 },
              40: { S: 0.97, M: 0.94 },
            },
          },
          {
            position: 8.07,
            samples: {
              10: { S: 1, M: 1 },
              20: { S: 0.96, M: 0.97 },
              40: { S: 0.91, M: 0.88 },
            },
          },
          {
            position: 10.76,
            samples: {
              10: { S: 0.99, M: 1 },
              20: { S: 0.92, M: 0.95 },
              40: { S: 0.75, M: 0.82 },
            },
          },
          {
            position: 13.45,
            samples: {
              10: { S: 0.96, M: 0.99 },
              20: { S: 0.84, M: 0.92 },
              40: { S: 0.64, M: 0.77 },
            },
          },
          {
            position: 16.14,
            samples: {
              10: { S: 0.91, M: 0.98 },
              20: { S: 0.74, M: 0.9 },
              40: { S: 0.57, M: 0.72 },
            },
          },
          {
            position: 18.83,
            samples: {
              10: { S: 0.85, M: 0.97 },
              20: { S: 0.64, M: 0.87 },
              40: { S: 0.5, M: 0.66 },
            },
          },
          {
            position: 21.52,
            samples: {
              10: { S: 0.77, M: 0.96 },
              20: { S: 0.58, M: 0.84 },
              40: { S: 0.44, M: 0.56 },
            },
          },
          {
            position: 24.21,
            samples: {
              10: { S: 0.68, M: 0.95 },
              20: { S: 0.52, M: 0.8 },
              40: { S: 0.4, M: 0.41 },
            },
          },
          {
            position: 26.9,
            samples: {
              10: { S: 0.61, M: 0.91 },
              20: { S: 0.47, M: 0.66 },
              40: { S: 0.35, M: 0.22 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-gf-45-100mm-f4-r-lm-ois-wr": {
    source:
      "https://fujifilm-x.com/en-us/products/lenses/gf45-100mmf4-r-lm-ois-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/4",
        focalLength: 45,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 1, M: 1 },
              20: { S: 0.98, M: 0.98 },
              40: { S: 0.95, M: 0.95 },
            },
          },
          {
            position: 2.69,
            samples: {
              10: { S: 1, M: 1 },
              20: { S: 0.98, M: 0.97 },
              40: { S: 0.94, M: 0.91 },
            },
          },
          {
            position: 5.38,
            samples: {
              10: { S: 1, M: 0.99 },
              20: { S: 0.98, M: 0.94 },
              40: { S: 0.92, M: 0.82 },
            },
          },
          {
            position: 8.07,
            samples: {
              10: { S: 1, M: 0.98 },
              20: { S: 0.97, M: 0.92 },
              40: { S: 0.92, M: 0.76 },
            },
          },
          {
            position: 10.76,
            samples: {
              10: { S: 1, M: 0.97 },
              20: { S: 0.97, M: 0.89 },
              40: { S: 0.91, M: 0.73 },
            },
          },
          {
            position: 13.45,
            samples: {
              10: { S: 1, M: 0.96 },
              20: { S: 0.97, M: 0.88 },
              40: { S: 0.91, M: 0.71 },
            },
          },
          {
            position: 16.14,
            samples: {
              10: { S: 1, M: 0.95 },
              20: { S: 0.97, M: 0.86 },
              40: { S: 0.91, M: 0.69 },
            },
          },
          {
            position: 18.83,
            samples: {
              10: { S: 0.99, M: 0.93 },
              20: { S: 0.96, M: 0.8 },
              40: { S: 0.9, M: 0.59 },
            },
          },
          {
            position: 21.52,
            samples: {
              10: { S: 0.99, M: 0.9 },
              20: { S: 0.96, M: 0.72 },
              40: { S: 0.89, M: 0.53 },
            },
          },
          {
            position: 24.21,
            samples: {
              10: { S: 0.99, M: 0.88 },
              20: { S: 0.94, M: 0.65 },
              40: { S: 0.83, M: 0.37 },
            },
          },
          {
            position: 26.9,
            samples: {
              10: { S: 0.97, M: 0.83 },
              20: { S: 0.9, M: 0.5 },
              40: { S: 0.77, M: 0.17 },
            },
          },
        ],
      },
      {
        aperture: "f/4",
        focalLength: 100,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.99, M: 0.99 },
              20: { S: 0.97, M: 0.97 },
              40: { S: 0.92, M: 0.92 },
            },
          },
          {
            position: 2.69,
            samples: {
              10: { S: 0.99, M: 0.99 },
              20: { S: 0.97, M: 0.96 },
              40: { S: 0.92, M: 0.91 },
            },
          },
          {
            position: 5.38,
            samples: {
              10: { S: 0.99, M: 0.98 },
              20: { S: 0.97, M: 0.96 },
              40: { S: 0.93, M: 0.88 },
            },
          },
          {
            position: 8.07,
            samples: {
              10: { S: 0.99, M: 0.98 },
              20: { S: 0.97, M: 0.94 },
              40: { S: 0.9, M: 0.8 },
            },
          },
          {
            position: 10.76,
            samples: {
              10: { S: 0.98, M: 0.97 },
              20: { S: 0.95, M: 0.9 },
              40: { S: 0.82, M: 0.72 },
            },
          },
          {
            position: 13.45,
            samples: {
              10: { S: 0.97, M: 0.95 },
              20: { S: 0.9, M: 0.85 },
              40: { S: 0.71, M: 0.64 },
            },
          },
          {
            position: 16.14,
            samples: {
              10: { S: 0.95, M: 0.93 },
              20: { S: 0.84, M: 0.81 },
              40: { S: 0.64, M: 0.58 },
            },
          },
          {
            position: 18.83,
            samples: {
              10: { S: 0.92, M: 0.9 },
              20: { S: 0.78, M: 0.77 },
              40: { S: 0.6, M: 0.53 },
            },
          },
          {
            position: 21.52,
            samples: {
              10: { S: 0.89, M: 0.92 },
              20: { S: 0.74, M: 0.77 },
              40: { S: 0.56, M: 0.51 },
            },
          },
          {
            position: 24.21,
            samples: {
              10: { S: 0.87, M: 0.92 },
              20: { S: 0.73, M: 0.77 },
              40: { S: 0.53, M: 0.46 },
            },
          },
          {
            position: 26.9,
            samples: {
              10: { S: 0.89, M: 0.89 },
              20: { S: 0.73, M: 0.72 },
              40: { S: 0.53, M: 0.36 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-gf-45mm-f2-8-r-wr": {
    source: "https://fujifilm-x.com/en-us/products/lenses/gf45mmf28-r-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.92, M: 0.92 },
              20: { S: 0.88, M: 0.88 },
              40: { S: 0.76, M: 0.76 },
            },
          },
          {
            position: 2.69,
            samples: {
              10: { S: 0.92, M: 0.92 },
              20: { S: 0.88, M: 0.89 },
              40: { S: 0.75, M: 0.75 },
            },
          },
          {
            position: 5.38,
            samples: {
              10: { S: null, M: null },
              20: { S: 0.87, M: 0.88 },
              40: { S: 0.74, M: 0.74 },
            },
          },
          {
            position: 8.07,
            samples: {
              10: { S: 0.91, M: 0.92 },
              20: { S: 0.87, M: 0.89 },
              40: { S: 0.73, M: 0.74 },
            },
          },
          {
            position: 10.76,
            samples: {
              10: { S: 0.91, M: 0.92 },
              20: { S: 0.85, M: 0.88 },
              40: { S: 0.7, M: 0.71 },
            },
          },
          {
            position: 13.45,
            samples: {
              10: { S: 0.89, M: 0.91 },
              20: { S: 0.82, M: 0.86 },
              40: { S: 0.64, M: 0.67 },
            },
          },
          {
            position: 16.14,
            samples: {
              10: { S: 0.88, M: 0.91 },
              20: { S: 0.78, M: 0.85 },
              40: { S: 0.58, M: 0.66 },
            },
          },
          {
            position: 18.83,
            samples: {
              10: { S: 0.86, M: 0.9 },
              20: { S: 0.74, M: 0.82 },
              40: { S: 0.53, M: 0.59 },
            },
          },
          {
            position: 21.52,
            samples: {
              10: { S: 0.84, M: 0.89 },
              20: { S: 0.72, M: 0.78 },
              40: { S: 0.52, M: 0.57 },
            },
          },
          {
            position: 24.21,
            samples: {
              10: { S: 0.81, M: 0.89 },
              20: { S: 0.69, M: 0.79 },
              40: { S: 0.54, M: 0.56 },
            },
          },
          {
            position: 26.9,
            samples: {
              10: { S: 0.76, M: 0.88 },
              20: { S: 0.65, M: 0.77 },
              40: { S: 0.54, M: 0.52 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-gf-500mm-f5-6-r-lm-ois-wr": {
    source:
      "https://fujifilm-x.com/en-us/products/lenses/gf500mmf56-r-lm-ois-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/5.6",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.89, M: 0.89 },
              20: { S: 0.89, M: 0.89 },
              40: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 2.69,
            samples: {
              15: { S: 0.89, M: 0.89 },
              20: { S: 0.89, M: 0.89 },
              40: { S: 0.98, M: 0.99 },
            },
          },
          {
            position: 5.38,
            samples: {
              15: { S: 0.89, M: 0.89 },
              20: { S: 0.89, M: 0.89 },
              40: { S: 0.99, M: 0.97 },
            },
          },
          {
            position: 8.07,
            samples: {
              15: { S: 0.89, M: 0.88 },
              20: { S: 0.89, M: 0.88 },
              40: { S: 0.99, M: 0.95 },
            },
          },
          {
            position: 10.76,
            samples: {
              15: { S: 0.89, M: 0.88 },
              20: { S: 0.89, M: 0.87 },
              40: { S: 0.99, M: 0.92 },
            },
          },
          {
            position: 13.45,
            samples: {
              15: { S: 0.89, M: 0.88 },
              20: { S: 0.89, M: 0.87 },
              40: { S: 0.99, M: 0.91 },
            },
          },
          {
            position: 16.14,
            samples: {
              15: { S: 0.89, M: 0.88 },
              20: { S: 0.89, M: 0.86 },
              40: { S: 0.98, M: 0.9 },
            },
          },
          {
            position: 18.83,
            samples: {
              15: { S: 0.89, M: 0.88 },
              20: { S: 0.89, M: 0.86 },
              40: { S: 0.97, M: 0.91 },
            },
          },
          {
            position: 21.52,
            samples: {
              15: { S: 0.89, M: 0.88 },
              20: { S: 0.88, M: 0.86 },
              40: { S: 0.95, M: 0.89 },
            },
          },
          {
            position: 24.21,
            samples: {
              15: { S: 0.88, M: 0.88 },
              20: { S: 0.88, M: 0.86 },
              40: { S: 0.94, M: 0.87 },
            },
          },
          {
            position: 26.9,
            samples: {
              15: { S: 0.88, M: 0.88 },
              20: { S: 0.88, M: 0.85 },
              40: { S: 0.93, M: 0.81 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-gf-50mm-f3-5-r-lm-wr": {
    source: "https://fujifilm-x.com/en-us/products/lenses/gf50mmf35-r-lm-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/3.5",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.97, M: 0.97 },
              20: { S: 0.95, M: 0.95 },
              45: { S: 0.9, M: 0.9 },
            },
          },
          {
            position: 2.69,
            samples: {
              15: { S: 0.97, M: 0.97 },
              20: { S: 0.95, M: 0.94 },
              45: { S: 0.89, M: 0.87 },
            },
          },
          {
            position: 5.38,
            samples: {
              15: { S: 0.97, M: 0.97 },
              20: { S: 0.94, M: 0.93 },
              45: { S: 0.86, M: 0.83 },
            },
          },
          {
            position: 8.07,
            samples: {
              15: { S: 0.96, M: 0.96 },
              20: { S: 0.92, M: 0.93 },
              45: { S: 0.81, M: 0.83 },
            },
          },
          {
            position: 10.76,
            samples: {
              15: { S: 0.96, M: 0.97 },
              20: { S: 0.91, M: 0.94 },
              45: { S: 0.76, M: 0.86 },
            },
          },
          {
            position: 13.45,
            samples: {
              15: { S: 0.95, M: 0.97 },
              20: { S: 0.89, M: 0.93 },
              45: { S: 0.71, M: 0.84 },
            },
          },
          {
            position: 16.14,
            samples: {
              15: { S: 0.94, M: 0.96 },
              20: { S: 0.87, M: 0.92 },
              45: { S: 0.66, M: 0.81 },
            },
          },
          {
            position: 18.83,
            samples: {
              15: { S: 0.93, M: 0.96 },
              20: { S: 0.83, M: 0.91 },
              45: { S: 0.64, M: 0.79 },
            },
          },
          {
            position: 21.52,
            samples: {
              15: { S: 0.89, M: 0.95 },
              20: { S: 0.75, M: 0.87 },
              45: { S: 0.62, M: 0.69 },
            },
          },
          {
            position: 24.21,
            samples: {
              15: { S: 0.8, M: 0.93 },
              20: { S: 0.63, M: 0.81 },
              45: { S: 0.51, M: 0.54 },
            },
          },
          {
            position: 26.9,
            samples: {
              15: { S: 0.63, M: 0.89 },
              20: { S: 0.46, M: 0.72 },
              45: { S: 0.3, M: 0.38 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-gf-55mm-f1-7-r-wr": {
    source: "https://fujifilm-x.com/en-us/products/lenses/gf55mmf17-r-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.7",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.98, M: 0.98 },
              20: { S: 0.94, M: 0.94 },
              40: { S: 1, M: 1 },
            },
          },
          {
            position: 2.69,
            samples: {
              10: { S: 0.98, M: 0.97 },
              20: { S: 0.93, M: 0.92 },
              40: { S: 1, M: 1 },
            },
          },
          {
            position: 5.38,
            samples: {
              10: { S: 0.98, M: 0.97 },
              20: { S: 0.94, M: 0.92 },
              40: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 8.07,
            samples: {
              10: { S: 0.98, M: 0.98 },
              20: { S: 0.94, M: 0.93 },
              40: { S: 1, M: 1 },
            },
          },
          {
            position: 10.76,
            samples: {
              10: { S: 0.96, M: 0.98 },
              20: { S: 0.91, M: 0.94 },
              // 40 M: eye-read override 0.95 (extractor pins to plateau
              // ceiling 1.0; chart shows M40 dipping below S40). See
              // docs/optical-specs/fujifilm-gf-55mm-f1-7-r-wr/eye-read.md.
              40: { S: 0.96, M: 0.95 },
            },
          },
          {
            position: 13.45,
            samples: {
              10: { S: 0.93, M: 0.98 },
              20: { S: 0.81, M: 0.94 },
              // 40 M: eye-read override 0.92 (extractor pins to plateau
              // ceiling 1.0; chart shows M40 dipping). See
              // docs/optical-specs/fujifilm-gf-55mm-f1-7-r-wr/eye-read.md.
              40: { S: 0.83, M: 0.92 },
            },
          },
          {
            position: 16.14,
            samples: {
              10: { S: 0.86, M: 0.98 },
              20: { S: 0.71, M: 0.94 },
              40: { S: 0.79, M: 1 },
            },
          },
          {
            position: 18.83,
            samples: {
              10: { S: 0.77, M: 0.97 },
              20: { S: 0.67, M: 0.91 },
              40: { S: 0.72, M: 0.89 },
            },
          },
          {
            position: 21.52,
            samples: {
              10: { S: 0.68, M: 0.96 },
              20: { S: 0.6, M: 0.86 },
              40: { S: 0.64, M: 0.74 },
            },
          },
          {
            position: 24.21,
            samples: {
              10: { S: 0.6, M: 0.92 },
              20: { S: 0.49, M: 0.76 },
              40: { S: 0.51, M: 0.68 },
            },
          },
          {
            position: 26.9,
            samples: {
              10: { S: 0.5, M: 0.87 },
              20: { S: 0.36, M: 0.63 },
              40: { S: 0.31, M: 0.51 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-gf-63mm-f2-8-r-wr": {
    source: "https://fujifilm-x.com/en-us/products/lenses/gf63mmf28-r-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.94, M: 0.94 },
              20: { S: 0.88, M: 0.88 },
              45: { S: 0.76, M: 0.76 },
            },
          },
          {
            position: 2.69,
            samples: {
              10: { S: 0.94, M: 0.94 },
              20: { S: 0.88, M: 0.88 },
              45: { S: 0.75, M: 0.75 },
            },
          },
          {
            position: 5.38,
            samples: {
              10: { S: 0.93, M: 0.93 },
              20: { S: 0.87, M: 0.87 },
              45: { S: 0.72, M: 0.74 },
            },
          },
          {
            position: 8.07,
            samples: {
              10: { S: 0.93, M: 0.95 },
              20: { S: 0.85, M: 0.87 },
              45: { S: 0.65, M: 0.72 },
            },
          },
          {
            position: 10.76,
            samples: {
              10: { S: 0.93, M: 0.95 },
              20: { S: 0.82, M: 0.87 },
              45: { S: 0.57, M: 0.7 },
            },
          },
          {
            position: 13.45,
            samples: {
              10: { S: 0.92, M: 0.95 },
              20: { S: 0.79, M: 0.87 },
              45: { S: 0.48, M: 0.67 },
            },
          },
          {
            position: 16.14,
            samples: {
              10: { S: 0.91, M: 0.95 },
              20: { S: 0.78, M: 0.87 },
              45: { S: 0.45, M: 0.66 },
            },
          },
          {
            position: 18.83,
            samples: {
              10: { S: 0.91, M: 0.95 },
              20: { S: 0.77, M: 0.86 },
              45: { S: 0.49, M: 0.63 },
            },
          },
          {
            position: 21.52,
            samples: {
              10: { S: 0.88, M: 0.94 },
              20: { S: 0.74, M: 0.83 },
              45: { S: 0.55, M: 0.58 },
            },
          },
          {
            position: 24.21,
            samples: {
              10: { S: 0.82, M: 0.93 },
              20: { S: 0.67, M: 0.78 },
              45: { S: 0.52, M: 0.49 },
            },
          },
          {
            position: 26.9,
            samples: {
              10: { S: 0.71, M: 0.91 },
              20: { S: 0.53, M: 0.74 },
              45: { S: 0.38, M: 0.42 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-gf-80mm-f1-7-r-wr": {
    source: "https://fujifilm-x.com/en-us/products/lenses/gf80mmf17-r-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.7",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.86, M: 0.86 },
              20: { S: 0.76, M: 0.76 },
              40: { S: null, M: null },
            },
          },
          {
            position: 2.69,
            samples: {
              10: { S: 0.85, M: 0.84 },
              20: { S: 0.74, M: 0.74 },
              40: { S: null, M: null },
            },
          },
          {
            position: 5.38,
            samples: {
              10: { S: 0.85, M: 0.83 },
              20: { S: 0.74, M: 0.73 },
              40: { S: null, M: null },
            },
          },
          {
            position: 8.07,
            samples: {
              10: { S: 0.85, M: 0.83 },
              20: { S: 0.74, M: 0.72 },
              40: { S: null, M: null },
            },
          },
          {
            position: 10.76,
            samples: {
              10: { S: 0.84, M: 0.84 },
              20: { S: 0.74, M: 0.72 },
              40: { S: null, M: null },
            },
          },
          {
            position: 13.45,
            samples: {
              10: { S: 0.83, M: 0.85 },
              20: { S: 0.73, M: 0.71 },
              40: { S: null, M: null },
            },
          },
          {
            position: 16.14,
            samples: {
              10: { S: 0.81, M: 0.85 },
              20: { S: 0.67, M: 0.7 },
              40: { S: null, M: null },
            },
          },
          {
            position: 18.83,
            samples: {
              10: { S: 0.74, M: 0.85 },
              20: { S: 0.56, M: 0.69 },
              40: { S: null, M: null },
            },
          },
          {
            position: 21.52,
            samples: {
              10: { S: 0.64, M: 0.85 },
              20: { S: 0.52, M: 0.69 },
              40: { S: null, M: null },
            },
          },
          {
            position: 24.21,
            samples: {
              10: { S: 0.56, M: 0.84 },
              20: { S: 0.51, M: 0.68 },
              40: { S: 0.97, M: null },
            },
          },
          {
            position: 26.9,
            samples: {
              10: { S: 0.53, M: 0.8 },
              20: { S: 0.46, M: 0.64 },
              40: { S: 0.87, M: null },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xc-13-33mm-f3-5-6-3-ois": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xc13-33mmf35-63-ois/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/3.5",
        focalLength: 13,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.99, M: 0.99 },
              45: { S: 0.96, M: 0.96 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.99, M: 0.99 },
              45: { S: 0.95, M: 0.9 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.99, M: 0.96 },
              45: { S: 0.91, M: 0.76 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.98, M: 0.95 },
              45: { S: 0.86, M: 0.7 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.98, M: 0.95 },
              45: { S: 0.83, M: 0.71 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.97, M: 0.95 },
              45: { S: 0.81, M: 0.74 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.96, M: 0.96 },
              45: { S: 0.79, M: 0.77 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.94, M: 0.95 },
              45: { S: 0.78, M: 0.76 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.9, M: 0.94 },
              45: { S: 0.75, M: 0.72 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.86, M: 0.91 },
              45: { S: 0.67, M: 0.63 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.83, M: 0.89 },
              45: { S: 0.62, M: 0.6 },
            },
          },
        ],
      },
      {
        aperture: "f/3.5",
        focalLength: 33,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 1, M: 1 },
              45: { S: 0.99, M: 0.99 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 1, M: 1 },
              45: { S: 0.98, M: 0.97 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 1, M: 0.99 },
              45: { S: 0.97, M: 0.92 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.99, M: 0.99 },
              45: { S: 0.95, M: 0.89 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.99, M: 0.98 },
              45: { S: 0.92, M: 0.85 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.98, M: 0.97 },
              45: { S: 0.87, M: 0.79 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.97, M: 0.95 },
              45: { S: 0.78, M: 0.7 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.95, M: 0.93 },
              45: { S: 0.68, M: 0.6 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.93, M: 0.9 },
              45: { S: 0.58, M: 0.5 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.89, M: 0.84 },
              45: { S: 0.51, M: 0.37 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.86, M: 0.77 },
              45: { S: 0.48, M: 0.26 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xc-35mm-f2-0": {
    source: "https://fujifilm-x.com/global/products/lenses/xc35mmf2/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.0",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.88, M: 0.88 },
              45: { S: 0.88, M: 0.88 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.89, M: 0.88 },
              45: { S: 0.89, M: 0.88 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.89, M: 0.88 },
              45: { S: 0.89, M: 0.88 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.89, M: 0.88 },
              45: { S: 0.89, M: 0.88 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.89, M: 0.88 },
              45: { S: 0.89, M: 0.88 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.87, M: 0.88 },
              45: { S: 0.87, M: 0.88 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.85, M: 0.86 },
              45: { S: 0.85, M: 0.86 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.79, M: 0.84 },
              45: { S: 0.79, M: 0.84 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.57, M: 0.8 },
              45: { S: 0.57, M: 0.8 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.28, M: 0.75 },
              45: { S: 0.28, M: 0.75 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.12, M: 0.75 },
              45: { S: 0.12, M: 0.75 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xc-50-230mm-f4-5-6-7-ois-ii": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xc50-230mmf45-67-ois-ii/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/4.5",
        focalLength: 50,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.95, M: 0.95 },
              45: { S: 0.89, M: 0.89 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.94, M: 0.94 },
              45: { S: 0.89, M: 0.88 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.95, M: 0.94 },
              45: { S: 0.89, M: 0.85 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.95, M: 0.93 },
              45: { S: 0.89, M: 0.8 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.94, M: 0.92 },
              45: { S: 0.89, M: 0.74 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.94, M: 0.91 },
              45: { S: 0.89, M: 0.67 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.94, M: 0.89 },
              45: { S: 0.88, M: 0.59 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.94, M: 0.86 },
              45: { S: 0.87, M: 0.55 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.93, M: 0.83 },
              45: { S: 0.8, M: 0.56 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.9, M: 0.8 },
              45: { S: 0.63, M: 0.57 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.85, M: 0.77 },
              45: { S: 0.41, M: 0.48 },
            },
          },
        ],
      },
      {
        aperture: "f/4.5",
        focalLength: 230,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.91, M: 0.91 },
              45: { S: 0.88, M: 0.88 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.91, M: 0.9 },
              45: { S: 0.87, M: 0.83 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.91, M: 0.88 },
              45: { S: 0.85, M: 0.72 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.9, M: 0.86 },
              45: { S: 0.83, M: 0.64 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.9, M: 0.83 },
              45: { S: 0.82, M: 0.62 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.9, M: 0.79 },
              45: { S: 0.8, M: 0.62 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.9, M: 0.76 },
              45: { S: 0.79, M: 0.65 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.9, M: 0.72 },
              45: { S: 0.79, M: 0.66 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.9, M: 0.67 },
              45: { S: 0.79, M: 0.6 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.9, M: 0.63 },
              45: { S: 0.79, M: 0.52 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.9, M: 0.59 },
              45: { S: 0.79, M: 0.42 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-10-24mm-f4-r-ois": {
    source: "https://fujifilm-x.com/global/products/lenses/xf10-24mmf4-r-ois/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/4",
        focalLength: 10,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.89, M: 0.89 },
              45: { S: 0.8, M: 0.8 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.89, M: 0.89 },
              45: { S: 0.8, M: 0.78 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.88, M: 0.88 },
              45: { S: 0.76, M: 0.74 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.88, M: 0.87 },
              45: { S: 0.73, M: 0.68 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.88, M: 0.86 },
              45: { S: 0.71, M: 0.56 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.88, M: 0.82 },
              45: { S: 0.71, M: 0.44 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.88, M: 0.79 },
              45: { S: 0.72, M: 0.37 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.88, M: 0.76 },
              45: { S: 0.71, M: 0.36 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.87, M: 0.76 },
              45: { S: 0.69, M: 0.37 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.86, M: 0.74 },
              45: { S: 0.66, M: 0.37 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.87, M: 0.66 },
              45: { S: 0.69, M: 0.28 },
            },
          },
        ],
      },
      {
        aperture: "f/4",
        focalLength: 24,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.87, M: 0.87 },
              45: { S: 0.71, M: 0.71 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.87, M: 0.86 },
              45: { S: 0.68, M: 0.65 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.86, M: 0.85 },
              45: { S: 0.65, M: 0.62 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.86, M: 0.84 },
              45: { S: 0.64, M: 0.61 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.85, M: 0.83 },
              45: { S: 0.62, M: 0.57 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.85, M: 0.82 },
              45: { S: 0.59, M: 0.55 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.84, M: 0.81 },
              45: { S: 0.54, M: 0.56 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.83, M: 0.81 },
              45: { S: 0.48, M: 0.54 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.8, M: 0.78 },
              45: { S: 0.39, M: 0.43 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.72, M: 0.75 },
              45: { S: 0.27, M: 0.3 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.65, M: 0.72 },
              45: { S: 0.24, M: 0.23 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-10-24mm-f4-r-ois-wr": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xf10-24mmf4-r-ois-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/4",
        focalLength: 10,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.89, M: 0.89 },
              45: { S: 0.8, M: 0.8 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.89, M: 0.89 },
              45: { S: 0.8, M: 0.78 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.88, M: 0.88 },
              45: { S: 0.76, M: 0.74 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.88, M: 0.87 },
              45: { S: 0.73, M: 0.68 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.88, M: 0.86 },
              45: { S: 0.71, M: 0.56 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.88, M: 0.82 },
              45: { S: 0.71, M: 0.44 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.88, M: 0.79 },
              45: { S: 0.72, M: 0.37 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.88, M: 0.76 },
              45: { S: 0.71, M: 0.36 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.87, M: 0.76 },
              45: { S: 0.69, M: 0.37 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.86, M: 0.74 },
              45: { S: 0.66, M: 0.37 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.87, M: 0.66 },
              45: { S: 0.69, M: 0.28 },
            },
          },
        ],
      },
      {
        aperture: "f/4",
        focalLength: 24,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.87, M: 0.87 },
              45: { S: 0.71, M: 0.71 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.87, M: 0.86 },
              45: { S: 0.68, M: 0.65 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.86, M: 0.85 },
              45: { S: 0.65, M: 0.62 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.86, M: 0.84 },
              45: { S: 0.64, M: 0.61 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.85, M: 0.83 },
              45: { S: 0.62, M: 0.57 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.85, M: 0.82 },
              45: { S: 0.59, M: 0.55 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.84, M: 0.81 },
              45: { S: 0.54, M: 0.56 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.83, M: 0.81 },
              45: { S: 0.48, M: 0.54 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.8, M: 0.78 },
              45: { S: 0.39, M: 0.43 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.72, M: 0.75 },
              45: { S: 0.27, M: 0.3 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.65, M: 0.72 },
              45: { S: 0.24, M: 0.23 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-100-400mm-f4-5-5-6-r-lm-ois-wr": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xf100-400mmf45-56-r-lm-ois-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/4.5",
        focalLength: 100,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.95, M: 0.95 },
              45: { S: 0.9, M: 0.9 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.95, M: 0.95 },
              45: { S: 0.9, M: 0.9 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.94, M: 0.94 },
              45: { S: 0.9, M: 0.87 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: null, M: null },
              45: { S: 0.88, M: 0.83 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.94, M: 0.92 },
              45: { S: 0.84, M: 0.78 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.93, M: 0.9 },
              45: { S: 0.79, M: 0.74 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.92, M: 0.87 },
              45: { S: 0.75, M: 0.68 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.91, M: 0.89 },
              45: { S: 0.74, M: 0.65 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.92, M: 0.9 },
              45: { S: 0.76, M: 0.62 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.92, M: 0.88 },
              45: { S: 0.74, M: 0.56 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.91, M: 0.86 },
              45: { S: 0.68, M: 0.5 },
            },
          },
        ],
      },
      {
        aperture: "f/4.5",
        focalLength: 400,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.94, M: 0.94 },
              45: { S: 0.84, M: 0.84 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.93, M: 0.93 },
              45: { S: 0.83, M: 0.81 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.93, M: 0.91 },
              45: { S: 0.79, M: 0.72 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.92, M: 0.9 },
              45: { S: 0.74, M: 0.62 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.91, M: 0.88 },
              45: { S: 0.68, M: 0.55 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.91, M: 0.88 },
              45: { S: 0.64, M: 0.52 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.9, M: 0.88 },
              45: { S: 0.61, M: 0.53 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.9, M: 0.88 },
              45: { S: 0.6, M: 0.56 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.9, M: 0.88 },
              45: { S: 0.62, M: 0.59 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.91, M: 0.88 },
              45: { S: 0.66, M: 0.61 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.92, M: 0.87 },
              45: { S: 0.7, M: 0.6 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-14mm-f2-8-r": {
    source: "https://fujifilm-x.com/global/products/lenses/xf14mmf28-r/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.89, M: 0.89 },
              45: { S: 0.72, M: 0.72 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.89, M: 0.89 },
              45: { S: 0.71, M: 0.72 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.89, M: 0.89 },
              45: { S: 0.72, M: 0.74 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.89, M: 0.89 },
              45: { S: 0.69, M: 0.73 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.88, M: 0.89 },
              45: { S: 0.64, M: 0.7 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.88, M: 0.88 },
              45: { S: 0.59, M: 0.67 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.88, M: 0.87 },
              45: { S: 0.6, M: 0.59 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.84, M: 0.87 },
              45: { S: 0.51, M: 0.55 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.73, M: 0.87 },
              45: { S: 0.49, M: 0.57 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.57, M: 0.86 },
              45: { S: 0.41, M: 0.52 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.45, M: 0.84 },
              45: { S: 0.31, M: 0.45 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-150-600mm-f5-6-8-r-lm-ois-wr": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xf150-600mmf56-8-r-lm-ois-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/5.6",
        focalLength: 150,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.99, M: 0.99 },
              45: { S: 1, M: 1 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.99, M: 0.99 },
              45: { S: null, M: null },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.99, M: 0.98 },
              45: { S: null, M: null },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.99, M: 0.97 },
              45: { S: null, M: null },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.99, M: 0.96 },
              45: { S: null, M: null },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.98, M: 0.95 },
              45: { S: 0.97, M: 0.97 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.98, M: 0.94 },
              45: { S: 0.94, M: 0.94 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.97, M: 0.93 },
              45: { S: 0.97, M: 0.97 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.97, M: 0.93 },
              45: { S: 0.99, M: 0.98 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.96, M: 0.92 },
              45: { S: 0.97, M: 0.99 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.96, M: 0.91 },
              45: { S: 0.95, M: 0.87 },
            },
          },
        ],
      },
      {
        aperture: "f/5.6",
        focalLength: 600,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 1, M: 1 },
              45: { S: 0.99, M: 0.99 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 1, M: 1 },
              45: { S: 0.98, M: 0.98 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 1, M: 1 },
              45: { S: 0.99, M: 0.97 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 1, M: 0.99 },
              45: { S: 0.98, M: 0.94 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 1, M: 0.99 },
              45: { S: 0.97, M: 0.9 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 1, M: 0.98 },
              45: { S: 0.96, M: 0.85 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 1, M: 0.97 },
              45: { S: 0.94, M: 0.81 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.99, M: 0.96 },
              45: { S: 0.92, M: 0.77 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.99, M: 0.96 },
              45: { S: 0.9, M: 0.78 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.99, M: 0.95 },
              45: { S: 0.89, M: 0.8 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.99, M: 0.93 },
              45: { S: 0.89, M: 0.74 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-16-50mm-f2-8-4-8-r-lm-wr": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xf16-50mmf28-48-r-lm-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        focalLength: 16,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.95, M: 0.95 },
              45: { S: 1, M: 1 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.95, M: 0.94 },
              45: { S: null, M: null },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.94, M: 0.93 },
              45: { S: null, M: null },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.94, M: 0.92 },
              45: { S: null, M: null },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.94, M: 0.92 },
              45: { S: null, M: null },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.95, M: 0.91 },
              45: { S: null, M: null },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.95, M: 0.9 },
              45: { S: 1, M: 1 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.94, M: 0.88 },
              45: { S: 0.94, M: 0.94 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.91, M: 0.85 },
              45: { S: 0.97, M: 0.97 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.85, M: 0.82 },
              45: { S: 0.91, M: 0.86 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.74, M: 0.79 },
              45: { S: 0.61, M: 0.62 },
            },
          },
        ],
      },
      {
        aperture: "f/2.8",
        focalLength: 50,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.95, M: 0.95 },
              45: { S: null, M: null },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.95, M: 0.95 },
              45: { S: null, M: null },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.95, M: 0.95 },
              45: { S: null, M: null },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.95, M: 0.95 },
              45: { S: null, M: null },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.95, M: 0.95 },
              45: { S: null, M: null },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.95, M: 0.95 },
              45: { S: null, M: null },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.94, M: 0.94 },
              45: { S: null, M: null },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.94, M: 0.94 },
              45: { S: null, M: null },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.93, M: 0.93 },
              45: { S: null, M: null },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.91, M: 0.93 },
              45: { S: null, M: null },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.89, M: 0.92 },
              45: { S: 0.83, M: null },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-16-55mm-f2-8-r-lm-wr": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xf16-55mmf28-r-lm-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        focalLength: 16,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.92, M: 0.92 },
              45: { S: 1, M: 1 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.92, M: 0.92 },
              45: { S: 0.89, M: 0.87 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.92, M: 0.92 },
              45: { S: 0.87, M: 0.8 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.92, M: 0.9 },
              45: { S: 0.83, M: 0.74 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.91, M: 0.89 },
              45: { S: 0.77, M: 0.67 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.91, M: 0.88 },
              45: { S: 0.74, M: 0.62 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.9, M: 0.86 },
              45: { S: 0.72, M: 0.58 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.9, M: 0.86 },
              45: { S: 0.73, M: 0.6 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.9, M: 0.86 },
              45: { S: 0.75, M: 0.6 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.88, M: 0.84 },
              45: { S: 0.72, M: 0.59 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.85, M: 0.84 },
              45: { S: 0.64, M: 0.62 },
            },
          },
        ],
      },
      {
        aperture: "f/2.8",
        focalLength: 55,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.91, M: 0.91 },
              45: { S: 0.87, M: 0.87 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.91, M: 0.9 },
              45: { S: 0.85, M: 0.82 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.91, M: 0.89 },
              45: { S: 0.82, M: 0.73 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.9, M: 0.87 },
              45: { S: 0.78, M: 0.68 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.89, M: 0.84 },
              45: { S: 0.71, M: 0.65 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.87, M: 0.83 },
              45: { S: 0.63, M: 0.64 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.85, M: 0.82 },
              45: { S: 0.56, M: 0.63 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.82, M: 0.81 },
              45: { S: 0.51, M: 0.57 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.8, M: 0.78 },
              45: { S: 0.46, M: 0.46 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.78, M: 0.75 },
              45: { S: 0.41, M: 0.38 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.76, M: 0.75 },
              45: { S: 0.39, M: 0.37 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-16-55mm-f2-8-r-lm-wr-ii": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xf16-55mmf28-r-lm-wr-ii/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        focalLength: 16,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.94, M: 0.94 },
              45: { S: 0.86, M: 0.86 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.94, M: 0.93 },
              45: { S: 0.84, M: 0.79 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.93, M: 0.92 },
              45: { S: 0.81, M: 0.76 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.93, M: 0.92 },
              45: { S: 0.79, M: 0.74 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.93, M: 0.93 },
              45: { S: 0.76, M: 0.77 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.93, M: 0.91 },
              45: { S: 0.74, M: 0.68 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.92, M: 0.89 },
              45: { S: 0.73, M: 0.58 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.93, M: 0.92 },
              45: { S: 0.75, M: 0.73 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.94, M: 0.93 },
              45: { S: 0.82, M: 0.79 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.94, M: 0.9 },
              45: { S: 0.87, M: 0.65 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.88, M: 0.84 },
              45: { S: 0.57, M: 0.33 },
            },
          },
        ],
      },
      {
        aperture: "f/2.8",
        focalLength: 55,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.94, M: 0.94 },
              45: { S: 0.87, M: 0.87 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.94, M: 0.94 },
              45: { S: 0.85, M: 0.83 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.94, M: 0.93 },
              45: { S: 0.83, M: 0.8 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.94, M: 0.92 },
              45: { S: 0.82, M: 0.77 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.93, M: 0.9 },
              45: { S: 0.8, M: 0.73 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.93, M: 0.87 },
              45: { S: 0.76, M: 0.71 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.92, M: 0.85 },
              45: { S: 0.7, M: 0.66 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.9, M: 0.84 },
              45: { S: 0.63, M: 0.66 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.88, M: 0.85 },
              45: { S: 0.54, M: 0.65 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.86, M: 0.84 },
              45: { S: 0.49, M: 0.56 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.85, M: 0.82 },
              45: { S: 0.48, M: 0.48 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-16-80mm-f4-r-ois-wr": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xf16-80mmf4-r-ois-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/4",
        focalLength: 16,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: null, M: null },
              45: { S: 1, M: 1 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: null, M: null },
              45: { S: 0.99, M: 0.99 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: null, M: null },
              45: { S: 0.84, M: 0.84 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: null, M: null },
              45: { S: 0.66, M: 0.66 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: null, M: null },
              45: { S: 0.52, M: 0.52 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: null, M: null },
              45: { S: 0.41, M: 0.41 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: null, M: null },
              45: { S: 0.41, M: 0.41 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: null, M: null },
              45: { S: 0.96, M: 0.52 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: null, M: null },
              45: { S: 0.84, M: 0.49 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: null, M: 0.92 },
              45: { S: 0.78, M: 0.28 },
            },
          },
        ],
      },
      {
        aperture: "f/4",
        focalLength: 80,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: null, M: null },
              45: { S: 1, M: 1 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: null, M: null },
              45: { S: 1, M: 0.98 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: null, M: null },
              45: { S: 0.98, M: 0.93 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: null, M: null },
              45: { S: 0.98, M: 0.85 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: null, M: null },
              45: { S: 0.98, M: 0.75 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: null, M: null },
              45: { S: 0.97, M: 0.65 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: null, M: null },
              45: { S: 0.91, M: 0.55 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: null, M: 1 },
              45: { S: 0.78, M: 0.44 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: null, M: 0.97 },
              45: { S: 0.75, M: 0.35 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: null, M: 0.95 },
              45: { S: 0.76, M: 0.33 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: null, M: null },
              45: { S: 0.72, M: 0.29 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-16mm-f1-4-r-wr": {
    source: "https://fujifilm-x.com/global/products/lenses/xf16mmf14-r-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.82, M: 0.82 },
              45: { S: 0.57, M: 0.57 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.83, M: 0.83 },
              45: { S: 0.58, M: 0.54 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.83, M: 0.83 },
              45: { S: 0.56, M: 0.5 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.84, M: 0.84 },
              45: { S: 0.54, M: 0.52 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.84, M: 0.84 },
              45: { S: 0.53, M: 0.53 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.82, M: 0.86 },
              45: { S: 0.51, M: 0.54 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.74, M: 0.86 },
              45: { S: 0.44, M: 0.6 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.62, M: 0.86 },
              45: { S: 0.46, M: 0.58 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.54, M: 0.84 },
              45: { S: 0.4, M: 0.49 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.49, M: 0.83 },
              45: { S: 0.31, M: 0.45 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.44, M: 0.83 },
              45: { S: 0.23, M: 0.45 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-16mm-f2-8-r-wr": {
    source: "https://fujifilm-x.com/global/products/lenses/xf16mmf28-r-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.91, M: 0.91 },
              45: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.91, M: 0.91 },
              45: { S: 0.78, M: 0.75 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.91, M: 0.89 },
              45: { S: 0.79, M: 0.69 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.91, M: 0.87 },
              45: { S: 0.8, M: 0.64 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.9, M: 0.86 },
              45: { S: 0.78, M: 0.62 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.88, M: 0.84 },
              45: { S: 0.69, M: 0.61 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.83, M: 0.81 },
              45: { S: 0.63, M: 0.6 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.73, M: 0.78 },
              45: { S: 0.57, M: 0.6 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.65, M: 0.76 },
              45: { S: 0.51, M: 0.57 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.57, M: 0.75 },
              45: { S: 0.42, M: 0.5 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.51, M: 0.71 },
              45: { S: 0.32, M: 0.45 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-18-120mm-f4-lm-pz-wr": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xf18-120mmf4-lm-pz-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/4",
        focalLength: 18,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.98, M: 0.98 },
              45: { S: 0.91, M: 0.91 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.98, M: 0.97 },
              45: { S: 0.9, M: 0.85 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.98, M: 0.95 },
              45: { S: 0.88, M: 0.7 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.97, M: 0.92 },
              45: { S: 0.85, M: 0.55 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.97, M: 0.89 },
              45: { S: 0.83, M: 0.47 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.96, M: 0.84 },
              45: { S: 0.78, M: 0.42 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.96, M: 0.8 },
              45: { S: 0.75, M: 0.4 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.95, M: 0.79 },
              45: { S: 0.73, M: 0.45 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.95, M: 0.78 },
              45: { S: 0.66, M: 0.47 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.95, M: 0.74 },
              45: { S: 0.65, M: 0.4 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.97, M: 0.79 },
              45: { S: 0.75, M: 0.4 },
            },
          },
        ],
      },
      {
        aperture: "f/4",
        focalLength: 120,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.96, M: 0.96 },
              45: { S: 0.84, M: 0.84 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.97, M: 0.95 },
              45: { S: 0.83, M: 0.77 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.96, M: 0.92 },
              45: { S: 0.81, M: 0.63 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.96, M: 0.87 },
              45: { S: 0.78, M: 0.51 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.95, M: 0.8 },
              45: { S: 0.74, M: 0.44 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.94, M: 0.73 },
              45: { S: 0.71, M: 0.46 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.94, M: 0.71 },
              45: { S: 0.7, M: 0.44 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.94, M: 0.7 },
              45: { S: 0.68, M: 0.39 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.92, M: 0.7 },
              45: { S: 0.61, M: 0.35 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.87, M: 0.69 },
              45: { S: 0.46, M: 0.33 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.8, M: 0.65 },
              45: { S: 0.32, M: 0.28 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-18-135mm-f3-5-5-6-r-lm-ois-wr": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xf18-135mmf35-56-r-lm-ois-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/3.5",
        focalLength: 18,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.89, M: 0.89 },
              45: { S: 0.74, M: 0.74 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.9, M: 0.89 },
              45: { S: 0.75, M: 0.71 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.9, M: 0.84 },
              45: { S: 0.78, M: 0.53 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.9, M: 0.84 },
              45: { S: 0.78, M: 0.52 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.9, M: 0.79 },
              45: { S: 0.81, M: 0.48 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.91, M: 0.76 },
              45: { S: 0.84, M: 0.55 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.9, M: 0.7 },
              45: { S: 0.79, M: 0.5 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.86, M: 0.67 },
              45: { S: 0.59, M: 0.47 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.77, M: 0.65 },
              45: { S: 0.43, M: 0.44 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.63, M: 0.63 },
              45: { S: 0.37, M: 0.35 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.49, M: 0.6 },
              45: { S: 0.27, M: 0.34 },
            },
          },
        ],
      },
      {
        aperture: "f/3.5",
        focalLength: 135,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.9, M: 0.9 },
              45: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.88, M: 0.87 },
              45: { S: 0.74, M: 0.68 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.87, M: 0.8 },
              45: { S: 0.65, M: 0.51 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.87, M: 0.8 },
              45: { S: 0.65, M: 0.5 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.86, M: 0.77 },
              45: { S: 0.61, M: 0.43 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.85, M: 0.76 },
              45: { S: 0.59, M: 0.39 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.85, M: 0.74 },
              45: { S: 0.58, M: 0.39 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.85, M: 0.72 },
              45: { S: 0.58, M: 0.41 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.85, M: 0.67 },
              45: { S: 0.56, M: 0.39 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.84, M: 0.62 },
              45: { S: 0.54, M: 0.34 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.82, M: 0.58 },
              45: { S: 0.48, M: 0.29 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-18-55mm-f2-8-4-0-r-lm-ois": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xf18-55mmf28-4-r-lm-ois/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        focalLength: 18,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.9, M: 0.9 },
              45: { S: 0.66, M: 0.66 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.89, M: 0.86 },
              45: { S: 0.61, M: 0.56 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.87, M: 0.83 },
              45: { S: 0.56, M: 0.44 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.86, M: 0.84 },
              45: { S: 0.54, M: 0.38 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.87, M: 0.86 },
              45: { S: 0.57, M: 0.43 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.89, M: 0.87 },
              45: { S: 0.64, M: 0.52 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.91, M: 0.85 },
              45: { S: 0.72, M: 0.5 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.91, M: 0.83 },
              45: { S: 0.74, M: 0.49 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.88, M: 0.81 },
              45: { S: 0.67, M: 0.51 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.84, M: 0.82 },
              45: { S: 0.57, M: 0.62 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.78, M: 0.8 },
              45: { S: 0.53, M: 0.47 },
            },
          },
        ],
      },
      {
        aperture: "f/2.8",
        focalLength: 55,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.9, M: 0.9 },
              45: { S: 0.66, M: 0.66 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.9, M: 0.88 },
              45: { S: 0.65, M: 0.66 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.89, M: 0.87 },
              45: { S: 0.65, M: 0.65 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.89, M: 0.85 },
              45: { S: 0.64, M: 0.59 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.88, M: 0.83 },
              45: { S: 0.62, M: 0.51 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.88, M: 0.81 },
              45: { S: 0.59, M: 0.48 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.87, M: 0.79 },
              45: { S: 0.57, M: 0.45 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.87, M: 0.79 },
              45: { S: 0.55, M: 0.42 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.85, M: 0.76 },
              45: { S: 0.48, M: 0.44 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.85, M: 0.8 },
              45: { S: 0.38, M: 0.52 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.85, M: 0.72 },
              45: { S: 0.36, M: 0.25 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-18mm-f1-4-r-lm-wr": {
    source: "https://fujifilm-x.com/global/products/lenses/xf18mmf14-r-lm-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.97, M: 0.97 },
              45: { S: 0.75, M: 0.75 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.97, M: 0.97 },
              45: { S: 0.74, M: 0.73 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.97, M: 0.97 },
              45: { S: 0.74, M: 0.7 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.97, M: 0.96 },
              45: { S: 0.72, M: 0.67 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.96, M: 0.95 },
              45: { S: 0.69, M: 0.66 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.96, M: 0.94 },
              45: { S: 0.66, M: 0.65 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.95, M: 0.94 },
              45: { S: 0.62, M: 0.65 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.94, M: 0.96 },
              45: { S: 0.61, M: 0.65 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.93, M: 0.96 },
              45: { S: 0.58, M: 0.68 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.88, M: 0.94 },
              45: { S: 0.54, M: 0.61 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.8, M: 0.93 },
              45: { S: 0.53, M: 0.57 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-18mm-f2-0-r": {
    source: "https://fujifilm-x.com/global/products/lenses/xf18mmf2-r/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.0",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.83, M: 0.83 },
              45: { S: 0.62, M: 0.62 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.84, M: 0.82 },
              45: { S: 0.62, M: 0.58 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.84, M: 0.82 },
              45: { S: 0.63, M: 0.54 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.84, M: 0.81 },
              45: { S: 0.64, M: 0.55 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.83, M: 0.8 },
              45: { S: 0.65, M: 0.55 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.8, M: 0.78 },
              45: { S: 0.58, M: 0.48 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.75, M: 0.75 },
              45: { S: 0.5, M: 0.39 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.68, M: 0.73 },
              45: { S: 0.45, M: 0.33 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.62, M: 0.68 },
              45: { S: 0.42, M: 0.29 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.57, M: 0.58 },
              45: { S: 0.39, M: 0.28 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.53, M: 0.41 },
              45: { S: 0.32, M: 0.15 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-200mm-f2-0-r-lm-ois-wr": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xf200mmf2-r-lm-ois-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.0",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.89, M: 0.89 },
              45: { S: 0.83, M: 0.83 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.89, M: 0.89 },
              45: { S: 0.82, M: 0.82 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.88, M: 0.88 },
              45: { S: 0.82, M: 0.8 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.88, M: 0.88 },
              45: { S: 0.8, M: 0.79 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.88, M: 0.88 },
              45: { S: 0.78, M: 0.77 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.88, M: 0.88 },
              45: { S: 0.76, M: 0.77 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.88, M: 0.88 },
              45: { S: 0.75, M: 0.76 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.88, M: 0.88 },
              45: { S: 0.76, M: 0.75 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.88, M: 0.88 },
              45: { S: 0.78, M: 0.74 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.88, M: 0.88 },
              45: { S: 0.76, M: 0.74 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.86, M: 0.88 },
              45: { S: 0.7, M: 0.73 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-23mm-f1-4-r": {
    source: "https://fujifilm-x.com/global/products/lenses/xf23mmf14-r/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.79, M: 0.79 },
              45: { S: 0.62, M: 0.62 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.8, M: 0.79 },
              45: { S: 0.61, M: 0.59 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.79, M: 0.78 },
              45: { S: 0.6, M: 0.56 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.8, M: 0.78 },
              45: { S: 0.57, M: 0.53 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.8, M: 0.78 },
              45: { S: 0.52, M: 0.53 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.79, M: 0.78 },
              45: { S: 0.47, M: 0.53 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.76, M: 0.79 },
              45: { S: 0.41, M: 0.54 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.7, M: 0.81 },
              45: { S: 0.43, M: 0.56 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.61, M: 0.81 },
              45: { S: 0.45, M: 0.55 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.51, M: 0.8 },
              45: { S: 0.39, M: 0.58 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.41, M: 0.81 },
              45: { S: 0.25, M: 0.61 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-23mm-f2-0-r-wr": {
    source: "https://fujifilm-x.com/global/products/lenses/xf23mmf2-r-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.0",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.82, M: 0.82 },
              45: { S: 0.63, M: 0.63 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.82, M: 0.82 },
              45: { S: 0.63, M: 0.61 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.8, M: 0.8 },
              45: { S: 0.62, M: 0.55 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.81, M: 0.79 },
              45: { S: 0.58, M: 0.51 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.78, M: 0.78 },
              45: { S: 0.52, M: 0.49 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.75, M: 0.77 },
              45: { S: 0.46, M: 0.47 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.73, M: 0.77 },
              45: { S: 0.43, M: 0.46 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.7, M: 0.76 },
              45: { S: 0.42, M: 0.46 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.67, M: 0.76 },
              45: { S: 0.45, M: 0.45 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.62, M: 0.75 },
              45: { S: 0.41, M: 0.43 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.57, M: 0.73 },
              45: { S: 0.36, M: 0.41 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-23mm-f2-8-r-wr": {
    source: "https://fujifilm-x.com/global/products/lenses/xf23mmf28-r-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              45: { S: 1, M: 1 },
            },
          },
          {
            position: 2.84,
            samples: {
              45: { S: 1, M: 1 },
            },
          },
          {
            position: 4.26,
            samples: {
              45: { S: 1, M: 1 },
            },
          },
          {
            position: 7.1,
            samples: {
              45: { S: 0.99, M: 0.99 },
            },
          },
          {
            position: 8.52,
            samples: {
              45: { S: 0.97, M: 0.95 },
            },
          },
          {
            position: 9.94,
            samples: {
              45: { S: 0.9, M: 0.86 },
            },
          },
          {
            position: 11.36,
            samples: {
              45: { S: 0.83, M: 0.77 },
            },
          },
          {
            position: 12.78,
            samples: {
              45: { S: 0.77, M: 0.72 },
            },
          },
          {
            position: 14.2,
            samples: {
              45: { S: 0.76, M: 0.71 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-27mm-f2-8-r": {
    source: "https://fujifilm-x.com/global/products/lenses/xf27mmf28/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.89, M: 0.89 },
              45: { S: 0.72, M: 0.72 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.89, M: 0.87 },
              45: { S: 0.69, M: 0.65 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.88, M: 0.86 },
              45: { S: 0.63, M: 0.59 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.86, M: 0.84 },
              45: { S: 0.57, M: 0.56 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.85, M: 0.83 },
              45: { S: 0.51, M: 0.56 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.84, M: 0.82 },
              45: { S: 0.47, M: 0.52 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.82, M: 0.81 },
              45: { S: 0.46, M: 0.5 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.8, M: 0.82 },
              45: { S: 0.5, M: 0.49 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.76, M: 0.82 },
              45: { S: 0.55, M: 0.46 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.69, M: 0.82 },
              45: { S: 0.53, M: 0.42 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.59, M: 0.72 },
              45: { S: 0.39, M: 0.33 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-27mm-f2-8-r-wr": {
    source: "https://fujifilm-x.com/global/products/lenses/xf27mmf28-r-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.89, M: 0.89 },
              45: { S: 0.72, M: 0.72 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.89, M: 0.87 },
              45: { S: 0.69, M: 0.65 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.88, M: 0.86 },
              45: { S: 0.63, M: 0.59 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.86, M: 0.84 },
              45: { S: 0.57, M: 0.56 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.85, M: 0.83 },
              45: { S: 0.51, M: 0.56 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.84, M: 0.82 },
              45: { S: 0.47, M: 0.52 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.82, M: 0.81 },
              45: { S: 0.46, M: 0.5 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.8, M: 0.82 },
              45: { S: 0.5, M: 0.49 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.76, M: 0.82 },
              45: { S: 0.55, M: 0.46 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.69, M: 0.82 },
              45: { S: 0.53, M: 0.42 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.59, M: 0.72 },
              45: { S: 0.39, M: 0.33 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-30mm-f2-8-r-lm-wr-macro": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xf30mmf28-r-lm-wr-macro/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.97, M: 0.97 },
              45: { S: 0.92, M: 0.92 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.96, M: 0.96 },
              45: { S: 0.93, M: 0.91 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.97, M: 0.96 },
              45: { S: 0.91, M: 0.85 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.94, M: 0.94 },
              45: { S: 0.8, M: 0.75 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.91, M: 0.93 },
              45: { S: 0.67, M: 0.63 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.84, M: 0.91 },
              45: { S: 0.61, M: 0.54 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.78, M: 0.9 },
              45: { S: 0.55, M: 0.48 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.73, M: 0.89 },
              45: { S: 0.52, M: 0.48 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.7, M: 0.9 },
              45: { S: 0.49, M: 0.53 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.68, M: 0.91 },
              45: { S: 0.49, M: 0.57 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.66, M: 0.9 },
              45: { S: 0.49, M: 0.54 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-33mm-f1-4-r-lm-wr": {
    source: "https://fujifilm-x.com/global/products/lenses/xf33mmf14-r-lm-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.89, M: 0.89 },
              45: { S: 0.76, M: 0.76 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.89, M: 0.89 },
              45: { S: 0.76, M: 0.75 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.9, M: 0.89 },
              45: { S: 0.75, M: 0.7 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.89, M: 0.88 },
              45: { S: 0.72, M: 0.66 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.88, M: 0.89 },
              45: { S: 0.66, M: 0.69 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.86, M: 0.89 },
              45: { S: 0.59, M: 0.69 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.82, M: 0.88 },
              45: { S: 0.54, M: 0.64 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.77, M: 0.88 },
              45: { S: 0.51, M: 0.62 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.72, M: 0.88 },
              45: { S: 0.51, M: 0.62 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.68, M: 0.87 },
              45: { S: 0.53, M: 0.63 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.63, M: 0.86 },
              45: { S: 0.5, M: 0.59 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-35mm-f1-4-r": {
    source: "https://fujifilm-x.com/global/products/lenses/xf35mmf14-r/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.81, M: 0.81 },
              45: { S: 0.56, M: 0.56 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.81, M: 0.82 },
              45: { S: 0.58, M: 0.56 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.8, M: 0.82 },
              45: { S: 0.58, M: 0.53 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.79, M: 0.82 },
              45: { S: 0.54, M: 0.48 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.75, M: 0.82 },
              45: { S: 0.48, M: 0.43 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.7, M: 0.81 },
              45: { S: 0.42, M: 0.4 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.66, M: 0.8 },
              45: { S: 0.36, M: 0.39 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.63, M: 0.81 },
              45: { S: 0.33, M: 0.4 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.58, M: 0.81 },
              45: { S: 0.35, M: 0.41 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.51, M: 0.81 },
              45: { S: 0.36, M: 0.41 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.43, M: 0.8 },
              45: { S: 0.26, M: 0.37 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-35mm-f2-0-r-wr": {
    source: "https://fujifilm-x.com/global/products/lenses/xf35mmf2-r-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.0",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.88, M: 0.88 },
              45: { S: 0.76, M: 0.76 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.89, M: 0.88 },
              45: { S: 0.75, M: 0.73 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.89, M: 0.88 },
              45: { S: 0.74, M: 0.73 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.89, M: 0.88 },
              45: { S: 0.71, M: 0.73 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.89, M: 0.88 },
              45: { S: 0.67, M: 0.71 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.87, M: 0.88 },
              45: { S: 0.6, M: 0.67 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.85, M: 0.86 },
              45: { S: 0.59, M: 0.51 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.79, M: 0.84 },
              45: { S: 0.51, M: 0.47 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.57, M: 0.8 },
              45: { S: 0.13, M: 0.24 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.28, M: 0.75 },
              45: { S: 0.02, M: 0.21 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.12, M: 0.75 },
              45: { S: 0.03, M: 0.19 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-50-140mm-f2-8-r-lm-ois-wr": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xf50-140mmf28-r-lm-ois-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        focalLength: 50,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.94, M: 0.94 },
              45: { S: 0.84, M: 0.84 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.94, M: 0.94 },
              45: { S: 0.85, M: 0.85 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.93, M: 0.93 },
              45: { S: 0.83, M: 0.81 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.93, M: 0.93 },
              45: { S: 0.8, M: 0.77 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.93, M: 0.93 },
              45: { S: 0.76, M: 0.73 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.93, M: 0.93 },
              45: { S: 0.73, M: 0.72 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.92, M: 0.92 },
              45: { S: 0.71, M: 0.7 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.92, M: 0.92 },
              45: { S: 0.74, M: 0.66 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.93, M: 0.9 },
              45: { S: 0.76, M: 0.6 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.92, M: 0.9 },
              45: { S: 0.68, M: 0.56 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.88, M: 0.9 },
              45: { S: 0.54, M: 0.55 },
            },
          },
        ],
      },
      {
        aperture: "f/2.8",
        focalLength: 140,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.93, M: 0.93 },
              45: { S: 0.91, M: 0.91 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.93, M: 0.93 },
              45: { S: 0.89, M: 0.88 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.93, M: 0.92 },
              45: { S: 0.88, M: 0.81 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.93, M: 0.91 },
              45: { S: 0.87, M: 0.77 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.93, M: 0.9 },
              45: { S: 0.87, M: 0.74 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.92, M: 0.9 },
              45: { S: 0.85, M: 0.7 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.92, M: 0.89 },
              45: { S: 0.83, M: 0.67 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.92, M: 0.88 },
              45: { S: 0.81, M: 0.67 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.92, M: 0.88 },
              45: { S: 0.78, M: 0.69 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.91, M: 0.86 },
              45: { S: 0.77, M: 0.68 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.91, M: 0.85 },
              45: { S: 0.76, M: 0.67 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-500mm-f5-6-r-lm-ois-wr": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xf500mmf56-r-lm-ois-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/5.6",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.93, M: 0.93 },
              45: { S: 0.9, M: 0.9 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.92, M: 0.93 },
              45: { S: 0.9, M: 0.9 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.92, M: 0.93 },
              45: { S: 0.9, M: 0.91 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.93, M: 0.93 },
              45: { S: 0.91, M: 0.9 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.93, M: 0.93 },
              45: { S: 0.91, M: 0.89 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.93, M: 0.92 },
              45: { S: 0.91, M: 0.88 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.93, M: 0.92 },
              45: { S: 0.92, M: 0.86 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.93, M: 0.92 },
              45: { S: 0.92, M: 0.85 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.93, M: 0.92 },
              45: { S: 0.92, M: 0.83 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.93, M: 0.92 },
              45: { S: 0.91, M: 0.83 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.93, M: 0.92 },
              45: { S: 0.91, M: 0.82 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-50mm-f1-0-r-wr": {
    source: "https://fujifilm-x.com/global/products/lenses/xf50mmf1-r-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.0",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.72, M: 0.72 },
              45: { S: 0.53, M: 0.53 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.74, M: 0.74 },
              45: { S: 0.54, M: 0.54 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.76, M: 0.77 },
              45: { S: 0.55, M: 0.55 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.76, M: 0.77 },
              45: { S: 0.52, M: 0.52 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.76, M: 0.74 },
              45: { S: 0.46, M: 0.45 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.75, M: 0.72 },
              45: { S: 0.39, M: 0.4 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.73, M: 0.7 },
              45: { S: 0.31, M: 0.35 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.72, M: 0.7 },
              45: { S: 0.3, M: 0.34 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.69, M: 0.71 },
              45: { S: 0.37, M: 0.33 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.6, M: 0.74 },
              45: { S: 0.42, M: 0.33 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.48, M: 0.76 },
              45: { S: 0.31, M: 0.43 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-50mm-f2-0-r-wr": {
    source: "https://fujifilm-x.com/global/products/lenses/xf50mmf2-r-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.0",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.83, M: 0.83 },
              45: { S: 0.7, M: 0.7 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.83, M: 0.83 },
              45: { S: 0.7, M: 0.67 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.83, M: 0.83 },
              45: { S: 0.7, M: 0.67 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.84, M: 0.83 },
              45: { S: 0.71, M: 0.66 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.85, M: 0.83 },
              45: { S: 0.7, M: 0.61 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.85, M: 0.82 },
              45: { S: 0.68, M: 0.52 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.85, M: 0.8 },
              45: { S: 0.68, M: 0.43 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.84, M: 0.8 },
              45: { S: 0.65, M: 0.4 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.81, M: 0.83 },
              45: { S: 0.56, M: 0.49 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.71, M: 0.87 },
              45: { S: 0.47, M: 0.59 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.61, M: 0.88 },
              45: { S: 0.39, M: 0.55 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-55-200mm-f3-5-4-8-r-lm-ois": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xf55-200mmf35-48-r-lm-ois/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/3.5",
        focalLength: 55,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.91, M: 0.91 },
              45: { S: 0.8, M: 0.8 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.91, M: 0.9 },
              45: { S: 0.8, M: 0.78 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.91, M: 0.9 },
              45: { S: 0.78, M: 0.73 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.9, M: 0.89 },
              45: { S: 0.76, M: 0.68 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.9, M: 0.88 },
              45: { S: 0.74, M: 0.64 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.9, M: 0.87 },
              45: { S: 0.72, M: 0.6 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.9, M: 0.86 },
              45: { S: 0.72, M: 0.59 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.9, M: 0.85 },
              45: { S: 0.73, M: 0.53 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.91, M: 0.83 },
              45: { S: 0.76, M: 0.47 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.9, M: 0.79 },
              45: { S: 0.76, M: 0.34 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.87, M: 0.74 },
              45: { S: 0.63, M: 0.23 },
            },
          },
        ],
      },
      {
        aperture: "f/3.5",
        focalLength: 200,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.88, M: 0.88 },
              45: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.88, M: 0.87 },
              45: { S: 0.76, M: 0.73 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.87, M: 0.85 },
              45: { S: 0.73, M: 0.68 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.87, M: 0.84 },
              45: { S: 0.69, M: 0.61 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.86, M: 0.82 },
              45: { S: 0.67, M: 0.59 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.86, M: 0.81 },
              45: { S: 0.67, M: 0.6 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.86, M: 0.8 },
              45: { S: 0.69, M: 0.59 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.87, M: 0.77 },
              45: { S: 0.72, M: 0.56 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.87, M: 0.76 },
              45: { S: 0.73, M: 0.54 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.87, M: 0.74 },
              45: { S: 0.73, M: 0.53 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.87, M: 0.71 },
              45: { S: 0.72, M: 0.44 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-56mm-f1-2-r": {
    source: "https://fujifilm-x.com/global/products/lenses/xf56mmf12-r/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.2",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.8, M: 0.8 },
              45: { S: 0.64, M: 0.64 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.8, M: 0.79 },
              45: { S: 0.62, M: 0.57 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.8, M: 0.77 },
              45: { S: 0.58, M: 0.5 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.79, M: 0.74 },
              45: { S: 0.52, M: 0.48 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.78, M: 0.75 },
              45: { S: 0.48, M: 0.46 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.78, M: 0.78 },
              45: { S: 0.44, M: 0.43 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.77, M: 0.8 },
              45: { S: 0.38, M: 0.44 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.76, M: 0.82 },
              45: { S: 0.37, M: 0.48 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.74, M: 0.83 },
              45: { S: 0.43, M: 0.52 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.68, M: 0.83 },
              45: { S: 0.46, M: 0.51 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.58, M: 0.83 },
              45: { S: 0.4, M: 0.46 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-56mm-f1-2-r-apd": {
    source: "https://fujifilm-x.com/global/products/lenses/xf56mmf12-r-apd/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.2",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.85, M: 0.85 },
              45: { S: 0.67, M: 0.67 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.85, M: 0.84 },
              45: { S: 0.67, M: 0.62 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.85, M: 0.81 },
              45: { S: 0.62, M: 0.55 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.84, M: 0.79 },
              45: { S: 0.54, M: 0.55 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.82, M: 0.79 },
              45: { S: 0.47, M: 0.53 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.81, M: 0.82 },
              45: { S: 0.41, M: 0.52 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.81, M: 0.85 },
              45: { S: 0.38, M: 0.56 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.83, M: 0.88 },
              45: { S: 0.43, M: 0.62 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.83, M: 0.89 },
              45: { S: 0.53, M: 0.64 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.79, M: 0.89 },
              45: { S: 0.57, M: 0.61 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.74, M: 0.88 },
              45: { S: 0.51, M: 0.56 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-56mm-f1-2-r-wr": {
    source: "https://fujifilm-x.com/global/products/lenses/xf56mmf12-r-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.2",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.85, M: 0.85 },
              45: { S: 0.87, M: 0.87 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.85, M: 0.85 },
              45: { S: 0.87, M: 0.85 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.84, M: 0.84 },
              45: { S: 0.86, M: 0.81 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.84, M: 0.84 },
              45: { S: 0.86, M: 0.82 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.84, M: 0.84 },
              45: { S: 0.85, M: 0.83 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.84, M: 0.84 },
              45: { S: 0.79, M: 0.8 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.82, M: 0.83 },
              45: { S: 0.7, M: 0.72 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.81, M: 0.83 },
              45: { S: 0.59, M: 0.69 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.79, M: 0.83 },
              45: { S: 0.54, M: 0.72 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.75, M: 0.84 },
              45: { S: 0.61, M: 0.76 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.67, M: 0.84 },
              45: { S: 0.57, M: 0.76 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-60mm-f2-4-r-macro": {
    source: "https://fujifilm-x.com/global/products/lenses/xf60mmf24-r-macro/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.85, M: 0.85 },
              45: { S: 0.66, M: 0.66 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.85, M: 0.85 },
              45: { S: 0.66, M: 0.66 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.86, M: 0.86 },
              45: { S: 0.65, M: 0.66 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.86, M: 0.86 },
              45: { S: 0.65, M: 0.66 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.86, M: 0.86 },
              45: { S: 0.63, M: 0.67 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.86, M: 0.87 },
              45: { S: 0.62, M: 0.68 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.86, M: 0.87 },
              45: { S: 0.61, M: 0.68 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.85, M: 0.86 },
              45: { S: 0.62, M: 0.66 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.83, M: 0.85 },
              45: { S: 0.58, M: 0.59 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.78, M: 0.83 },
              45: { S: 0.49, M: 0.51 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.67, M: 0.76 },
              45: { S: 0.38, M: 0.42 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-70-300mm-f4-5-6-r-lm-ois-wr": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xf70-300mmf4-56-r-lm-ois-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/4.5",
        focalLength: 70,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.98, M: 0.98 },
              45: { S: 0.88, M: 0.88 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.98, M: 0.98 },
              45: { S: 0.89, M: 0.87 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.98, M: 0.97 },
              45: { S: 0.88, M: 0.83 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.98, M: 0.97 },
              45: { S: 0.87, M: 0.79 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.98, M: 0.96 },
              45: { S: 0.87, M: 0.73 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.98, M: 0.95 },
              45: { S: 0.86, M: 0.68 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.98, M: 0.94 },
              45: { S: 0.86, M: 0.64 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.97, M: 0.93 },
              45: { S: 0.85, M: 0.62 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.96, M: 0.92 },
              45: { S: 0.81, M: 0.59 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.93, M: 0.91 },
              45: { S: 0.68, M: 0.55 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.88, M: 0.9 },
              45: { S: 0.4, M: 0.53 },
            },
          },
        ],
      },
      {
        aperture: "f/4.5",
        focalLength: 300,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.91, M: 0.91 },
              45: { S: 0.78, M: 0.78 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.91, M: 0.9 },
              45: { S: 0.77, M: 0.75 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.9, M: 0.88 },
              45: { S: 0.74, M: 0.65 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.89, M: 0.85 },
              45: { S: 0.69, M: 0.57 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.89, M: 0.83 },
              45: { S: 0.66, M: 0.51 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.88, M: 0.81 },
              45: { S: 0.64, M: 0.48 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.88, M: 0.8 },
              45: { S: 0.63, M: 0.47 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.88, M: 0.79 },
              45: { S: 0.63, M: 0.49 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.88, M: 0.78 },
              45: { S: 0.65, M: 0.53 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.88, M: 0.75 },
              45: { S: 0.65, M: 0.55 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.87, M: 0.72 },
              45: { S: 0.63, M: 0.55 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-8-16mm-f2-8-r-lm-wr": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xf8-16mmf28-r-lm-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        focalLength: 8,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.92, M: 0.92 },
              45: { S: 0.87, M: 0.87 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.92, M: 0.92 },
              45: { S: 0.87, M: 0.86 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.92, M: 0.92 },
              45: { S: 0.85, M: 0.84 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.91, M: 0.91 },
              45: { S: 0.82, M: 0.8 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.91, M: 0.91 },
              45: { S: 0.78, M: 0.79 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.91, M: 0.91 },
              45: { S: 0.78, M: 0.79 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.91, M: 0.89 },
              45: { S: 0.82, M: 0.69 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.91, M: 0.88 },
              45: { S: 0.78, M: 0.64 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.89, M: 0.86 },
              45: { S: 0.66, M: 0.6 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.85, M: 0.84 },
              45: { S: 0.48, M: 0.52 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.8, M: 0.8 },
              45: { S: 0.31, M: 0.43 },
            },
          },
        ],
      },
      {
        aperture: "f/2.8",
        focalLength: 16,
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.92, M: 0.92 },
              45: { S: 0.82, M: 0.82 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.92, M: 0.92 },
              45: { S: 0.82, M: 0.83 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.92, M: 0.92 },
              45: { S: 0.8, M: 0.82 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.91, M: 0.91 },
              45: { S: 0.76, M: 0.79 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.91, M: 0.91 },
              45: { S: 0.72, M: 0.75 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.9, M: 0.9 },
              45: { S: 0.71, M: 0.71 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.9, M: 0.89 },
              45: { S: 0.7, M: 0.66 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.9, M: 0.88 },
              45: { S: 0.69, M: 0.63 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.87, M: 0.89 },
              45: { S: 0.59, M: 0.6 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.84, M: 0.88 },
              45: { S: 0.48, M: 0.57 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.79, M: 0.87 },
              45: { S: 0.39, M: 0.54 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-80mm-f2-8-r-lm-ois-wr-macro": {
    source:
      "https://fujifilm-x.com/global/products/lenses/xf80mmf28-r-lm-ois-wr-macro/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.91, M: 0.91 },
              45: { S: 0.78, M: 0.78 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.91, M: 0.91 },
              45: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.9, M: 0.9 },
              45: { S: 0.77, M: 0.75 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.9, M: 0.9 },
              45: { S: 0.75, M: 0.71 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.88, M: 0.88 },
              45: { S: 0.7, M: 0.64 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.88, M: 0.88 },
              45: { S: 0.66, M: 0.6 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: null, M: null },
              45: { S: 0.62, M: 0.6 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.87, M: 0.89 },
              45: { S: 0.62, M: 0.65 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.91, M: 0.89 },
              45: { S: 0.73, M: 0.68 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.91, M: 0.87 },
              45: { S: 0.81, M: 0.63 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.91, M: 0.85 },
              45: { S: 0.82, M: 0.56 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-8mm-f3-5-r-wr": {
    source: "https://fujifilm-x.com/global/products/lenses/xf8mmf35-r-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/3.5",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              45: { S: 1, M: 1 },
            },
          },
          {
            position: 11.36,
            samples: {
              45: { S: 0.91, M: 0.91 },
            },
          },
          {
            position: 12.78,
            samples: {
              45: { S: 0.83, M: 0.78 },
            },
          },
          {
            position: 14.2,
            samples: {
              45: { S: 0.73, M: 0.69 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-90mm-f2-0-r-lm-wr": {
    source: "https://fujifilm-x.com/global/products/lenses/xf90mmf2-r-lm-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.0",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.89, M: 0.89 },
              45: { S: 0.69, M: 0.69 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: 0.89, M: 0.89 },
              45: { S: 0.69, M: 0.69 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.88, M: 0.88 },
              45: { S: 0.68, M: 0.68 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.88, M: 0.88 },
              45: { S: 0.69, M: 0.68 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.88, M: 0.88 },
              45: { S: 0.68, M: 0.68 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.87, M: 0.88 },
              45: { S: 0.67, M: 0.67 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.86, M: 0.88 },
              45: { S: 0.66, M: 0.67 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.85, M: 0.87 },
              45: { S: 0.65, M: 0.64 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.84, M: 0.86 },
              45: { S: 0.58, M: 0.58 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.83, M: 0.85 },
              45: { S: 0.52, M: 0.52 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.8, M: 0.84 },
              45: { S: 0.46, M: 0.46 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-gf-23mm-f4-r-lm-wr": {
    source: "https://fujifilm-x.com/en-us/products/lenses/gf23mmf4-r-lm-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.99, M: 0.99 },
              20: { S: 0.97, M: 0.97 },
              40: { S: 0.89, M: 0.89 },
            },
          },
          {
            position: 2.69,
            samples: {
              15: { S: 0.99, M: 0.99 },
              20: { S: 0.97, M: 0.97 },
              40: { S: 0.9, M: 0.9 },
            },
          },
          {
            position: 5.38,
            samples: {
              15: { S: 0.99, M: 0.99 },
              20: { S: 0.97, M: 0.95 },
              40: { S: 0.88, M: 0.86 },
            },
          },
          {
            position: 8.07,
            samples: {
              15: { S: 0.99, M: 0.99 },
              20: { S: 0.95, M: 0.94 },
              40: { S: 0.84, M: 0.84 },
            },
          },
          {
            position: 10.76,
            samples: {
              15: { S: 0.98, M: 0.98 },
              20: { S: 0.94, M: 0.92 },
              40: { S: 0.79, M: 0.82 },
            },
          },
          {
            position: 13.45,
            samples: {
              15: { S: 0.98, M: 0.98 },
              20: { S: 0.92, M: 0.91 },
              40: { S: 0.74, M: 0.72 },
            },
          },
          {
            position: 16.14,
            samples: {
              15: { S: 0.97, M: 0.97 },
              20: { S: 0.89, M: 0.9 },
              40: { S: 0.71, M: 0.73 },
            },
          },
          {
            position: 18.83,
            samples: {
              15: { S: 0.94, M: 0.96 },
              20: { S: 0.81, M: 0.89 },
              40: { S: 0.67, M: 0.71 },
            },
          },
          {
            position: 21.52,
            samples: {
              15: { S: 0.88, M: 0.96 },
              20: { S: 0.71, M: 0.89 },
              40: { S: 0.6, M: 0.74 },
            },
          },
          {
            position: 24.21,
            samples: {
              15: { S: 0.82, M: 0.94 },
              20: { S: 0.63, M: 0.86 },
              40: { S: 0.53, M: 0.7 },
            },
          },
          {
            position: 26.9,
            samples: {
              15: { S: 0.76, M: 0.92 },
              20: { S: 0.58, M: 0.79 },
              40: { S: 0.48, M: 0.56 },
            },
          },
        ],
      },
    ],
  },
  "fujifilm-xf-23mm-f1-4-r-lm-wr": {
    source: "https://fujifilm-x.com/global/products/lenses/xf23mmf14-r-lm-wr/",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              15: { S: 0.96, M: 0.96 },
              45: { S: 0.8, M: 0.8 },
            },
          },
          {
            position: 1.42,
            samples: {
              15: { S: null, M: null },
              45: { S: 0.79, M: 0.75 },
            },
          },
          {
            position: 2.84,
            samples: {
              15: { S: 0.95, M: 0.95 },
              45: { S: 0.76, M: 0.72 },
            },
          },
          {
            position: 4.26,
            samples: {
              15: { S: 0.95, M: 0.96 },
              45: { S: 0.73, M: 0.72 },
            },
          },
          {
            position: 5.68,
            samples: {
              15: { S: 0.93, M: 0.96 },
              45: { S: 0.66, M: 0.72 },
            },
          },
          {
            position: 7.1,
            samples: {
              15: { S: 0.91, M: 0.96 },
              45: { S: 0.58, M: 0.72 },
            },
          },
          {
            position: 8.52,
            samples: {
              15: { S: 0.88, M: 0.95 },
              45: { S: 0.53, M: 0.69 },
            },
          },
          {
            position: 9.94,
            samples: {
              15: { S: 0.85, M: 0.94 },
              45: { S: 0.51, M: 0.68 },
            },
          },
          {
            position: 11.36,
            samples: {
              15: { S: 0.83, M: 0.94 },
              45: { S: 0.53, M: 0.67 },
            },
          },
          {
            position: 12.78,
            samples: {
              15: { S: 0.82, M: 0.92 },
              45: { S: 0.56, M: 0.6 },
            },
          },
          {
            position: 14.2,
            samples: {
              15: { S: 0.81, M: 0.86 },
              45: { S: 0.58, M: 0.48 },
            },
          },
        ],
      },
    ],
  },
  "ttartisan-11mm-f2-8-fisheye-gfx": {
    source: "https://www.ttartisan.com/?full-frame-lenses/62.html",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.82, M: 0.82 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.82, M: 0.81 },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.96, M: 0.97 },
              30: { S: 0.75, M: 0.82 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.95, M: 0.97 },
              30: { S: 0.7, M: 0.82 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.94, M: 0.97 },
              30: { S: 0.65, M: 0.83 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.94, M: 0.97 },
              30: { S: 0.65, M: 0.84 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.66, M: 0.82 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.64, M: 0.73 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.92, M: 0.88 },
              30: { S: 0.61, M: 0.55 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.8, M: 0.88 },
              30: { S: 0.56, M: 0.4 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.87, M: 0.71 },
              30: { S: 0.42, M: 0.34 },
            },
          },
        ],
      },
      {
        aperture: "f/5.6",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.81, M: 0.81 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.79, M: 0.81 },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.94, M: 0.93 },
              30: { S: 0.74, M: 0.81 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.94, M: 0.92 },
              30: { S: 0.67, M: 0.8 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.93, M: 0.91 },
              30: { S: 0.61, M: 0.79 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.9, M: 0.93 },
              30: { S: 0.58, M: 0.77 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.9, M: 0.93 },
              30: { S: 0.58, M: 0.76 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.9, M: 0.93 },
              30: { S: 0.59, M: 0.77 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.9, M: 0.93 },
              30: { S: 0.59, M: 0.78 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.9, M: 0.94 },
              30: { S: 0.58, M: 0.8 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.89, M: 0.94 },
              30: { S: 0.55, M: 0.8 },
            },
          },
        ],
      },
    ],
  },
  "ttartisan-23mm-f1-4": {
    source: "https://www.ttartisan.com/?aps-c-lenses/76.html",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.58, M: 0.58 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.92, M: 0.93 },
              30: { S: 0.57, M: 0.58 },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.55, M: 0.6 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.55, M: 0.6 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.57, M: 0.58 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.93, M: 0.92 },
              30: { S: 0.57, M: 0.54 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.92, M: 0.9 },
              30: { S: 0.53, M: 0.48 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.9, M: 0.86 },
              30: { S: 0.51, M: 0.46 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.88, M: 0.8 },
              30: { S: 0.48, M: 0.51 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.85, M: 0.71 },
              30: { S: 0.37, M: 0.5 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.78, M: 0.58 },
              30: { S: 0.18, M: 0.36 },
            },
          },
        ],
      },
      {
        aperture: "f/5.6",
        confidence: "LOW",
        confidenceReason: "prior_failed_not_suspiciously_flat",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.81, M: 0.81 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.82, M: 0.82 },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.85, M: 0.83 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.87, M: 0.83 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.87, M: 0.81 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.84, M: 0.78 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.8, M: 0.75 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.75, M: 0.74 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.82, M: 0.77 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.94, M: 0.96 },
              30: { S: 0.86, M: 0.68 },
            },
          },
        ],
      },
    ],
  },
  "ttartisan-25mm-f2-0": {
    source: "https://www.ttartisan.com/?aps-c-lenses/78.html",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2",
        confidence: "LOW",
        confidenceReason: "precision_below_threshold",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.78, M: 0.76 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.96, M: 0.94 },
              30: { S: 0.81, M: 0.75 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.8, M: 0.71 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.7, M: 0.66 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.91, M: 0.92 },
              30: { S: 0.6, M: 0.61 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.9, M: 0.9 },
              30: { S: 0.54, M: 0.61 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.9, M: 0.86 },
              30: { S: 0.56, M: 0.58 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.88, M: 0.7 },
              30: { S: 0.46, M: 0.49 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.76, M: 0.5 },
              30: { S: 0.12, M: 0.31 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.41, M: 0.36 },
              30: { S: 0.07, M: 0.14 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.79, M: 0.79 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.79, M: 0.79 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.81, M: 0.79 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.8, M: 0.79 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.8, M: 0.79 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.93, M: 0.92 },
              30: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.75, M: 0.75 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.73, M: 0.73 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.78, M: 0.68 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.88, M: 0.92 },
              30: { S: 0.79, M: 0.48 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.78, M: 0.91 },
              30: { S: 0.72, M: 0.09 },
            },
          },
        ],
      },
    ],
  },
  "ttartisan-35mm-f1-4": {
    source: "https://www.ttartisan.com/?aps-c-lenses/71.html",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.59, M: 0.59 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.58, M: 0.59 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.9, M: 0.91 },
              30: { S: 0.57, M: 0.57 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.88, M: 0.89 },
              30: { S: 0.56, M: 0.53 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.88, M: 0.89 },
              30: { S: 0.55, M: 0.49 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.88, M: 0.87 },
              30: { S: 0.54, M: 0.45 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.88, M: 0.85 },
              30: { S: 0.52, M: 0.41 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.87, M: 0.83 },
              30: { S: 0.49, M: 0.4 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.83, M: 0.79 },
              30: { S: 0.41, M: 0.4 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.74, M: 0.74 },
              30: { S: 0.21, M: 0.34 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.59, M: 0.62 },
              30: { S: 0.06, M: 0.28 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.8, M: 0.8 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.8, M: 0.8 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.8, M: 0.8 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.81, M: 0.8 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.93, M: 0.94 },
              30: { S: 0.81, M: 0.8 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.8, M: 0.8 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.8, M: 0.77 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.79, M: 0.76 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.76, M: 0.76 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.91, M: 0.94 },
              30: { S: 0.78, M: 0.66 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.86, M: 0.94 },
              30: { S: 0.8, M: 0.48 },
            },
          },
        ],
      },
    ],
  },
  "ttartisan-40mm-f2-8-macro": {
    source: "https://www.ttartisan.com/?aps-c-lenses/75.html",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.76, M: 0.77 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.97, M: 0.96 },
              30: { S: 0.73, M: 0.77 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.93, M: 0.96 },
              30: { S: 0.7, M: 0.77 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.91, M: 0.96 },
              30: { S: 0.67, M: 0.77 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.89, M: 0.95 },
              30: { S: 0.64, M: 0.76 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.87, M: 0.95 },
              30: { S: 0.61, M: 0.75 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.84, M: 0.95 },
              30: { S: 0.58, M: 0.75 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.82, M: 0.95 },
              30: { S: 0.57, M: 0.72 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.81, M: 0.92 },
              30: { S: 0.55, M: 0.64 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.8, M: 0.85 },
              30: { S: 0.53, M: 0.53 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.81, M: 0.81 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.81, M: 0.81 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.81, M: 0.81 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.82, M: 0.8 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.81, M: 0.8 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.8, M: 0.79 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.78, M: 0.78 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.76, M: 0.76 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.76, M: 0.76 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.76, M: 0.75 },
            },
          },
        ],
      },
    ],
  },
  "ttartisan-500mm-f6-3": {
    source: "https://www.ttartisan.com/?full-frame-lenses/500-F6-3.html",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/6.3",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.87, M: 0.87 },
              30: { S: 0.51, M: 0.51 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.86, M: 0.86 },
              30: { S: 0.5, M: 0.5 },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.86, M: 0.86 },
              30: { S: 0.5, M: 0.5 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.86, M: 0.87 },
              30: { S: 0.49, M: 0.5 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.86, M: 0.86 },
              30: { S: 0.48, M: 0.51 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.86, M: 0.87 },
              30: { S: 0.46, M: 0.51 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.85, M: 0.86 },
              30: { S: 0.43, M: 0.5 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.85, M: 0.86 },
              30: { S: 0.4, M: 0.5 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.83, M: 0.87 },
              30: { S: 0.36, M: 0.48 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.82, M: 0.87 },
              30: { S: 0.32, M: 0.46 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.8, M: 0.86 },
              30: { S: 0.3, M: 0.44 },
            },
          },
        ],
      },
      {
        aperture: "f/11",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.88, M: 0.88 },
              30: { S: 0.68, M: 0.68 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.88, M: 0.88 },
              30: { S: 0.68, M: 0.68 },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.89, M: 0.89 },
              30: { S: 0.68, M: 0.67 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.89, M: 0.89 },
              30: { S: 0.68, M: 0.67 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.88, M: 0.88 },
              30: { S: 0.67, M: 0.66 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.88, M: 0.88 },
              30: { S: 0.68, M: 0.65 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.88, M: 0.88 },
              30: { S: 0.68, M: 0.63 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.87, M: 0.88 },
              30: { S: 0.68, M: 0.6 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.87, M: 0.88 },
              30: { S: 0.67, M: 0.57 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.86, M: 0.87 },
              30: { S: 0.65, M: 0.53 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.85, M: 0.88 },
              30: { S: 0.64, M: 0.49 },
            },
          },
        ],
      },
    ],
  },
  "ttartisan-500mm-f6-3-gfx": {
    source: "https://www.ttartisan.com/?full-frame-lenses/500-F6-3.html",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/6.3",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.87, M: 0.87 },
              30: { S: 0.51, M: 0.51 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.86, M: 0.86 },
              30: { S: 0.5, M: 0.5 },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.86, M: 0.86 },
              30: { S: 0.5, M: 0.5 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.86, M: 0.87 },
              30: { S: 0.49, M: 0.5 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.86, M: 0.86 },
              30: { S: 0.48, M: 0.51 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.86, M: 0.87 },
              30: { S: 0.46, M: 0.51 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.85, M: 0.86 },
              30: { S: 0.43, M: 0.5 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.85, M: 0.86 },
              30: { S: 0.4, M: 0.5 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.83, M: 0.87 },
              30: { S: 0.36, M: 0.48 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.82, M: 0.87 },
              30: { S: 0.32, M: 0.46 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.8, M: 0.86 },
              30: { S: 0.3, M: 0.44 },
            },
          },
        ],
      },
      {
        aperture: "f/11",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.88, M: 0.88 },
              30: { S: 0.68, M: 0.68 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.88, M: 0.88 },
              30: { S: 0.68, M: 0.68 },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.89, M: 0.89 },
              30: { S: 0.68, M: 0.67 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.89, M: 0.89 },
              30: { S: 0.68, M: 0.67 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.88, M: 0.88 },
              30: { S: 0.67, M: 0.66 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.88, M: 0.88 },
              30: { S: 0.68, M: 0.65 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.88, M: 0.88 },
              30: { S: 0.68, M: 0.63 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.87, M: 0.88 },
              30: { S: 0.68, M: 0.6 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.87, M: 0.88 },
              30: { S: 0.67, M: 0.57 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.86, M: 0.87 },
              30: { S: 0.65, M: 0.53 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.85, M: 0.88 },
              30: { S: 0.64, M: 0.49 },
            },
          },
        ],
      },
    ],
  },
  "ttartisan-50mm-f1-2": {
    source: "https://www.ttartisan.com/?aps-c-lenses/73.html",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.2",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.88, M: 0.88 },
              30: { S: 0.41, M: 0.41 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.89, M: 0.9 },
              30: { S: 0.44, M: 0.43 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.9, M: 0.9 },
              30: { S: 0.49, M: 0.46 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.91, M: 0.91 },
              30: { S: 0.53, M: 0.5 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.91, M: 0.89 },
              30: { S: 0.53, M: 0.5 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.89, M: 0.87 },
              30: { S: 0.47, M: 0.46 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.85, M: 0.85 },
              30: { S: 0.41, M: 0.37 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.84, M: 0.83 },
              30: { S: 0.39, M: 0.3 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.86, M: 0.79 },
              30: { S: 0.46, M: 0.3 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.88, M: 0.72 },
              30: { S: 0.48, M: 0.36 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.79, M: 0.61 },
              30: { S: 0.31, M: 0.4 },
            },
          },
        ],
      },
      {
        aperture: "f/5.6",
        confidence: "LOW",
        confidenceReason: "prior_failed_center_ge_edge",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.78, M: 0.78 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.79, M: null },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.81, M: 0.81 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.83, M: 0.83 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.85, M: 0.83 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.83, M: 0.79 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.78, M: 0.75 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.73, M: 0.7 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.72, M: 0.72 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.77, M: 0.76 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.93, M: 0.94 },
              30: { S: 0.84, M: 0.7 },
            },
          },
        ],
      },
    ],
  },
  "ttartisan-50mm-f2-0": {
    source: "https://www.ttartisan.com/?full-frame-lenses/TTArtisan-50-F2.html",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 1, M: 1 },
              30: { S: 0.73, M: 0.73 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.76, M: 0.75 },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.77, M: 0.74 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.96, M: 0.95 },
              30: { S: 0.78, M: 0.73 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.94, M: 0.93 },
              30: { S: 0.76, M: 0.7 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.93, M: 0.95 },
              30: { S: 0.7, M: 0.64 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.9, M: 0.87 },
              30: { S: 0.63, M: 0.62 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.92, M: 0.81 },
              30: { S: 0.56, M: 0.57 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.89, M: 0.74 },
              30: { S: 0.49, M: 0.54 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.85, M: 0.66 },
              30: { S: 0.42, M: 0.48 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.79, M: 0.58 },
              30: { S: 0.34, M: 0.42 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.8, M: 0.8 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.8, M: 0.8 },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.8, M: 0.81 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.94, M: 0.95 },
              30: { S: 0.79, M: 0.81 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.94, M: 0.96 },
              30: { S: 0.78, M: 0.82 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.94, M: 0.95 },
              30: { S: 0.75, M: 0.82 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.94, M: 0.95 },
              30: { S: 0.72, M: 0.81 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.93, M: 0.95 },
              30: { S: 0.68, M: 0.79 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.92, M: 0.93 },
              30: { S: 0.64, M: 0.77 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.92, M: 0.93 },
              30: { S: 0.61, M: 0.77 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.9, M: 0.94 },
              30: { S: 0.57, M: 0.77 },
            },
          },
        ],
      },
    ],
  },
  "ttartisan-7-5mm-f2-0-fisheye": {
    source: "https://www.ttartisan.com/?aps-c-lenses/72.html",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.71, M: 0.71 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.72, M: 0.77 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.73, M: 0.74 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.69, M: 0.75 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.61, M: 0.72 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.91, M: 0.94 },
              30: { S: 0.54, M: 0.67 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.9, M: 0.94 },
              30: { S: 0.53, M: 0.66 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.9, M: 0.94 },
              30: { S: 0.49, M: 0.7 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.9, M: 0.9 },
              30: { S: 0.46, M: 0.69 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.91, M: 0.81 },
              30: { S: 0.53, M: 0.58 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.92, M: 0.75 },
              30: { S: 0.57, M: 0.49 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.77, M: 0.78 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.77, M: 0.79 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.76, M: 0.8 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.92, M: 0.93 },
              30: { S: 0.73, M: 0.8 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.92, M: 0.93 },
              30: { S: 0.7, M: 0.79 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.92, M: 0.93 },
              30: { S: 0.69, M: 0.77 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.92, M: 0.93 },
              30: { S: 0.7, M: 0.77 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.91, M: 0.92 },
              30: { S: 0.69, M: 0.78 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.91, M: 0.93 },
              30: { S: 0.65, M: 0.79 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.9, M: 0.93 },
              30: { S: 0.58, M: 0.79 },
            },
          },
        ],
      },
    ],
  },
  "ttartisan-90mm-f1-25-gfx": {
    source: "https://www.ttartisan.com/?full-frame-lenses/56.html",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.25",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.58, M: 0.58 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.92, M: 0.93 },
              30: { S: 0.57, M: 0.58 },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.55, M: 0.6 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.55, M: 0.6 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.57, M: 0.58 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.93, M: 0.92 },
              30: { S: 0.57, M: 0.54 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.92, M: 0.9 },
              30: { S: 0.53, M: 0.48 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.9, M: 0.86 },
              30: { S: 0.51, M: 0.46 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.88, M: 0.8 },
              30: { S: 0.48, M: 0.51 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.85, M: 0.71 },
              30: { S: 0.37, M: 0.5 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.78, M: 0.58 },
              30: { S: 0.18, M: 0.36 },
            },
          },
        ],
      },
      {
        aperture: "f/5.6",
        confidence: "LOW",
        confidenceReason: "prior_failed_not_suspiciously_flat",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.81, M: 0.81 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.82, M: 0.82 },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.85, M: 0.83 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.87, M: 0.83 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.87, M: 0.81 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.84, M: 0.78 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.8, M: 0.75 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.75, M: 0.74 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.82, M: 0.77 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.94, M: 0.96 },
              30: { S: 0.86, M: 0.68 },
            },
          },
        ],
      },
    ],
  },
  "ttartisan-af-27mm-f2-8": {
    source: "https://www.ttartisan.com/?af-lens/38.html",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.76, M: 0.76 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.76, M: 0.77 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.77, M: 0.8 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.78, M: 0.81 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.93, M: 0.94 },
              30: { S: 0.75, M: 0.8 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.71, M: 0.8 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.7, M: 0.79 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.75, M: 0.8 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.95, M: 0.93 },
              30: { S: 0.83, M: 0.8 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.94, M: 0.92 },
              30: { S: 0.82, M: 0.77 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.91, M: 0.91 },
              30: { S: 0.65, M: 0.7 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "LOW",
        confidenceReason: "prior_failed_center_ge_edge",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.73, M: 0.73 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.74, M: null },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.76, M: 0.76 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.79, M: 0.78 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.8, M: 0.8 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.81, M: 0.8 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.8, M: 0.79 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.78, M: 0.78 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.79, M: 0.77 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.8, M: 0.75 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.92, M: 0.9 },
              30: { S: 0.79, M: 0.73 },
            },
          },
        ],
      },
    ],
  },
  "ttartisan-af-35mm-f1-8": {
    source: "https://www.ttartisan.com/?af-lens/AF-35-II.html",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.79, M: 0.79 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.79, M: 0.78 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.8, M: 0.74 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.96, M: 0.95 },
              30: { S: 0.77, M: 0.72 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.67, M: 0.71 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.91, M: 0.92 },
              30: { S: 0.56, M: 0.67 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.54, M: 0.64 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.93, M: 0.92 },
              30: { S: 0.68, M: 0.63 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.89, M: 0.9 },
              30: { S: 0.67, M: 0.63 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.71, M: 0.89 },
              // 30 M: eye-read override 0.58 (extractor produces 0.66 —
              // ridge tracker still locks onto solid S30 at the right
              // corner crossing despite #1214 fixing pos 14). See
              // docs/optical-specs/ttartisan-af-35mm-f1-8/eye-read.md.
              30: { S: 0.31, M: 0.58 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.38, M: 0.88 },
              30: { S: 0.12, M: null },
            },
          },
        ],
      },
      {
        aperture: "f/5.6",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.84, M: 0.84 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.84, M: 0.84 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.86, M: 0.84 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.95, M: 0.94 },
              30: { S: 0.86, M: 0.82 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.85, M: 0.8 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.81, M: 0.81 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.79, M: 0.78 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.78, M: 0.78 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.95, M: 0.93 },
              30: { S: 0.85, M: 0.73 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.95, M: 0.91 },
              30: { S: 0.82, M: 0.67 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.88, M: 0.88 },
              30: { S: 0.49, M: 0.63 },
            },
          },
        ],
      },
    ],
  },
  "ttartisan-af-56mm-f1-8": {
    source: "https://www.ttartisan.com/?af-lens/AF-56.html",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.89, M: 0.89 },
              30: { S: 0.54, M: 0.54 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.88, M: 0.88 },
              30: { S: 0.54, M: 0.54 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.89, M: 0.89 },
              30: { S: 0.56, M: 0.55 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.91, M: 0.9 },
              30: { S: 0.6, M: 0.55 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.91, M: 0.91 },
              30: { S: 0.62, M: 0.55 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.91, M: 0.9 },
              30: { S: 0.63, M: 0.54 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.91, M: 0.89 },
              30: { S: 0.62, M: 0.56 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.91, M: 0.9 },
              30: { S: 0.59, M: 0.49 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.87, M: 0.87 },
              30: { S: 0.52, M: 0.45 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.79, M: 0.86 },
              30: { S: 0.43, M: 0.4 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.66, M: 0.87 },
              30: { S: 0.33, M: 0.4 },
            },
          },
        ],
      },
      {
        aperture: "f/5.6",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.83, M: 0.83 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.82, M: 0.82 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.83, M: 0.81 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.84, M: 0.8 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.84, M: 0.78 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.94, M: 0.93 },
              30: { S: 0.84, M: 0.74 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.94, M: 0.92 },
              30: { S: 0.83, M: 0.7 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.94, M: 0.91 },
              30: { S: 0.82, M: 0.65 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.94, M: 0.89 },
              30: { S: 0.82, M: 0.56 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.94, M: 0.87 },
              30: { S: 0.83, M: 0.48 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.92, M: 0.86 },
              30: { S: 0.83, M: 0.46 },
            },
          },
        ],
      },
    ],
  },
  "ttartisan-af-75mm-f2-0": {
    source: "https://www.ttartisan.com/?af-lens/FF-AF75.html",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.97, M: 0.97 },
              30: { S: 0.83, M: 0.83 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.97, M: 0.96 },
              30: { S: 0.82, M: 0.79 },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.77, M: 0.76 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.74, M: 0.74 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.92, M: 0.93 },
              30: { S: 0.69, M: 0.72 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.89, M: 0.93 },
              30: { S: 0.62, M: 0.71 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.86, M: 0.91 },
              30: { S: 0.58, M: 0.69 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.82, M: 0.9 },
              30: { S: 0.55, M: 0.68 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.8, M: 0.89 },
              30: { S: 0.56, M: 0.66 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.75, M: 0.87 },
              30: { S: 0.55, M: 0.6 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.64, M: 0.84 },
              30: { S: 0.41, M: 0.52 },
            },
          },
        ],
      },
      {
        aperture: "f/5.6",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.88, M: 0.88 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.88, M: 0.88 },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.93, M: 0.94 },
              30: { S: 0.87, M: 0.87 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.94, M: 0.95 },
              30: { S: 0.86, M: 0.87 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.94, M: 0.96 },
              30: { S: 0.83, M: 0.87 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.93, M: 0.95 },
              30: { S: 0.78, M: 0.86 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.93, M: 0.94 },
              30: { S: 0.72, M: 0.83 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.93, M: 0.94 },
              30: { S: 0.68, M: 0.8 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.69, M: 0.73 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.94, M: 0.9 },
              30: { S: 0.78, M: 0.63 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.95, M: 0.88 },
              30: { S: 0.81, M: 0.55 },
            },
          },
        ],
      },
    ],
  },
  "ttartisan-tilt-35mm-f1-4": {
    source: "https://www.ttartisan.com/?aps-c-lenses/Tilt-C-35.html",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.91, M: 0.91 },
              30: { S: 0.58, M: 0.58 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.91, M: 0.91 },
              30: { S: 0.58, M: 0.58 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.9, M: 0.9 },
              30: { S: 0.57, M: 0.56 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.88, M: 0.89 },
              30: { S: 0.56, M: 0.53 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.87, M: 0.87 },
              30: { S: 0.54, M: 0.49 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.87, M: 0.86 },
              30: { S: 0.53, M: 0.45 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.87, M: 0.84 },
              30: { S: 0.51, M: 0.41 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.86, M: 0.82 },
              30: { S: 0.49, M: 0.4 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.82, M: 0.78 },
              30: { S: 0.39, M: 0.39 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.73, M: 0.72 },
              30: { S: 0.2, M: 0.33 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.58, M: 0.61 },
              30: { S: 0.05, M: 0.27 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.79, M: 0.79 },
            },
          },
          {
            position: 1.4,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.79, M: 0.79 },
            },
          },
          {
            position: 2.8,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.79, M: 0.79 },
            },
          },
          {
            position: 4.2,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.8, M: 0.79 },
            },
          },
          {
            position: 5.6,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.8, M: 0.79 },
            },
          },
          {
            position: 7,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.79, M: 0.79 },
            },
          },
          {
            position: 8.4,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.79, M: 0.76 },
            },
          },
          {
            position: 9.8,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.78, M: 0.75 },
            },
          },
          {
            position: 11.2,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.75, M: 0.74 },
            },
          },
          {
            position: 12.6,
            samples: {
              10: { S: 0.9, M: 0.93 },
              30: { S: 0.78, M: 0.64 },
            },
          },
          {
            position: 14,
            samples: {
              10: { S: 0.85, M: 0.93 },
              30: { S: 0.79, M: 0.46 },
            },
          },
        ],
      },
    ],
  },
  "ttartisan-tilt-50mm-f1-4": {
    source: "https://www.ttartisan.com/?full-frame-lenses/60.html",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/1.4",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.75, M: 0.75 },
              30: { S: 0.28, M: 0.28 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.77, M: 0.76 },
              30: { S: 0.27, M: 0.29 },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.8, M: 0.75 },
              30: { S: 0.28, M: 0.29 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.77, M: 0.76 },
              30: { S: 0.26, M: 0.3 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.7, M: 0.74 },
              30: { S: 0.21, M: 0.3 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.64, M: 0.71 },
              30: { S: 0.16, M: 0.27 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.61, M: 0.67 },
              30: { S: 0.12, M: 0.25 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.55, M: 0.63 },
              30: { S: 0.09, M: 0.23 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.45, M: 0.58 },
              30: { S: 0.09, M: 0.16 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.33, M: 0.48 },
              30: { S: 0.08, M: 0.08 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.15, M: 0.37 },
              30: { S: 0.02, M: 0.07 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.74, M: 0.74 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.73, M: 0.75 },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.92, M: 0.92 },
              30: { S: 0.71, M: 0.75 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.92, M: 0.93 },
              30: { S: 0.67, M: 0.76 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.9, M: 0.93 },
              30: { S: 0.61, M: 0.76 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.9, M: 0.93 },
              30: { S: 0.57, M: 0.75 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.9, M: 0.93 },
              30: { S: 0.55, M: 0.73 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.9, M: 0.92 },
              30: { S: 0.56, M: 0.71 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.9, M: 0.92 },
              30: { S: 0.61, M: 0.73 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.89, M: 0.93 },
              30: { S: 0.54, M: 0.75 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.92, M: 0.8 },
              30: { S: 0.27, M: 0.74 },
            },
          },
        ],
      },
    ],
  },
  "ttartisan-100mm-f2-8-macro-2x-gfx": {
    source: "https://www.ttartisan.com/?full-frame-lenses/TS-100-Macro.html",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.75, M: 0.75 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.75, M: null },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.95, M: 0.96 },
              30: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.95, M: 0.96 },
              30: { S: 0.77, M: 0.78 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.96, M: 0.95 },
              30: { S: 0.72, M: 0.72 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.8, M: 0.69 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.77, M: 0.72 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.92, M: 0.93 },
              30: { S: 0.58, M: 0.72 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.83, M: 0.83 },
              30: { S: 0.32, M: 0.52 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.75, M: 0.57 },
              30: { S: 0.18, M: 0.22 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.76, M: 0.76 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.79, M: 0.79 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.8, M: 0.8 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.8, M: 0.8 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.73, M: 0.73 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.7, M: 0.7 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.69, M: 0.68 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.91, M: 0.93 },
              30: { S: 0.75, M: 0.62 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.87, M: 0.94 },
              30: { S: 0.78, M: 0.44 },
            },
          },
        ],
      },
    ],
  },
  "ttartisan-100mm-f2-8-macro-2x": {
    source: "https://www.ttartisan.com/?full-frame-lenses/TS-100-Macro.html",
    mtfType: "computed",
    charts: [
      {
        aperture: "f/2.8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.75, M: 0.75 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.75, M: null },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.95, M: 0.96 },
              30: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.95, M: 0.96 },
              30: { S: 0.77, M: 0.78 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.95, M: 0.95 },
              30: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.96, M: 0.95 },
              30: { S: 0.72, M: 0.72 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.8, M: 0.69 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.96, M: 0.96 },
              30: { S: 0.77, M: 0.72 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.92, M: 0.93 },
              30: { S: 0.58, M: 0.72 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.83, M: 0.83 },
              30: { S: 0.32, M: 0.52 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.75, M: 0.57 },
              30: { S: 0.18, M: 0.22 },
            },
          },
        ],
      },
      {
        aperture: "f/8",
        confidence: "HIGH",
        readings: [
          {
            position: 0,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.76, M: 0.76 },
            },
          },
          {
            position: 2.05,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 4.1,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.79, M: 0.79 },
            },
          },
          {
            position: 6.15,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.8, M: 0.8 },
            },
          },
          {
            position: 8.2,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.8, M: 0.8 },
            },
          },
          {
            position: 10.25,
            samples: {
              10: { S: 0.94, M: 0.94 },
              30: { S: 0.77, M: 0.77 },
            },
          },
          {
            position: 12.3,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.73, M: 0.73 },
            },
          },
          {
            position: 14.35,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.7, M: 0.7 },
            },
          },
          {
            position: 16.4,
            samples: {
              10: { S: 0.93, M: 0.93 },
              30: { S: 0.69, M: 0.68 },
            },
          },
          {
            position: 18.45,
            samples: {
              10: { S: 0.91, M: 0.93 },
              30: { S: 0.75, M: 0.62 },
            },
          },
          {
            position: 20.5,
            samples: {
              10: { S: 0.87, M: 0.94 },
              30: { S: 0.78, M: 0.44 },
            },
          },
        ],
      },
    ],
  },
};

export { mtfReadings };
