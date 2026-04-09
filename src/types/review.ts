// =============================================================================
// REVIEW SOURCE — ordered by measurement rigour
// =============================================================================
//
//  1. lensrentals         — optical bench MTF
//  2. lenstip             — lab MTF charts
//  3. opticallimits       — lab MTF
//  4. dxomark             — sensor + lens measurements
//  5. the-digital-picture — ISO chart comparisons
//  6. dustinabbott        — field + lab
//  7. imaging-resource    — lab resolution/noise
//  8. ephotozine          — lab MTF
//  9. dpreview            — comprehensive (archived)
// 10. phillipreeve        — manual focus specialist
// 11. cameralabs          — video + stills
// 12. fujivsfuji          — Fuji head-to-head
// 13. photographyblog     — hands-on
// 14. digitalcameraworld  — buyer's guide

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
  | "phillipreeve"
  | "cameralabs"
  | "fujivsfuji"
  | "photographyblog"
  | "digitalcameraworld"
  | "other";

// =============================================================================
// REVIEW LINK
// =============================================================================

interface ReviewLink {
  product: string;
  source: ReviewSource;
  url: string;
  title?: string;
}

// =============================================================================
// EXPORTS
// =============================================================================

export type { ReviewLink, ReviewSource };
