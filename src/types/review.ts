/** Source of a review — ordered by measurement rigour */
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
