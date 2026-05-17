# Lens Detail Page — Content Spine Specification

## Page structure

1. **Summary** — verdict + strengths/weaknesses
2. **Specifications** — lens configuration, MTF charts, specs table
3. **Optical Quality** — prose interpretation (4 clusters)
4. **Genre Fit** — 9 sub-sections, each with pros AND cons
5. **Reviews** — professional review source links
6. **Community** — user opinions (populated gradually, hidden when empty)
7. **Alternatives** — direct competitor lenses (internal cross-links)

---

## Section 1: Summary

### Template

```
A {fl} f/{aperture} {type} for Fujifilm {mount}-mount ({equiv}mm equivalent) —
{flContext}. {weight}g, ~${price}. {status}.
```

### Strengths (score ≥ 1.5)

Bullet list using phrase table (see Section 3 wording tables).

### Weaknesses (score ≤ 0.5)

Bullet list using phrase table (see Section 3 wording tables).

### Focal length context phrases

| Equivalent | Phrase                                                           |
| ---------- | ---------------------------------------------------------------- |
| ≤ 18mm     | ultra-wide field of view for interiors and dramatic perspectives |
| 19–28mm    | wide-angle suited for landscapes and architecture                |
| 29–40mm    | moderate wide angle for street and environmental portraits       |
| 41–60mm    | standard field of view close to human vision                     |
| 61–90mm    | short telephoto ideal for portraits and subject isolation        |
| 91–135mm   | telephoto compression for portraits and detail shots             |
| 136–200mm  | telephoto reach for sports and candid photography                |
| 201–400mm  | super-telephoto reach for wildlife and distant subjects          |
| 401+mm     | extreme telephoto for birding and surveillance distances         |

---

## Section 2: Specifications

Three sub-sections:

### Lens configuration

Optical design diagram or element/group description (future — requires new data field).

### MTF charts

Manufacturer MTF chart image from `docs/mtf-charts/`. Available for 31 lenses.
Omit sub-section entirely when no chart exists.

### Specs table

Existing data tables (focal length, aperture, weight, dimensions, filter thread, etc.).
Already implemented on current lens detail pages.

---

## Section 3: Optical Quality

4 clusters. Each cluster contains prose sentences generated from scores using the
wording tables below. Includes sweet spot aperture.

### Cluster: Sharpness

Fields: `centerWideOpen`, `cornerWideOpen`, `centerStopped`, `cornerStopped`

| Field          | Score 2                                           | Score 1.5                                    | Score 0.5                                        | Score 0                                   |
| -------------- | ------------------------------------------------- | -------------------------------------------- | ------------------------------------------------ | ----------------------------------------- |
| centerStopped  | excellent center sharpness when stopped down      | very good center sharpness when stopped down | average center sharpness even stopped down       | poor center sharpness stopped down        |
| cornerStopped  | excellent corner-to-corner sharpness stopped down | very good corner sharpness stopped down      | soft corners even stopped down                   | very weak corner performance stopped down |
| centerWideOpen | sharp in the center wide open                     | good center performance wide open            | soft center wide open, improves on stopping down | weak center sharpness wide open           |
| cornerWideOpen | impressive corner sharpness even wide open        | decent corner performance wide open          | soft corners wide open                           | very weak corner performance wide open    |

Sweet spot: append "Sharpest at f/{sweetSpotAperture}." when defined.

### Cluster: Aberrations

Fields: `longitudinalCA`, `lateralCA`, `coma`, `astigmatism`, `sphericalAberration`

| Field               | Score 2                                       | Score 1.5                              | Score 0.5                                    | Score 0                                              |
| ------------------- | --------------------------------------------- | -------------------------------------- | -------------------------------------------- | ---------------------------------------------------- |
| longitudinalCA      | negligible longitudinal chromatic aberration  | well-corrected longitudinal CA         | noticeable longitudinal chromatic aberration | pronounced longitudinal CA (color fringing in bokeh) |
| lateralCA           | practically zero lateral chromatic aberration | low lateral chromatic aberration       | visible lateral chromatic aberration         | strong lateral CA on frame edges                     |
| coma                | well-controlled coma                          | moderate coma control                  | noticeable coma in corners                   | strong coma (problematic for point light sources)    |
| astigmatism         | minimal astigmatism                           | moderate astigmatism                   | noticeable astigmatism                       | strong astigmatism                                   |
| sphericalAberration | well-controlled spherical aberration          | proper spherical aberration correction | noticeable spherical aberration              | poorly controlled spherical aberration               |

### Cluster: Rendering

Fields: `bokeh`, `vignettingWideOpen`, `vignettingStopped`, `flareResistance`

