# ADR-023: Formal criteria for review source trust levels

**Status:** Accepted
**Date:** 2026-05-13

## Context

ADR-014 defines a trust hierarchy (trust-3 sources override trust-2) and
aggregation rules (two trust-2 sources equal one trust-3 for a field), but
never defines what makes a source trust-3 vs trust-2. The 10 trust-3 and
30 trust-2 assignments in `src/data/reviews.ts` follow an implicit pattern
that has never been codified.

Without formal criteria:

- Adding new sources requires guessing what qualifies
- Promoting a source (e.g. ePHOTOzine from trust-2 to trust-3) has no
  checklist
- Different scorers could disagree on trust assignment for the same source

## Decision

A review source is assigned a trust level based on three criteria for lab
sources and three criteria for field sources. A source MUST meet ALL
criteria for its methodology type to qualify for trust-3. Failing any one
criterion places it at trust-2.

### Lab sources

| Criterion                   | Trust-3                                                                                                          | Trust-2                                                                        |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **Reproducibility**         | Publishes numerical data (lpmm, %, EV, MTF curves) that another lab could verify                                 | Publishes ratings, scores, or qualitative assessments without raw measurements |
| **Field coverage**          | Systematically tests most optical fields (resolution, CA, distortion, vignetting, aberrations) per review        | Covers a subset of fields or varies coverage between reviews                   |
| **Methodology consistency** | Uses the same test rig and process across all reviews; methodology is documented or inferable from output format | Test approach varies between reviews or is not documented                      |

### Field sources

| Criterion                  | Trust-3                                                                                                              | Trust-2                                                                         |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| **Controlled methodology** | Uses repeatable test scenes or controlled conditions (chart targets, star fields, standardized crops)                | Relies on casual real-world samples without controlled comparison               |
| **Per-field analysis**     | Explicitly addresses individual optical properties by name (CA, coma, bokeh, flare, etc.) with dedicated test images | Mentions optical properties in passing or bundles them into general impressions |
| **Domain authority**       | Recognized expertise in the field; cited by other reviewers; consistent track record across many lens reviews        | Useful perspective but limited track record or narrower lens coverage           |

### Trust-1

Trust-1 sources are useful references but unreliable for scoring. They
include: user forums, social media, single-lens reviews without comparative
context, sources with known bias or affiliate-driven methodology, and
sources that have been found to contradict lab data without explanation.

### Validation of existing assignments

**Lab trust-3** (all 3/3 criteria met):

| Source              | Reproducibility                                                            | Field coverage                                       | Methodology consistency                               |
| ------------------- | -------------------------------------------------------------------------- | ---------------------------------------------------- | ----------------------------------------------------- |
| LensTip             | lpmm, %, EV, MTF                                                           | All 14 fields                                        | Standardized rig, consistent format                   |
| OpticalLimits       | Imatest lpmm, MTF                                                          | All major fields                                     | Imatest rig, 15+ year track record                    |
| LensRentals         | Raw MTF, sample variation                                                  | Resolution + variation                               | Imatest, multi-copy testing                           |
| DxOMark             | Sharpness maps, CA, distortion, vignetting                                 | All major fields                                     | Automated bench, standardized                         |
| The Digital Picture | ISO 12233 crops, comparison tool                                           | Resolution, CA, distortion, vignetting               | Consistent test environment                           |
| ePHOTOzine          | Imatest MTF bar charts, CA in pixels, vignetting in stops, distortion in % | Resolution, CA, distortion, vignetting, flare, bokeh | Imatest rig, consistent chart format across 10+ years |
| ColorFoto           | LP/BH, MTF values, CA in pixels, vignetting in stops, distortion in %      | Resolution, contrast, CA, distortion, vignetting     | Image Engineering lab, versioned protocol (v1.4/v1.5) |

**Field trust-3** (all 3/3 criteria met):

