# Carl Zeiss Touit 12mm f/2.8 — MTF Chart Analysis

Source: [Zeiss Touit 2.8/12 datasheet PDF](https://www.zeiss.com/content/dam/pno/downloads/photo-lenses/datasheets/touit-lenses/datasheet-zeiss-touit-2812.pdf)
(the product page is discontinued; the datasheet is the canonical official source — see `specs-log.md`).

MTF charts:

- [zeiss-touit-12mm-f2-8-mtf.png](zeiss-touit-12mm-f2-8-mtf.png) — stacked
  panels, max (k=2.8) top + stopped (k=5.6) bottom, 10/20/40 lp/mm, white
  light. Canonical digitized chart.

## Chart legend

- Two stacked panels: top = max aperture (f/2.8), bottom = stopped (f/5.6)
- Solid = Sagittal (S), dashed = Meridional / tangential (M)
- Three frequencies per panel: 10 / 20 / 40 lp/mm
- X-axis: image height (0-14 mm), Y-axis: MTF (0-1)

## Readings

Per-panel digitized readings (EYE-vs-EX sample grid, center/edge summary,
shape metrics) live in [digitization-log.md](digitization-log.md). Not
re-tabulated here per ADR-033. Tier 1 maintainer eye-read ground truth
(132 cells) is the source for the assessment below.

## Astigmatism / field-curvature assessment

S/M divergence (from the eye-read GT):

- Center to ~8.4 mm: S and M track within ~0.03 at all three frequencies —
  well-corrected across the inner two-thirds of the field.
- Max panel, outer field: meridional runs above sagittal from ~9.8 mm out —
  at the corner the 10 lp/mm gap reaches ~0.20 (0.62 S / 0.82 M) and the
  20 lp/mm gap ~0.13. At 40 lp/mm the pair stays within ~0.06.
- Stopped panel: closer overall; the divergence appears only at the
  extreme corner and reverses sign (14 mm, 40 lp/mm: 0.60 S / 0.42 M).

**Assessment:** the edge divergence is field-edge-localized and the sign
reverses between panels — pointing to field curvature rather than pure
astigmatism. The MTF chart cannot isolate the two (ADR-014); LensTip's
measured average S/M difference is just 4.7%, giving astigmatism = 2.0.
Lab data takes precedence.

## Construction-based predictions

- Distagon retrofocus wide-angle (11 elements / 8 groups) -> expect
  moderate barrel distortion and edge light falloff typical of a fast
  12 mm on APS-C (matches distortion = 0.5, vignettingWideOpen = 0.5).
- 2 aspherical elements -> spherical aberration well controlled
  (matches sphericalAberration = 2.0).
- 3 anomalous-partial-dispersion elements -> lateral CA correction
  (matches lateralCA = 2.0).
- No element type supports a coma inference — coma is measured
  (LensTip) at 0.5, not predicted from construction (ADR-014).

## Bridge to OQ scoring

- Center MTF is high and flat (10 lp/mm ~ 0.95-0.96 across both panels)
  -> centerStopped = 2.0, centerWideOpen = 1.5.
- Corner MTF holds up stopped down (10 lp/mm ~ 0.85-0.91 at the edge) but
  softens wide open in the outer field -> cornerStopped = 1.5,
  cornerWideOpen = 1.0.
- Full per-field scoring justification and LensTip source data:
  [scoring-log.md](scoring-log.md).
