/**
 * Source of a review — ordered by measurement rigour:
 * 1. lensrentals    — Roger Cicala; optical bench MTF (most rigorous)
 * 2. lenstip        — lab MTF charts, resolution measurements
 * 3. opticallimits  — lab MTF, formerly photozone.de
 * 4. dxomark        — sensor + lens measurements (limited Fuji X)
 * 5. the-digital-picture — Bryan Carnathan; ISO chart comparisons
 * 6. dustinabbott   — thorough field + lab; CA, flare, bokeh
 * 7. imaging-resource — lab-based resolution and noise testing
 * 8. ephotozine     — lab-tested MTF + resolution charts
 * 9. dpreview       — comprehensive (archived, still referenced)
 * 10. phillipreeve  — manual focus and adapted lens specialist
 * 11. cameralabs    — Gordon Laing; thorough video + stills
 * 12. fujivsfuji    — Fuji-specific head-to-head comparisons
 * 13. photographyblog — decent hands-on reviews
 * 14. digitalcameraworld — buyer's guide oriented
 */
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

interface ReviewLink {
  /** Lens or camera model this review covers */
  product: string;
  source: ReviewSource;
  url: string;
  title?: string;
}

export type { ReviewLink, ReviewSource };
