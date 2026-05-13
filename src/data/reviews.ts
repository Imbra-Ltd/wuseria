import type { ReviewSource, ReviewSourceInfo } from "../types/review";

// =============================================================================
// REVIEW SOURCE DIRECTORY — methodology and trust per source
// =============================================================================

const reviewSourceDirectory: Record<ReviewSource, ReviewSourceInfo> = {
  // --- lab, trust 3 ---
  lensrentals: {
    methodology: "lab",
    trust: 3,
    name: "LensRentals",
    site: "lensrentals.com",
  },
  lenstip: {
    methodology: "lab",
    trust: 3,
    name: "LensTip",
    site: "lenstip.com",
  },
  opticallimits: {
    methodology: "lab",
    trust: 3,
    name: "OpticalLimits",
    site: "opticallimits.com",
  },

  // --- lab, trust 3 (upgraded) ---
  dxomark: {
    methodology: "lab",
    trust: 3,
    name: "DxOMark",
    site: "dxomark.com",
  },
  "the-digital-picture": {
    methodology: "lab",
    trust: 3,
    name: "The Digital Picture",
    site: "the-digital-picture.com",
  },
  // --- lab, trust 3 (promoted per ADR-023) ---
  ephotozine: {
    methodology: "lab",
    trust: 3,
    name: "ePHOTOzine",
    site: "ephotozine.com",
  },
  colorfoto: {
    methodology: "lab",
    trust: 3,
    name: "ColorFoto",
    site: "connect-living.de/colorfoto",
  },

  // --- lab, trust 2 ---
  "imaging-resource": {
    methodology: "lab",
    trust: 2,
    name: "Imaging Resource",
    site: "imaging-resource.com",
  },

  // --- field, trust 3 ---
  dustinabbott: {
    methodology: "field",
    trust: 3,
    name: "Dustin Abbott",
    site: "dustinabbott.net",
  },
  dpreview: {
    methodology: "field",
    trust: 3,
    name: "DPReview",
    site: "dpreview.com",
  },
  phillipreeve: {
    methodology: "field",
    trust: 3,
    name: "Phillip Reeve",
    site: "phillipreeve.net",
  },
  diglloyd: {
    methodology: "field",
    trust: 3,
    name: "Lloyd Chambers",
    site: "diglloyd.com",
  },
  lonelyspeck: {
    methodology: "field",
    trust: 3,
    name: "Lonely Speck",
    site: "lonelyspeck.com",
  },
  nightscapephotographer: {
    methodology: "field",
    trust: 2,
    name: "Nightscape Photographer",
    site: "nightscapephotographer.com",
  },

  // --- field, trust 2 ---
  admiringlight: {
    methodology: "field",
    trust: 2,
    name: "Admiring Light",
    site: "admiringlight.com",
  },
  photographylife: {
    methodology: "field",
    trust: 2,
    name: "Photography Life",
    site: "photographylife.com",
  },
  cameralabs: {
    methodology: "field",
    trust: 2,
    name: "Camera Labs",
    site: "cameralabs.com",
  },
  christopherfrost: {
    methodology: "field",
    trust: 2,
    name: "Christopher Frost",
    site: "christopherfrost.co.uk",
  },
  fujivsfuji: {
    methodology: "field",
    trust: 2,
    name: "Fuji vs Fuji",
    site: "fujivsfuji.com",
  },
  sansmirror: {
    methodology: "field",
    trust: 2,
    name: "Thom Hogan (Sans Mirror)",
    site: "sansmirror.com",
  },
  whatdigitalcamera: {
    methodology: "lab",
    trust: 2,
    name: "What Digital Camera",
    site: "whatdigitalcamera.com",
  },
  photographyblog: {
    methodology: "lab",
    trust: 2,
    name: "Photography Blog",
    site: "photographyblog.com",
  },
  amateurphotographer: {
    methodology: "lab",
    trust: 2,
    name: "Amateur Photographer",
    site: "amateurphotographer.com",
  },
  digitalcameraworld: {
    methodology: "lab",
    trust: 2,
    name: "Digital Camera World",
    site: "digitalcameraworld.com",
  },
  objektivtest: {
    methodology: "lab",
    trust: 2,
    name: "Objektivtest",
    site: "objektivtest.se",
  },
  mirrorlessons: {
    methodology: "field",
    trust: 2,
    name: "MirrorLessons",
    site: "mirrorlessons.com",
  },
  thephoblographer: {
    methodology: "field",
    trust: 2,
    name: "The Phoblographer",
    site: "thephoblographer.com",
  },
  lesnumeriques: {
    methodology: "lab",
    trust: 2,
    name: "Les Numériques",
    site: "lesnumeriques.com",
  },
  kamerabild: {
    methodology: "lab",
    trust: 2,
    name: "Kamera & Bild",
    site: "kamerabild.se",
  },
  dcwatch: {
    methodology: "field",
    trust: 2,
    name: "DC.Watch",
    site: "dc.watch.impress.co.jp",
  },
  dcfever: {
    methodology: "field",
    trust: 2,
    name: "DCFever",
    site: "dcfever.com",
  },
  cined: {
    methodology: "lab",
    trust: 2,
    name: "CineD",
    site: "cined.com",
  },
  provideocoalition: {
    methodology: "field",
    trust: 2,
    name: "ProVideo Coalition",
    site: "provideocoalition.com",
  },

  // --- lab, trust 2 (multilingual) ---
  "digitalkamera-de": {
    methodology: "lab",
    trust: 2,
    name: "digitalkamera.de",
    site: "digitalkamera.de",
  },
  fotomagazin: {
    methodology: "lab",
    trust: 2,
    name: "fotoMAGAZIN",
    site: "fotomagazin.de",
  },
  "focus-review": {
    methodology: "lab",
    trust: 2,
    name: "Focus Review",
    site: "focus-review.com",
  },
  fotografidigitali: {
    methodology: "lab",
    trust: 2,
    name: "Fotografi Digitali",
    site: "fotografidigitali.it",
  },

  // --- field, trust 2 (multilingual) ---
  asobinet: {
    methodology: "field",
    trust: 2,
    name: "Asobinet (とるなら)",
    site: "asobinet.com",
  },
  fujiyacamera: {
    methodology: "field",
    trust: 2,
    name: "Fujiya Camera",
    site: "fujiya-camera.co.jp",
  },
  mapcamera: {
    methodology: "field",
    trust: 2,
    name: "Map Camera KASYAPA",
    site: "news.mapcamera.com",
  },
  radojuva: {
    methodology: "field",
    trust: 2,
    name: "Radojuva",
    site: "radojuva.com",
  },
};

export { reviewSourceDirectory };
