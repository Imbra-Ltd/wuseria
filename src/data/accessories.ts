import type {
  Accessory,
  FlashAccessory,
  BatteryGripAccessory,
  GenericAccessory,
  BatteryAccessory,
  ChargerAccessory,
  LensAccessory,
  AdapterAccessory,
  RemoteAccessory,
  AudioAccessory,
} from "../types/accessory";

// -----------------------------------------------------------------------------
// FLASH
// -----------------------------------------------------------------------------

const flashes: FlashAccessory[] = [
  {
    category: "flash",
    brand: "Fujifilm",
    model: "EF-X500",
    description:
      "Top-tier TTL flash. FP high-speed sync, wireless commander/remote. Accepts EF-BP1 battery pack.",
    mount: "X",
    guideNumber: 50,
    hasTtl: true,
    hasHss: true,
    isWirelessCommander: true,
    isWirelessReceiver: true,
    price: 450,
    officialUrl: "https://fujifilm-x.com/global/products/accessories/ef-x500/",
  },
  {
    category: "flash",
    brand: "Fujifilm",
    model: "EF-60",
    description:
      "Radio-controlled wireless TTL flash. First Fuji flash with built-in radio receiver. Works with EF-W1.",
    mount: "X",
    guideNumber: 60,
    hasTtl: true,
    hasHss: true,
    isWirelessReceiver: true,
    price: 400,
    officialUrl: "https://fujifilm-x.com/global/products/accessories/ef-60/",
  },
  {
    category: "flash",
    brand: "Fujifilm",
    model: "EF-42",
    description: "Mid-range TTL/manual flash. Good travel companion.",
    mount: "X",
    guideNumber: 42,
    hasTtl: true,
    hasHss: false,
    isDiscontinued: true,
    price: 200,
    officialUrl: "https://fujifilm-x.com/global/products/accessories/ef-42/",
  },
  {
    category: "flash",
    brand: "Fujifilm",
    model: "EF-X20",
    description: "Compact TTL flash. Minimal footprint.",
    mount: "X",
    guideNumber: 20,
    hasTtl: true,
    hasHss: false,
    isDiscontinued: true,
    price: 170,
    officialUrl: "https://fujifilm-x.com/global/products/accessories/ef-x20/",
  },
  {
    category: "flash",
    brand: "Fujifilm",
    model: "EF-20",
    description:
      "Entry clip-on flash. TTL only, no manual. Draws from hotshoe.",
    mount: "X",
    guideNumber: 20,
    hasTtl: true,
    hasHss: false,
    isDiscontinued: true,
    price: 130,
    officialUrl: "https://fujifilm-x.com/global/products/accessories/ef-20/",
  },
  {
    category: "flash",
    brand: "Fujifilm",
    model: "EF-X8",
    description:
      "Tiny built-in-style clip flash. Powered by camera. Covers 16mm (24mm FF).",
    mount: "X",
    guideNumber: 8,
    hasTtl: true,
    hasHss: false,
    price: 52,
    officialUrl: "https://fujifilm-x.com/global/products/accessories/ef-x8/",
  },
  {
    category: "flash",
    brand: "Fujifilm",
    model: "EF-W1",
    description:
      "Wireless commander. Controls EF-60 units via radio. No flash output of its own.",
    mount: "X",
    guideNumber: 0,
    hasTtl: false,
    hasHss: false,
    isWirelessCommander: true,
    price: 200,
    officialUrl: "https://fujifilm-x.com/global/products/accessories/ef-w1/",
  },
];

// -----------------------------------------------------------------------------
// BATTERY GRIP
// -----------------------------------------------------------------------------

