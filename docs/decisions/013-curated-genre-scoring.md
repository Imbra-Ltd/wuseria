# ADR-013: Genre scoring — per-genre optical suitability from lens measurements

**Status:** Accepted (supersedes ADR-007)
**Date:** 2026-04-11

## Context

ADR-007 proposed pure scoring functions (`Lens -> ScoreResult`) but left the
formula design vague. The prototype used a single hand-assigned `mtf` number
(0–10) as a stand-in while the optical data pipeline was built. With the lens
catalog now carrying 12 individual optical quality fields (0–2 scale each),
the scoring system can be defined properly.

## Decision

Each genre defines a **suitability formula** that combines optical quality
fields with physical lens properties. The formula produces a **mark**
(1–5 in 0.5 steps) that represents how suited the lens is for that
genre's photographic intent.

The formula draws from two sources on the `Lens` type:

1. **Optical quality fields** (0–2 scale, from review sources per ADR-014)
2. **Physical properties** (mapped to 0–2 scale per genre):
   - `maxAperture` → light gathering score (used by street, travel)
   - `weight` → portability score (used by travel)

Physical properties are included only where they directly enable or
prevent the photographic work — aperture determines whether handheld
night capture is possible, weight determines whether the lens is
carried at all.

OIS, autofocus speed, weather sealing, and build quality are NOT
scoring inputs — they are features, not physical or optical properties.

### Optical quality fields available on `Lens`

From MTF charts (0–2 scale):

| Field | What it measures |
|-------|-----------------|
| `centerStopped` | Center resolution at optimal aperture |
| `cornerStopped` | Corner resolution at optimal aperture |
| `centerWideOpen` | Center resolution at maximum aperture |
| `cornerWideOpen` | Corner resolution at maximum aperture |
| `astigmatism` | Point-source elongation across the field |

From lab tests and field reports (0–2 scale):

| Field | What it measures |
|-------|-----------------|
| `coma` | Off-axis point-source distortion |
| `longitudinalCA` | Axial colour fringing |
| `lateralCA` | Transverse colour fringing |
| `distortion` | Barrel/pincushion geometric distortion |
| `vignettingWideOpen` | Corner light loss at max aperture |
| `vignettingStopped` | Corner light loss at f/5.6-f/8 |
| `bokeh` | Out-of-focus rendering quality |
| `flareResistance` | Resistance to flare and ghosting |

Additional scoring inputs: `maxAperture` (light gathering), `minFocusDistance`,
`isTiltShift`, `shiftRange`, `tiltAngle`, `imageCircle`.

### Genre suitability — what each formula prioritises

Each genre formula uses **primary floor + weighted average**:
- Primary fields (w=3) determine the tier — mark cannot exceed floor
  (min of all primary values)
- Secondary fields (w=1) determine rank within tier
- Floor = min(all primary fields), capped = min(raw, floor)
- Mark mapping: capped × 2 + 1, rounded to nearest 0.5, clamped 1–5
- Primary fields must all be present; 50% of all optical fields required

| Genre | Primary (w=3) | Secondary (w=1) |
|-------|--------------|-----------------|
| **Astro** | coma, astigmatism, apertureScore | lateralCA, centerWideOpen, cornerWideOpen, longitudinalCA, vignettingWideOpen, sphericalAberration |
| **Landscape** | cornerStopped, centerStopped | distortion, lateralCA, longitudinalCA, vignettingStopped, flareResistance, astigmatism, coma |
| **Architecture** | cornerStopped, centerStopped, distortion | lateralCA, vignettingStopped, flareResistance |
| **Portrait** | bokeh, centerWideOpen | longitudinalCA, sphericalAberration, vignettingWideOpen |
| **Street** | centerStopped, apertureScore | centerWideOpen, flareResistance, longitudinalCA, coma |
| **Travel** | centerStopped, weightScore | apertureScore, flareResistance, longitudinalCA |
| **Sport** | centerWideOpen | apertureScore, longitudinalCA, lateralCA |
| **Wildlife** | centerWideOpen, centerStopped | apertureScore, longitudinalCA, lateralCA |
| **Macro** | centerStopped, magnificationScore | distortion, lateralCA, longitudinalCA, sphericalAberration, bokeh |

