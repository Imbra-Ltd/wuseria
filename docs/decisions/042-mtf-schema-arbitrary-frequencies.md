# ADR-042: Generalize MTF schema to arbitrary frequencies

**Status:** Accepted
**Date:** 2026-06-06

## Context

The MTF reading schema (`src/types/mtf.ts`) hardcodes exactly four
fields per reading row:

```typescript
interface MtfReading {
  position: number;
  contrast10S: number | null;
  contrast10M: number | null;
  resolution30S: number | null;
  resolution30M: number | null;
}
```

This was correct when the data came from Sigma (10 + 30 lp/mm),
Samyang (10 + 30), 7Artisans (10 + 30), Tokina (10 + 30), and Viltrox
(10 + 30) — the five anchored brands. Every published chart in those
families plots exactly two spatial frequencies, both at the canonical
10 and 30 lp/mm.

Fujifilm publishes MTF at different frequencies entirely:

| Lens shape | Frequencies plotted (lp/mm) | Charts per lens |
| ---------- | --------------------------- | --------------- |
| GF prime   | 15, 20, 40                  | 3               |
| GF zoom    | 10, 20, 40 × {wide, tele}   | 6               |

Inventory: 62 Fujifilm lenses, 129 MTF chart images. The schema as it
stands cannot represent any of them losslessly.

The schema problem is upstream of every other Fujifilm-specific
concern (multi-image-per-lens orchestration, 282×212 small-image
extraction, per-frequency filename parsing) — those all assume there
is a place to store the readings. Without a schema that can hold
{15, 20, 40} lp/mm side-by-side, the downstream work has nowhere to
write the result. The same problem will hit every future brand that
publishes at non-canonical frequencies (Voigtländer when its
APO-LANTHAR charts get digitized, Zeiss Touit at 10 + 20 + 40,
Carl Zeiss Otus / Milvus on the historical record).

A schema migration is the load-bearing change for un-anchored brand
work in general — not just Fujifilm.

## Decision

Generalize `MtfReading` from four fixed fields to a frequency map.

```typescript
interface MtfReading {
  position: number;
  // Per-frequency S/M samples. Key is the spatial frequency in lp/mm
  // (e.g. 10, 15, 20, 30, 40). Each entry's `S` (sagittal) or `M`
  // (meridional) value MAY be null when the source chart has no
  // usable data at this position for that orientation.
  //
  // A reading row MAY omit frequencies entirely — Fuji primes carry
  // {15, 20, 40}; Sigma carries {10, 30}; nothing forces a row to
  // populate frequencies the lens does not publish.
  samples: Record<number, { S: number | null; M: number | null }>;
}
```

Each `MtfReading` row still represents one image-height position; the
shape change is purely how per-position values are stored.

### Renaming "contrast" and "resolution"

The fixed-field names embedded an interpretation: 10 lp/mm "is
contrast," 30 lp/mm "is resolution." That mapping is conventional
(low-frequency MTF correlates with perceived contrast, high-frequency
MTF correlates with resolving power) but it is not load-bearing in
the schema — what the schema needs is the frequency and the
sagittal/meridional pair. The contrast / resolution wording lives in
display labels, scoring rule names, and wiki copy; those keep their
language. The data shape drops the wording.

### Scoring under arbitrary frequencies

Scoring formulas that read `contrast10S` and `resolution30S` today
need a per-lens fallback when the canonical 10 + 30 frequencies are
absent. The rule:

1. Prefer the exact canonical frequency (10 or 30) when present.
2. Otherwise pick the **closest published frequency** by absolute
   distance in lp/mm.
3. Surface the chosen frequency in the score's `source` field so the
   scoring log records which frequency was substituted.

Examples under this rule:

| Lens family | Wants contrast (≈10) | Wants resolution (≈30) | Notes                                            |
| ----------- | -------------------- | ---------------------- | ------------------------------------------------ |
| Sigma       | 10                   | 30                     | exact match                                      |
| Fuji prime  | 15                   | 40                     | 15 closer to 10 than 20; 40 closer to 30 than 20 |
| Fuji zoom   | 10                   | 40                     | 10 exact; 40 closest to 30                       |
| Zeiss Touit | 10                   | 40                     | (if/when digitized) — same as Fuji zoom          |

The closest-frequency choice is stable per (brand, family) — a
reviewer comparing two Fujifilm primes always reads the same
frequency for contrast on both — so cross-lens comparisons within a
brand stay consistent. Cross-brand comparison (Fuji prime at 15 vs
Sigma at 10) is already imperfect because the lenses are physically
different; the schema generalization does not introduce a new
imprecision, it makes the existing imprecision visible.

### Reading-row consistency

