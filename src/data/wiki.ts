import type { WikiEntry } from "../types/wiki";

const wiki: WikiEntry[] = [
  // ---------------------------------------------------------------------------
  // AF MOTORS (#30)
  // ---------------------------------------------------------------------------
  {
    slug: "af-motors",
    title: "AF Motors",
    summary: "How autofocus motors work in Fujifilm lenses: DC, STM, and LM types compared.",
    body: [
      "Fujifilm X-mount lenses use three types of autofocus motor. The motor type affects focus speed, accuracy, noise, and video suitability.",
      "DC (coreless motor) is the oldest design, found in early XF lenses. It uses a small DC motor with a gear train. Focus is adequate for stills but audible and slower than modern alternatives. DC lenses hunt more in low light and are not ideal for video due to motor noise.",
      "STM (stepping motor) is a stepper motor that moves in precise increments. It is quieter than DC and well-suited to video because it produces smooth, silent focus transitions. STM lenses are common in mid-range XF and XC lenses. Focus speed is good but not class-leading.",
      "LM (linear motor) is Fujifilm's fastest and quietest AF technology. It uses electromagnetic force to move the focus group directly, without gears. LM lenses focus almost instantly, track moving subjects reliably, and are virtually silent. All recent flagship XF lenses (f/1.4 R LM WR series, XF 50-140mm, XF 150-600mm) use linear motors.",
      "For sport, wildlife, and video, LM lenses are strongly preferred. For general photography, STM is more than adequate. DC lenses still take sharp photos but may struggle with fast action.",
    ],
    related: ["focus-modes"],
  },

  // ---------------------------------------------------------------------------
  // ASPECT RATIOS (#33)
  // ---------------------------------------------------------------------------
  {
    slug: "aspect-ratios",
    title: "Aspect Ratios",
    summary: "Common sensor aspect ratios in Fujifilm cameras and how they affect composition.",
    body: [
      "Aspect ratio is the proportional relationship between an image's width and height. Fujifilm X-series cameras use a 3:2 sensor (same as 35mm film), while GFX medium format cameras use a 4:3 sensor.",
      "3:2 is slightly wider and suits landscapes, environmental portraits, and street photography. It matches standard print sizes like 6x4 inches. Most Fuji X photographers shoot natively in 3:2.",
      "4:3 is taller and more balanced, common in medium format. It gives more vertical space for architecture and portraits. GFX cameras default to 4:3.",
      "Fujifilm cameras can crop in-camera to other ratios: 16:9 (cinematic wide), 1:1 (square, good for social media and symmetry), and 65:24 (panoramic, available on some models). These crops reduce resolution since the sensor is physically 3:2 or 4:3.",
      "The aspect ratio you choose affects composition. Wider ratios emphasize horizontal lines and lead the eye across the frame. Taller ratios give subjects more breathing room above and below. Square crops force symmetrical or centered compositions.",
    ],
  },

  // ---------------------------------------------------------------------------
  // BODY STYLES (#26)
  // ---------------------------------------------------------------------------
  {
    slug: "body-styles",
    title: "Body Styles",
    summary: "Fujifilm camera form factors: standard, pro grip, rangefinder, and compact.",
    body: [
      "Fujifilm cameras come in four form factors, each suited to different shooting styles.",
      "Standard bodies (X-T series) resemble traditional SLR cameras with a central viewfinder hump and top-plate dials. They are the most versatile form factor, comfortable for extended handheld shooting, and accept battery grips for vertical shooting. The X-T5 and X-T4 are the most popular examples.",
      "Pro grip bodies (X-H series) have a deep integrated grip and larger body optimized for heavy lenses and long sessions. The X-H2S and X-H2 are built for professional sport, wildlife, and video work where ergonomics and heat dissipation matter.",
      "Rangefinder bodies (X-Pro series) place the viewfinder in the top-left corner, like classic Leica rangefinders. This allows shooting with both eyes open. The X-Pro3 is the current model. These cameras appeal to street and documentary photographers who value a discreet, mechanical shooting experience.",
      "Compact bodies (X-E, X-S, X-M, X-A series) are smaller and lighter, often without a viewfinder hump. The X-E4 and X-S20 are popular travel cameras. The X100 series is a fixed-lens compact with a leaf shutter, beloved for street photography.",
    ],
    related: ["af-motors"],
  },

  // ---------------------------------------------------------------------------
  // BORTLE SCALE (#25)
  // ---------------------------------------------------------------------------
  {
    slug: "bortle-scale",
    title: "Bortle Scale",
    summary: "A 1-9 scale measuring night sky darkness, critical for astrophotography and nightscape planning.",
    body: [
      "The Bortle scale rates night sky darkness from 1 (pristine) to 9 (inner-city). It was created by amateur astronomer John Bortle in 2001 and is the standard reference for astrophotography site selection.",
      "Bortle 1-2: Excellent dark sky. The Milky Way casts visible shadows. Zodiacal light extends to the zenith. These sites are remote — think national parks far from cities. Ideal for deep-sky widefield astrophotography.",
      "Bortle 3-4: Good dark sky. The Milky Way is clearly structured with dark lanes visible. Some light domes on the horizon from distant towns. Most dedicated astrophotography is done at Bortle 3-4 — accessible yet dark enough for serious work.",
      "Bortle 5-6: Suburban sky. The Milky Way is visible but washed out. Light pollution is obvious in all directions. Short focal length nightscape shots are still possible, but long exposures show significant sky glow. A light pollution filter helps.",
      "Bortle 7-9: Urban sky. Only bright stars and planets are visible. The Milky Way is invisible at Bortle 7+ and the sky never gets truly dark. Astrophotography is limited to the moon, planets, and very bright nebulae with narrowband filters.",
      "For Fuji nightscape shooters: at Bortle 4 or darker, an f/1.4 prime on a star tracker produces stunning results. At Bortle 5-6, a light pollution filter and stacking multiple exposures compensates for the brighter sky. At Bortle 7+, consider driving to a darker site.",
    ],
  },

  // ---------------------------------------------------------------------------
  // COMA (#29)
  // ---------------------------------------------------------------------------
  {
    slug: "coma",
    title: "Coma",
    summary: "An optical aberration that stretches point light sources into comet-like shapes near frame edges.",
    body: [
      "Coma (short for comatic aberration) causes point light sources — especially stars — to appear as small comet or bird-wing shapes instead of sharp points. It is worst in the corners of the frame and at wide apertures.",
      "Coma is caused by off-axis light rays hitting the lens at an angle. Rays passing through different zones of the lens converge at slightly different points, smearing the image radially outward from center.",
      "For nightscape and astrophotography, coma is the most important optical flaw to evaluate. A lens with strong coma turns corner stars into distracting smears, ruining widefield Milky Way shots. Coma cannot be corrected in post-processing.",
      "Stopping down reduces coma significantly — most lenses improve dramatically by f/2.8. But nightscape shooters need wide apertures for light gathering, so a lens that controls coma wide open is far more valuable than one that only sharpens stopped down.",
      "In the Fuji.me! scoring system, coma is rated 0-2 based on corner star rendering at maximum aperture. A score of 2 means minimal coma even wide open — stars stay tight points across the frame. A score of 0 means heavy coma that makes the lens unsuitable for astrophotography without stopping down.",
    ],
    related: ["scoring-methodology", "mtf-charts"],
  },

  // ---------------------------------------------------------------------------
  // DIFFRACTION LIMIT (#31)
  // ---------------------------------------------------------------------------
  {
    slug: "diffraction-limit",
    title: "Diffraction Limit",
    summary: "The aperture beyond which stopping down reduces sharpness instead of increasing it.",
    body: [
      "Diffraction is a physical property of light: when light passes through a small opening, it bends and spreads. In photography, as you stop down the aperture, the opening becomes small enough that diffraction begins to soften the image.",
      "Every lens has a diffraction-limited aperture beyond which further stopping down reduces overall sharpness even though depth of field increases. On Fujifilm X-Trans sensors (APS-C, ~23.5mm crop), diffraction becomes visible around f/8-f/11 depending on the sensor resolution.",
      "On the 26MP X-Trans IV/V sensors (X-T4, X-T5, X-H2S), diffraction softening is noticeable from about f/11. On the 40MP X-H2, it starts closer to f/8 because the smaller pixel pitch is more sensitive to diffraction spread.",
      "On GFX medium format (44x33mm sensor), the larger sensor and pixel pitch push the diffraction limit to around f/16-f/22, giving more room to stop down for depth of field.",
      "Practical takeaway: for maximum sharpness on APS-C Fuji cameras, stay between f/5.6 and f/8. Use f/11 only when you need the depth of field. Avoid f/16 and smaller unless depth of field is more important than pixel-level sharpness. For landscapes where you want front-to-back sharpness, focus stacking at f/5.6-f/8 gives better results than shooting at f/16.",
    ],
  },

  // ---------------------------------------------------------------------------
  // FILTER TYPES (#35)
  // ---------------------------------------------------------------------------
  {
    slug: "filter-types",
    title: "Filter Types",
    summary: "Lens filters for Fujifilm shooters: CPL, ND, GND, UV, black mist, IR, and light pollution.",
    body: [
      "Lens filters screw onto the front of a lens (or slot into a holder) and modify the light before it reaches the sensor. Fujifilm lenses use standard filter threads, so any brand of filter works.",
      "CPL (circular polarizer): Reduces reflections from water and glass, deepens blue skies, and increases color saturation. Essential for landscape photography. Rotate the filter ring to control the effect. Costs about 1 stop of light.",
      "ND (neutral density): A dark filter that reduces light evenly, allowing longer exposures in bright conditions. Common strengths are ND8 (3 stops), ND64 (6 stops), and ND1000 (10 stops). Used for smooth water, motion blur in daylight, and shooting wide open in bright sun.",
      "GND (graduated neutral density): Dark on top, clear on bottom, with a gradual transition. Balances a bright sky against a darker foreground in a single exposure. Available in soft-edge (gradual transition) and hard-edge (sharp line) versions. Most useful for seascapes and flat horizons.",
      "Black mist (or pro-mist): A diffusion filter that softens highlights and reduces contrast, creating a cinematic or dreamy look. Popular for portrait and street photography. Strengths like 1/4 or 1/8 are subtle; 1/2 is more obvious.",
      "Light pollution filter: Blocks specific wavelengths of artificial light (sodium vapor, LED). Used for nightscape and astrophotography in suburban areas (Bortle 5-6). Does not replace dark skies but improves contrast on the Milky Way.",
      "UV and IR filters are less common in digital photography. UV filters are sometimes used as lens protection but can cause flare. IR filters block visible light for infrared photography, which requires camera conversion or very long exposures.",
    ],
    related: ["bortle-scale"],
  },

  // ---------------------------------------------------------------------------
  // FOCUS MODES (#34)
  // ---------------------------------------------------------------------------
  {
    slug: "focus-modes",
    title: "Focus Modes",
    summary: "Autofocus modes on Fujifilm cameras: AF-S, AF-C, and MF explained.",
    body: [
      "Fujifilm cameras offer three focus modes, selected via the focus mode switch on the camera body.",
      "AF-S (single autofocus): The camera focuses once when you half-press the shutter. Focus locks and does not change until you release and press again. Best for stationary subjects: landscapes, architecture, portraits of still subjects, macro. AF-S is the most accurate mode because the camera can take its time to confirm focus.",
      "AF-C (continuous autofocus): The camera continuously adjusts focus as long as the shutter button is half-pressed. Essential for moving subjects: sport, wildlife, street, children. The camera predicts subject motion and adjusts accordingly. On newer bodies (X-T5, X-H2S), AF-C with subject detection (face, eye, animal, vehicle) is highly reliable.",
      "MF (manual focus): The camera does not autofocus. You turn the focus ring to set focus manually. Essential for manual-focus lenses (vintage adapts, Laowa, 7Artisans) and preferred by some photographers for deliberate focus control. Fujifilm's focus peaking highlights in-focus edges in a chosen color, and the digital split image (on X-Pro and X-T bodies) replicates the rangefinder focusing experience.",
      "Most Fujifilm cameras also support AF+MF hybrid mode: the camera autofocuses with AF-S, then you can fine-tune with the focus ring without releasing the shutter button. This is useful for macro and product photography where autofocus gets close but needs manual refinement.",
    ],
    related: ["af-motors"],
  },

  // ---------------------------------------------------------------------------
  // MTF CHARTS (#28)
  // ---------------------------------------------------------------------------
  {
    slug: "mtf-charts",
    title: "MTF Charts",
    summary: "How to read MTF (Modulation Transfer Function) charts to evaluate lens sharpness.",
    body: [
      "MTF (Modulation Transfer Function) measures how well a lens reproduces contrast at different levels of detail. An MTF chart plots contrast (vertical axis, 0-1) against distance from the image center to the edge (horizontal axis). Higher values mean sharper images.",
      "MTF charts typically show two line types: sagittal (parallel to a line from center to corner) and meridional (perpendicular to that line). When both lines are close together, the lens has low astigmatism. When they diverge, point light sources become elongated in one direction.",
      "Charts are usually measured at two spatial frequencies: 10 lp/mm (line pairs per millimeter) for contrast, and 30 lp/mm (or 40 lp/mm on higher resolution tests) for fine detail resolution. The 10 lp/mm lines tell you about overall contrast and \"pop\"; the 30 lp/mm lines tell you about resolving power and fine texture.",
      "A great lens shows both lines above 0.8 across the frame at 10 lp/mm, and above 0.6 at 30 lp/mm. A lens that starts high in the center but drops sharply toward the edges has good center sharpness but weak corners — common in fast primes wide open.",
      "MTF charts have limitations: they are measured at a single aperture (usually wide open and f/8), do not capture chromatic aberration, coma, or flare, and lab conditions do not match real-world shooting. Use them as one input alongside field reports, sample images, and optical scores.",
      "In Fuji.me!, the center/corner stopped and wide-open scores are derived from MTF data and lab tests. They are simplified to a 0-2 scale for quick comparison across the entire lens lineup.",
    ],
    related: ["scoring-methodology", "coma"],
  },

  // ---------------------------------------------------------------------------
  // SCORING METHODOLOGY (#27)
  // ---------------------------------------------------------------------------
  {
    slug: "scoring-methodology",
    title: "Scoring Methodology",
    summary: "How Fuji.me! scores lenses for each photography genre using optical data and weighted formulas.",
    body: [
      "Fuji.me! scores lenses on a 0-100 scale for each photography genre. Scores are calculated from optical performance data, not marketing specs or subjective reviews. The goal is to answer: \"How well does this lens perform for this specific genre?\"",
      "Each genre uses a weighted formula that emphasizes the optical qualities most important for that type of photography. For example, nightscape scoring heavily weights coma and wide-open corner sharpness, while portrait scoring emphasizes bokeh and center sharpness wide open.",
      "Optical data comes from lab tests and detailed field reports by trusted review sources (LensTip, Optical Limits, DPReview). Each optical field (center sharpness, corner sharpness, coma, astigmatism, chromatic aberration, distortion, vignetting, bokeh, flare resistance) is rated on a 0-2 scale where 0 is poor, 1 is average, and 2 is excellent.",
      "Lenses without sufficient optical data are shown as \"Not yet scored\" rather than estimated. We only score lenses when we have data from trusted sources. This means some newer or niche lenses may lack scores until reviews are published.",
      "Genre scores are supplemented by editorial picks — lenses that the formula alone might not surface but that are widely recognized as exceptional for a given genre based on field experience and photographer consensus.",
      "Scoring is opinionated and transparent. The weights and formulas are visible in the codebase. We acknowledge that no formula perfectly captures real-world performance, and encourage photographers to use scores as a starting point, not a final verdict.",
    ],
    related: ["mtf-charts", "coma"],
  },

  // ---------------------------------------------------------------------------
  // SUNSTARS (#32)
  // ---------------------------------------------------------------------------
  {
    slug: "sunstars",
    title: "Sunstars",
    summary: "How aperture blade count and shape create starburst patterns around point light sources.",
    body: [
      "Sunstars (also called starbursts or diffraction spikes) are the radiating lines that appear around bright point light sources — the sun, streetlights, candles — when you stop down the aperture. They are caused by light diffracting around the aperture blade edges.",
      "The number of points in a sunstar depends on the number of aperture blades. Lenses with an even number of blades (6, 8, 10) produce that same number of points. Lenses with an odd number of blades (7, 9) produce twice that number of points (14, 18) because each blade edge creates a spike that overlaps with the opposite edge's spike.",
      "Most Fujifilm XF lenses have 7 or 9 rounded aperture blades, producing 14-point or 18-point sunstars. The rounded blade design prioritizes smooth bokeh at wide apertures but can produce softer, less defined sunstars compared to straight-bladed lenses.",
      "Sunstar quality depends on stopping down: they typically appear from f/8 and become more defined at f/11-f/16. Wider apertures produce soft, bloomy highlights instead of defined spikes.",
      "For architecture and cityscape photographers, well-defined sunstars add visual interest to streetlight and window reflections. For nightscape shooters, sunstars on bright stars can be a feature or a distraction depending on the composition. Landscape photographers often use sunstars on the sun peeking over a ridge as a compositional anchor.",
    ],
    related: ["diffraction-limit"],
  },
];

export { wiki };