| Field              | Score 2                              | Score 1.5                             | Score 0.5                                        | Score 0                                 |
| ------------------ | ------------------------------------ | ------------------------------------- | ------------------------------------------------ | --------------------------------------- |
| bokeh              | smooth, pleasing bokeh rendering     | good bokeh character                  | busy bokeh character                             | harsh, distracting bokeh                |
| vignettingWideOpen | minimal light falloff wide open      | moderate vignetting wide open         | distinct vignetting wide open                    | heavy light falloff at maximum aperture |
| vignettingStopped  | virtually no vignetting stopped down | negligible vignetting stopped down    | some vignetting persists stopped down            | notable vignetting even stopped down    |
| flareResistance    | excellent flare resistance           | good performance against bright light | performance against bright light could be better | poor flare resistance                   |

### Cluster: Distortion

Fields: `distortion`

| Field      | Score 2               | Score 1.5      | Score 0.5             | Score 0                                     |
| ---------- | --------------------- | -------------- | --------------------- | ------------------------------------------- |
| distortion | negligible distortion | low distortion | noticeable distortion | significant distortion requiring correction |

---

## Section 4: Genre Fit

9 sub-sections — one per genre. Each explains why the lens IS or ISN'T suited,
referencing the genre formula's primary and secondary fields.

### Generation logic

For each genre:

1. Look up the genre formula (primary + secondary fields)
2. For each field in the formula, get the lens's score
3. Generate a sentence explaining:
   - Fields that help (score ≥ 1.5 on a formula field)
   - Fields that hurt (score ≤ 0.5 on a formula field)
   - Derived fields (\_apertureScore, \_weightScore, \_magnificationScore) described naturally

### Genre formula reference

| Genre        | Primary fields                           | Secondary fields                                                                                  |
| ------------ | ---------------------------------------- | ------------------------------------------------------------------------------------------------- |
| nightscape   | centerWideOpen                           | \_apertureScore, lateralCA, longitudinalCA, vignettingStopped, flareResistance, astigmatism, coma |
| landscape    | centerStopped, cornerStopped             | lateralCA, longitudinalCA, vignettingStopped, flareResistance, astigmatism, coma                  |
| architecture | cornerStopped, centerStopped, distortion | lateralCA, vignettingStopped, flareResistance                                                     |
| portrait     | bokeh, centerWideOpen                    | longitudinalCA, sphericalAberration, vignettingWideOpen                                           |
| street       | centerStopped, \_apertureScore           | centerWideOpen, flareResistance, longitudinalCA, coma                                             |
| travel       | centerStopped, \_weightScore             | \_apertureScore, flareResistance, longitudinalCA                                                  |
| sport        | centerWideOpen                           | \_apertureScore, longitudinalCA, lateralCA                                                        |
| wildlife     | centerWideOpen, centerStopped            | \_apertureScore, longitudinalCA, lateralCA                                                        |
| macro        | centerStopped, \_magnificationScore      | distortion, lateralCA, longitudinalCA, sphericalAberration, bokeh                                 |

### Derived field descriptions

| Derived field               | Natural language                           |
| --------------------------- | ------------------------------------------ |
| \_apertureScore (high)      | fast maximum aperture                      |
| \_apertureScore (low)       | slow maximum aperture limits low-light use |
| \_weightScore (high)        | lightweight and portable                   |
| \_weightScore (low)         | heavy for travel use                       |
| \_magnificationScore (high) | strong close-focus magnification           |
| \_magnificationScore (low)  | low magnification limits close-up work     |

### Template per genre

```
**{Genre} ({mark}/5):** {pros from formula fields}. {cons from formula fields}.
```

Omit entire section when `genreMarks` is null. Show "Not yet scored." fallback.

---

## Section 5: Reviews

List professional review sources with links from `reviewSources` field.

```
Reviewed by: LensTip, Phillip Reeve, Radojuva
```

Each source linked via `rel="nofollow sponsored" target="_blank"`.
Omit section when no review sources exist.

---

## Section 6: Community

User opinions as bullet points from `communityNotes: string[]`.

```
- Known for slow, noisy AF
- Beloved for rendering character wide open
- Popular street lens in the Fuji community
```

Populated during scoring research. Section hidden when field is empty/absent.
Data model: `communityNotes?: string[]` on Lens interface.

---

## Section 7: Alternatives

Direct competitor lenses computed at build time. Links to other lens detail pages.

### Matching logic

Same mount + overlapping focal length range (±10mm equivalent):

- For a 56mm prime → show all primes in 46–66mm range
- For a 16-55mm zoom → show zooms that overlap that range

### Sort order

By genre similarity (highest overlap in top genres), then by price.

### Limit

