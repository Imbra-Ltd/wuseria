---
title: "MTF Confidence"
fullTitle: "How Wuseria Reads MTF Charts"
categories:
  - "Optics"
summary: "How Wuseria's MTF curves are produced from official charts and digitized third-party charts, and what that means for trust."
related:
  - "mtf"
  - "mtf-charts"
---

MTF curves on Wuseria come from two places. Curves from official manufacturer charts (Fujifilm, Sigma) are read directly and are as trustworthy as any reputable lab MTF. Curves from third-party brands (TTartisan, 7Artisans, Tokina, Viltrox) are digitized from published chart images — the original art is often dense, low resolution, or uses overlapping colored curves, and the extractor cannot always separate them cleanly.

Digitized curves are checked by an automated gate that compares each extracted curve against the source image and against a small set of optical-plausibility rules (e.g. center should not be sharper than edge in unusual ways, low-frequency curves should sit above high-frequency curves). When the gate is satisfied, the curve ships as **high confidence**. When the gate flags something, the curve still ships — but as **low confidence**.

### Why low-confidence curves are still shown

A flagged curve is not the same as a wrong curve. In the TTartisan cohort, 41 of 43 readings on a flagged pass were within ±0.05 of maintainer-pinned ground truth. The gate is often rejecting _plausibility_ (the shape does not match a textbook expectation) rather than _accuracy_ (the numbers are off). Hiding flagged curves would throw away mostly-accurate data.

Practically: treat digitized MTF curves as a _direction_ indicator, not a precise measurement. Use the lens's optical-quality scores and the field reviews linked on each lens page to confirm what the chart suggests.

### Why hand-read curves are more trustworthy

Official manufacturer MTF charts published as clean vector graphics or high-resolution renders can be eye-read directly from the optical design — no extractor in the loop, no plausibility rule to misfire. Wuseria treats those as the baseline. The digitizer + gate pipeline only runs on brands that do not publish charts in a readable form.

### The pipeline

```
Source MTF chart (PNG)
        |
        v
Curve extraction by hue + spatial frequency
        |
        v
Render-match precision check vs source
        |
        v
Optical-plausibility rules
        |
        v
high confidence  (curve committed)
        OR
low confidence   (curve committed, flagged internally)
```

Hand-read entries from official charts skip this pipeline entirely.
