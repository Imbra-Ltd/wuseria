import type {
  ReviewSource,
  ReviewSourceInfo,
} from "../types/review";

// =============================================================================
// REVIEW SOURCE DIRECTORY — methodology and trust per source
// =============================================================================

const reviewSourceDirectory: Record<ReviewSource, ReviewSourceInfo> = {
  // --- lab, trust 3 ---
  "lensrentals": {
    methodology: "lab",
    trust: 3,
    name: "LensRentals",
    site: "lensrentals.com",
  },
  "lenstip": {
    methodology: "lab",
    trust: 3,
    name: "LensTip",
    site: "lenstip.com",
  },
  "opticallimits": {
    methodology: "lab",
    trust: 3,
    name: "OpticalLimits",
    site: "opticallimits.com",
  },

  // --- lab, trust 2 ---
  "dxomark": {
    methodology: "lab",
    trust: 2,
    name: "DxOMark",
    site: "dxomark.com",
  },
  "the-digital-picture": {
    methodology: "lab",
    trust: 2,
    name: "The Digital Picture",
    site: "the-digital-picture.com",
  },
  "imaging-resource": {
    methodology: "lab",
    trust: 2,
    name: "Imaging Resource",
    site: "imaging-resource.com",
  },
  "ephotozine": {
    methodology: "lab",
    trust: 2,
    name: "ePHOTOzine",
    site: "ephotozine.com",
  },

  // --- field, trust 3 ---
  "dustinabbott": {
    methodology: "field",
    trust: 3,
    name: "Dustin Abbott",
    site: "dustinabbott.net",
  },
  "dpreview": {
    methodology: "field",
    trust: 3,
    name: "DPReview",
    site: "dpreview.com",
  },
  "phillipreeve": {
    methodology: "field",
    trust: 3,
    name: "Phillip Reeve",
    site: "phillipreeve.net",
  },

  // --- field, trust 2 ---
  "admiringlight": {
    methodology: "field",
    trust: 2,
    name: "Admiring Light",
    site: "admiringlight.com",
  },
  "photographylife": {
    methodology: "field",
    trust: 2,
    name: "Photography Life",
    site: "photographylife.com",
  },
  "cameralabs": {
    methodology: "field",
    trust: 2,
    name: "Camera Labs",
    site: "cameralabs.com",
  },
  "christopherfrost": {
    methodology: "field",
    trust: 2,
    name: "Christopher Frost",
    site: "christopherfrost.co.uk",
  },
  "fujivsfuji": {
    methodology: "field",
    trust: 2,
    name: "Fuji vs Fuji",
    site: "fujivsfuji.com",
  },
  "sansmirror": {
    methodology: "field",
    trust: 2,
    name: "Thom Hogan (Sans Mirror)",
    site: "sansmirror.com",
  },
};

export { reviewSourceDirectory };
