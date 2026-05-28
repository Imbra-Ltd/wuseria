"""Reader for the me-fuji lens database (src/data/lenses.ts).

This is the one module in brandkit that couples to the me-fuji project
layout — it parses the TypeScript data file. Brand tools depend on it for
the list of lenses to process and (for #779) the stored physical specs to
cross-validate against.

The file is not valid JSON, so it is parsed with targeted regexes over
brand-delimited blocks — the same approach every brand common.py used,
extracted here once.

"Physical specs" here means fields a manufacturer publishes and we can
verify against their page — dimensions, core optical specs, build flags,
AF motor, and tilt-shift geometry. It deliberately excludes our scored
OQ/MTF measurements, price, and genre data.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Literal

FieldKind = Literal["numeric", "boolean", "string"]

# Every page-verifiable physical spec, with its lenses.ts key and value kind.
# Booleans follow the Lens-type contract "absent = false".
PHYSICAL_SPEC_FIELDS: tuple[tuple[str, FieldKind], ...] = (
    # dimensions
    ("weight", "numeric"),
    ("diameter", "numeric"),
    ("length", "numeric"),
    ("filterThread", "numeric"),
    ("apertureBlades", "numeric"),
    ("maxMagnification", "numeric"),
    ("minFocusDistance", "numeric"),
    # core optical specs
    ("focalLengthMin", "numeric"),
    ("focalLengthMax", "numeric"),
    ("maxAperture", "numeric"),
    # build flags (absent = false)
    ("hasOis", "boolean"),
    ("isWeatherSealed", "boolean"),
    ("hasApertureRing", "boolean"),
    ("isApertureClickless", "boolean"),
    ("hasFocusRing", "boolean"),
    ("isFocusByWire", "boolean"),
    ("hasDistanceScale", "boolean"),
    ("hasCircularAperture", "boolean"),
    ("hasTripodMount", "boolean"),
    ("hasRotatingFront", "boolean"),
    # autofocus
    ("afMotor", "string"),
    # tilt-shift geometry
    ("isTiltShift", "boolean"),
    ("shiftRange", "numeric"),
    ("tiltAngle", "numeric"),
    ("imageCircle", "numeric"),
)

# Kind lookup by key, for the diff layer.
FIELD_KIND: dict[str, FieldKind] = {key: kind for key, kind in PHYSICAL_SPEC_FIELDS}

# Booleans that the data omits when false — used to fill "absent = false".
_BOOLEAN_KEYS = tuple(key for key, kind in PHYSICAL_SPEC_FIELDS if kind == "boolean")

# Backwards-compatible alias: the original numeric-only field set (#779 v1).
PHYSICAL_FIELDS = tuple(
    key for key, kind in PHYSICAL_SPEC_FIELDS if kind == "numeric"
)

PhysicalValue = float | bool | str


@dataclass(frozen=True)
class LensEntry:
    """One lens as read from lenses.ts."""

    model: str
    url: str  # officialUrl, after any brand normalization
    physical: dict[str, PhysicalValue] = field(default_factory=dict)


def _split_brand_blocks(content: str) -> list[str]:
    """Split lenses.ts into per-lens blocks (each begins with `brand:`).

    Tolerates `//` comment lines between the opening brace and the brand
    field — some entries carry a leading comment, and the naive split would
    merge them into the previous block and drop the lens."""
    return re.split(r"(?=\{\s*\n\s*(?://[^\n]*\n\s*)*brand:)", content)


def _parse_number(raw: str) -> float | None:
    try:
        return float(raw)
    except ValueError:
        return None


class LensesFile:
    """Parsed view of lenses.ts, queried per brand."""

    def __init__(self, path: Path):
        self._path = path
        self._content = path.read_text(encoding="utf-8")

    @property
    def path(self) -> Path:
        return self._path

    def entries_for(
        self, brand: str, normalize_url: Callable[[str], str] | None = None
    ) -> list[LensEntry]:
        """Return every lens for a brand that has both a model and an
        officialUrl. normalize_url, if given, massages each URL (e.g.
        Tokina hyphen-to-underscore)."""
        normalize = normalize_url or (lambda u: u)
        entries: list[LensEntry] = []
        for block in _split_brand_blocks(self._content):
            if f'brand: "{brand}"' not in block:
                continue
            model_m = re.search(r'model:\s*"([^"]+)"', block)
            url_m = re.search(r'officialUrl:\s*\n?\s*"([^"]+)"', block)
            if model_m and url_m:
                entries.append(
                    LensEntry(
                        model=model_m.group(1),
                        url=normalize(url_m.group(1)),
                        physical=self._physical_from_block(block),
                    )
                )
        return entries

    @staticmethod
    def _physical_from_block(block: str) -> dict[str, PhysicalValue]:
        """Extract every stored physical spec present in a block, typed.

        Booleans absent from the block default to False (the Lens-type
        contract: absent boolean = false). Numerics and strings that are
        absent stay absent (unknown, not a value)."""
        physical: dict[str, PhysicalValue] = {}
        for key, kind in PHYSICAL_SPEC_FIELDS:
            if kind == "numeric":
                m = re.search(rf"\b{key}:\s*([0-9.]+)", block)
                if m:
                    value = _parse_number(m.group(1))
                    if value is not None:
                        physical[key] = value
            elif kind == "string":
                m = re.search(rf'\b{key}:\s*"([^"]+)"', block)
                if m:
                    physical[key] = m.group(1)
            else:  # boolean
                m = re.search(rf"\b{key}:\s*(true|false)\b", block)
                if m:
                    physical[key] = m.group(1) == "true"
        # Fill absent booleans as False per the type contract.
        for key in _BOOLEAN_KEYS:
            physical.setdefault(key, False)
        return physical
