# ADR-046: Anchor readhelpers use the clean source chart

**Status:** Accepted
**Date:** 2026-06-09

## Context

Tier 1 anchor promotion (ADR-041) requires the maintainer to eye-read
ground-truth values from the chart and enter them into
`_<LENS>_GT` tuples in `referenceset/charts.py`. The eye-read is the
calibration signal the entire production-digitization gate depends on,
so its independence from the extractor is load-bearing — an eye-read
that drifts toward the extractor's answer turns the calibration into a
self-confirming loop.

`scaffold_anchor_helpers.py` produces two artifacts per anchor (was
three; merged in ADR-048):

1. `<stem>-<view>-readhelper.png` — the chart upscaled 3× with green
   vertical sample-position lines and labels, used as the maintainer's
   eye-read aid.
2. `eye-read.md` — legend + per-cell tables pre-populated with the
   extractor's predictions. Maintainer marks corrected cells with `!`
   and unknown cells with `?`; bare cells count as silent
   verification (see ADR-048 for the cell-state contract).

The TTartisan dual-aperture dispatch (introduced in the same change
that promoted the 50mm f/1.2 anchor, #1093/#1094) chose
`<stem>-<aperture>-overlay.png` as the readhelper's base image when
that file existed — the per-aperture overlay PNG from
`extract.py:_write_inspection_artifacts`, which renders the
extractor's traced polylines over the original chart. The intent was
to make it easy to see "the extractor traced these curves" while
eye-reading. The actual effect is the opposite of the eye-read's
purpose: the maintainer's eye is nudged toward the traced points
before forming an independent reading.

A symmetrically-shaped problem would arise for any future style-
family helper that copies the same "overlay if it exists" pattern.

## Decision

Readhelper PNGs MUST be rendered from the clean source chart, never
from any artifact that depicts extractor output (overlay PNG, SVG
trace, review HTML capture). The only marks added on top of the
chart are the maintainer's reading guides:

- **Green vertical sample lines** at each of the 11 image-height
  fractions, with mm labels above the plot.
- **Orange dashed horizontal gridlines** filling in every 0.05 OTF
  the source chart does not print natively. Together with the
  chart's own gridlines they yield a uniform 0.05 grid that lets
  the maintainer eye-read at ±0.02 precision (half a 0.05 tick)
  regardless of how dense the chart's native gridlines are.

`_resolve_helper_views` and every style-family helper-view builder
inside `scaffold_anchor_helpers.py` MUST set `HelperView.base_image_path`
to a chart PNG produced by the data-source pipeline (or the lens's
chart directory), not to an extractor-produced overlay. Each style
family also supplies its `readhelper_extra_otf` tuple — the OTF
positions where the dashed gridline fills the gap to the next 0.05
multiple. Families whose native chart already prints every 0.05
(none today) leave the tuple empty.

```
+----------------------------+----------------------------+
|        ARTIFACT            |  CONTAINS EXTRACTOR OUTPUT |
+----------------------------+----------------------------+
| <stem>-<view>-readhelper   |  NO  (clean source + guide |
|                            |       lines only)          |
| <stem>-<view>-overlay      |  YES (polylines drawn over |
|                            |       the chart)           |
| <stem>-<view>.svg          |  YES (raw extractor trace) |
| <stem>-<view>-review.html  |  YES (overlay + tables)    |
+----------------------------+----------------------------+
```

When the maintainer wants to compare extractor output to the chart,
they look at the overlay PNG and review HTML — separate artifacts,
opened after the eye-read fills the GT tuple.

## Alternatives considered

**Layer the overlay underneath the helper, dimmed.** Reduces but
does not eliminate the bias — the extractor's curve is still the
strongest visual cue near each sample line. The eye still
gravitates to it. Rejected.

**Render extractor output above the helper at low alpha.** Same
problem as above with extra implementation complexity. Rejected.

**Trust the maintainer to ignore the overlay.** The whole point of
the eye-read is to inject a signal the extractor cannot produce.
A workflow that requires the maintainer to consciously discount
what their eye sees defeats that. Rejected.

**Keep the overlay only for multi-curve charts where the
maintainer needs to disambiguate which curve is which (e.g.
TTartisan dual-aperture).** The chart's legend already provides
disambiguation; if it does not, the fix is to add maintainer-
oriented disambiguation marks (color-coded sample lines per
curve, e.g.) rather than to import the extractor's answer.
Rejected.

## Consequences

- `scaffold_anchor_helpers.py:_ttartisan_dual_aperture_views` uses
  the source chart as the base unconditionally; the prior overlay-
  preference branch is removed.
- Existing TTartisan anchor readhelpers (currently only
  `ttartisan-50mm-f1-2`) are regenerated as part of #1095.
- New style-family helper-view builders MUST follow the same rule.
  A regression here is hard to spot by review (the helper still
  shows green lines and chart curves — only the underlying chart
  has changed) so this ADR is the canonical reference; the code
  comment in `_ttartisan_dual_aperture_views` points at this ADR.
- PLAYBOOK §"Maintainer eye-read helpers" updated to state the
  rule for the dispatch listing.
- Does not change the calibration / Tier-1 promotion workflow
  itself — same files, same maintainer steps, same calibration
  gate — only the contents of the readhelper PNG.
