"""Emit TTartisan Tier 2 MTF readings as TS literals for `mtf-readings.ts`.

Walks the 19 TTartisan ReferenceChart entries (style family
`ttartisan-4color-dual-aperture`) and produces one `MtfData` literal
per lens. Each chart packs two apertures by color encoding (ADR-044),
so every emitted literal carries **two** `MtfChart` panels — one per
aperture pass — with the actual f-numbers (read from
`chart.apertures[i]`, NOT the orchestrator's `"max"`/`"stopped"` labels).

This is the bridge from "extracted to disk" (the production
digitization-log.md artifacts) to "visible on the lens detail page"
(src/data/mtf-readings.ts).

Usage::

    cd tools
    py -m mtfdigitizer.scripts.emit_ttartisan_tier2          # preview to stdout
    py -m mtfdigitizer.scripts.emit_ttartisan_tier2 --write   # patch mtf-readings.ts

Without `--write` the literals print to stdout for review. With it, the
script splices each entry into `src/data/mtf-readings.ts` using the
same shape as `emit_fuji_tier2._splice_entries`.

`source` URL comes from each lens's `officialUrl` field in
`src/data/lenses.ts` — never re-derived from the slug (per #1062 the
TTartisan brand URL pattern is not slug-mangle-recoverable).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from mtfdigitizer.autotriage import _run_pipeline
from mtfdigitizer.pipeline.types import SampledReading
from mtfdigitizer.referenceset.charts import REFERENCE_CHARTS, ReferenceChart


REPO_ROOT = Path(__file__).resolve().parents[3]
MTF_READINGS_PATH = REPO_ROOT / "src" / "data" / "mtf-readings.ts"
LENSES_PATH = REPO_ROOT / "src" / "data" / "lenses.ts"


# Match a single top-level lens entry: from `^  {` to the matching `^  },`.
_LENS_BLOCK_RE = re.compile(r"^  \{$.*?^  \},?$", re.DOTALL | re.MULTILINE)
_BRAND_RE = re.compile(r'^\s*brand:\s*"([^"]+)"', re.MULTILINE)
_MODEL_RE = re.compile(r'^\s*model:\s*"([^"]+)"', re.MULTILINE)
_OFFICIAL_URL_RE = re.compile(
    r'^\s*officialUrl:\s*(?:\n\s*)?"([^"]+)"', re.MULTILINE
)


def _format_value(v: float | None) -> str:
    if v is None:
        return "null"
    rounded = round(v, 2)
    text = f"{rounded:.2f}".rstrip("0").rstrip(".")
    return text or "0"


def _format_reading(r: SampledReading) -> str:
    inner_lines: list[str] = []
    # Frequencies in the reading's sample keys: freq10S/M, freq30S/M, ...
    freqs: set[int] = set()
    for field in r.samples:
        m = re.match(r"freq(\d+)[SM]$", field)
        if m:
            freqs.add(int(m.group(1)))
    for freq in sorted(freqs):
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


def _has_any_data(r: SampledReading) -> bool:
    return any(v is not None for v in r.samples.values())


def _format_chart_block(
    aperture: str,
    readings: tuple[SampledReading, ...],
    confidence: str,
    confidence_reason: str | None,
) -> str:
    """Emit one MtfChart panel — aperture string + readings array.

    Mirrors the prime-shape emit in `emit_fuji_tier2._format_chart_block`
    but without focalLength (TTartisan does not publish per-focal-length
    charts; even the 500mm super-tele ships one chart per lens). Carries
    the per-pass confidence verdict + reason code (ADR-053 + #1134).
    """
    rendered: list[str] = []
    for r in readings:
        if _has_any_data(r) or r.position_mm == 0.0:
            rendered.append(_format_reading(r))
    rows = "\n".join(rendered)
    reason_line = (
        f'        confidenceReason: "{confidence_reason}",\n'
        if confidence == "LOW" and confidence_reason
        else ""
    )
    return (
        "      {\n"
        f'        aperture: "{aperture}",\n'
        f'        confidence: "{confidence}",\n'
        f"{reason_line}"
        "        readings: [\n"
        f"{rows}\n"
        "        ],\n"
        "      },"
    )


_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def _to_slug(brand_model: str) -> str:
    """Port of src/utils/slug.ts:toSlug — must stay byte-equivalent."""
    lowered = brand_model.lower().replace("/", "")
    return _NON_ALNUM_RE.sub("-", lowered).strip("-")


def _load_official_urls() -> dict[str, str]:
    """Parse `src/data/lenses.ts` into a slug → officialUrl mapping."""
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
    """Return the verified TTartisan product URL for `slug`.

    Reads from `lenses.ts`'s `officialUrl` field rather than deriving
    from the slug — TTartisan's URL pattern is not slug-mangle-
    recoverable (different paths for AF / Tilt / GFX product lines).
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
    """Build the TS object literal for one TTartisan lens.

    Returns ``(literal, panel_count, total_positions)``. Every TTartisan
    chart produces exactly two panels — one per aperture in the
    profile's `apertures_per_chart`. The aperture in each panel is the
    actual f-number (from `chart.apertures[i]`), aligned positionally
    with the profile's aperture labels.

    Confidence (ADR-053 + #1134): each panel runs through the
    `autotriage._run_pipeline` gate (ADR-052) and emits
    `confidence: HIGH|LOW` plus, when LOW, the first reason code from
    `verdict.reasons`. The pipeline is the single source of truth for
    both autotriage's CLI and emit's verdict — they always agree.
    """
    blocks: list[str] = []
    total_positions = 0

    # Profile aperture labels and chart.apertures positions must align —
    # the scaffolder enforces this; assert here to catch any later drift.
    from mtfdigitizer.family_profile import profile_for_chart  # noqa: PLC0415

    profile = profile_for_chart(chart)
    assert profile.apertures_per_chart is not None
    assert len(profile.apertures_per_chart) == len(chart.apertures), (
        f"{chart.slug}: profile.apertures_per_chart "
        f"({profile.apertures_per_chart!r}) length != "
        f"chart.apertures ({chart.apertures!r}) length"
    )

    pass_results = _run_pipeline(chart)
    by_aperture = {pr.verdict.pass_key: pr for pr in pass_results}

    for label, f_number in zip(profile.apertures_per_chart, chart.apertures):
        pass_result = by_aperture[label]
        verdict = pass_result.verdict
        if verdict.verdict == "HIGH":
            confidence = "HIGH"
            reason: str | None = None
        else:
            confidence = "LOW"
            reason = (
                verdict.reasons[0].value if verdict.reasons else "unknown"
            )
        blocks.append(
            _format_chart_block(
                f_number,
                pass_result.extracted.readings,
                confidence,
                reason,
            )
        )
        total_positions += len(pass_result.extracted.readings)

    chart_blocks = "\n".join(blocks)
    literal = (
        f'  "{chart.slug}": {{\n'
        f'    source: "{_source_url(chart.slug, official_urls)}",\n'
        '    mtfType: "computed",\n'
        "    charts: [\n"
        f"{chart_blocks}\n"
        "    ],\n"
        "  },"
    )
    return literal, len(blocks), total_positions


def _ttartisan_lenses() -> list[ReferenceChart]:
    """Every TTartisan multi-aperture chart in the reference set."""
    return [
        c for c in REFERENCE_CHARTS
        if c.style_family == "ttartisan-4color-dual-aperture"
    ]


# --- mtf-readings.ts patching ---------------------------------------------
# Direct port of emit_fuji_tier2._splice_entries — single-source-of-truth
# patching keyed by lens slug. Existing entries are replaced in place;
# new entries are appended just before the record's closing `};`.

_ENTRY_OPEN_RE = re.compile(r'^\s*"(?P<slug>[^"]+)":\s*\{\s*$')


def _splice_entries(source: str, new_entries: dict[str, str]) -> str:
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
            brace_depth = 0
            while i < n:
                cur = lines[i]
                brace_depth += cur.count("{") - cur.count("}")
                i += 1
                if brace_depth <= 0:
                    break
            out.append(new_entries[slug] + "\n")
            replaced.add(slug)
            continue

        if line.startswith("};"):
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
    parser.add_argument(
        "--write",
        action="store_true",
        help="Patch src/data/mtf-readings.ts with the emitted entries. "
        "Without this flag the literals print to stdout for review.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit emission to the first N lenses (smoke-test).",
    )
    args = parser.parse_args(argv)

    lenses = _ttartisan_lenses()
    if args.limit is not None:
        lenses = lenses[: args.limit]
    if not lenses:
        print("No TTartisan multi-aperture lenses found.", file=sys.stderr)
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
