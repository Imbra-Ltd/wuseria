# Carl Zeiss Touit 32mm f/1.8 — MTF Chart Analysis

Source: [Zeiss Touit 1.8/32 datasheet PDF](https://www.zeiss.com/content/dam/pno/downloads/photo-lenses/datasheets/touit-lenses/datasheet-zeiss-touit-1832.pdf)
(the product page is discontinued; the datasheet is the canonical official source — see `specs-log.md`).

MTF charts:

- [zeiss-touit-32mm-f1-8-mtf.png](zeiss-touit-32mm-f1-8-mtf.png) — stacked
  panels, max (k=1.8) top + stopped (k=4) bottom, 10/20/40 lp/mm, white
  light. Canonical digitized chart.

## Chart legend

- Two stacked panels: top = max aperture (f/1.8), bottom = stopped (f/4)
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

- Max panel (f/1.8): meridional runs above sagittal across almost the
  whole field — at 10 lp/mm the gap is ~0.09 by 8.4 mm and ~0.15 at the
  corner (0.66 S / 0.81 M); the pattern persists at 20 and 40 lp/mm.
- Stopped panel (f/4): S and M collapse to within ~0.03 through most of
  the field, separating only at 40 lp/mm in the outer third.

**Assessment:** the strong, whole-field S/M split wide open is the
signature of field curvature and coma rather than pure astigmatism — the
MTF chart cannot separate them (ADR-014). LensTip point-source testing
isolates the two: astigmatism = 2.0 (low), coma = 0.0 (severe wide open).
Lab data takes precedence.

## Construction-based predictions

- Planar double-Gauss (8 elements / 5 groups), no aspherical or
  special-dispersion elements -> construction supports no CA or spherical
  inference (ADR-014); those fields are lab-measured (sphericalAberration
  = 1.0, longitudinalCA = 0.5, lateralCA = 1.0).
- A fast standard Planar with no aspherics is consistent with the severe
  wide-open coma the lab measured (coma = 0.0) and moderate distortion
  (distortion = 1.0).

## Bridge to OQ scoring

- Center MTF is modest wide open (10 lp/mm ~ 0.86, 40 lp/mm ~ 0.52) but
  excellent stopped (10 lp/mm ~ 0.95) -> centerWideOpen = 1.0,
  centerStopped = 2.0.
- The corner is the weakest of the three Touits wide open (heavy outer-
  field falloff at f/1.8) and only fair stopped -> cornerWideOpen = 0.0,
  cornerStopped = 1.0.
- Full per-field scoring justification and LensTip source data:
  [scoring-log.md](scoring-log.md).
