"""Emit Fujifilm Tier 2 MTF readings as TS literals for `mtf-readings.ts`.

Walks the per-frequency Fuji ReferenceChart entries (style family
`fujifilm-permfreq`) and produces one `MtfData` literal per lens. For
primes the literal carries one chart with all per-frequency samples
merged at each position; for zooms the literal carries two charts
(wide and tele), each with the merged samples at its focal length.

This is the bridge from "extracted to disk" (the production
digitization-log.md artifacts) to "visible on the lens detail page"
(src/data/mtf-readings.ts).

Usage::

    cd tools
    py -m mtfdigitizer.scripts.emit_fuji_tier2          # preview to stdout
    py -m mtfdigitizer.scripts.emit_fuji_tier2 --write   # patch mtf-readings.ts

Without `--write` the literals print to stdout for review. With it, the
script appends each entry to `src/data/mtf-readings.ts` at the
sentinel position just before the closing `};` of the `mtfReadings`
record. Entries already present (matching slug) are replaced in place.

`source` URL is derived from the lens slug:
`https://fujifilm-x.com/global/products/lenses/<slug-without-fujifilm->/`.
The maintainer can adjust per-lens after the bulk emission.
"""

from __future__ import annotations

import argparse
import dataclasses
import re
import sys
from collections import defaultdict
from pathlib import Path