const batteryGrips: BatteryGripAccessory[] = [
  {
    category: "battery-grip",
    brand: "Fujifilm",
    model: "VG-XT4",
    description:
      "Vertical grip for X-T4. Holds 2x NP-W235. WR. Portrait shutter, AF-ON, AE-L, command dials.",
    mount: "X",
    compatibleWith: ["X-T4"],
    batteryType: "NP-W235",
    batteryCount: 2,
    hasVerticalControls: true,
    isWeatherSealed: true,
    price: 349,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/vg-xt4/",
  },
  {
    category: "battery-grip",
    brand: "Fujifilm",
    model: "VBG-XH",
    description:
      "Vertical grip for X-H2 / X-H2S. Holds 2x NP-W235. WR. Up to 1700 frames.",
    mount: "X",
    compatibleWith: ["X-H2", "X-H2S"],
    batteryType: "NP-W235",
    batteryCount: 2,
    hasVerticalControls: true,
    isWeatherSealed: true,
    price: 450,
    officialUrl: "https://fujifilm-x.com/global/products/accessories/vg-xh/",
  },
  {
    category: "battery-grip",
    brand: "Fujifilm",
    model: "VG-GFX100 II",
    description:
      "Grip for GFX100 II. WR. Extends battery life for long studio or field sessions.",
    mount: "GFX",
    compatibleWith: ["GFX100 II"],
    batteryType: "NP-T125",
    hasVerticalControls: true,
    isWeatherSealed: true,
    price: 500,
    officialUrl:
      "https://fujifilm-x.com/en-us/products/accessories/vg-gfx100ii/",
  },
  {
    category: "battery-grip",
    brand: "Fujifilm",
    model: "FT-XH",
    description:
      "File Transmitter Battery Grip for X-H2S. Wired LAN + high-speed wireless. Holds 2x NP-W235.",
    mount: "X",
    compatibleWith: ["X-H2S"],
    batteryType: "NP-W235",
    batteryCount: 2,
    hasVerticalControls: true,
    isWeatherSealed: true,
    price: 999,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/ft-xh/",
  },
  {
    category: "battery-grip",
    brand: "Fujifilm",
    model: "VPB-XT2",
    description:
      "Power Booster Grip for X-T2. Holds 2x NP-W126S. WR. Adds headphone jack, portrait controls.",
    mount: "X",
    compatibleWith: ["X-T2"],
    batteryType: "NP-W126S",
    batteryCount: 2,
    hasVerticalControls: true,
    isWeatherSealed: true,
    isDiscontinued: true,
    price: 250,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/vpb-xt2/",
  },
  {
    category: "battery-grip",
    brand: "Fujifilm",
    model: "VG-XT1",
    description:
      "Weather-sealed vertical grip for X-T1. Doubles battery life with 2x NP-W126. Adds portrait controls and command dials.",
    mount: "X",
    compatibleWith: ["X-T1"],
    batteryType: "NP-W126",
    batteryCount: 2,
    hasVerticalControls: true,
    isWeatherSealed: true,
    isDiscontinued: true,
    price: 250,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/vg-xt1/",
  },
  {
    category: "battery-grip",
    brand: "Fujifilm",
    model: "VG-XT3",
    description: "Vertical Battery Grip for X-T3. Holds 2x NP-W126S. WR.",
    mount: "X",
    compatibleWith: ["X-T3"],
    batteryType: "NP-W126S",
    batteryCount: 2,
    hasVerticalControls: true,
    isWeatherSealed: true,
    isDiscontinued: true,
    price: 250,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/vg-xt3/",
  },
  {
    category: "battery-grip",
    brand: "Fujifilm",
    model: "VG-XPro1",
    description:
      "Vertical Battery Grip for X-Pro1. Holds 2x NP-W126. First Fuji X grip.",
    mount: "X",
    compatibleWith: ["X-Pro1"],
    batteryType: "NP-W126",
    batteryCount: 2,
    hasVerticalControls: true,
    isDiscontinued: true,
    price: 250,
  },
];

// -----------------------------------------------------------------------------
// HAND GRIP
// -----------------------------------------------------------------------------

const handGrips: GenericAccessory[] = [
  {
    category: "hand-grip",
    brand: "Fujifilm",
    model: "MHG-XT3",
    description:
      "Metal Hand Grip for X-T3. Improves ergonomics, adds Arca-Swiss rail mount.",
    compatibleWith: ["X-T3"],
    isDiscontinued: true,
    price: 80,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/mhg-xt3/",
  },
  {
    category: "hand-grip",
    brand: "Fujifilm",
    model: "MHG-XT4",
    description:
      "Metal Hand Grip for X-T4. Improves grip, adds Arca-Swiss compatible rail.",
    compatibleWith: ["X-T4"],
    price: 80,
  },
  {
    category: "hand-grip",
    brand: "Fujifilm",
    model: "MHG-XT5",
    description:
      "Metal Hand Grip for X-T5. Improves grip, adds Arca-Swiss compatible rail.",
    compatibleWith: ["X-T5"],
    price: 170,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/mhg-xt5/",
  },
  {
    category: "hand-grip",
    brand: "Fujifilm",
    model: "MHG-XH",
    description:
      "Metal Hand Grip for X-H2 / X-H2S. Arca-Swiss rail, improved ergonomics.",
    compatibleWith: ["X-H2", "X-H2S"],
    price: 80,
  },
  {
    category: "hand-grip",
    brand: "Fujifilm",
    model: "MHG-XPRO2",
    description:
      "Metal Hand Grip for X-Pro2. Arca-Swiss rail, improves grip on the rangefinder-style body.",
    compatibleWith: ["X-Pro2"],
    isDiscontinued: true,
    price: 80,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/mhg-xpro2/",
  },
  {
    category: "hand-grip",
    brand: "Fujifilm",
    model: "MHG-XT10",
    description:
      "Metal Hand Grip for X-T10/X-T20. Improves grip, adds Arca-Swiss rail.",
    compatibleWith: ["X-T10", "X-T20"],
    isDiscontinued: true,
    price: 80,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/mhg-xt10/",
  },
];