**Physical property scores** (computed from lens specs, not reviews):
- `apertureScore`: f/1.4+=2.0, f/2=1.5, f/2.8=1.0, f/4=0.5, f/4.5+=0.0
- `weightScore`: <200g=2.0, ≤400g=1.5, ≤700g=1.0, ≤1000g=0.5, >1000g=0.0
- `magnificationScore`: ≥1.0x=2.0, ≥0.5x=1.5, ≥0.25x=1.0, ≥0.15x=0.5, <0.15x=0.0

**Focal length is never a scoring input.** It is a creative choice. The genre
guide shows recommended FL ranges as filter presets, but FL does not affect
the mark.

**OIS, weather resistance, and autofocus are not scoring inputs.**
These are display attributes shown alongside marks in the genre guide.
Weight and aperture ARE scoring inputs for genres where they directly
enable or prevent the photographic work (see ADR-014 for thresholds).

### Data coverage rule

A lens is **only scored if it has sufficient optical data** from trusted review
sources (Lenstip, Opticallimits, Dustin Abbott, LensRentals, etc.). If the
required optical fields for a genre's formula are missing, the lens is excluded
from that genre entirely.

This means:
- ~80–100 lenses from established brands (Fujifilm, Sigma, Tamron, Viltrox,
  Samyang, Voigtlander) will be scored
- ~140 obscure lenses without published optical data are excluded from
  genre results — they remain in the Lens Explorer as a spec reference
- No "Not yet scored" placeholder — a lens earns its genre slot by having data

### Data integrity rule

An optical quality field is populated **only** when a trusted review source
provides an explicit measurement or assessment. No inference, no
interpolation, no guessing from related fields. If a source did not test a
property, the field stays `undefined`. Genre formulas work with available
fields and require a minimum threshold before producing a mark.

For LensTip reviews, always cross-check against the **summary page**
(final chapter). The summary is LensTip's considered final opinion and
overrides individual test pages on contradiction. See ADR-014 for the
full rule.

### Mark scale

| Mark | Meaning |
|------|---------|
| 5 | Excellent optical fit — reference-level performance for this genre |
| 4 | Very good — strong performer, minor compromises |
| 3 | Good — capable, noticeable weaknesses |
| 2 | Adequate — usable but clearly outperformed |
| 1 | Poor optical fit — significant weaknesses for this genre |

### Current state

The prototype's curated data (`src/data/genres.ts`) uses hand-assigned marks
and a single `mtf` number as interim values. These will be replaced by
formula-computed marks as optical quality fields are populated on `Lens`
objects from trusted review sources. The per-genre formulas will be implemented in
`src/utils/scoring.ts` as optical data is populated on Lens objects.

### Suitability calculations (separate from marks)

The GenreGuide also computes **exposure suitability** at runtime — ideal ISO,
minimum shutter speed — based on user-selected EV, ISO, and crop factor. These
are physics calculations from focal length and aperture, distinct from the
optical quality mark.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| **Single MTF number** | Different genres value different optical properties; a single number flattens the judgment |
| **Hand-assigned marks only** | Does not scale; not reproducible; no transparency |
| **Score all lenses with defaults** | Guessing optical quality is worse than showing nothing |
| **User-submitted scores** | No user system; introduces moderation burden |
| **ML model** | Scoring formulas are explicit weighted sums; ML adds opacity for no accuracy gain |

## Consequences

- Scoring functions are **deterministic and testable** — same lens data always
  produces the same mark
- Adding a lens to genre results requires **populating its optical fields** from
  a trusted review source, not editorial judgment
- Genre formulas are **transparent** — users can see which optical properties
  matter for each genre
- The interim curated data provides a working baseline while optical fields are
  populated
- ADR-007's `ScoreResult` / `ScoreBreakdown` types have been removed as dead code
