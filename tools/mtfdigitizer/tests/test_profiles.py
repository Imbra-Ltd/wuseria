"""Tests for the MTF profile abstraction (#934, ADR-038 §1).

Acceptance criteria from issue #934:

- Profile type + per-brand declarations for the existing styles (Sigma,
  Samyang to start)
- Auto-suggest proposes a profile; never silently overrides a declared one
- Unknown/mismatched profile is refused, not guessed (B1 preserved)
- Tests cover declared, auto-suggested, and refused cases

Each acceptance line maps to a section below.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mtfdigitizer.profiles import (
    DECLARED_PROFILES,
    HueRange,
    MtfProfile,
    ProfileMatch,
    ProfileMismatch,
    SAMYANG_4COLOR_ALL_SOLID,
    SEVENARTISANS_2COLOR_SAMECOLOR_DASHED,
    SIGMA_2COLOR_SOLID_DASHED,
    TOKINA_2COLOR_FREQUENCY,
    VILTROX_BW_DASHED_F12,
    resolve,
    suggest_profile,
)
from mtfdigitizer.referenceset import REFERENCE_CHARTS


REPO_ROOT = Path(__file__).resolve().parents[3]


def _ref_chart_path(slug: str) -> Path:
    """Resolve a reference chart's absolute path by lens slug."""
    for chart in REFERENCE_CHARTS:
        if chart.slug == slug:
            return REPO_ROOT / chart.chart_path
    raise KeyError(f"no reference chart for slug {slug!r}")


SIGMA_56_CHART = lambda: _ref_chart_path("sigma-56mm-f1-4-dc-dn-c")
SAMYANG_85_CHART = lambda: _ref_chart_path("samyang-85mm-f1-4-as-if-umc")
SAMYANG_300_CHART = lambda: _ref_chart_path("samyang-300mm-f6-3-ed-umc-cs-reflex")
SEVENARTISANS_50_CHART = lambda: _ref_chart_path("7artisans-50mm-f1-2-mark-ii")
SEVENARTISANS_35_CHART = lambda: _ref_chart_path("7artisans-35mm-f1-2-mark-ii")
TOKINA_23_CHART = lambda: _ref_chart_path("tokina-atx-m-23mm-f1-4-x")
VILTROX_75_CHART = lambda: _ref_chart_path("viltrox-af-75mm-f1-2-pro")
ZEISS_TOUIT_CHART = lambda: _ref_chart_path("zeiss-touit-32mm-f1-8")


# --- Profile type + per-brand declarations ---------------------------------


def test_declared_profiles_cover_in_band_families() -> None:
    """One profile per in-band reference set family (+ the Tokina wide-zoom
    DP variant of the prime profile, + the Fujifilm per-frequency profile
    added in ADR-043, + the TTartisan dual-aperture profile added in
    ADR-044)."""
    names = {p.name for p in DECLARED_PROFILES}
    assert names == {
        "sigma-2color-solid-dashed",
        "samyang-4color-all-solid",
        "7artisans-2color-samecolor-dashed",
        "tokina-2color-frequency",
        "tokina-2color-frequency-geodesic-dp",
        "viltrox-bw-dashed-f1.2",
        "fujifilm-permfreq-2color-solid-dashed",
        "ttartisan-4color-dual-aperture",
    }


def test_profile_names_are_unique() -> None:
    names = [p.name for p in DECLARED_PROFILES]
    assert len(names) == len(set(names))


def test_hue_count_collapses_wraparound() -> None:
    """A profile listing the same hue at both ends of the hue circle
    counts it once (red wraps in HSV)."""
    assert SIGMA_2COLOR_SOLID_DASHED.hue_count == 2  # red + blue, despite 3 HueRange entries


def test_profile_is_frozen() -> None:
    """Profiles are declarative data — never mutated at runtime."""
    with pytest.raises((AttributeError, Exception)):
        SIGMA_2COLOR_SOLID_DASHED.name = "mutated"  # type: ignore[misc]


def test_hue_range_is_frozen() -> None:
    hue = HueRange(name="x", h_lo=0, h_hi=10)
    with pytest.raises((AttributeError, Exception)):
        hue.h_lo = 99  # type: ignore[misc]


def test_multi_aperture_profile_hue_names_carry_prefix() -> None:
    """ADR-044 contract: every HueRange in a multi-aperture profile must
    be name-prefixed with one of the declared apertures plus a hyphen.
    The orchestrator's `_hue_filtered_profile` splits on `f"{aperture}-"`;
    a hue without the prefix is silently dropped on every pass, which
    would leave the extractor with zero hues and fail loud — but only
    at extraction time. Catch the mis-naming at declaration time instead.
    """
    for profile in DECLARED_PROFILES:
        if profile.apertures_per_chart is None:
            continue
        valid_prefixes = tuple(f"{ap}-" for ap in profile.apertures_per_chart)
        for hue in profile.hues:
            assert hue.name.startswith(valid_prefixes), (
                f"profile {profile.name!r} hue {hue.name!r} does not start "
                f"with any of {valid_prefixes!r}; ADR-044 requires every "
                f"hue in a multi-aperture profile to declare its aperture "
                f"via a name prefix"
            )


# --- Auto-suggest: declared style is matched -------------------------------


def test_suggest_matches_sigma_chart_to_sigma_profile() -> None:
    result = suggest_profile(SIGMA_56_CHART())
    assert result.profile is not None
    assert result.profile.name == "sigma-2color-solid-dashed"
    assert result.confidence >= 0.99