// -----------------------------------------------------------------------------
// BATTERY
// -----------------------------------------------------------------------------

const batteries: BatteryAccessory[] = [
  {
    category: "battery",
    brand: "Fujifilm",
    model: "NP-W126S",
    description:
      "Standard X-series Li-ion battery. Improved over NP-W126. ~350 frames.",
    compatibleWith: [
      "X-T1",
      "X-T2",
      "X-T3",
      "X-Pro1",
      "X-Pro2",
      "X-E1",
      "X-E2",
      "X-E3",
      "X-T10",
      "X-T20",
      "X-T30",
      "X-H1",
    ],
    batteryType: "NP-W126S",
    price: 65,
    officialUrl: "https://fujifilm-x.com/global/products/accessories/np-w126s/",
  },
  {
    category: "battery",
    brand: "Fujifilm",
    model: "NP-W235",
    description:
      "High-capacity Li-ion for newer flagships. ~680 frames (X-T5).",
    compatibleWith: ["X-T4", "X-T5", "X-H2", "X-H2S", "X-S20"],
    batteryType: "NP-W235",
    price: 89,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/np-w235/",
  },
  {
    category: "battery",
    brand: "Fujifilm",
    model: "NP-W126",
    description:
      "Original X-series Li-ion battery. Replaced by NP-W126S but still compatible. Widely available used.",
    compatibleWith: [
      "X-T1",
      "X-T2",
      "X-T3",
      "X-Pro1",
      "X-Pro2",
      "X-E1",
      "X-E2",
      "X-E3",
      "X-T10",
      "X-T20",
      "X-T30",
      "X-H1",
    ],
    batteryType: "NP-W126",
    isDiscontinued: true,
    price: 50,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/np-w126/",
  },
];

// -----------------------------------------------------------------------------
// CHARGER
// -----------------------------------------------------------------------------

const chargers: ChargerAccessory[] = [
  {
    category: "charger",
    brand: "Fujifilm",
    model: "BC-W126S",
    description: "Single-slot charger for NP-W126S. Compact, travel-friendly.",
    compatibleWith: ["NP-W126S"],
    batteryType: "NP-W126S",
    slots: 1,
    price: 70,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/bc-w126s/",
  },
];

// -----------------------------------------------------------------------------
// LENS ACCESSORY
// -----------------------------------------------------------------------------

