// =============================================================================
// REVIEW SOURCE
// =============================================================================

type ReviewSource =
  | "lensrentals"
  | "lenstip"
  | "opticallimits"
  | "dxomark"
  | "the-digital-picture"
  | "dustinabbott"
  | "imaging-resource"
  | "ephotozine"
  | "dpreview"
  | "admiringlight"
  | "phillipreeve"
  | "cameralabs"
  | "christopherfrost"
  | "fujivsfuji"
  | "sansmirror"
  | "photographylife";

// =============================================================================
// METHODOLOGY & TRUST
// =============================================================================

// How the data is gathered
type ReviewMethodology = "lab" | "field";

// How reliable the source is
// 3 = gold standard, consistently accurate, peer-verified
// 2 = reliable, minor inconsistencies or gaps
// 1 = useful reference, take with grain of salt
type ReviewTrust = 1 | 2 | 3;

interface ReviewSourceInfo {
  methodology: ReviewMethodology;
  trust: ReviewTrust;
  name: string;
  site: string;
}

// =============================================================================
// EXPORTS
// =============================================================================

export type { ReviewSource, ReviewMethodology, ReviewTrust, ReviewSourceInfo };
