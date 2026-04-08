/** Affiliate retailer */
type AffiliateRetailer = "amazon" | "bhphoto" | "adorama" | "mpb" | "keh";

/** Region for pricing and availability */
type AffiliateRegion = "eu" | "us" | "uk";

interface AffiliateLink {
  retailer: AffiliateRetailer;
  url: string;
  product: string;
  region: AffiliateRegion;
}

export type { AffiliateLink, AffiliateRetailer, AffiliateRegion };