const lensAccessories: LensAccessory[] = [
  {
    category: "lens-accessory",
    brand: "Fujifilm",
    model: "MCEX-11 WR",
    description:
      "Extension tube 11mm. Increases macro magnification. WR. Manual focus only.",
    mount: "X",
    compatibleWith: [
      "XF 16mm",
      "XF 23mm",
      "XF 27mm",
      "XF 35mm",
      "XF 50mm",
      "XF 56mm",
      "XF 60mm",
      "XF 80mm",
      "XF 90mm",
    ],
    isWeatherSealed: true,
    price: 100,
  },
  {
    category: "lens-accessory",
    brand: "Fujifilm",
    model: "MCEX-16 WR",
    description: "Extension tube 16mm. Greater magnification than MCEX-11. WR.",
    mount: "X",
    compatibleWith: [
      "XF 16mm",
      "XF 23mm",
      "XF 27mm",
      "XF 35mm",
      "XF 50mm",
      "XF 56mm",
      "XF 60mm",
      "XF 80mm",
      "XF 90mm",
    ],
    isWeatherSealed: true,
    price: 100,
  },
  {
    category: "lens-accessory",
    brand: "Fujifilm",
    model: "MCEX-11",
    description:
      "Original non-WR extension tube 11mm. Works with all XF lenses. No autofocus.",
    mount: "X",
    isDiscontinued: true,
    price: 108,
    officialUrl: "https://fujifilm-x.com/global/products/accessories/mcex-11/",
  },
  {
    category: "lens-accessory",
    brand: "Fujifilm",
    model: "MCEX-16",
    description:
      "Original non-WR extension tube 16mm. Works with all XF lenses. No autofocus.",
    mount: "X",
    isDiscontinued: true,
    price: 99,
    officialUrl: "https://fujifilm-x.com/global/products/accessories/mcex-16/",
  },
  {
    category: "lens-accessory",
    brand: "Fujifilm",
    model: "MCEX-18G WR",
    description: "Extension tube 18mm for G-Mount. WR.",
    mount: "GFX",
    isWeatherSealed: true,
    price: 200,
    officialUrl:
      "https://fujifilm-x.com/global/products/accessories/mcex-18g-wr/",
  },
  {
    category: "lens-accessory",
    brand: "Fujifilm",
    model: "MCEX-45G WR",
    description:
      "Extension tube 45mm for G-Mount. WR. High magnification for macro work on GFX.",
    mount: "GFX",
    isWeatherSealed: true,
    price: 500,
    officialUrl:
      "https://fujifilm-x.com/global/products/accessories/mcex-45g-wr/",
  },
  {
    category: "lens-accessory",
    brand: "Fujifilm",
    model: "XF 1.4x TC WR",
    description:
      "Teleconverter 1.4x. 1 stop light loss. AF retained on compatible XF lenses.",
    mount: "X",
    compatibleWith: [
      "XF 50-140mm",
      "XF 100-400mm",
      "XF 200mm",
      "XF 70-300mm",
      "XF 150-600mm",
    ],
    magnificationFactor: 1.4,
    isAfRetained: true,
    isWeatherSealed: true,
    price: 449,
    officialUrl: "https://fujifilm-x.com/global/products/lenses/xf14x-tc-wr/",
  },
  {
    category: "lens-accessory",
    brand: "Fujifilm",
    model: "XF 2.0x TC WR",
    description:
      "Teleconverter 2.0x. 2 stop light loss. AF retained on compatible XF lenses.",
    mount: "X",
    compatibleWith: [
      "XF 50-140mm",
      "XF 100-400mm",
      "XF 200mm",
      "XF 70-300mm",
      "XF 150-600mm",
    ],
    magnificationFactor: 2.0,
    isAfRetained: true,
    isWeatherSealed: true,
    price: 449,
    officialUrl: "https://fujifilm-x.com/global/products/lenses/xf2x-tc-wr/",
  },
];

// -----------------------------------------------------------------------------
// ADAPTER
// -----------------------------------------------------------------------------

const adapters: AdapterAccessory[] = [
  {
    category: "adapter",
    brand: "Fujifilm",
    model: "M Mount Adapter",
    description: "Allows Leica M-mount lenses on X-mount. Manual focus only.",
    compatibleWith: [
      "X-T1",
      "X-T2",
      "X-T3",
      "X-T4",
      "X-T5",
      "X-Pro1",
      "X-Pro2",
      "X-Pro3",
      "X-H1",
      "X-H2",
      "X-H2S",
    ],
    sourceMount: "Leica M",
    targetMount: "X",
    isAfSupported: false,
    price: 260,
    officialUrl:
      "https://fujifilm-x.com/global/products/accessories/m-mount-adapter/",
  },
  {
    category: "adapter",
    brand: "Fujifilm",
    model: "H Mount Adapter G",
    description:
      "Allows older Fujifilm H-mount medium format lenses on GFX. Manual aperture control.",
    compatibleWith: [
      "GFX 50S",
      "GFX 50R",
      "GFX 50S II",
      "GFX 100",
      "GFX 100S",
      "GFX 100 II",
    ],
    sourceMount: "Fuji H",
    targetMount: "GFX",
    isAfSupported: false,
    hasApertureControl: true,
    price: 660,
    officialUrl:
      "https://fujifilm-x.com/global/products/accessories/h-mount-adapter-g/",
  },
];

// -----------------------------------------------------------------------------
// REMOTE
// -----------------------------------------------------------------------------

