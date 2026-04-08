/** Source of a review — ordered by measurement rigour */
type ReviewSource =
  | "lensrentals"          // Roger Cicala; optical bench MTF — most rigorous
  | "lenstip"              // lab MTF charts, resolution measurements
  | "opticallimits"        // lab MTF, formerly photozone.de
  | "dxomark"              // sensor + lens measurements (limited Fuji X)
  | "the-digital-picture"  // Bryan Carnathan; ISO chart comparisons, MTF
  | "dustinabbott"         // thorough field + lab; CA, flare, bokeh analysis
  | "imaging-resource"     // lab-based resolution and noise testing
  | "ephotozine"           // lab-tested MTF + resolution charts
  | "dpreview"             // comprehensive (archived, still referenced)
  | "phillipreeve"         // manual focus and adapted lens specialist
  | "cameralabs"           // Gordon Laing; thorough video + stills
  | "fujivsfuji"           // Fuji-specific head-to-head comparisons
  | "photographyblog"      // decent hands-on reviews
  | "digitalcameraworld"   // buyer's guide oriented
  | "other";

interface ReviewLink {
  source: ReviewSource;
  url: string;
  title?: string;
}

export type { ReviewLink, ReviewSource };
