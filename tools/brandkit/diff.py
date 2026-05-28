"""Physical-spec cross-validation (#779).

Compares the values stored in lenses.ts against values extracted from the
official product page, and reports mismatches. Born from Session 76, where
swapped weights and wrong magnification values went undetected because no
tool compared stored data against the source.

Comparison is typed (see lenses.PHYSICAL_SPEC_FIELDS):
- numeric: small relative tolerance, so rounding (276 vs 275.8) is not a
  mismatch but real errors (swapped values, wrong by tens) are;
- boolean: exact;
- string: case-insensitive exact.

A field is compared only when present on BOTH sides — a spec the page does
not expose is unknown, not a mismatch. (Stored booleans default to False per
the Lens-type contract; the extractor returns a boolean only when the page
affirmatively confirms it, so unmentioned flags are naturally skipped.)
"""

from dataclasses import dataclass

from .lenses import FIELD_KIND, PhysicalValue

# Relative tolerance for numeric fields; magnification needs a looser
# absolute floor because its values are tiny (e.g. 0.1).
_REL_TOLERANCE = 0.02
_ABS_FLOOR = {"maxMagnification": 0.005}


@dataclass(frozen=True)
class Mismatch:
    field: str
    stored: PhysicalValue
    extracted: PhysicalValue

    def __str__(self) -> str:
        return f"{self.field}: stored={self.stored} page={self.extracted}"


def _is_number(value: object) -> bool:
    """True for real numeric values. bool is excluded (it is an int subclass
    but never a valid numeric spec value)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _numbers_agree(field: str, stored: float, extracted: float) -> bool:
    if stored == extracted:
        return True
    abs_floor = _ABS_FLOOR.get(field, 0.0)
    if abs(stored - extracted) <= abs_floor:
        return True
    scale = max(abs(stored), abs(extracted))
    if scale == 0:
        return True
    return abs(stored - extracted) / scale <= _REL_TOLERANCE


def _agree(field: str, stored: PhysicalValue, extracted: PhysicalValue) -> bool:
    """Compare one field's values according to its kind. Unknown/ill-typed
    pairs are treated as agreeing (not a mismatch)."""
    kind = FIELD_KIND.get(field, "numeric")
    if kind == "boolean":
        if not isinstance(stored, bool) or not isinstance(extracted, bool):
            return True
        return stored == extracted
    if kind == "string":
        if not isinstance(stored, str) or not isinstance(extracted, str):
            return True
        return stored.strip().lower() == extracted.strip().lower()
    # numeric
    if not _is_number(stored) or not _is_number(extracted):
        return True
    return _numbers_agree(field, stored, extracted)


def diff_physical(
    stored: dict[str, PhysicalValue], extracted: dict[str, PhysicalValue]
) -> list[Mismatch]:
    """Return a mismatch for each field present in BOTH dicts whose values
    disagree. A field absent from either side is skipped (unknown)."""
    mismatches: list[Mismatch] = []
    for field, extracted_value in extracted.items():
        if field not in stored:
            continue
        if not _agree(field, stored[field], extracted_value):
            mismatches.append(Mismatch(field, stored[field], extracted_value))
    return mismatches
