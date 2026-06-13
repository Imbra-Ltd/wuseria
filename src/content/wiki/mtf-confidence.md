---
title: "MTF Confidence"
fullTitle: "MTF Per-Pass Confidence (HIGH / LOW)"
categories:
  - "Optics"
summary: "What the HIGH/LOW confidence badges on MTF charts mean and how the digitization pipeline produces them."
related:
  - "mtf"
  - "mtf-charts"
---

Some MTF charts on Wuseria are read directly from clean, official manufacturer charts (Fujifilm, Sigma). Others are digitized from third-party charts (TTartisan, 7Artisans, Tokina, Viltrox) where the original chart art is dense, low resolution, or uses overlapping colored curves that the extractor cannot always separate cleanly. To be honest about which is which, every MTF aperture pass carries a confidence verdict: HIGH or LOW.

**HIGH** means the readings are trustworthy. Either the chart was eye-read by a maintainer from an official optical-design chart, or the autotriage gate (which compares each extracted curve against the source PNG and against a small set of optical-plausibility priors) accepted the pass. Treat HIGH curves the same way you would treat any reputable lab MTF.

**LOW** means the autotriage gate flagged the pass. The samples are still shown, because the underlying readings are usually within ±0.05 of ground truth even on a LOW pass — the gate is rejecting plausibility, not accuracy. But you should not lean on a LOW pass to settle a sharpness comparison; cross-check with field reviews and the lens's optical-quality scores instead.

### Reason codes

A LOW pass shows the reason the gate rejected it:

- **`precision_below_threshold`** — the extractor's render-match precision against the source PNG fell below the calibrated threshold. Usually means colored curves overlapped or the chart axis labels intersected a curve.
- **`prior_failed_center_ge_edge`** — at one or more frequencies, the extracted edge MTF is higher than the center MTF. Common on stopped-down APS-C wide primes (corner sharpness recovers as the center stops responding to diffraction), so the prior itself is not always sound — but the gate flags it for human review.
- **`prior_failed_low_freq_ge_high`** — the high-frequency curve (e.g. 30 lp/mm) tracks above the low-frequency curve (10 lp/mm) at some position. Physically should not happen; usually means the extractor swapped two curves.
- **`prior_failed_not_suspiciously_flat`** — a curve sits within a narrow band across the full image height. Usually a sign the extractor locked onto the chart's grid line or the MTF=1.0 ceiling rather than the real curve.

### The pipeline

```
Source MTF chart (PNG)
        |
        v
Curve extraction by hue + spatial frequency
        |
        v
Render-match precision vs source
        |
        v
Optical-plausibility priors
        |
        v
HIGH (committed) or LOW (badged, samples kept)
```

Hand-curated entries skip this pipeline entirely and ship as HIGH by construction.

### Why we keep LOW samples

A LOW verdict on a single pass is not the same as wrong data. Evidence from the TTartisan cohort showed 41 of 43 readings on a LOW pass were within ±0.05 of maintainer-pinned ground truth. Hiding LOW passes would throw away ~34% of digitized data that is mostly accurate. Surfacing the badge is the more honest move: the curve is shown, the gate's reservation is shown, and the link back here explains what to do with that information.