Within one lens's chart series, every row in the same chart MUST
carry the same set of frequency keys. A row with `samples: {10, 30}`
followed by a row with `samples: {15, 40}` indicates either a
malformed dataset or a curator error — validation tests enforce that
the key set is constant across rows of one `MtfChart`.

A `MtfChart` MAY have a different frequency set from another
`MtfChart` on the same lens (prime: only one chart; zoom: wide and
tele are separate charts and could in principle differ — though
in every observed case the two share frequencies).

## Alternatives considered

| Alternative                                                       | Why rejected                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Lossy mapping (Fuji 15 → 10, 40 → 30; drop 20)                    | Treats two physically distinct frequencies as one. Downstream the rendered chart says "10 lp/mm" but the data is from 15 lp/mm — silent data drift that surfaces only if someone cross-references the source. Loses the 20 lp/mm panel entirely (1/3 of the Fuji prime publication). Pragmatic for a weekend but creates a class of "lossy" lens that the renderer cannot mark as such without an out-of-band flag.              |
| Option A — add optional `contrast15S/M`, `resolution40S/M` fields | Smaller blast radius (~6 h refactor vs ~10 h). Existing data untouched. Schema becomes busier with every new brand-specific frequency, though, and the renderer ends up with a long if-then ladder over optional field names. Reaches the same end state by walking through every intermediate Fuji-specific shape; the generalized record is one migration that absorbs every future brand including the not-yet-imagined ones. |
| Per-frequency reading rows (one row per `{position, freq, S, M}`) | Flatter; easier to filter. Breaks the "one position = one reading" mental model that Sigma/Samyang readers (and the existing chart renderer's polyline construction) rely on. Forces every renderer to group-by-position internally before drawing. Net cost is higher than the record-of-frequencies shape.                                                                                                                     |
| Defer the schema change; skip Fujifilm this weekend               | Honest scope cut. Rejected because the user explicitly chose to invest the weekend in the generalized schema. The schema change unblocks every future non-canonical-frequency brand, not just Fuji — the work has compounding return.                                                                                                                                                                                            |

## Consequences

- **Branch model.** Work proceeds on stacked PRs from
  `feat/mtf-schema-generalization`:
  1. Schema migration (this ADR + type + data + renderer + tests + scoring audit)
  2. Digitizer field-set generalization (`tools/mtfdigitizer/` refactor)
  3. Fujifilm profile + per-frequency orchestrator (ADR-043)
  4. Fujifilm Tier 1 anchor + Tier 2 production runs
- **Schema migration is atomic with renderer and tests.** The type,
  data, renderer, and validation tests change together in one PR;
  any one of them on its own breaks the build. The renderer must
  draw arbitrary-frequency polylines (color-by-frequency, line-style
  by S/M) before the data shape lands.
- **Scoring formulas grow a "closest frequency" lookup.** Each call
  site that today reads `contrast10S` becomes a small helper:
  `mtfValue(reading, targetFreqLpmm: 10, sm: 'S')` that walks
  `Object.keys(reading.samples)`, picks the closest, and returns
  the value. The helper centralizes the rule; call sites stay
  expressive. Scoring documentation (`docs/decisions/014-optical-quality-rubric.md`)
  picks up a paragraph on the closest-frequency rule.
- **Digitizer field set is per-profile.** Today the dispatch
  hardcodes `_FIELD_BY_KEY: dict[tuple[int, str], str]` mapping
  `(10, 'S') → 'contrast10S'`. After this ADR, the field set is
  derived from `profile.frequencies_lpmm × {'S', 'M'}`. Sister
  fallback (10S/10M pair, 30S/30M pair) generalizes to "for each
  frequency in the profile, pair S with M." Center symmetry (S=M
  at position 0) is per-frequency.
- **Provenance survives.** Existing committed data round-trips
  losslessly: `contrast10S=0.98` becomes `samples[10].S=0.98`. No
  numerical value changes, only the access path.
- **Future brand work unblocks.** Voigtländer APO-LANTHAR (when /
  if digitized), Zeiss Touit, Carl Zeiss historical lenses, and any
  yet-unseen frequency convention land without further schema
  changes. The cost of brand N is the cost of its profile + its
  Tier 1 anchor, not a schema migration.
- **MtfChart.astro renderer becomes frequency-driven.** Color key
  switches from "red = 10, blue = 30" (the Sigma convention baked
  into the component) to a per-frequency color assigned at render
  time. Document the color rule in the renderer.
- **No backwards-compat shim.** Per project convention
  ("backwards-compatibility shims" are anti-pattern) the migration
  is hard — no dual-read of old + new shape. The PR migrates all
  in-tree data atomically. There is no published external consumer
  of the schema.
