import type { MtfData } from "../types/mtf";

const mtfReadings: Record<string, MtfData> = {
  "sigma-16mm-f1-4-dc-dn-c": {
    source: "https://www.sigma-global.com/en/lenses/c017_16_14/",
    charts: [
      {
        aperture: "f/1.4",
        readings: [
          {
            position: 0,
            contrast10S: 0.96,
            contrast10M: 0.96,
            resolution30S: 0.81,
            resolution30M: 0.79,
          },
          {
            position: 2.5,
            contrast10S: 0.96,
            contrast10M: 0.96,
            resolution30S: 0.82,
            resolution30M: 0.79,
          },
          {
            position: 5,
            contrast10S: 0.96,
            contrast10M: 0.96,
            resolution30S: 0.82,
            resolution30M: 0.77,
          },
          {
            position: 7.5,
            contrast10S: 0.96,
            contrast10M: 0.96,
            resolution30S: 0.78,
            resolution30M: 0.74,
          },
          {
            position: 10,
            contrast10S: 0.93,
            contrast10M: 0.95,
            resolution30S: 0.68,
            resolution30M: 0.72,
          },
          {
            position: 12.5,
            contrast10S: 0.83,
            contrast10M: 0.93,
            resolution30S: 0.59,
            resolution30M: 0.64,
          },
          {
            position: 14,
            contrast10S: 0.71,
            contrast10M: 0.89,
            resolution30S: 0.5,
            resolution30M: 0.56,
          },
        ],
      },
    ],
  },
  "sigma-56mm-f1-4-dc-dn-c": {
    source: "https://www.sigma-global.com/en/lenses/c018_56_14/",
    charts: [
      {
        aperture: "f/1.4",
        readings: [
          {
            position: 0,
            contrast10S: 0.98,
            contrast10M: 0.98,
            resolution30S: 0.86,
            resolution30M: 0.86,
          },
          {
            position: 2.5,
            contrast10S: 0.98,
            contrast10M: 0.98,
            resolution30S: 0.87,
            resolution30M: 0.87,
          },
          {
            position: 5,
            contrast10S: 0.98,
            contrast10M: 0.98,
            resolution30S: 0.86,
            resolution30M: 0.86,
          },
          {
            position: 7.5,
            contrast10S: 0.97,
            contrast10M: 0.97,
            resolution30S: 0.81,
            resolution30M: 0.85,
          },
          {
            position: 10,
            contrast10S: 0.97,
            contrast10M: 0.97,
            resolution30S: 0.8,
            resolution30M: 0.86,
          },
          {
            position: 12.5,
            contrast10S: 0.91,
            contrast10M: 0.95,
            resolution30S: 0.61,
            resolution30M: 0.74,
          },
          {
            position: 14,
            contrast10S: 0.72,
            contrast10M: 0.93,
            resolution30S: 0.36,
            resolution30M: 0.61,
          },
        ],
      },
    ],
  },
  "samyang-12mm-f2-0-ncs-cs": {
    source: "https://www.lksamyang.com/en/product/product-view.php?seq=351",
    charts: [
      {
        aperture: "f/2",
        readings: [
          {
            position: 0,
            contrast10S: 1,
            contrast10M: 0.98,
            resolution30S: 0.92,
            resolution30M: 0.84,
          },
          {
            position: 2,
            contrast10S: 0.99,
            contrast10M: 0.97,
            resolution30S: 0.91,
            resolution30M: 0.79,
          },
          {
            position: 4,
            contrast10S: 0.98,
            contrast10M: 0.95,
            resolution30S: 0.91,
            resolution30M: 0.72,
          },
          {
            position: 6,
            contrast10S: 0.98,
            contrast10M: 0.93,
            resolution30S: 0.9,
            resolution30M: 0.58,
          },
          {
            position: 8,
            contrast10S: 0.97,
            contrast10M: 0.94,
            resolution30S: 0.7,
            resolution30M: 0.5,
          },
          {
            position: 10,
            contrast10S: 0.96,
            contrast10M: 0.93,
            resolution30S: 0.52,
            resolution30M: 0.48,
          },
          {
            position: 12,
            contrast10S: 0.95,
            contrast10M: 0.91,
            resolution30S: 0.5,
            resolution30M: 0.35,
          },
          {
            position: 14,
            contrast10S: 0.82,
            contrast10M: 0.8,
            resolution30S: 0.35,
            resolution30M: 0.22,
          },
        ],
      },
      {
        aperture: "f/8",
        readings: [
          {
            position: 0,
            contrast10S: 1,
            contrast10M: 1,
            resolution30S: 0.97,
            resolution30M: 0.95,
          },
          {
            position: 2,
            contrast10S: 1,
            contrast10M: 1,
            resolution30S: 0.96,
            resolution30M: 0.94,
          },
          {
            position: 4,
            contrast10S: 1,
            contrast10M: 0.99,
            resolution30S: 0.95,
            resolution30M: 0.92,
          },
          {
            position: 6,
            contrast10S: 1,
            contrast10M: 0.99,
            resolution30S: 0.95,
            resolution30M: 0.88,
          },
          {
            position: 8,
            contrast10S: 1,
            contrast10M: 0.98,
            resolution30S: 0.72,
            resolution30M: 0.6,
          },
          {
            position: 10,
            contrast10S: 0.99,
            contrast10M: 0.95,
            resolution30S: 0.5,
            resolution30M: 0.48,
          },
          {
            position: 12,
            contrast10S: 0.98,
            contrast10M: 0.95,
            resolution30S: 0.5,
            resolution30M: 0.22,
          },
          {
            position: 14,
            contrast10S: 0.97,
            contrast10M: 0.96,
            resolution30S: 0.22,
            resolution30M: 0.12,
          },
        ],
      },
    ],
  },
};

export { mtfReadings };
