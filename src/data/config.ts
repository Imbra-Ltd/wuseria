/** Default currency for all prices in data files */
const DEFAULT_CURRENCY = "USD" as const;

/** Supported currencies for display */
type Currency = "USD" | "EUR" | "GBP" | "BGN";

/** Currency symbols for UI rendering */
const CURRENCY_SYMBOLS: Record<Currency, string> = {
  USD: "$",
  EUR: "€",
  GBP: "£",
  BGN: "лв",
};

export { DEFAULT_CURRENCY, CURRENCY_SYMBOLS };
export type { Currency };