def test_suggest_matches_samyang_chart_to_samyang_profile() -> None:
    result = suggest_profile(SAMYANG_85_CHART())
    assert result.profile is not None
    assert result.profile.name == "samyang-4color-all-solid"
    assert result.confidence >= 0.99


def test_suggest_returns_profile_match_with_reason() -> None:
    """Every result has a human-readable reason for debugging."""
    result = suggest_profile(SIGMA_56_CHART())
    assert isinstance(result, ProfileMatch)
    assert result.reason  # non-empty


# --- Auto-suggest: refused cases ------------------------------------------


def test_suggest_matches_7artisans_chart_to_7artisans_profile() -> None:
    result = suggest_profile(SEVENARTISANS_50_CHART())
    assert result.profile is not None
    assert result.profile.name == "7artisans-2color-samecolor-dashed"


def test_tokina_is_not_auto_suggestable() -> None:
    """Tokina's red+blue palette overlaps Sigma's; the presence-based
    suggest scorer cannot disambiguate them, so Tokina is opted out
    of auto-suggest and must be explicitly declared."""
    assert TOKINA_2COLOR_FREQUENCY.auto_suggestable is False
    # The chart still resolves correctly when Tokina is declared.
    result = resolve(TOKINA_23_CHART(), declared=TOKINA_2COLOR_FREQUENCY)
    assert result is TOKINA_2COLOR_FREQUENCY


def test_viltrox_is_not_auto_suggestable() -> None:
    """Viltrox's neutral hue range matches every chart with text or
    gridlines, so it would poison suggest disambiguation. It must be
    explicitly declared; suggest never returns it."""
    assert VILTROX_BW_DASHED_F12.auto_suggestable is False
    result = suggest_profile(VILTROX_75_CHART())
    # Auto-suggest can't pick Viltrox; either it returns None (no other
    # profile fits the B&W chart's lack of saturated hues) or an
    # unrelated false match. The contract: never Viltrox.
    if result.profile is not None:
        assert result.profile.name != "viltrox-bw-dashed-f1.2"
    # Explicit declaration still works.
    declared = resolve(VILTROX_75_CHART(), declared=VILTROX_BW_DASHED_F12)
    assert declared is VILTROX_BW_DASHED_F12


def test_suggest_refuses_multi_color_promo() -> None:
    """The 7Artisans 35 promo plot has 8+ curve colors. Every declared
    profile matches *some* of them, so the ambiguity guard must refuse."""
    result = suggest_profile(SEVENARTISANS_35_CHART())
    assert result.profile is None


def test_suggest_refuses_zeiss_press_kit() -> None:
    """Zeiss is B&W with 3 frequencies; no declared profile fits."""
    result = suggest_profile(ZEISS_TOUIT_CHART())
    assert result.profile is None


def test_suggest_with_empty_candidates_refuses() -> None:
    result = suggest_profile(SIGMA_56_CHART(), candidates=())
    assert result.profile is None
    assert "no candidate" in result.reason


# --- resolve(): use declared when image agrees ----------------------------


def test_resolve_uses_declared_when_image_agrees() -> None:
    """Image matches declared profile — happy path, return declared."""
    result = resolve(SIGMA_56_CHART(), declared=SIGMA_2COLOR_SOLID_DASHED)
    assert result is SIGMA_2COLOR_SOLID_DASHED


# --- resolve(): B1 fail-loud on declared/image mismatch -------------------


def test_resolve_refuses_when_declared_disagrees_with_image() -> None:
    """ADR-038 §1: never silently switch a declared profile.

    Declaring Sigma on a Samyang chart must raise — this is the entire
    point of the B1 fail-loud gate.
    """
    with pytest.raises(ProfileMismatch) as exc:
        resolve(SAMYANG_85_CHART(), declared=SIGMA_2COLOR_SOLID_DASHED)
    assert "sigma-2color-solid-dashed" in str(exc.value)
    assert "samyang-4color-all-solid" in str(exc.value)


def test_resolve_refuses_when_declared_and_image_unmatchable() -> None:
    """Declared profile but image matches nothing — also a mismatch."""
    with pytest.raises(ProfileMismatch):
        resolve(ZEISS_TOUIT_CHART(), declared=SIGMA_2COLOR_SOLID_DASHED)


# --- resolve(): use auto-suggest when nothing declared -------------------


def test_resolve_falls_back_to_suggest_when_undeclared() -> None:
    """No declared profile, image cleanly matches one — return suggested."""
    result = resolve(SAMYANG_85_CHART(), declared=None)
    assert result.name == "samyang-4color-all-solid"


# --- resolve(): refuse rather than guess --------------------------------


def test_resolve_refuses_when_nothing_declared_and_no_match() -> None:
    """B1: undeclared + unmatchable = refuse, never guess."""
    with pytest.raises(ProfileMismatch):
        resolve(ZEISS_TOUIT_CHART(), declared=None)


def test_resolve_refuses_when_nothing_declared_and_ambiguous() -> None:
    """B1: undeclared + ambiguous = refuse."""
    with pytest.raises(ProfileMismatch):
        resolve(SEVENARTISANS_35_CHART(), declared=None)


# --- ADR-038 §4 flat-axis blind spot ------------------------------------


def test_idealized_flat_chart_matches_its_dialect_profile() -> None:
    """The 300mm reflex is the flat-axis blind-spot probe case.

    Its style is Samyang's (4 colors, all solid); the profile system
    correctly accepts it. Catching the flatness is the plausibility
    prior's job (#935), not the profile system's — verifying that
    separation here documents the design contract.
    """
    result = resolve(SAMYANG_300_CHART(), declared=SAMYANG_4COLOR_ALL_SOLID)
    assert result is SAMYANG_4COLOR_ALL_SOLID
