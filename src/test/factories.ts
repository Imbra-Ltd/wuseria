import type { Lens } from "../types/lens";
import type { Camera } from "../types/camera";

function makeLens(
  overrides: Partial<Lens> & Pick<Lens, "brand" | "model">,
): Lens {
  return {
    type: "prime",
    mount: "X",
    focalLengthMin: 35,
    focalLengthMax: 35,
    maxAperture: 1.4,
    weight: 200,
    price: 600,
    ...overrides,
  };
}

function makeCamera(
  overrides: Partial<Camera> & Pick<Camera, "model">,
): Camera {
  return {
    mount: "X",
    year: 2022,
    series: "X-T",
    evfPosition: "center",
    formFactor: "standard",
    sensor: "X-Trans IV",
    megapixels: 26,
    weight: 500,
    price: 1500,
    videoSpec: "4K",
    ...overrides,
  };
}

export { makeLens, makeCamera };
