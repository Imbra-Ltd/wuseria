"""model_to_slug tests — parametrized across all 11 brand prefixes.

The example for each brand mirrors the docstring/behavior of that brand's
original common.py model_to_slug, proving the shared implementation is a
faithful replacement.
"""

import pytest

from brandkit import model_to_slug


@pytest.mark.parametrize(
    "prefix,model,expected",
    [
        ("tokina", "atx-m 23mm f/1.4 X", "tokina-atx-m-23mm-f1-4-x"),
        ("sigma", "30mm f/1.4 DC DN | C", "sigma-30mm-f1-4-dc-dn-c"),
        ("samyang", "14mm f/2.8 ED AS IF UMC", "samyang-14mm-f2-8-ed-as-if-umc"),
        ("tamron", "11-20mm f/2.8 Di III-A RXD", "tamron-11-20mm-f2-8-di-iii-a-rxd"),
        ("ttartisan", "35mm f/1.4", "ttartisan-35mm-f1-4"),
        ("viltrox", "AF 27mm f/1.2 Pro", "viltrox-af-27mm-f1-2-pro"),
        ("voigtlander", "Ultron 27mm f/2.0", "voigtlander-ultron-27mm-f2-0"),
        ("venus-laowa", "9mm f/2.8 Zero-D", "venus-laowa-9mm-f2-8-zero-d"),
        ("zeiss", "Touit 32mm f/1.8", "zeiss-touit-32mm-f1-8"),
        ("mitakon", "Speedmaster 35mm f/0.95 Mark II", "mitakon-speedmaster-35mm-f0-95-mark-ii"),
        ("fujifilm", "XF 35mm f/1.4 R", "fujifilm-xf-35mm-f1-4-r"),
    ],
)
def test_model_to_slug(prefix, model, expected):
    assert model_to_slug(prefix, model) == expected


def test_trailing_and_leading_separators_stripped():
    assert model_to_slug("x", "  weird / name  ") == "x-weird-name"


def test_collapses_runs_of_non_alnum():
    assert model_to_slug("x", "a---b___c") == "x-a-b-c"
