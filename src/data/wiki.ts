import type { WikiEntry } from "../types/wiki";

const wiki: WikiEntry[] = [
  {
    slug: "active-af",
    title: "Active AF",
    fullTitle: "Active Autofocus",
    category: "Focus",
    summary: "AF category where the camera emits energy (light or sound) and measures the reflection to determine distance to the subject.",
    body: [
      "AF category where the camera emits energy (light or sound) and measures the reflection to determine distance to the subject. Works in complete darkness and on low-contrast subjects. Range is limited and can be fooled by glass. Used as AF-assist in some cameras.",
    ],
  },
  {
    slug: "af-motors",
    title: "AF Motors",
    category: "Focus",
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
  {
    slug: "af-c",
    title: "AF-C",
    fullTitle: "Continuous AF",
    category: "Focus",
    summary: "Camera continuously adjusts focus while the shutter is held half-pressed, tracking moving subjects.",
    body: [
      "Camera continuously adjusts focus while the shutter is held half-pressed, tracking moving subjects. Essential for sport and wildlife. Fuji X-series AF-C uses PDAF only within PDAF coverage zones.",
    ],
  },
  {
    slug: "af-s",
    title: "AF-S",
    fullTitle: "Single AF",
    category: "Focus",
    summary: "Camera focuses once, then locks.",
    body: [
      "Camera focuses once, then locks. Best for stationary subjects. Typically uses hybrid CDAF/PDAF for accuracy. See Focus modes sheet for Fuji-specific behaviour by focus point type.",
    ],
  },
  {
    slug: "aliasing",
    title: "Aliasing",
    fullTitle: "Aliasing",
    category: "Optics",
    summary: "Artefact caused when the sensor resolution is insufficient to capture fine detail, resulting in moiré patterns or stair-stepping on diagonal lines.",
    body: [
      "Artefact caused when the sensor resolution is insufficient to capture fine detail, resulting in moiré patterns or stair-stepping on diagonal lines. Prevented by anti-aliasing filters.",
    ],
  },
  {
    slug: "angular-resolution",
    title: "Angular resolution",
    fullTitle: "Angular Resolution",
    category: "Optics",
    summary: "The minimum angle between two point sources that a system can resolve as distinct.",
    body: [
      "The minimum angle between two point sources that a system can resolve as distinct. For a camera: limited by both the diffraction limit (aperture) and sensor pixel pitch. Determines effective resolving power at a given distance.",
    ],
  },
  {
    slug: "anti-aliasing",
    title: "Anti-aliasing",
    category: "Optics",
    summary: "An optical low-pass filter placed in front of the sensor that slightly blurs the image to prevent aliasing artefacts.",
    body: [
      "An optical low-pass filter placed in front of the sensor that slightly blurs the image to prevent aliasing artefacts. Reduces sharpness marginally; many modern cameras omit it.",
    ],
  },
  {
    slug: "anti-reflective-coating",
    title: "Anti-Reflective Coating",
    category: "Optics",
    summary: "A specific type of lens coating that minimises light reflection at glass-air interfaces.",
    body: [
      "A specific type of lens coating that minimises light reflection at glass-air interfaces. Without it, each lens element reflects ~4% of light, causing flare and contrast loss.",
    ],
  },
  {
    slug: "aov",
    title: "AoV",
    fullTitle: "Angle of View",
    category: "Geometry",
    summary: "The angular extent of the scene captured by a lens, measured diagonally, horizontally or vertically.",
    body: [
      "The angular extent of the scene captured by a lens, measured diagonally, horizontally or vertically. Wider AoV = wider lens. Determined by focal length and sensor size.",
    ],
  },
  {
    slug: "apd",
    title: "APD",
    fullTitle: "Apodization Filter",
    category: "Lenses",
    summary: "A radial neutral-density filter built into the lens that gradually reduces light transmission towards the outer aperture zone.",
    body: [
      "A radial neutral-density filter built into the lens that gradually reduces light transmission towards the outer aperture zone. Smooths bokeh by eliminating the hard edge of the aperture disc. Used in the Fujifilm XF 56mm f/1.2 APD. Causes ~1 stop light loss.",
    ],
  },
  {
    slug: "aperture",
    title: "Aperture",
    fullTitle: "Aperture",
    category: "Exposure",
    summary: "The opening in the lens that controls light transmission.",
    body: [
      "The opening in the lens that controls light transmission. Expressed as f-number (f/2.8, f/8). Wider aperture (lower f-number) = more light, shallower DoF, faster shutter possible.",
    ],
  },
  {
    slug: "aperture-ring",
    title: "Aperture Ring",
    category: "Lenses",
    summary: "A physical ring on the lens barrel that controls the aperture directly, independent of camera dials.",
    body: [
      "A physical ring on the lens barrel that controls the aperture directly, independent of camera dials. XF lenses marked 'R' feature an aperture ring with click stops at each f-stop. Preferred by photographers who want tactile aperture control without diving into menus.",
    ],
  },
  {
    slug: "aperture-sweet-spot",
    title: "Aperture Sweet Spot",
    category: "Exposure",
    summary: "The aperture at which a lens delivers peak sharpness across the frame, typically 2–3 stops below maximum aperture.",
    body: [
      "The aperture at which a lens delivers peak sharpness across the frame, typically 2–3 stops below maximum aperture. For APS-C the sweet spot is f/5.6–f/8 — the lower end applies to high-resolution bodies (40MP+) where diffraction becomes visible earlier. Stopping down further reduces sharpness due to diffraction.",
    ],
  },
  {
    slug: "aps-c",
    title: "APS-C",
    fullTitle: "Advanced Photo System type-C",
    category: "Sensor",
    summary: "A sensor format measuring approximately 23.",
    body: [
      "A sensor format measuring approximately 23.5×15.6mm, with a crop factor of 1.5× (Fujifilm). Smaller and lighter than full-frame but captures less light per pixel at equivalent aperture.",
    ],
  },
  {
    slug: "aspect-ratios",
    title: "Aspect Ratios",
    category: "Geometry",
    summary: "Common sensor aspect ratios in Fujifilm cameras and how they affect composition.",
    body: [
      "Aspect ratio is the proportional relationship between an image's width and height. Fujifilm X-series cameras use a 3:2 sensor (same as 35mm film), while GFX medium format cameras use a 4:3 sensor.",
      "3:2 is slightly wider and suits landscapes, environmental portraits, and street photography. It matches standard print sizes like 6x4 inches. Most Fuji X photographers shoot natively in 3:2.",
      "4:3 is taller and more balanced, common in medium format. It gives more vertical space for architecture and portraits. GFX cameras default to 4:3.",
      "Fujifilm cameras can crop in-camera to other ratios: 16:9 (cinematic wide), 1:1 (square, good for social media and symmetry), and 65:24 (panoramic, available on some models). These crops reduce resolution since the sensor is physically 3:2 or 4:3.",
      "The aspect ratio you choose affects composition. Wider ratios emphasize horizontal lines and lead the eye across the frame. Taller ratios give subjects more breathing room above and below. Square crops force symmetrical or centered compositions.",
    ],
  },
  {
    slug: "beauty-dish",
    title: "Beauty dish",
    category: "Lighting",
    summary: "A circular modifier with a central deflector that produces a distinctive quality of light — softer than bare flash but harder than a softbox.",
    body: [
      "A circular modifier with a central deflector that produces a distinctive quality of light — softer than bare flash but harder than a softbox. Creates a characteristic ring catchlight. Widely used for portrait and fashion photography.",
    ],
  },
  {
    slug: "body-styles",
    title: "Body Styles",
    category: "Sensor",
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
  {
    slug: "bokeh",
    title: "Bokeh",
    fullTitle: "Bokeh",
    category: "Optics",
    summary: "The aesthetic quality of the out-of-focus areas in an image.",
    body: [
      "The aesthetic quality of the out-of-focus areas in an image. Determined by aperture shape, lens design, and aberrations. Smooth, circular bokeh is generally considered pleasing; 'nervous' bokeh has hard edges.",
    ],
  },
  {
    slug: "bortle-scale",
    title: "Bortle Scale",
    category: "Exposure",
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
  {
    slug: "brenizer-method",
    title: "Brenizer method",
    fullTitle: "Brenizer Method",
    category: "Composition",
    summary: "Technique pioneered by Ryan Brenizer: shoot a subject at wide aperture with a telephoto lens, then stitch multiple images into a panoramic frame.",
    body: [
      "Technique pioneered by Ryan Brenizer: shoot a subject at wide aperture with a telephoto lens, then stitch multiple images into a panoramic frame. Produces a field of view resembling a wide lens but with the extremely shallow DoF of a fast telephoto.",
    ],
  },
  {
    slug: "cdaf",
    title: "CDAF",
    fullTitle: "Contrast Detection AF  [Passive]",
    category: "Focus",
    summary: "Moves the lens in small steps and measures contrast at each position; stops when contrast peaks.",
    body: [
      "Moves the lens in small steps and measures contrast at each position; stops when contrast peaks. Accurate but slow — must overshoot and return to find the maximum. Best for static subjects and video. Used as fallback in Fuji X-series when PDAF is unavailable.",
    ],
  },
  {
    slug: "colour-harmony",
    title: "Colour harmony",
    category: "Composition",
    summary: "Intentional use of colour relationships to create mood: complementary colours (opposite on the colour wheel, e.",
    body: [
      "Intentional use of colour relationships to create mood: complementary colours (opposite on the colour wheel, e.g. orange/blue) create energy; analogous colours (adjacent, e.g. green/teal/blue) create calm and cohesion.",
    ],
  },
  {
    slug: "colour-temperature",
    title: "Colour temperature",
    category: "Lighting",
    summary: "The warmth or coolness of a light source, measured in Kelvin (K).",
    body: [
      "The warmth or coolness of a light source, measured in Kelvin (K). Candle ~1800K, tungsten ~3200K, daylight ~5500K, open shade ~7000K. Affects white balance — cooler light appears blue, warmer light appears orange.",
    ],
  },
  {
    slug: "coma",
    title: "Coma",
    category: "Optics",
    summary: "An optical aberration that stretches point light sources into comet-like shapes near frame edges.",
    body: [
      "Coma (short for comatic aberration) causes point light sources — especially stars — to appear as small comet or bird-wing shapes instead of sharp points. It is worst in the corners of the frame and at wide apertures.",
      "Coma is caused by off-axis light rays hitting the lens at an angle. Rays passing through different zones of the lens converge at slightly different points, smearing the image radially outward from center.",
      "For nightscape and astrophotography, coma is the most important optical flaw to evaluate. A lens with strong coma turns corner stars into distracting smears, ruining widefield Milky Way shots. Coma cannot be corrected in post-processing.",
      "Stopping down reduces coma significantly — most lenses improve dramatically by f/2.8. But nightscape shooters need wide apertures for light gathering, so a lens that controls coma wide open is far more valuable than one that only sharpens stopped down.",
      "In the Fuji.me! scoring system, coma is rated 0-2 based on corner star rendering at maximum aperture. A score of 2 means minimal coma even wide open — stars stay tight points across the frame. A score of 0 means heavy coma that makes the lens unsuitable for astrophotography without stopping down.",
    ],
    related: ["scoring-methodology","mtf-charts"],
  },
  {
    slug: "cri",
    title: "CRI",
    fullTitle: "Colour Rendering Index",
    category: "Lighting",
    summary: "A scale (0–100) measuring how accurately a light source renders colours compared to natural sunlight.",
    body: [
      "A scale (0–100) measuring how accurately a light source renders colours compared to natural sunlight. CRI 90+ is excellent for photography. Low CRI lights cause colours to appear muddy or shifted.",
    ],
  },
  {
    slug: "crop-factor",
    title: "Crop factor",
    fullTitle: "Crop Factor",
    category: "Geometry",
    summary: "Ratio of a sensor's diagonal to that of full-frame (36×24mm).",
    body: [
      "Ratio of a sensor's diagonal to that of full-frame (36×24mm). APS-C crop = 1.5×, GFX = 0.79×. Multiply FL by crop factor to get the full-frame equivalent.",
    ],
  },
  {
    slug: "deblurring",
    title: "Deblurring",
    fullTitle: "Deblurring",
    category: "Optics",
    summary: "Post-processing technique to recover sharpness from motion blur or defocus blur.",
    body: [
      "Post-processing technique to recover sharpness from motion blur or defocus blur. Modern AI deblurring (e.g. Lightroom AI Sharpening) can recover surprising detail but cannot exceed the sensor's Nyquist limit.",
    ],
  },
  {
    slug: "deconvolution",
    title: "Deconvolution",
    fullTitle: "Deconvolution",
    category: "Optics",
    summary: "Mathematical process to reverse the blurring effect of a known optical system (PSF).",
    body: [
      "Mathematical process to reverse the blurring effect of a known optical system (PSF). Used in microscopy and astrophotography to recover fine detail. Prone to amplifying noise.",
    ],
  },
  {
    slug: "depth",
    title: "Depth",
    fullTitle: "Depth and Layers",
    category: "Composition",
    summary: "Including a foreground, mid-ground, and background creates a sense of three-dimensional space in a flat image.",
    body: [
      "Including a foreground, mid-ground, and background creates a sense of three-dimensional space in a flat image. Wide-angle lenses exaggerate depth; objects in the foreground draw the eye in and provide scale.",
    ],
  },
  {
    slug: "dfd",
    title: "DFD",
    fullTitle: "Depth-From-Defocus  [Passive]",
    category: "Focus",
    summary: "Estimates defocus amount by comparing two images captured at different aperture diameters, using the known relationship between defocus blur size and depth.",
    body: [
      "Estimates defocus amount by comparing two images captured at different aperture diameters, using the known relationship between defocus blur size and depth. Developed by Panasonic. Faster than pure CDAF but not as predictive as PDAF. Not used in Fuji systems.",
    ],
  },
  {
    slug: "diffraction",
    title: "Diffraction",
    fullTitle: "Diffraction",
    category: "Optics",
    summary: "At small apertures (f/11+), light bends around the aperture blades, causing softness regardless of lens quality.",
    body: [
      "At small apertures (f/11+), light bends around the aperture blades, causing softness regardless of lens quality. The diffraction limit for APS-C is approximately f/11; for GFX, f/16.",
    ],
  },
  {
    slug: "diffraction-limit",
    title: "Diffraction Limit",
    category: "Optics",
    summary: "The aperture beyond which stopping down reduces sharpness instead of increasing it.",
    body: [
      "Diffraction is a physical property of light: when light passes through a small opening, it bends and spreads. In photography, as you stop down the aperture, the opening becomes small enough that diffraction begins to soften the image.",
      "Every lens has a diffraction-limited aperture beyond which further stopping down reduces overall sharpness even though depth of field increases. On Fujifilm X-Trans sensors (APS-C, ~23.5mm crop), diffraction becomes visible around f/8-f/11 depending on the sensor resolution.",
      "On the 26MP X-Trans IV/V sensors (X-T4, X-T5, X-H2S), diffraction softening is noticeable from about f/11. On the 40MP X-H2, it starts closer to f/8 because the smaller pixel pitch is more sensitive to diffraction spread.",
      "On GFX medium format (44x33mm sensor), the larger sensor and pixel pitch push the diffraction limit to around f/16-f/22, giving more room to stop down for depth of field.",
      "Practical takeaway: for maximum sharpness on APS-C Fuji cameras, stay between f/5.6 and f/8. Use f/11 only when you need the depth of field. Avoid f/16 and smaller unless depth of field is more important than pixel-level sharpness. For landscapes where you want front-to-back sharpness, focus stacking at f/5.6-f/8 gives better results than shooting at f/16.",
    ],
  },
  {
    slug: "diffraction-limited-system",
    title: "Diffraction-limited system",
    fullTitle: "Diffraction-Limited System",
    category: "Optics",
    summary: "An optical system where performance is limited by diffraction rather than aberrations or manufacturing imperfections.",
    body: [
      "An optical system where performance is limited by diffraction rather than aberrations or manufacturing imperfections. Represents the theoretical maximum sharpness for a given aperture.",
    ],
  },
  {
    slug: "diffuser",
    title: "Diffuser",
    category: "Lighting",
    summary: "Any material that scatters light to make it softer and more even.",
    body: [
      "Any material that scatters light to make it softer and more even. Can be a softbox panel, a translucent umbrella, a dome on a speedlight, or a large white sheet. The larger the diffuser relative to the subject, the softer the light.",
    ],
  },
  {
    slug: "dof",
    title: "DoF",
    fullTitle: "Depth of Field",
    category: "Geometry",
    summary: "The range of distances in a scene that appear acceptably sharp.",
    body: [
      "The range of distances in a scene that appear acceptably sharp. Controlled by aperture (wider = shallower DoF), focal length, and subject distance.",
    ],
  },
  {
    slug: "dynamic-dimensions",
    title: "Dynamic dimensions",
    fullTitle: "Dynamic Dimensions",
    category: "Composition",
    summary: "The use of strong leading lines, diagonals, and converging perspectives to create a sense of movement, depth or tension in a static image.",
    body: [
      "The use of strong leading lines, diagonals, and converging perspectives to create a sense of movement, depth or tension in a static image. Contrasts with static, symmetrical compositions.",
    ],
  },
  {
    slug: "ev",
    title: "EV",
    fullTitle: "Exposure Value",
    category: "Exposure",
    summary: "A single number representing a combination of shutter speed and aperture that produces the same exposure.",
    body: [
      "A single number representing a combination of shutter speed and aperture that produces the same exposure. EV 0 = 1s at f/1. Each stop doubles or halves the exposure. EV 15 = bright sun.",
    ],
  },
  {
    slug: "f-value",
    title: "f-Value",
    fullTitle: "f-Number (f-Stop)",
    category: "Exposure",
    summary: "The ratio of focal length to aperture diameter.",
    body: [
      "The ratio of focal length to aperture diameter. f/2.8 on a 50mm lens means the aperture is 50/2.8 = 17.9mm wide. Each full stop (f/2.8→f/4) halves the light.",
    ],
  },
  {
    slug: "fill-the-frame",
    title: "Fill the frame",
    category: "Composition",
    summary: "Getting close to the subject so it occupies most or all of the frame, eliminating distracting backgrounds.",
    body: [
      "Getting close to the subject so it occupies most or all of the frame, eliminating distracting backgrounds. Creates intimacy and impact. Particularly effective for portraits, textures, and details.",
    ],
  },
  {
    slug: "filter-types",
    title: "Filter Types",
    category: "Lenses",
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
  {
    slug: "fl",
    title: "FL",
    fullTitle: "Focal Length",
    category: "Geometry",
    summary: "Distance in mm from the optical centre of the lens to the focal point on the sensor.",
    body: [
      "Distance in mm from the optical centre of the lens to the focal point on the sensor. Determines magnification and angle of view. Shorter = wider, longer = more telephoto.",
    ],
  },
  {
    slug: "fl-ff",
    title: "FL FF",
    fullTitle: "Focal Length Full-Frame Equivalent",
    category: "Geometry",
    summary: "The focal length on a full-frame camera that produces the same angle of view.",
    body: [
      "The focal length on a full-frame camera that produces the same angle of view. For APS-C: FL FF = FL × 1.5. Useful for comparing lenses across sensor formats.",
    ],
  },
  {
    slug: "flash",
    title: "Flash",
    category: "Lighting",
    summary: "A brief, intense burst of artificial light used to illuminate a scene.",
    body: [
      "A brief, intense burst of artificial light used to illuminate a scene. Can be on-camera (hotshoe), off-camera (remote triggered), or built-in. Power is measured in watt-seconds (Ws) for studio units or guide number (GN) for speedlights.",
    ],
  },
  {
    slug: "focus-modes",
    title: "Focus Modes",
    category: "Focus",
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
  {
    slug: "foreground-interest",
    title: "Foreground interest",
    category: "Composition",
    summary: "Placing a visually interesting element in the immediate foreground to anchor the composition and create depth.",
    body: [
      "Placing a visually interesting element in the immediate foreground to anchor the composition and create depth. Particularly important in landscape photography where a strong foreground transforms an ordinary scene into a compelling image.",
    ],
  },
  {
    slug: "fov",
    title: "FoV",
    fullTitle: "Field of View",
    category: "Geometry",
    summary: "The physical area of a scene captured at a given distance.",
    body: [
      "The physical area of a scene captured at a given distance. Unlike AoV (angular), FoV is expressed in metres. FoV grows proportionally with distance.",
    ],
  },
  {
    slug: "framing",
    title: "Framing",
    category: "Composition",
    summary: "Using elements within the scene (doorways, arches, foliage, windows) to form a natural frame around the subject.",
    body: [
      "Using elements within the scene (doorways, arches, foliage, windows) to form a natural frame around the subject. Draws attention to the subject, adds depth, and provides context about the environment.",
    ],
  },
  {
    slug: "fresnel-lens",
    title: "Fresnel Lens",
    category: "Lighting",
    summary: "A stepped focusing lens placed in front of a light source to concentrate and shape the beam.",
    body: [
      "A stepped focusing lens placed in front of a light source to concentrate and shape the beam. Used on studio heads and LED panels to produce a hard, directional, focusable light — adjustable from flood to spot.",
    ],
  },
  {
    slug: "full-frame",
    title: "Full-frame",
    fullTitle: "Full-Frame",
    category: "Sensor",
    summary: "Sensor size matching 35mm film: 36×24mm, crop factor 1.",
    body: [
      "Sensor size matching 35mm film: 36×24mm, crop factor 1.0×. Larger photosites capture more light, yielding better dynamic range and high-ISO performance than smaller formats.",
    ],
  },
  {
    slug: "g-mount",
    title: "G-Mount",
    category: "Lenses",
    summary: "Fujifilm's lens mount for the GFX medium format system.",
    body: [
      "Fujifilm's lens mount for the GFX medium format system. Larger than X-Mount to accommodate the bigger sensor. GF lenses are not compatible with X-Mount bodies. The mount supports tilt-shift lenses and features a wide flange distance for optical quality.",
    ],
  },
  {
    slug: "gamma-correction",
    title: "Gamma correction",
    fullTitle: "Gamma Correction",
    category: "Optics",
    summary: "A nonlinear tone mapping applied to image data to match human perception of brightness.",
    body: [
      "A nonlinear tone mapping applied to image data to match human perception of brightness. Camera sensors capture linear light; gamma encoding (e.g. sRGB γ=2.2) compresses highlights and expands shadows.",
    ],
  },
  {
    slug: "gfx-medium-format",
    title: "GFX / Medium Format",
    fullTitle: "GFX / Medium Format",
    category: "Sensor",
    summary: "Fujifilm's medium format system uses a 43.",
    body: [
      "Fujifilm's medium format system uses a 43.8×32.9mm sensor, crop factor 0.79×. Larger than full-frame, producing extremely high resolution (up to 102MP) and exceptional tonal gradation.",
    ],
  },
  {
    slug: "golden-ratio",
    title: "Golden ratio",
    fullTitle: "Golden Ratio",
    category: "Composition",
    summary: "Mathematical ratio ≈1.",
    body: [
      "Mathematical ratio ≈1.618:1 (φ, phi) found throughout nature and classical art. Used as a compositional guide: placing subjects at golden ratio intersections or along spiral curves creates naturally pleasing images.",
    ],
  },
  {
    slug: "golden-rectangle",
    title: "Golden rectangle",
    fullTitle: "Golden Rectangle",
    category: "Composition",
    summary: "A rectangle whose sides are in the golden ratio (1:1.",
    body: [
      "A rectangle whose sides are in the golden ratio (1:1.618). Subdividing it repeatedly produces a logarithmic spiral used in the Fibonacci/golden spiral compositional guide.",
    ],
  },
  {
    slug: "guide-number",
    title: "Guide number",
    category: "Lighting",
    summary: "A standardised measure of flash power: GN = distance × f-number (at ISO 100).",
    body: [
      "A standardised measure of flash power: GN = distance × f-number (at ISO 100). A GN of 60 means at 6m you need f/10, or at 3m you need f/20. Higher GN = more powerful flash.",
    ],
  },
  {
    slug: "handheld",
    title: "Handheld",
    fullTitle: "Handheld Shooting",
    category: "Exposure",
    summary: "Shooting without a tripod or other support.",
    body: [
      "Shooting without a tripod or other support. Subject to camera shake, which sets a minimum shutter speed determined by focal length, stabilisation, and sensor resolution. The reciprocal rule (1/FL) is the standard guideline.",
    ],
  },
  {
    slug: "honeycomb-grid",
    title: "Honeycomb Grid",
    category: "Lighting",
    summary: "A honeycomb-shaped attachment that fits over a modifier to control light spill and keep illumination directional.",
    body: [
      "A honeycomb-shaped attachment that fits over a modifier to control light spill and keep illumination directional. Measured in degrees (10°, 20°, 40°) — tighter grids produce more controlled beams.",
    ],
  },
  {
    slug: "hss",
    title: "HSS",
    fullTitle: "High Speed Sync",
    category: "Lighting",
    summary: "Allows flash to be used at shutter speeds above the camera sync speed (typically 1/250s).",
    body: [
      "Allows flash to be used at shutter speeds above the camera sync speed (typically 1/250s). The flash fires multiple rapid pulses throughout the exposure. Trades power for speed — useful for outdoor portraits at wide aperture in bright light.",
    ],
  },
  {
    slug: "hybrid-af",
    title: "Hybrid AF",
    fullTitle: "Hybrid AF  [Passive]",
    category: "Focus",
    summary: "Combines PDAF (for speed and direction) with CDAF (for final accuracy).",
    body: [
      "Combines PDAF (for speed and direction) with CDAF (for final accuracy). The camera uses PDAF to get close, then switches to CDAF for precise confirmation. Used in virtually all modern Fuji X-series bodies.",
    ],
  },
  {
    slug: "ibis",
    title: "IBIS",
    fullTitle: "In-Body Image Stabilisation",
    category: "Sensor",
    summary: "Sensor-shift stabilisation built into the camera body.",
    body: [
      "Sensor-shift stabilisation built into the camera body. Works with any lens, including manual and adapted lenses without optical stabilisation. Fuji X-H2, X-H2S, X-T4, and X-T5 feature IBIS. Combined OIS+IBIS can provide up to 7 stops of compensation.",
    ],
  },
  {
    slug: "image-resolution",
    title: "Image resolution",
    fullTitle: "Image Resolution",
    category: "Optics",
    summary: "The number of pixels in a captured image, typically expressed as megapixels (MP) or as width × height (e.",
    body: [
      "The number of pixels in a captured image, typically expressed as megapixels (MP) or as width × height (e.g. 7728×5152). Higher resolution enables larger prints and more crop flexibility.",
    ],
  },
  {
    slug: "integrating-sphere",
    title: "Integrating sphere",
    fullTitle: "Integrating Sphere",
    category: "Optics",
    summary: "A hollow sphere with diffuse white interior coating used to measure total luminous flux from a light source.",
    body: [
      "A hollow sphere with diffuse white interior coating used to measure total luminous flux from a light source. Used in lens and sensor calibration laboratories.",
    ],
  },
  {
    slug: "ir-af",
    title: "IR AF",
    fullTitle: "IR Beam AF  [Active]",
    category: "Focus",
    summary: "Emits an infrared beam and measures the angle or time-of-flight of the reflection to determine distance.",
    body: [
      "Emits an infrared beam and measures the angle or time-of-flight of the reflection to determine distance. Used as AF-assist illuminators in some cameras and dedicated video follow-focus systems. Limited range (~5m).",
    ],
  },
  {
    slug: "iso",
    title: "ISO",
    fullTitle: "ISO Sensitivity",
    category: "Exposure",
    summary: "The sensor's amplification of the captured light signal.",
    body: [
      "The sensor's amplification of the captured light signal. Higher ISO = brighter image in low light but more noise. Base ISO (typically 100–200) gives cleanest results.",
    ],
  },
  {
    slug: "leading-lines",
    title: "Leading lines",
    category: "Composition",
    summary: "Lines within the scene (roads, rivers, fences, shadows) that draw the viewer's eye towards the main subject or deeper into the frame.",
    body: [
      "Lines within the scene (roads, rivers, fences, shadows) that draw the viewer's eye towards the main subject or deeper into the frame. Most effective when they originate from a corner and converge toward the subject.",
    ],
  },
  {
    slug: "led-panel",
    title: "LED panel",
    fullTitle: "LED Continuous Light",
    category: "Lighting",
    summary: "A continuous (always-on) light source using LEDs.",
    body: [
      "A continuous (always-on) light source using LEDs. Unlike flash, it allows real-time preview of lighting. Useful for video. Modern bi-colour LED panels adjust from tungsten (3200K) to daylight (5600K).",
    ],
  },
  {
    slug: "lens-coating",
    title: "Lens Coating",
    category: "Optics",
    summary: "Multi-layer anti-reflective coatings applied to lens elements to reduce flare, ghosting, and light loss.",
    body: [
      "Multi-layer anti-reflective coatings applied to lens elements to reduce flare, ghosting, and light loss. High-quality coatings (e.g. Fuji EBC, Zeiss T*) significantly improve contrast in backlit situations.",
    ],
  },
  {
    slug: "lidar-af",
    title: "LiDAR AF",
    fullTitle: "LiDAR AF  [Active]",
    category: "Focus",
    summary: "Emits pulsed laser light and measures the time-of-flight of the reflection with high precision.",
    body: [
      "Emits pulsed laser light and measures the time-of-flight of the reflection with high precision. Used in iPhone Pro (camera app depth assist) and some cinema accessories. Not used in Fuji stills cameras.",
    ],
  },
  {
    slug: "lighting-umbrella",
    title: "Lighting Umbrella",
    category: "Lighting",
    summary: "A modifier used with flash or studio lights.",
    body: [
      "A modifier used with flash or studio lights. Shoot-through umbrellas diffuse light for a soft source; reflective umbrellas redirect light for a larger, directional source. Portable and inexpensive.",
    ],
  },
  {
    slug: "lm",
    title: "LM",
    fullTitle: "Linear Motor (actuator)",
    category: "Focus",
    summary: "A lens AF actuator using a linear electromagnetic motor rather than a traditional rotating motor.",
    body: [
      "A lens AF actuator using a linear electromagnetic motor rather than a traditional rotating motor. Provides faster, quieter, and more accurate focus tracking. Not an AF detection method — pairs with any of the above. Critical for sport and wildlife photography.",
    ],
  },
  {
    slug: "macro",
    title: "Macro",
    fullTitle: "Macro Photography",
    category: "Lenses",
    summary: "Close-up photography at reproduction ratios of 1:1 (life-size) or greater.",
    body: [
      "Close-up photography at reproduction ratios of 1:1 (life-size) or greater. A true macro lens focuses close enough to project a 1:1 image on the sensor — a 10mm insect fills 10mm of the sensor. Fuji XF 80mm f/2.8 and XF 30mm f/2.8 are native macro lenses.",
    ],
  },
  {
    slug: "metering",
    title: "Metering",
    fullTitle: "Metering",
    category: "Exposure",
    summary: "The camera's system for measuring scene brightness to determine exposure.",
    body: [
      "The camera's system for measuring scene brightness to determine exposure. Modes include evaluative/matrix (whole scene), spot (small area), and centre-weighted.",
    ],
  },
  {
    slug: "moir-pattern",
    title: "Moiré pattern",
    fullTitle: "Moiré Pattern",
    category: "Optics",
    summary: "An interference pattern that appears when two regular patterns (e.",
    body: [
      "An interference pattern that appears when two regular patterns (e.g. fine fabric texture and sensor grid) overlap at similar frequencies. Reduced by anti-aliasing filters.",
    ],
  },
  {
    slug: "mrc",
    title: "MRC",
    fullTitle: "Minimum Resolvable Contrast",
    category: "Optics",
    summary: "The lowest contrast level that a lens or imaging system can still resolve as distinct detail.",
    body: [
      "The lowest contrast level that a lens or imaging system can still resolve as distinct detail. Related to MTF at high spatial frequencies.",
    ],
  },
  {
    slug: "mtf",
    title: "MTF",
    fullTitle: "Modulation Transfer Function",
    category: "Optics",
    summary: "A measure of a lens's ability to reproduce fine detail and contrast.",
    body: [
      "A measure of a lens's ability to reproduce fine detail and contrast. Plotted as a curve: higher values across spatial frequencies = sharper, higher contrast image. The gold standard for lens testing.",
    ],
  },
  {
    slug: "mtf-charts",
    title: "MTF Charts",
    category: "Optics",
    summary: "How to read MTF (Modulation Transfer Function) charts to evaluate lens sharpness.",
    body: [
      "MTF (Modulation Transfer Function) measures how well a lens reproduces contrast at different levels of detail. An MTF chart plots contrast (vertical axis, 0-1) against distance from the image center to the edge (horizontal axis). Higher values mean sharper images.",
      "MTF charts typically show two line types: sagittal (parallel to a line from center to corner) and meridional (perpendicular to that line). When both lines are close together, the lens has low astigmatism. When they diverge, point light sources become elongated in one direction.",
      "Charts are usually measured at two spatial frequencies: 10 lp/mm (line pairs per millimeter) for contrast, and 30 lp/mm (or 40 lp/mm on higher resolution tests) for fine detail resolution. The 10 lp/mm lines tell you about overall contrast and \"pop\"; the 30 lp/mm lines tell you about resolving power and fine texture.",
      "A great lens shows both lines above 0.8 across the frame at 10 lp/mm, and above 0.6 at 30 lp/mm. A lens that starts high in the center but drops sharply toward the edges has good center sharpness but weak corners — common in fast primes wide open.",
      "MTF charts have limitations: they are measured at a single aperture (usually wide open and f/8), do not capture chromatic aberration, coma, or flare, and lab conditions do not match real-world shooting. Use them as one input alongside field reports, sample images, and optical scores.",
      "In Fuji.me!, the center/corner stopped and wide-open scores are derived from MTF data and lab tests. They are simplified to a 0-2 scale for quick comparison across the entire lens lineup.",
    ],
    related: ["scoring-methodology","coma"],
  },
  {
    slug: "nd",
    title: "ND",
    fullTitle: "Neutral Density Filter",
    category: "Exposure",
    summary: "A filter that reduces light entering the lens without affecting colour balance.",
    body: [
      "A filter that reduces light entering the lens without affecting colour balance. Allows slower shutter speeds (silk water, light trails) or wider apertures (shallower DoF) in bright conditions. Expressed in stops (ND2=1 stop, ND8=3 stops, ND64=6 stops, ND1000=10 stops).",
    ],
  },
  {
    slug: "negative-space",
    title: "Negative space",
    fullTitle: "Negative Space",
    category: "Composition",
    summary: "The empty or unoccupied area surrounding the main subject.",
    body: [
      "The empty or unoccupied area surrounding the main subject. Effective use of negative space creates breathing room, emphasises the subject, and conveys mood. Often seen in minimalist photography.",
    ],
  },
  {
    slug: "ois",
    title: "OIS",
    fullTitle: "Optical Image Stabilisation",
    category: "Lenses",
    summary: "In-lens mechanism that shifts optical elements to compensate for camera shake.",
    body: [
      "In-lens mechanism that shifts optical elements to compensate for camera shake. Measured in EV stops of compensation. Particularly valuable at long focal lengths and slow shutter speeds. Fuji XF lenses mark OIS-equipped models explicitly.",
    ],
  },
  {
    slug: "optical-resolution",
    title: "Optical resolution",
    fullTitle: "Optical Resolution",
    category: "Optics",
    summary: "The true resolving power of a lens, independent of sensor resolution.",
    body: [
      "The true resolving power of a lens, independent of sensor resolution. Expressed as line pairs per millimetre (lp/mm). A lens must exceed the sensor's Nyquist frequency to avoid resolution bottleneck.",
    ],
  },
  {
    slug: "oversampling",
    title: "Oversampling",
    fullTitle: "Oversampling",
    category: "Optics",
    summary: "Capturing at higher resolution than needed and downsampling.",
    body: [
      "Capturing at higher resolution than needed and downsampling. Improves effective sharpness and reduces noise. Used in video modes (e.g. Fuji X-T5 shoots 40MP to produce oversampled 8K video).",
    ],
  },
  {
    slug: "panning",
    title: "Panning",
    fullTitle: "Panning",
    category: "Exposure",
    summary: "Technique of tracking a moving subject with the camera during a relatively slow exposure.",
    body: [
      "Technique of tracking a moving subject with the camera during a relatively slow exposure. The subject appears sharp while the background streaks horizontally. Requires a shutter speed slow enough to create motion blur in the background, typically 1/30–1/125s depending on subject speed.",
    ],
  },
  {
    slug: "passive-af",
    title: "Passive AF",
    fullTitle: "Passive Autofocus",
    category: "Focus",
    summary: "AF category that analyses the incoming image itself to determine focus — no light is emitted by the camera.",
    body: [
      "AF category that analyses the incoming image itself to determine focus — no light is emitted by the camera. All methods below (CDAF, PDAF, Hybrid, DFD) are passive. Works in any lighting where there is enough contrast or phase information in the scene.",
    ],
  },
  {
    slug: "patterns-and-texture",
    title: "Patterns and texture",
    category: "Composition",
    summary: "Repeating shapes, lines, or textures create rhythm and visual interest.",
    body: [
      "Repeating shapes, lines, or textures create rhythm and visual interest. Breaking a pattern with a single different element (pattern interrupt) immediately draws the eye. Textures are best revealed by side-lighting.",
    ],
  },
  {
    slug: "pdaf",
    title: "PDAF",
    fullTitle: "Phase Detection AF  [Passive]",
    category: "Focus",
    summary: "Dedicated pixel pairs on the sensor receive light from slightly different angles; the phase difference between them reveals the direction and magnitude of defocus.",
    body: [
      "Dedicated pixel pairs on the sensor receive light from slightly different angles; the phase difference between them reveals the direction and magnitude of defocus. Fast, predictive, and does not need to hunt. Used in Fuji X-series within PDAF coverage zones. Performance degrades above f/8.",
    ],
  },
  {
    slug: "point-of-view",
    title: "Point of view",
    category: "Composition",
    summary: "The physical relationship between photographer, subject, and background.",
    body: [
      "The physical relationship between photographer, subject, and background. Shooting at eye-level with children or animals creates connection; shooting from above creates distance. Changing point of view is the single most impactful compositional decision.",
    ],
  },
  {
    slug: "reciprocal-rule",
    title: "Reciprocal Rule",
    category: "Exposure",
    summary: "The minimum handheld shutter speed to avoid camera-shake blur equals 1 divided by the focal length.",
    body: [
      "The minimum handheld shutter speed to avoid camera-shake blur equals 1 divided by the focal length. For a 50mm lens on APS-C: minimum shutter = 1/(50×1.5) = 1/75s. High-resolution sensors require a stricter version: 1/(√(MP/12) × crop × FL).",
    ],
  },
  {
    slug: "reflector",
    title: "Reflector",
    fullTitle: "Reflector",
    category: "Lighting",
    summary: "A surface used to redirect ambient or artificial light onto a subject.",
    body: [
      "A surface used to redirect ambient or artificial light onto a subject. White = soft fill, silver = brighter harder fill, gold = warm fill. Used to reduce contrast in portrait and product photography.",
    ],
  },
  {
    slug: "rule-of-500",
    title: "Rule of 500",
    fullTitle: "Rule of 500 (Astrophotography)",
    category: "Exposure",
    summary: "Maximum untracked exposure time before stars trail: 500 ÷ (crop factor × focal length).",
    body: [
      "Maximum untracked exposure time before stars trail: 500 ÷ (crop factor × focal length). For a 16mm lens on APS-C (crop 1.5): 500 ÷ (1.5 × 16) = 20 seconds. A stricter version using 300 is preferred for high-resolution sensors.",
    ],
  },
  {
    slug: "rule-of-odds",
    title: "Rule of odds",
    category: "Composition",
    summary: "Groups of odd numbers of subjects (3, 5, 7) are more visually pleasing than even groups.",
    body: [
      "Groups of odd numbers of subjects (3, 5, 7) are more visually pleasing than even groups. An odd number creates a natural focal point — one subject stands out. Particularly useful in product and food photography.",
    ],
  },
  {
    slug: "rule-of-thirds",
    title: "Rule of thirds",
    category: "Composition",
    summary: "Divide the frame into a 3×3 grid; place key subjects or horizon lines along the grid lines or at their intersections (power points).",
    body: [
      "Divide the frame into a 3×3 grid; place key subjects or horizon lines along the grid lines or at their intersections (power points). Creates more dynamic, balanced compositions than centring the subject. The most fundamental compositional guideline in photography.",
    ],
  },
  {
    slug: "s-curve",
    title: "S-curve",
    fullTitle: "S-Curve",
    category: "Composition",
    summary: "A flowing S-shaped curve (rivers, roads, staircases) that leads the eye gracefully through the frame.",
    body: [
      "A flowing S-shaped curve (rivers, roads, staircases) that leads the eye gracefully through the frame. More dynamic than a straight leading line; conveys elegance and movement. Common in landscape and portrait photography.",
    ],
  },
  {
    slug: "scoring-methodology",
    title: "Scoring Methodology",
    category: "Optics",
    summary: "How Fuji.me! scores lenses for each photography genre using optical data and weighted formulas.",
    body: [
      "Fuji.me! scores lenses on a 0-100 scale for each photography genre. Scores are calculated from optical performance data, not marketing specs or subjective reviews. The goal is to answer: \"How well does this lens perform for this specific genre?\"",
      "Each genre uses a weighted formula that emphasizes the optical qualities most important for that type of photography. For example, nightscape scoring heavily weights coma and wide-open corner sharpness, while portrait scoring emphasizes bokeh and center sharpness wide open.",
      "Optical data comes from lab tests and detailed field reports by trusted review sources (LensTip, Optical Limits, DPReview). Each optical field (center sharpness, corner sharpness, coma, astigmatism, chromatic aberration, distortion, vignetting, bokeh, flare resistance) is rated on a 0-2 scale where 0 is poor, 1 is average, and 2 is excellent.",
      "Lenses without sufficient optical data are shown as \"Not yet scored\" rather than estimated. We only score lenses when we have data from trusted sources. This means some newer or niche lenses may lack scores until reviews are published.",
      "Genre scores are supplemented by editorial picks — lenses that the formula alone might not surface but that are widely recognized as exceptional for a given genre based on field experience and photographer consensus.",
      "Scoring is opinionated and transparent. The weights and formulas are visible in the codebase. We acknowledge that no formula perfectly captures real-world performance, and encourage photographers to use scores as a starting point, not a final verdict.",
    ],
    related: ["mtf-charts","coma"],
  },
  {
    slug: "siemens-star",
    title: "Siemens star",
    fullTitle: "Siemens Star",
    category: "Optics",
    summary: "A test chart consisting of alternating black and white wedges radiating from a centre point.",
    body: [
      "A test chart consisting of alternating black and white wedges radiating from a centre point. Used to measure resolving power and detect astigmatism or other aberrations at different field positions.",
    ],
  },
  {
    slug: "simplicity",
    title: "Simplicity",
    category: "Composition",
    summary: "Reducing the scene to its essential elements by choosing a clean background, isolating the subject, or finding an uncluttered angle.",
    body: [
      "Reducing the scene to its essential elements by choosing a clean background, isolating the subject, or finding an uncluttered angle. Minimalist compositions are often the most powerful. 'If in doubt, take it out.'",
    ],
  },
  {
    slug: "sitf",
    title: "SiTF",
    fullTitle: "Signal Transfer Function",
    category: "Optics",
    summary: "Describes how a sensor or imaging system converts scene radiance to output signal.",
    body: [
      "Describes how a sensor or imaging system converts scene radiance to output signal. Used in scientific imaging to characterise linearity and dynamic range.",
    ],
  },
  {
    slug: "snoot",
    title: "Snoot",
    category: "Lighting",
    summary: "A cone or tube attached to a flash or studio head to narrow the light beam to a small spot.",
    body: [
      "A cone or tube attached to a flash or studio head to narrow the light beam to a small spot. Used to isolate subjects, light hair, or create dramatic accent lighting without spill.",
    ],
  },
  {
    slug: "snr",
    title: "SNR",
    fullTitle: "Signal-to-Noise Ratio",
    category: "Optics",
    summary: "Ratio of the useful image signal to background noise.",
    body: [
      "Ratio of the useful image signal to background noise. Higher SNR = cleaner image. Decreases at high ISO. Larger sensor pixels generally produce better SNR.",
    ],
  },
  {
    slug: "softbox",
    title: "Softbox",
    category: "Lighting",
    summary: "A box-shaped modifier that diffuses light through a translucent panel, producing soft, even illumination with gentle shadow transitions.",
    body: [
      "A box-shaped modifier that diffuses light through a translucent panel, producing soft, even illumination with gentle shadow transitions. Size determines softness — larger = softer. Common shapes: rectangular, octabox, strip.",
    ],
  },
  {
    slug: "speedlight",
    title: "Speedlight",
    category: "Lighting",
    summary: "A portable battery-powered flash unit that mounts on the camera hotshoe or is used off-camera.",
    body: [
      "A portable battery-powered flash unit that mounts on the camera hotshoe or is used off-camera. Less powerful than studio strobes but highly portable. Supports TTL and HSS on compatible cameras.",
    ],
  },
  {
    slug: "strehl-ratio",
    title: "Strehl ratio",
    fullTitle: "Strehl Ratio",
    category: "Optics",
    summary: "A measure of optical quality comparing peak intensity of an aberrated system to a perfect diffraction-limited system.",
    body: [
      "A measure of optical quality comparing peak intensity of an aberrated system to a perfect diffraction-limited system. Value of 1.0 = perfect. Values above 0.8 are considered diffraction-limited.",
    ],
  },
  {
    slug: "studio-strobe",
    title: "Studio Strobe",
    category: "Lighting",
    summary: "A powerful mains-powered flash unit used in studio settings.",
    body: [
      "A powerful mains-powered flash unit used in studio settings. Significantly more powerful than speedlights (100–1000+ Ws). Usually includes a modelling lamp to preview light direction before shooting.",
    ],
  },
  {
    slug: "sunstars",
    title: "Sunstars",
    category: "Optics",
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
  {
    slug: "super-resolution-imaging",
    title: "Super-resolution imaging",
    fullTitle: "Super-Resolution Imaging",
    category: "Optics",
    summary: "Techniques to produce images with resolution beyond the sensor's native limit.",
    body: [
      "Techniques to produce images with resolution beyond the sensor's native limit. In-camera pixel shift (e.g. Fuji Pixel Shift Multi-Shot) combines multiple exposures; AI upscaling uses neural networks.",
    ],
  },
  {
    slug: "superlens",
    title: "Superlens",
    fullTitle: "Superlens",
    category: "Optics",
    summary: "A theoretical or experimental optical device using metamaterials with negative refractive index to overcome the diffraction limit.",
    body: [
      "A theoretical or experimental optical device using metamaterials with negative refractive index to overcome the diffraction limit. Not yet practical for photography.",
    ],
  },
  {
    slug: "symmetry",
    title: "Symmetry",
    category: "Composition",
    summary: "Placing the subject centrally to exploit mirror-like reflections or architectural symmetry.",
    body: [
      "Placing the subject centrally to exploit mirror-like reflections or architectural symmetry. Breaks the rule of thirds intentionally to create a sense of balance, calm, and formality. Most effective with strong reflections or geometric patterns.",
    ],
  },
  {
    slug: "tc",
    title: "TC",
    fullTitle: "Tele Converter",
    category: "Lenses",
    summary: "An optical accessory placed between camera body and lens to multiply focal length.",
    body: [
      "An optical accessory placed between camera body and lens to multiply focal length. Fujifilm XF 1.4× TC WR and XF 2.0× TC WR are compatible with select XF lenses. The 1.4× costs 1 stop of light; the 2.0× costs 2 stops. AF performance is maintained on compatible lenses.",
    ],
  },
  {
    slug: "tilt-shift",
    title: "Tilt-Shift",
    category: "Lenses",
    summary: "A lens with mechanical movements allowing the optical axis to be tilted (controls plane of focus) or shifted (corrects perspective distortion).",
    body: [
      "A lens with mechanical movements allowing the optical axis to be tilted (controls plane of focus) or shifted (corrects perspective distortion). Used in architecture to keep vertical lines parallel. Fujifilm offers GF 30mm f/5.6 T/S and GF 110mm f/5.6 T/S Macro.",
    ],
  },
  {
    slug: "ttl",
    title: "TTL",
    fullTitle: "Through The Lens metering",
    category: "Lighting",
    summary: "Automatic flash exposure system where the camera meters light through the lens and adjusts flash power accordingly.",
    body: [
      "Automatic flash exposure system where the camera meters light through the lens and adjusts flash power accordingly. Fires a pre-flash to measure the scene, then sets the main flash power. Convenient but can be fooled by reflective or dark subjects.",
    ],
  },
  {
    slug: "ulbricht-sphere",
    title: "Ulbricht sphere",
    fullTitle: "Ulbricht Sphere",
    category: "Optics",
    summary: "Another name for an integrating sphere, named after German physicist Ulbricht.",
    body: [
      "Another name for an integrating sphere, named after German physicist Ulbricht. Used to achieve spatially uniform illumination for radiometric measurements.",
    ],
  },
  {
    slug: "viewpoint",
    title: "Viewpoint",
    category: "Composition",
    summary: "The position and angle from which a photo is taken dramatically changes its meaning.",
    body: [
      "The position and angle from which a photo is taken dramatically changes its meaning. Low angles make subjects imposing; high angles create vulnerability or show patterns. Moving just a metre can transform a cluttered scene into a clean composition.",
    ],
  },
  {
    slug: "wr",
    title: "WR",
    fullTitle: "Weather Resistance",
    category: "Lenses",
    summary: "Sealing at lens barrel joints and focus ring to resist dust and moisture ingress.",
    body: [
      "Sealing at lens barrel joints and focus ring to resist dust and moisture ingress. WR lenses require a WR camera body for full protection. Essential for outdoor sport, wildlife, and landscape work in variable conditions.",
    ],
  },
  {
    slug: "x-mount",
    title: "X-Mount",
    category: "Lenses",
    summary: "Fujifilm's mirrorless interchangeable lens mount for the X-series APS-C system.",
    body: [
      "Fujifilm's mirrorless interchangeable lens mount for the X-series APS-C system. Short 17.7mm flange distance allows compact lens designs. Compatible with XF and XC lenses. Not compatible with GFX / G-Mount lenses.",
    ],
  },
  {
    slug: "xc",
    title: "XC",
    fullTitle: "XC Lens Series",
    category: "Lenses",
    summary: "Fujifilm's budget X-Mount lens series.",
    body: [
      "Fujifilm's budget X-Mount lens series. Plastic mount, no weather resistance, lighter and more compact than XF equivalents. Designed for entry-level X-series bodies. The XC 15-45mm, 16-50mm, 35mm f/2, and 50-230mm are the main examples.",
    ],
  },
  {
    slug: "xf",
    title: "XF",
    fullTitle: "XF Lens Series",
    category: "Lenses",
    summary: "Fujifilm's main X-Mount lens lineup.",
    body: [
      "Fujifilm's main X-Mount lens lineup. Covers professional primes and zooms with consistent quality, weather-resistant options, and linear motor variants. Designed for the full X-series camera range.",
    ],
  },
];

export { wiki };
