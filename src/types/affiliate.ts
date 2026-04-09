// =============================================================================
// TYPES
// =============================================================================

type AffiliateRetailer = "amazon" | "bhphoto" | "adorama" | "mpb" | "keh";

type AffiliateRegion = "eu" | "us" | "uk";

// =============================================================================
// AFFILIATE LINK
// =============================================================================

interface AffiliateLink {
  retailer: AffiliateRetailer;
  url: string;
  product: string;
  region: AffiliateRegion;
}

// =============================================================================
// EXPORTS
// =============================================================================

export type { AffiliateLink, AffiliateRetailer, AffiliateRegion };
