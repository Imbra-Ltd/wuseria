import type { Lens } from "../types/lens";

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

export { makeLens };
