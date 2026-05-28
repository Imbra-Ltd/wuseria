"""Physical-spec diff tests (#779), including the Session-76 error class."""

from brandkit import diff_physical
from brandkit.diff import Mismatch


def test_identical_specs_no_mismatch():
    stored = {"weight": 276, "filterThread": 52}
    assert diff_physical(stored, stored) == []


def test_swapped_weights_are_caught():
    # Session 76: 23mm and 33mm weights were swapped in lenses.ts.
    stored = {"weight": 285}  # wrong — belongs to the 33mm
    extracted = {"weight": 276}  # the page for the 23mm
    mismatches = diff_physical(stored, extracted)
    assert len(mismatches) == 1
    assert mismatches[0].field == "weight"
    assert mismatches[0].stored == 285
    assert mismatches[0].extracted == 276


def test_small_rounding_difference_within_tolerance():
    # 276 vs 275.8 is < 2% — not a mismatch.
    assert diff_physical({"weight": 276}, {"weight": 275.8}) == []


def test_magnification_absolute_floor():
    # Tiny magnification values: 0.10 vs 0.104 is within the absolute floor.
    assert diff_physical({"maxMagnification": 0.10}, {"maxMagnification": 0.104}) == []


def test_magnification_real_error_is_caught():
    # 0.1 vs 0.2 is a real error (the formula-estimate class #779 warns about).
    mismatches = diff_physical({"maxMagnification": 0.1}, {"maxMagnification": 0.2})
    assert len(mismatches) == 1
    assert mismatches[0].field == "maxMagnification"


def test_fields_missing_from_page_are_skipped():
    # The page does not expose filterThread — that is unknown, not a mismatch.
    stored = {"weight": 276, "filterThread": 52}
    extracted = {"weight": 276}
    assert diff_physical(stored, extracted) == []


def test_fields_missing_from_stored_are_skipped():
    stored = {"weight": 276}
    extracted = {"weight": 276, "apertureBlades": 9}
    assert diff_physical(stored, extracted) == []


def test_multiple_mismatches_reported():
    stored = {"weight": 200, "diameter": 60, "length": 50}
    extracted = {"weight": 276, "diameter": 65, "length": 50}
    fields = {m.field for m in diff_physical(stored, extracted)}
    assert fields == {"weight", "diameter"}


def test_mismatch_str_is_readable():
    assert str(Mismatch("weight", 285, 276)) == "weight: stored=285 page=276"


def test_non_numeric_extracted_value_is_skipped_not_crashed():
    # A future extractor whose regex matched but captured nothing could
    # yield None — must be treated as unknown, never crash.
    assert diff_physical({"weight": 276}, {"weight": None}) == []


def test_non_numeric_stored_value_is_skipped():
    assert diff_physical({"weight": "276g"}, {"weight": 276}) == []


def test_bool_is_not_treated_as_number():
    # apertureBlades is numeric; a stray True must not be diffed as 1.
    assert diff_physical({"apertureBlades": 9}, {"apertureBlades": True}) == []


# --- typed comparison: booleans ---


def test_boolean_match_no_mismatch():
    assert diff_physical({"hasOis": True}, {"hasOis": True}) == []
    assert diff_physical({"isWeatherSealed": False}, {"isWeatherSealed": False}) == []


def test_boolean_mismatch_caught():
    # Stored says weather-sealed; page says it is not.
    m = diff_physical({"isWeatherSealed": True}, {"isWeatherSealed": False})
    assert len(m) == 1
    assert m[0].field == "isWeatherSealed"


def test_boolean_skipped_when_page_silent():
    # The extractor only returns a flag it confirmed; if it omits hasOis, the
    # stored False is not compared (page did not address it).
    assert diff_physical({"hasOis": False}, {}) == []


# --- typed comparison: strings (afMotor) ---


def test_string_match_case_insensitive():
    assert diff_physical({"afMotor": "STM"}, {"afMotor": "stm"}) == []


def test_string_mismatch_caught():
    m = diff_physical({"afMotor": "STM"}, {"afMotor": "LM"})
    assert len(m) == 1
    assert m[0].field == "afMotor"


def test_mixed_field_set_reports_each_kind():
    stored = {"weight": 276, "hasOis": False, "afMotor": "STM"}
    extracted = {"weight": 300, "hasOis": True, "afMotor": "STM"}
    fields = {m.field for m in diff_physical(stored, extracted)}
    # weight off by ~9%, OIS flipped; afMotor agrees.
    assert fields == {"weight", "hasOis"}
