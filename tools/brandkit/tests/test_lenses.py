"""LensesFile tests against the sample lenses.ts fixture."""

from brandkit import LensesFile


def test_entries_for_brand_filters_and_requires_url(lenses_sample_path):
    lf = LensesFile(lenses_sample_path)
    tokina = lf.entries_for("Tokina")
    models = [e.model for e in tokina]
    # Two Tokina lenses have URLs; the third (no officialUrl) is excluded.
    assert models == ["atx-m 23mm f/1.4 X", "atx-m 33mm f/1.4 X"]


def test_multiline_official_url_is_parsed(lenses_sample_path):
    lf = LensesFile(lenses_sample_path)
    entries = {e.model: e for e in lf.entries_for("Tokina")}
    assert (
        entries["atx-m 33mm f/1.4 X"].url
        == "https://tokinalens.com/product/atx-m-33mm-f1-4-x/"
    )


def test_normalize_url_hook_is_applied(lenses_sample_path):
    lf = LensesFile(lenses_sample_path)
    entries = lf.entries_for("Tokina", normalize_url=lambda u: u.replace("-", "_"))
    assert "atx_m_23mm" in entries[0].url


def test_physical_fields_extracted(lenses_sample_path):
    lf = LensesFile(lenses_sample_path)
    entry = lf.entries_for("Tokina")[0]
    assert entry.physical["weight"] == 276
    assert entry.physical["diameter"] == 65
    assert entry.physical["filterThread"] == 52
    assert entry.physical["maxMagnification"] == 0.1
    assert entry.physical["apertureBlades"] == 9
    assert entry.physical["minFocusDistance"] == 300


def test_missing_physical_fields_omitted(lenses_sample_path):
    lf = LensesFile(lenses_sample_path)
    # The 33mm entry only declares weight.
    entry = lf.entries_for("Tokina")[1]
    assert entry.physical == {"weight": 285.0}


def test_other_brand_isolated(lenses_sample_path):
    lf = LensesFile(lenses_sample_path)
    sigma = lf.entries_for("Sigma")
    assert len(sigma) == 1
    assert sigma[0].model == "30mm f/1.4 DC DN | C"


def test_unknown_brand_returns_empty(lenses_sample_path):
    assert LensesFile(lenses_sample_path).entries_for("Nikon") == []
