"""Physical-spec cross-validation (#779).

Compares the values stored in lenses.ts against values extracted from the
official product page, and reports mismatches. Born from Session 76, where
swapped weights and wrong magnification values went undetected because no
tool compared stored data against the source.

Numeric comparison uses a small relative tolerance so that rounding
differences (e.g. a weight stored as 276 vs a page that says 275.8) do not
register as mismatches, while genuine errors (swapped values, wrong by tens
of grams) do.
"""

from dataclasses import dataclass

# Relative tolerance for numeric fields; magnification needs a looser
# absolute floor because its values are tiny (e.g. 0.1).
_REL_TOLERANCE = 0.02
_ABS_FLOOR = {"maxMagnification": 0.005}


@dataclass(frozen=True)
class Mismatch:
    field: str
    stored: float
    extracted: float

    def __str__(self) -> str:
        return f"{self.field}: stored={self.stored} page={self.extracted}"


def _is_number(value: object) -> bool:
    """True for real numeric values. bool is excluded (it is an int subclass
    but never a valid spec value)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _values_agree(field: str, stored: float, extracted: float) -> bool:
    if stored == extracted:
        return True
    abs_floor = _ABS_FLOOR.get(field, 0.0)
    if abs(stored - extracted) <= abs_floor:
        return True
    scale = max(abs(stored), abs(extracted))
    if scale == 0:
        return True
    return abs(stored - extracted) / scale <= _REL_TOLERANCE


def diff_physical(
    stored: dict[str, float], extracted: dict[str, float]
) -> list[Mismatch]:
    """Return a mismatch for each field present in BOTH dicts whose values
    disagree beyond tolerance. Fields missing from either side are skipped —
    a value the page does not expose is not a mismatch, it is unknown.
    Non-numeric values on either side are skipped too: a field an extractor
    could not parse into a number is unknown, not a mismatch."""
    mismatches: list[Mismatch] = []
    for field, extracted_value in extracted.items():
        stored_value = stored.get(field)
        if not _is_number(stored_value) or not _is_number(extracted_value):
            continue
        if not _values_agree(field, stored_value, extracted_value):
            mismatches.append(Mismatch(field, stored_value, extracted_value))
    return mismatches