const remotes: RemoteAccessory[] = [
  {
    category: "remote",
    brand: "Fujifilm",
    model: "RR-100",
    description:
      "Wired remote release. 2.5mm jack. Reduces camera shake for tripod work and time exposures.",
    compatibleWith: [
      "X-T1",
      "X-T2",
      "X-T3",
      "X-T4",
      "X-T5",
      "X-Pro1",
      "X-Pro2",
      "X-Pro3",
      "X-H1",
      "X-H2",
      "X-H2S",
    ],
    connectionType: "wired-2.5mm",
    price: 40,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/rr-100/",
  },
  {
    category: "remote",
    brand: "Fujifilm",
    model: "TG-BT1",
    description:
      "Bluetooth tripod grip. Controls shutter, video, power zoom lenses via Bluetooth.",
    compatibleWith: [
      "X-T3",
      "X-T4",
      "X-T5",
      "X-Pro3",
      "X-H1",
      "X-H2",
      "X-H2S",
      "X-E4",
      "X-S10",
      "X-S20",
    ],
    connectionType: "bluetooth",
    price: 200,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/tg-bt1/",
  },
];

// -----------------------------------------------------------------------------
// AUDIO
// -----------------------------------------------------------------------------

const audio: AudioAccessory[] = [
  {
    category: "audio",
    brand: "Fujifilm",
    model: "MIC-ST1",
    description:
      "Compact stereo microphone. Mounts on hotshoe, plugs into 3.5mm mic input. Improves video audio.",
    compatibleWith: [
      "X-T1",
      "X-T2",
      "X-T3",
      "X-T4",
      "X-Pro1",
      "X-Pro2",
      "X-Pro3",
      "X-H1",
      "X-H2",
      "X-H2S",
    ],
    micPattern: "stereo",
    connectionType: "wired-2.5mm",
    price: 130,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/mic-st1/",
  },
];

// -----------------------------------------------------------------------------
// COOLING / BODY ACCESSORY
// -----------------------------------------------------------------------------

const bodyAccessories: GenericAccessory[] = [
  {
    category: "cooling",
    brand: "Fujifilm",
    model: "FAN-001",
    description:
      "Cooling fan for extended video recording. Prevents overheating during long 4K/6K sessions.",
    compatibleWith: ["X-M5", "X-H2S", "X-H2", "X-S20"],
    price: 199,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/fan-001/",
  },
  {
    category: "body-accessory",
    brand: "Fujifilm",
    model: "BLC-XT3",
    description:
      "Leather bottom case for X-T3. Pictures can be taken with case on.",
    compatibleWith: ["X-T3"],
    isDiscontinued: true,
    price: 80,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/blc-xt3/",
  },
  {
    category: "body-accessory",
    brand: "Fujifilm",
    model: "BLC-XT2",
    description:
      "Leather bottom case for X-T2. Full access to battery/card slot.",
    compatibleWith: ["X-T2"],
    isDiscontinued: true,
    price: 80,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/blc-xt2/",
  },
  {
    category: "body-accessory",
    brand: "Fujifilm",
    model: "BLC-XT1",
    description:
      "Leather bottom case for X-T1. Popular for the classic X-T1 aesthetic.",
    compatibleWith: ["X-T1"],
    isDiscontinued: true,
    price: 80,
  },
  {
    category: "body-accessory",
    brand: "Fujifilm",
    model: "LC-X100V",
    description:
      "Genuine leather case for X100V. Formfitting, improves grip, access to battery slot.",
    compatibleWith: ["X100V"],
    price: 295,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/lc-x100v/",
  },
  {
    category: "body-accessory",
    brand: "Fujifilm",
    model: "GB-001",
    description:
      "Grip belt add-on. Improves hand grip when combined with a hand grip accessory.",
    compatibleWith: ["X-T1", "X-T2", "X-T3", "X-T4", "X-T5"],
    price: 40,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/gb-001/",
  },
  {
    category: "body-accessory",
    brand: "Fujifilm",
    model: "CVR-XT3",
    description: "Cover set for X-T3. Protects connector covers from wear.",
    compatibleWith: ["X-T3"],
    isDiscontinued: true,
    price: 30,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/cvr-xt3/",
  },
  {
    category: "body-accessory",
    brand: "Fujifilm",
    model: "EF-BP1",
    description:
      "External battery pack for EF-X500 flash. Takes 8x AA batteries for extended flash sessions.",
    compatibleWith: ["EF-X500"],
    price: 200,
    officialUrl: "https://fujifilm-x.com/en-us/products/accessories/ef-bp1/",
  },
];

// -----------------------------------------------------------------------------
// COMBINED
// -----------------------------------------------------------------------------

const accessories: Accessory[] = [
  ...flashes,
  ...batteryGrips,
  ...handGrips,
  ...batteries,
  ...chargers,
  ...lensAccessories,
  ...adapters,
  ...remotes,
  ...audio,
  ...bodyAccessories,
];

export default accessories;
