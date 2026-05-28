"""Reader for the me-fuji lens database (src/data/lenses.ts).

This is the one module in brandkit that couples to the me-fuji project
layout — it parses the TypeScript data file. Brand tools depend on it for
the list of lenses to process and (for #779) the stored physical specs to
cross-validate against.

The file is not valid JSON, so it is parsed with targeted regexes over
brand-delimited blocks — the same approach every brand common.py used,
extracted here once.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

# Physical spec fields cross-validated by #779. Each maps to a lenses.ts key.
PHYSICAL_FIELDS = (
    "weight",
    "maxMagnification",
    "minFocusDistance",
    "filterThread",
    "apertureBlades",
    "diameter",
    "length",
)


@dataclass(frozen=True)
class LensEntry:
    """One lens as read from lenses.ts."""

    model: str
    url: str  # officialUrl, after any brand normalization
    physical: dict[str, float] = field(default_factory=dict)


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
    def _physical_from_block(block: str) -> dict[str, float]:
        """Extract the stored physical-spec values present in a block."""
        physical: dict[str, float] = {}
        for key in PHYSICAL_FIELDS:
            m = re.search(rf"\b{key}:\s*([0-9.]+)", block)
            if m:
                value = _parse_number(m.group(1))
                if value is not None:
                    physical[key] = value
        return physical
