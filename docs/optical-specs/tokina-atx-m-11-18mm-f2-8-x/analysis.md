# Tokina atx-m 11-18mm f/2.8 X — MTF Chart Analysis

Source: [Official Tokina product page](https://tokinalens.com/product/atx_m_11_18mm_f2_8_x/)

MTF charts:

- [tokina-atx-m-11-18mm-f2-8-x-mtf-11mm.png](tokina-atx-m-11-18mm-f2-8-x-mtf-11mm.png) — MTF (11mm, f/2.8)
- [tokina-atx-m-11-18mm-f2-8-x-mtf-18mm.png](tokina-atx-m-11-18mm-f2-8-x-mtf-18mm.png) — MTF (18mm, f/2.8)

## Chart legend

- Y-axis: contrast (%), 0–100
- X-axis: image height (mm), 0–14 mm
- Solid lines = Sagittal, dashed = Meridional
- Red = 10 lp/mm, blue = 30 lp/mm
- Aperture: wide-open (f/2.8) at each focal length

## Readings

Numerical readings are not duplicated here. See
[digitization-log.md](digitization-log.md) — Panel at 11mm and Panel at 18mm
each carry the per-field sample grid, center / edge summary, and shape
metrics. The interpretation below refers back to those tables.

## Astigmatism and field curvature

Both panels show a clean S/M separation that grows from center to corner —
characteristic of a wide-angle zoom with field-curvature contributions
rather than a free-standing astigmatic defect.

**11mm panel.** At the 90% field position, resolution-30 S = 0.55 and
M = 0.45 (digitization-log center/edge summary). The S-vs-M gap of
~18% sits at the upper boundary of ADR-014's astigmatism "10–18%" band
(score 1.0). Contrast-10 stays tight (S 0.89 vs M 0.86 at 0.9), so the
divergence is concentrated at high spatial frequencies, not low.

**18mm panel.** The gap widens at the long end: at 0.9 field, res30 S =
0.47 vs M = 0.34 (~28%), and at the corner res30 S = 0.44 vs M = 0.28.
This is the steepest astigmatism in the lens and the reason the scored
`astigmatism` field sits at 1.0 rather than 1.5 — averaging the two
panels per ADR-014's zoom rule (per-position mean of divergences) keeps
the field in the 10–18% band overall, but the tele end on its own would
fall into the 18–25% band (score 0.5).

The shape — S consistently higher than M, with the gap accelerating past
the 70% field marker — points to **field curvature** as the primary
contributor: meridional structures fall off faster as the focal plane
bends away from the sensor toward the corners. Stopping down brings both
curves up together, which Abbott (2025-02) confirms in the f/5.6–f/8
range.

## Construction-based predictions

The 13/11 optical formula carries **two aspherical + two SD elements**
(specs-log.md). Predictions consistent with that formula and validated
against the digitized readings:

- **Distortion** — UWA zooms in this class without aspherical correction
  at the wide end show 3–5% barrel; two aspherical elements typically
  pull that into the 1–2% range with profile correction handling the
  residual. Stored `distortion = 1.0` (ADR-014's "1.0–2.0%" band) is
  consistent. The vendor MTF carries no distortion signal directly —
  this prediction is rubric-applied from review measurements, not
  inferred from the chart.
- **Lateral CA** — two SD elements at the wide end of a UWA zoom is a
  standard countermeasure for lateral colour at the corners. Abbott
  reports it as well controlled out of camera; stored `lateralCA = 2.0`
  is consistent with the "negligible" band.
- **Longitudinal CA** — UWA primes and zooms rarely show significant
  longCA because the long-focal failure modes (purple/green fringing on
  out-of-focus highlights) are minimal at f/2.8 with this short focal
  range. Stored `longitudinalCA = 1.5` is consistent.
- **Vignetting** — fast UWA zooms ship with strong wide-open vignetting;
  the published MTF does not measure it. Stored `vignettingWideOpen = 0`
  reflects the lab measurement that this lens is at the harsher end of
  the "> 2.0 EV" band. Stopping down to f/5.6–f/8 recovers most of it
  (`vignettingStopped = 1.0`).

## Bridge to OQ scoring fields

The MTF readings drive the resolution and astigmatism scores; the other
fields are filled from Abbott's review per ADR-014's trust hierarchy.
Detailed per-field rubric application lives in `scoring-log.md` (to be
authored when this lens is re-scored). Summary of how the digitized
readings map to the scored values currently in `lenses.ts`:

| Field              | Score | Driver                                              |
| ------------------ | ----- | --------------------------------------------------- |
| centerWideOpen     | 1.5   | res30 center ~0.97 (11mm) / 0.91 (18mm) on chart    |
| cornerWideOpen     | 1.0   | res30 corner 0.45 (11mm) / 0.44 (18mm) on chart     |
| centerStopped      | 1.5   | Abbott f/5.6–f/8 lab measurement                    |
| cornerStopped      | 1.0   | Abbott f/8 corner; chart only published at f/2.8    |
| astigmatism        | 1.0   | S-vs-M divergence per ADR-014 zoom-mean rule        |
| distortion         | 1.0   | Construction prediction + Abbott confirms ~1.5%     |
| lateralCA          | 2.0   | 2 SD elements + Abbott "well controlled"            |
| longitudinalCA     | 1.5   | UWA at f/2.8 — minimal longCA expected and observed |
| vignettingWideOpen | 0.0   | Abbott — strong wide-open fall-off                  |
| vignettingStopped  | 1.0   | Abbott — recovers at f/5.6–f/8                      |

> The Tokina chart is published at f/2.8 (wide-open) only. Stopped-down
> scores rely on the Abbott review measurements rather than on the
> vendor chart.