Max 5 alternatives. Omit section when fewer than 2 exist.

### Template

```
**Alternatives:**
- [Sigma 56mm f/1.4 DC DN C](/lenses/sigma-56mm-f1-4-dc-dn-c/) — ~$500, 280g
- [Viltrox AF 56mm f/1.4 STM](/lenses/viltrox-af-56mm-f1-4-stm/) — ~$250, 320g
- [TTartisan AF 56mm f/1.8](/lenses/ttartisan-af-56mm-f1-8/) — ~$250, 260g
```

Each link is an internal cross-link (SEO internal linking mesh).
Creates natural "vs" keyword clusters ("XF 56mm vs Sigma 56mm").

---

## Missing data handling

When a lens has no optical scores or genre marks, display an explanation
instead of hiding the section.

Data model: `scoringStatus?: "niche" | "new" | "discontinued" | "specialty" | "pending"`

| Status         | Phrase                                                       |
| -------------- | ------------------------------------------------------------ |
| `niche`        | Limited professional review coverage for this lens.          |
| `new`          | Recently released — professional reviews pending.            |
| `discontinued` | Discontinued before comprehensive optical testing.           |
| `specialty`    | Standard optical bench tests do not apply to this lens type. |
| `pending`      | Scoring in progress.                                         |

Default when `scoringStatus` absent on an unscored lens: `niche`.

Applies to: Optical Quality, Genre Fit sections.

---

## Meta description template

```
{brand} {model}: {topGenre1}, {topGenre2} lens. Strengths: {strength1}, {strength2}. {weight}g, ~${price}.
```

Target: ~150 characters, unique per lens, keyword-rich.

---

## Example: Fujifilm XF 56mm f/1.2 R

### Summary

A 56mm f/1.2 prime for Fujifilm X-mount (84mm equivalent) — short telephoto ideal for portraits and subject isolation. 400g, ~$1000. Discontinued.

**Strengths:**

- Excellent center sharpness when stopped down
- Minimal astigmatism
- Proper spherical aberration correction
- Practically zero lateral chromatic aberration
- Negligible distortion
- Virtually no vignetting stopped down
- Smooth, pleasing bokeh rendering

**Weaknesses:**

- Soft center wide open, improves on stopping down
- Very weak corner performance wide open
- Noticeable longitudinal chromatic aberration
- Distinct vignetting wide open
- Performance against bright light could be better

### Specifications

_(Lens configuration: future)_

_(MTF chart: not available for this lens)_

_(Specs table: existing implementation)_

### Optical Quality

**Sharpness:** Excellent center sharpness when stopped down, but soft center wide open that improves on stopping down. Very weak corner performance wide open. Sharpest at f/4.

**Aberrations:** Practically zero lateral chromatic aberration. Minimal astigmatism and proper spherical aberration correction. However, noticeable longitudinal chromatic aberration produces color fringing in bokeh.

**Rendering:** Smooth, pleasing bokeh rendering. Virtually no vignetting stopped down, but distinct vignetting wide open. Performance against bright light could be better.

**Distortion:** Negligible distortion.

### Genre Fit

**Street (4/5):** Excellent center sharpness stopped down and fast f/1.2 aperture make this ideal for decisive-moment shooting. Noticeable longitudinal CA is rarely an issue at street distances.

**Travel (4/5):** Excellent center sharpness stopped down in a compact 400g body. Performance against bright light could be better for harsh midday conditions.

**Nightscape (3/5):** Fast f/1.2 aperture gathers light well. However, soft center wide open and noticeable coma on point light sources limit astrophotography use. Distinct vignetting wide open.

**Landscape (3/5):** Excellent center sharpness stopped down, but very weak corner performance wide open requires stopping down. Negligible distortion is a plus.

**Architecture (3/5):** Excellent center and corner sharpness stopped down with negligible distortion. Weaker flare resistance may be problematic for interior shots with window light.

**Portrait (2/5):** Smooth bokeh rendering and proper spherical aberration correction work well for subject separation. However, soft center wide open limits critical sharpness at maximum aperture, and noticeable longitudinal CA produces color fringing in bokeh highlights.

**Sport (2/5):** Fast f/1.2 aperture helps in low light, but soft center wide open means AF accuracy is critical. Noticeable longitudinal CA.

**Wildlife (2/5):** Soft center wide open and limited reach (84mm equivalent) make this impractical for distant subjects.

**Macro (1/5):** Low magnification (0.09x) with 70cm minimum focus distance. Not suited for close-up work.

### User Consensus

Reviewed by: [LensTip](https://www.lenstip.com/420.1-Lens_review-Fujifilm_Fujinon_XF_56_mm_f_1.2_R.html)
