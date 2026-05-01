interface ExplorerCamera {
  model: string;
  mount: string;
  year: number;
  series: string;
  formFactor: string;
  sensor: string;
  megapixels: number;
  hasIbis?: boolean;
  isWeatherSealed?: boolean;
  isDiscontinued?: boolean;
  mechanicalBurstFps?: number;
  videoSpec: string;
  batteryLife?: number;
  weight: number;
  price: number;
}

export type { ExplorerCamera };
