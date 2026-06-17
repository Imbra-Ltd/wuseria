# ADR-056: Brand slug prefix may diverge from DB brand name

**Status:** Accepted
**Date:** 2026-06-17

## Context

Two slugging systems coexist for `docs/optical-specs/<slug>/` directory
naming:

1. **Python `brandkit`** (`tools/brandkit/extractor.py`,
   `tools/brandkit/slug.py`) builds dir names as
   `f"{slug_prefix}-{model_to_slug(model)}"`. Each `BrandExtractor`
   subclass declares its own `slug_prefix`. The Zeiss extractor
   (`tools/zeiss/extractor.py`) sets `slug_prefix="zeiss"` even though
   `name="Carl Zeiss"` — historically Zeiss-branded products use the
   shortened modern brand on disk and in filenames
   (`zeiss-touit-12mm-f2-8-datasheet.pdf`).

2. **TS directory-name invariant** (`src/data/mtf-readings.test.ts`,
   added in #1069) computes the expected dir name as
   `toSlug(lens.brand + " " + lens.model)` using `lens.brand` as it
   appears in `lenses.ts`. For Zeiss lenses, `brand: "Carl Zeiss"` →
   `carl-zeiss-touit-*`, which does not match the on-disk
   `zeiss-touit-*` dirs.

#1085 surfaced this as four "orphan" optical-specs directories on the
allowlist:

```
zeiss-touit-12mm-f2-8
zeiss-touit-32mm-f1-8
zeiss-touit-50mm-f2-8-macro
thingyfy-pinhole-pro-x   (separate cause: lens-accessory, not a lens)
```

The Zeiss directories are not orphan — they have matching
`Carl Zeiss Touit *` entries in `lenses.ts`. They look orphan only
because the two slugging systems disagree on whether "Carl" is part of
the slug.

```
  lenses.ts entry         brandkit on-disk           TS invariant expects
  ---------------------   ------------------------   -----------------------
  brand: "Carl Zeiss"     zeiss-touit-12mm-f2-8/     carl-zeiss-touit-12mm-f2-8
  model: "Touit 12..."    zeiss-touit-32mm-f1-8/     carl-zeiss-touit-32mm-f1-8
                          zeiss-touit-50mm-f2-8-     carl-zeiss-touit-50mm-f2-8-
                            macro/                     macro
```

## Decision

Treat brandkit's `slug_prefix` as authoritative for directory names
and DB brand as authoritative for display. The TS invariant honors
brandkit divergences via a small explicit override map:

```typescript
// src/data/mtf-readings.test.ts
const BRAND_SLUG_OVERRIDE: Record<string, string> = {
  "Carl Zeiss": "Zeiss",
};

function dirBrand(brand: string): string {
  return BRAND_SLUG_OVERRIDE[brand] ?? brand;
}
```

Today only one divergence exists (Carl Zeiss → Zeiss). Future
divergences MUST be added to this map and to the corresponding
brandkit extractor's `slug_prefix`.

The invariant also scans `accessories.ts` so accessory-only specs-log
dirs (Thingyfy Pinhole Pro X) are not flagged as orphan.

## Alternatives considered

- **Rename `docs/optical-specs/zeiss-touit-*` → `carl-zeiss-touit-*`.**
  Rejected: would break `ZeissExtractor.config.slug_prefix="zeiss"` —
  the next extractor run would write `zeiss-*-datasheet.pdf` back into
  the renamed dirs and create new orphans. Also touches
  `tools/mtfdigitizer/referenceset/charts.py` chart_path, mtfdigitizer
  README/REFERENCE_SET docs, and the zeiss extractor test fixture.
- **Change DB brand `"Carl Zeiss"` → `"Zeiss"` in `lenses.ts`.**
  Rejected: 13+ files reference "Carl Zeiss" (journal, ADR-042,
  bookmarks, lenstip-index.json, zeiss tooling, brand-enum type).
  Wide blast radius; the modern brand-name choice is orthogonal to
  the slug mismatch.
- **Keep the `KNOWN_PENDING_LENS_ENTRY` allowlist permanently.**
  Rejected: makes the invariant permanently leaky and pushes the
  systematic divergence into a list of one-off exceptions.

## Consequences

- The TS test and Python brandkit are weakly coupled through
  `BRAND_SLUG_OVERRIDE`. A new brand with `slug_prefix != name.lower()`
  MUST be added to both sides in the same PR.
- `KNOWN_PENDING_LENS_ENTRY` is removed; the invariant now passes
  without an allowlist. Future genuine orphans (dir for a lens that
  is not in `lenses.ts`/`accessories.ts`) fail the test
  unconditionally — which is the intended behavior of #1069.
- The accessories scan means accessory-only specs-log dirs are
  first-class. Per `specs-log.md` convention (CLAUDE.md §2.6
  Specs-log workflow), accessories that have a specs-log dir
  continue to satisfy the invariant without additional handling.
