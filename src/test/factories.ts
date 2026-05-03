import type { Lens } from "../types/lens";
import type { Camera } from "../types/camera";
import type { ExplorerLens } from "../components/interactive/LensExplorer/constants";

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

const EXPLORER_DEFAULTS: Omit<ExplorerLens, "brand" | "model"> = {
  type: "prime",
  mount: "X",
  focalLengthMin: 35,
  focalLengthMax: 35,
  maxAperture: 1.4,
  weight: 200,
  price: 600,
};

function makeExplorerLens(
  overrides: Partial<ExplorerLens> & Pick<ExplorerLens, "brand" | "model">,
): ExplorerLens {
  return { ...EXPLORER_DEFAULTS, ...overrides };
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

export { makeLens, makeExplorerLens, makeCamera };