from mtfdigitizer.emit import format_source_line
from mtfdigitizer.family_profile import profile_for_chart
from mtfdigitizer.per_frequency import parse_filename_frequency
from mtfdigitizer.pipeline import extract_chart
from mtfdigitizer.pipeline.dispatch import parse_field_name
from mtfdigitizer.pipeline.types import PlotBox, SampledReading
from mtfdigitizer.referenceset.charts import (
    REFERENCE_CHARTS,
    PlotBoxCoords,
    ReferenceChart,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
MTF_READINGS_PATH = REPO_ROOT / "src" / "data" / "mtf-readings.ts"
LENSES_PATH = REPO_ROOT / "src" / "data" / "lenses.ts"


_VIEW_INFIX_RE = re.compile(r"-(?P<view>wide|tele)-\d+lp\.png$", re.IGNORECASE)

# Match a single top-level lens entry: from `^  {` to the matching `^  },`.
_LENS_BLOCK_RE = re.compile(r"^  \{$.*?^  \},?$", re.DOTALL | re.MULTILINE)
_BRAND_RE = re.compile(r'^\s*brand:\s*"([^"]+)"', re.MULTILINE)
_MODEL_RE = re.compile(r'^\s*model:\s*"([^"]+)"', re.MULTILINE)
# `officialUrl:` may have the value on the same line or wrapped to the next.
_OFFICIAL_URL_RE = re.compile(
    r'^\s*officialUrl:\s*(?:\n\s*)?"([^"]+)"', re.MULTILINE
)


def _to_plotbox(
    coords: PlotBoxCoords,
    y_top_insets: tuple[tuple[str, int], ...] = (),
) -> PlotBox:
    return PlotBox(
        x_left=coords.x_left,
        x_right=coords.x_right,
        y_top=coords.y_top,
        y_bottom=coords.y_bottom,
        y_top_insets=y_top_insets,
    )


def _view_panel_key(image_path: Path) -> str | None:
    """Group key for the panel a chart view belongs to.

    Returns "wide" / "tele" for zoom views, None for prime lenses.
    """
    m = _VIEW_INFIX_RE.search(image_path.name)
    return m.group("view").lower() if m else None


def _format_value(v: float | None) -> str:
    if v is None:
        return "null"
    rounded = round(v, 2)
    text = f"{rounded:.2f}".rstrip("0").rstrip(".")
    return text or "0"


def _frequencies(reading: SampledReading) -> list[int]:
    freqs: set[int] = set()
    for field in reading.samples:
        try:
            freq, _sm = parse_field_name(field)
        except ValueError:
            continue
        freqs.add(freq)
    return sorted(freqs)


def _has_any_data(r: SampledReading) -> bool:
    return any(v is not None for v in r.samples.values())


def _format_reading(r: SampledReading) -> str:
    inner_lines: list[str] = []
    for freq in _frequencies(r):
        s_val = r.samples.get(f"freq{freq}S")
        m_val = r.samples.get(f"freq{freq}M")
        inner_lines.append(
            f"              {freq}: {{ S: {_format_value(s_val)}, "
            f"M: {_format_value(m_val)} }},"
        )
    samples_block = "\n".join(inner_lines)
    return (
        "          {\n"
        f"            position: {r.position_mm:g},\n"
        "            samples: {\n"
        f"{samples_block}\n"
        "            },\n"
        "          },"
    )


def _extract_view_readings(
    chart: ReferenceChart, view, repo_root: Path
) -> tuple[SampledReading, ...]:
    """Run extract_chart on one view with the parsed-frequency profile."""
    base_profile = profile_for_chart(chart)
    image_path = repo_root / view.chart_path
    freq = parse_filename_frequency(image_path)
    profile = dataclasses.replace(base_profile, frequencies_lpmm=(freq,))
    plot_box = _to_plotbox(view.plot_box, view.y_top_insets)
    result = extract_chart(
        image_path,
        profile,
        plot_box,
        image_height_mm=chart.image_height_mm,
    )
    return result.readings


def _merge_readings(
    per_view_readings: list[tuple[SampledReading, ...]],
) -> tuple[SampledReading, ...]:
    """Merge per-frequency readings at each position into one row each."""
    merged: dict[float, dict[str, float | None]] = {}
    for readings in per_view_readings:
        for r in readings:
            merged.setdefault(r.position_mm, {}).update(r.samples)
    return tuple(
        SampledReading(position_mm=pos, samples=merged[pos])
        for pos in sorted(merged.keys())
    )


def _slug_focal_range(slug: str) -> tuple[int, int] | None:
    """Pull a `(wide, tele)` focal-length pair from a zoom slug.

    Examples:
        `fujifilm-gf-100-200mm-f5-6-r-lm-ois-wr` → (100, 200)
        `fujifilm-xf-150-600mm-f5-6-8-r-lm-ois-wr` → (150, 600)
        `fujifilm-gf-23mm-f4-r-lm-wr` → None (prime)
    """
    # Strip the fujifilm-XX- prefix
    stripped = re.sub(r"^fujifilm-(?:gf|xf|mkx|xc)-", "", slug)
    m = re.match(r"^(\d+)-(\d+)mm", stripped)
    if m is None:
        return None
    return int(m.group(1)), int(m.group(2))


def _slug_prime_focal(slug: str) -> int | None:
    """Pull the focal length from a prime slug (e.g. `gf-23mm-f4-...` → 23)."""
    stripped = re.sub(r"^fujifilm-(?:gf|xf|mkx|xc)-", "", slug)
    m = re.match(r"^(\d+)mm", stripped)
    return int(m.group(1)) if m else None


def _max_aperture_from_slug(slug: str) -> str:
    """Pull the max aperture from a Fujifilm lens slug.

    Slug forms encountered:
        `gf-23mm-f4-r-...`        → integer aperture            → "f/4"
        `gf-100-200mm-f5-6-...`   → decimal aperture            → "f/5.6"
        `xf-150-600mm-f5-6-8-...` → variable-aperture zoom      → "f/5.6"
                                    (wide-end is the published max)
        `xf-50mm-f1-0-r-wr`       → fractional                   → "f/1.0"

    Returns the wide-end max aperture in canonical `f/N` or `f/N.N`
    form. Returns "f/?" on parse failure — surfaces the miss rather
    than silently emitting a wrong number.
    """
    stripped = re.sub(r"^fujifilm-(?:gf|xf|mkx|xc)-", "", slug)
    # Variable-aperture zoom: `-fA-B-C-` → use the wide-end (A.B).
    m = re.search(r"-f(\d+)-(\d+)-(\d+)(?:-|$)", stripped)
    if m:
        return f"f/{m.group(1)}.{m.group(2)}"
    # Decimal aperture: `-fA-B-`.
    m = re.search(r"-f(\d+)-(\d+)(?:-|$)", stripped)
    if m:
        return f"f/{m.group(1)}.{m.group(2)}"
    # Integer aperture: `-fA-` or `-fA$`.
    m = re.search(r"-f(\d+)(?:-|$)", stripped)
    if m:
        return f"f/{m.group(1)}"
    return "f/?"


def _format_chart_block(
    aperture: str,
    focal_length: int | None,
    readings: tuple[SampledReading, ...],
) -> str:
    # Emit every reading where any sample has data, plus position 0
    # unconditionally. The mtf-readings data-integrity test asserts the
    # first reading is at position 0 (the optical center) — if the
    # extractor returned None for every sample at center the row would
    # otherwise be dropped by `_has_any_data` and the next non-empty
    # row would be first. We keep position 0 as a null-valued row in
    # that case; renderers honor the nulls (B2: never fabricate).
    rendered: list[str] = []
    for r in readings:
        if _has_any_data(r) or r.position_mm == 0.0:
            rendered.append(_format_reading(r))
    rows = "\n".join(rendered)
    focal_line = (
        f"        focalLength: {focal_length},\n"
        if focal_length is not None
        else ""
    )
    # ADR-053 + #1134: Fujifilm Tier 2 charts ship as HIGH — they are
    # hand-curated from official manufacturer optical-design charts and
    # don't run through the autotriage gate. The HIGH literal here is
    # the explicit operator verdict for that provenance path.
    return (
        "      {\n"
        f'        aperture: "{aperture}",\n'
        f"{focal_line}"
        '        confidence: "HIGH",\n'
        "        readings: [\n"
        f"{rows}\n"
        "        ],\n"
        "      },"
    )


_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def _to_slug(brand_model: str) -> str:
    """Port of src/utils/slug.ts:toSlug — must stay byte-equivalent.

    "Fujifilm GF 23mm f/4 R LM WR" → "fujifilm-gf-23mm-f4-r-lm-wr"
    """
    lowered = brand_model.lower().replace("/", "")
    return _NON_ALNUM_RE.sub("-", lowered).strip("-")


def _load_official_urls() -> dict[str, str]:
    """Parse `src/data/lenses.ts` into a slug → officialUrl mapping.

    Lenses without an officialUrl field are omitted; the caller decides
    what to do (we fail loud in `_source_url` rather than emit a 404).
    """
    text = LENSES_PATH.read_text(encoding="utf-8")
    mapping: dict[str, str] = {}
    for block_match in _LENS_BLOCK_RE.finditer(text):
        block = block_match.group(0)
        brand_match = _BRAND_RE.search(block)
        model_match = _MODEL_RE.search(block)
        url_match = _OFFICIAL_URL_RE.search(block)
        if not (brand_match and model_match and url_match):
            continue
        slug = _to_slug(f"{brand_match.group(1)} {model_match.group(1)}")
        mapping[slug] = url_match.group(1)
    return mapping


def _source_url(slug: str, official_urls: dict[str, str]) -> str:
    """Return the verified Fujifilm product URL for `slug`.

    Reads from `lenses.ts`'s `officialUrl` field rather than deriving
    from the slug — Fujifilm's URL pattern uses a region segment
    (`/en-us/`) and hyphenated suffixes that simple slug-mangling
    cannot reconstruct. See issue #1062.
    """
    if slug not in official_urls:
        raise KeyError(
            f"No officialUrl found in lenses.ts for {slug!r}. Add the "
            f"field to the lens entry before re-running this script."
        )
    return official_urls[slug]


def _emit_one_lens(
    chart: ReferenceChart, official_urls: dict[str, str]
) -> tuple[str, int, int]:
    """Build the TS object literal for one Fuji lens.

    Returns (literal, panel_count, total_positions). Lenses with zoom
    views (wide + tele) produce two MtfChart panels with the appropriate
    focal lengths; prime lenses produce one panel.
    """
    aperture = chart.apertures[0]
    if aperture == "max":
        # Tier 2 ReferenceChart entries carry "max" as a placeholder;
        # derive the actual max aperture from the slug for the TS data.
        aperture = _max_aperture_from_slug(chart.slug)

    # Group views by panel (wide/tele/None) then collect per-view readings.
    by_panel: dict[str | None, list[tuple[str, tuple[SampledReading, ...]]]] = (
        defaultdict(list)
    )
    for view in chart.views:
        image_path = REPO_ROOT / view.chart_path
        panel = _view_panel_key(image_path)
        readings = _extract_view_readings(chart, view, REPO_ROOT)
        by_panel[panel].append((view.chart_path, readings))

    blocks: list[str] = []
    total_positions = 0

    has_wide_tele = "wide" in by_panel or "tele" in by_panel

    if has_wide_tele:
        # Zoom — wide and tele panels. If bare-named views also exist
        # for the same lens, Fujifilm published them as a (likely
        # mid-focal) summary; the wide/tele files carry the
        # per-focal-length data we want, so the bare-named views are
        # dropped from the emitted panels to avoid a misleading
        # third unlabelled chart.
        focal_pair = _slug_focal_range(chart.slug)
        wide_focal = focal_pair[0] if focal_pair else None
        tele_focal = focal_pair[1] if focal_pair else None
        for panel_key, focal in (("wide", wide_focal), ("tele", tele_focal)):
            if panel_key not in by_panel:
                continue
            merged = _merge_readings(
                [readings for _, readings in by_panel[panel_key]]
            )
            blocks.append(_format_chart_block(aperture, focal, merged))
            total_positions += len(merged)
    elif None in by_panel:
        # Prime — one chart, all per-frequency views merged.
        merged = _merge_readings(
            [readings for _, readings in by_panel[None]]
        )
        blocks.append(_format_chart_block(aperture, None, merged))
        total_positions += len(merged)

    chart_blocks = "\n".join(blocks)
    source_url = _source_url(chart.slug, official_urls)
    literal = (
        f'  "{chart.slug}": {{\n'
        f"{format_source_line(source_url)}"
        '    mtfType: "computed",\n'
        "    charts: [\n"
        f"{chart_blocks}\n"
        "    ],\n"
        "  },"
    )
    return literal, len(blocks), total_positions


def _fuji_lenses() -> list[ReferenceChart]:
    """Every Fujifilm-permfreq chart — both Tier 1 anchors and Tier 2 bulk.

    The script originally only walked the Tier 2 cohort (`ground_truth is
    None`) but the rendered lens-detail page needs MTF data for every
    Fuji lens, anchors included. The anchors run through the same
    extractor — their published GT is for calibration scoring, not for
    emission. See issue #1061.
    """
    return [c for c in REFERENCE_CHARTS if c.style_family == "fujifilm-permfreq"]


# --- mtf-readings.ts patching ---------------------------------------------


_ENTRY_OPEN_RE = re.compile(r'^\s*"(?P<slug>[^"]+)":\s*\{\s*$')
_ENTRY_CLOSE_RE = re.compile(r"^\s*\},\s*$")


def _splice_entries(source: str, new_entries: dict[str, str]) -> str:
    """Insert/replace entries in `mtf-readings.ts` while preserving order.

    Walks the file line by line; when it encounters a top-level entry
    whose slug is in `new_entries`, replaces it with the new literal.
    Slugs in `new_entries` not yet present get appended just before the
    closing `};` of the `mtfReadings` record (i.e. at the end of the
    record, before the export line).
    """
    lines = source.splitlines(keepends=True)
    out: list[str] = []
    replaced: set[str] = set()

    i = 0
    n = len(lines)
    inside_record = False
    while i < n:
        line = lines[i]
        if not inside_record:
            out.append(line)
            if "const mtfReadings" in line:
                inside_record = True
            i += 1
            continue

        m = _ENTRY_OPEN_RE.match(line)
        if m and m.group("slug") in new_entries:
            slug = m.group("slug")
            # Skip to the entry's closing line at the same indent level.
            brace_depth = 0
            while i < n:
                cur = lines[i]
                brace_depth += cur.count("{") - cur.count("}")
                i += 1
                if brace_depth <= 0:
                    break
            # Emit the replacement literal.
            out.append(new_entries[slug] + "\n")
            replaced.add(slug)
            continue

        # Detect the closing `};` of the record itself.
        if line.startswith("};"):
            # Append any new entries before the record closes.
            for slug, literal in new_entries.items():
                if slug not in replaced:
                    out.append(literal + "\n")
                    replaced.add(slug)
            out.append(line)
            inside_record = False
            i += 1
            continue

        out.append(line)
        i += 1

    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--write",
        action="store_true",
        help="Patch src/data/mtf-readings.ts with the emitted entries. "
        "Without this flag the literals print to stdout for review.",
    )
    mode.add_argument(
        "--check",
        action="store_true",
        help="Render entries in memory and compare against the committed "
        "src/data/mtf-readings.ts. Exit non-zero with a unified diff if "
        "any entry drifts from the current extractor output (#1296).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit emission to the first N lenses (smoke-test).",
    )
    args = parser.parse_args(argv)

    lenses = _fuji_lenses()
    if args.limit is not None:
        lenses = lenses[: args.limit]
    if not lenses:
        print("No Fujifilm Tier 2 lenses found.", file=sys.stderr)
        return 1

    official_urls = _load_official_urls()
    entries: dict[str, str] = {}
    total_positions = 0
    total_panels = 0
    for chart in lenses:
        literal, panels, positions = _emit_one_lens(chart, official_urls)
        entries[chart.slug] = literal
        total_panels += panels
        total_positions += positions
        print(
            f"emitted {chart.slug}: {panels} panel(s), "
            f"{positions} position(s)",
            file=sys.stderr,
        )

    if args.write:
        source = MTF_READINGS_PATH.read_text(encoding="utf-8")
        patched = _splice_entries(source, entries)
        MTF_READINGS_PATH.write_text(patched, encoding="utf-8", newline="\n")
        print(
            f"\npatched {MTF_READINGS_PATH.relative_to(REPO_ROOT)}: "
            f"{len(entries)} entries, {total_panels} panels, "
            f"{total_positions} positions.",
            file=sys.stderr,
        )
    elif args.check:
        from mtfdigitizer.scripts._emit_check import report_drift  # noqa: PLC0415

        source = MTF_READINGS_PATH.read_text(encoding="utf-8")
        patched = _splice_entries(source, entries)
        return report_drift(
            MTF_READINGS_PATH,
            source,
            patched,
            label="Fujifilm tier 2",
        )
    else:
        print("\n".join(entries.values()))
        print(
            f"\n# Preview only — pass --write to patch "
            f"{MTF_READINGS_PATH.relative_to(REPO_ROOT)}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
