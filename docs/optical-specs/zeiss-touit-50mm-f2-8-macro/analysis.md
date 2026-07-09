# Carl Zeiss Touit 50mm f/2.8 Macro — MTF Chart Analysis

Source: [Zeiss Touit 2.8/50M datasheet PDF](https://www.zeiss.com/content/dam/pno/downloads/photo-lenses/datasheets/touit-lenses/datasheet-zeiss-touit-2850m.pdf)
(the product page is discontinued; the datasheet is the canonical official source — see `specs-log.md`).

MTF charts:

- [zeiss-touit-50mm-f2-8-macro-mtf.png](zeiss-touit-50mm-f2-8-macro-mtf.png) —
  stacked panels, max (k=2.8) top + stopped (k=5.6) bottom, 10/20/40 lp/mm,
  white light. Canonical digitized chart.

## Chart legend

- Two stacked panels: top = max aperture (f/2.8), bottom = stopped (f/5.6)
- Solid = Sagittal (S), dotted = Meridional / tangential (M) — this chart
  uses a dotted (not dashed) meridional line
- Three frequencies per panel: 10 / 20 / 40 lp/mm
- X-axis: image height (0-14 mm), Y-axis: MTF (0-1)

## Readings

Per-panel digitized readings (EYE-vs-EX sample grid, center/edge summary,
shape metrics) live in [digitization-log.md](digitization-log.md). Not
re-tabulated here per ADR-033. Tier 1 maintainer eye-read ground truth
(132 cells) is the source for the assessment below.

## Astigmatism / field-curvature assessment

S/M divergence (from the eye-read GT):

- S and M track very closely across the entire field at 10 and 20 lp/mm
  in both panels (gap within ~0.03) — the best-corrected of the three
  Touits.
- Divergence appears only at 40 lp/mm in the outer third and at the
  extreme corner (stopped, 14 mm: 0.72 S / 0.50 M).

**Assessment:** near-coincident S/M lines through the working field ->
consistent with the lab's astigmatism = 2.0 and coma = 2.0. As a
Makro-Planar optimized for flat-field close work, the tight S/M tracking
is expected. Lab data takes precedence.

## Construction-based predictions

- Makro-Planar (14 elements / 11 groups) with 2 aspherical elements ->
  spherical aberration well controlled (matches sphericalAberration = 1.5).
- 2 anomalous-partial-dispersion elements -> CA correction (lateralCA = 1.0,
  longitudinalCA = 1.0).
- True 1:1 macro (maxMagnification = 1.0), flat-field corrected -> supports
  the strong across-field MTF and low astigmatism.

## Bridge to OQ scoring

- Center MTF is high in both panels (10 lp/mm ~ 0.93-0.95, 40 lp/mm ~ 0.81-
  0.82 at center) -> centerWideOpen = 2.0, centerStopped = 2.0.
- The corner softens wide open but recovers stopped down -> cornerWideOpen
  = 0.5, cornerStopped = 1.5.
- Full per-field scoring justification and LensTip source data:
  [scoring-log.md](scoring-log.md).