| Source        | Controlled methodology                    | Per-field analysis                           | Domain authority                     |
| ------------- | ----------------------------------------- | -------------------------------------------- | ------------------------------------ |
| Dustin Abbott | Controlled test scenes per field          | CA, coma, bokeh, flare, sunstars each tested | Widely cited, 500+ lens reviews      |
| DPReview      | Studio test scene, standardized tool      | Per-field breakdown in reviews               | Industry standard reference          |
| Phillip Reeve | Controlled star tests, resolution targets | Coma, flare, bokeh, sunstars explicitly      | Cited for astrophotography optics    |
| Diglloyd      | Extreme resolution crops, corner analysis | Resolution, CA, field curvature              | Medium format crossover authority    |
| Lonely Speck  | Controlled star-field methodology         | Coma, star aberrations, corner performance   | Gold standard for astro coma testing |

**Lab trust-2 examples** (criteria not fully met):

| Source              | Missing criterion                                                       |
| ------------------- | ----------------------------------------------------------------------- |
| Imaging Resource    | Field coverage — lab charts limited to sharpness; other fields sparse   |
| What Digital Camera | Reproducibility — magazine-style scoring; limited numerical data online |

**Field trust-2 examples** (criteria not fully met):

| Source            | Missing criterion                                                      |
| ----------------- | ---------------------------------------------------------------------- |
| Admiring Light    | Controlled methodology — real-world samples, no controlled test scenes |
| Christopher Frost | Per-field analysis — addresses some fields but not systematically      |
| Fuji vs Fuji      | Domain authority — Fuji-specific, smaller review corpus                |

### Reclassification recommendations

**ePHOTOzine: promoted from trust-2 to trust-3.** Uses Imatest with
published MTF bar charts (resolution scale on Y-axis), CA charts (pixel
width), vignetting (stops), and distortion (%). Methodology consistent
across reviews from 2014 to 2026. Verified on XF 56mm f/1.2 R (2014)
and Sigma 15mm f/1.4 DC C (2026) — both show identical Imatest chart
format and field coverage.

**ColorFoto: promoted from trust-2 to trust-3.** Uses Image Engineering
lab (FH Koln partnership) with versioned test protocol (v1.4/v1.5).
Publishes downloadable PDF Testtabelle with LP/BH resolution (center +
edge %), MTF contrast values, CA in pixels, distortion in %, vignetting
in stops. Tests at 9 Siemens star positions across the image field.
Verified on XF 8mm f/3.5 R WR — PDF freely downloadable with full
numerical data.

### Promotion checklist

To promote a source from trust-2 to trust-3:

1. Verify all three criteria for the source's methodology type
2. Document evidence for each criterion (link to methodology page,
   example reviews showing field coverage, citation examples)
3. Update `src/data/reviews.ts` trust level
4. Note the promotion in the scoring log with justification
5. Re-evaluate any lenses where the promoted source was used in
   trust-2 aggregation — they may now qualify for single-source scoring

## Alternatives considered

| Alternative                                        | Why rejected                                                                                                                                                                                        |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Single unified criteria for lab and field          | Lab and field sources produce fundamentally different evidence; unified criteria would either exclude valid field sources or lower the bar for lab sources                                          |
| Weighted scoring (points per criterion)            | Over-engineered for 40 sources; binary pass/fail per criterion is simpler and sufficient                                                                                                            |
| Peer review requirement (cited by N other sources) | Hard to verify systematically; domain authority captures this intent without requiring citation counting                                                                                            |
| Four trust levels                                  | Current three levels (3, 2, 1) map cleanly to scoring rules — trust-3 stands alone, trust-2 aggregates, trust-1 is reference only; a fourth level adds complexity without changing scoring behavior |

## Consequences

- Trust assignment is now a repeatable checklist, not a judgment call
- New sources can be evaluated against explicit criteria before adding
- The promotion path from trust-2 to trust-3 is documented
- ADR-014 trust hierarchy rules remain unchanged — this ADR defines the
  input criteria, ADR-014 defines the scoring behavior
- Existing scores are unaffected — no reclassifications required
