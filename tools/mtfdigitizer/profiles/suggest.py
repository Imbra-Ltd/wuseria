"""Profile auto-suggest + resolve (#934, ADR-038 §1).

`suggest_profile` is advisory: it inspects an image and proposes the
best-matching declared profile, but the caller decides what to do with
the proposal.

`resolve` is the entry point the extractor calls. It enforces the
fail-loud contract:

    declared    suggest          outcome
    --------    ----------       ------------------------------
    given       matches          use declared
    given       mismatches       raise ProfileMismatch (B1 gate)
    None        unique match     use suggested
    None        no match         raise ProfileMismatch

A declared profile is *never* silently switched, even when the
auto-suggest disagrees — that is the entire point of the B1 fail-loud
gate (PR #931 / ADR-038 §1).
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import cv2
import numpy as np

from ..loader import load_chart_hsv
from .declared import DECLARED_PROFILES
from .types import HueRange, MtfProfile, ProfileMatch, ProfileMismatch


# A hue counts as "present" when at least this fraction of the image
# matches its HSV box. Chosen empirically: a chart curve typically
# occupies 0.1-2% of the image; 0.05% rejects single-pixel noise without
# missing thin curves.
_HUE_PRESENCE_FRACTION = 0.0005

# A profile is suggested only when its match score is at least this high
# AND beats the next-best profile by this margin. Two profiles with very
# similar scores (e.g. 0.83 vs 0.80) is a sign of ambiguity — refuse,
# don't guess.
_SUGGEST_MIN_SCORE = 0.60
_SUGGEST_MIN_MARGIN = 0.20


# `_load_hsv` was inlined here; now delegated to the shared loader so
# alpha-aware loading is consistent across the package (see loader.py).
_load_hsv = load_chart_hsv


def _hue_pixel_count(hsv: np.ndarray, hue: HueRange) -> int:
    """How many pixels in the image fall within this HueRange's HSV box."""
    h, s, v = cv2.split(hsv)
    mask = (
        (h >= hue.h_lo)
        & (h <= hue.h_hi)
        & (s >= hue.s_min)
        & (s <= hue.s_max)
        & (v >= hue.v_min)
        & (v <= hue.v_max)
    )
    return int(mask.sum())


def _profile_match_score(hsv: np.ndarray, profile: MtfProfile) -> tuple[float, int]:
    """How well a profile matches an image: (score in 0..1, hues found).

    Score = fraction of the profile's *named* hues for which at least
    one declared HueRange produced ≥ `_HUE_PRESENCE_FRACTION` of the
    image. Wrap-around hues (red at both ends of the hue circle) share
    a name and are ORed.
    """
    pixel_count_threshold = int(hsv.shape[0] * hsv.shape[1] * _HUE_PRESENCE_FRACTION)
    hits_per_name: dict[str, int] = {}
    for hue in profile.hues:
        hits_per_name[hue.name] = hits_per_name.get(hue.name, 0) + _hue_pixel_count(hsv, hue)
    names_found = sum(1 for count in hits_per_name.values() if count >= pixel_count_threshold)
    total_names = len(hits_per_name)
    score = names_found / total_names if total_names > 0 else 0.0
    return score, names_found


def suggest_profile(
    image_path: str | Path,
    candidates: Sequence[MtfProfile] = DECLARED_PROFILES,
) -> ProfileMatch:
    """Inspect an image and propose the best-matching profile.

    Advisory only — the caller decides whether to use the suggestion.
    Returns a `ProfileMatch` with `profile=None` when no candidate
    cleanly wins.
    """
    hsv = _load_hsv(image_path)
    if not candidates:
        return ProfileMatch(
            profile=None,
            confidence=0.0,
            reason="no candidate profiles supplied",
            detected_hue_peaks=0,
        )

    scored = [(profile, *_profile_match_score(hsv, profile)) for profile in candidates]
    scored.sort(key=lambda item: item[1], reverse=True)
    best, best_score, best_hues = scored[0]
    second_score = scored[1][1] if len(scored) > 1 else 0.0

    if best_score < _SUGGEST_MIN_SCORE:
        return ProfileMatch(
            profile=None,
            confidence=best_score,
            reason=(
                f"best candidate {best.name!r} scored {best_score:.2f} "
                f"(found {best_hues}/{best.hue_count} declared hues); "
                f"below {_SUGGEST_MIN_SCORE:.2f} threshold"
            ),
            detected_hue_peaks=best_hues,
        )

    if best_score - second_score < _SUGGEST_MIN_MARGIN:
        runner_up = scored[1][0].name
        return ProfileMatch(
            profile=None,
            confidence=best_score,
            reason=(
                f"ambiguous: {best.name!r} ({best_score:.2f}) and "
                f"{runner_up!r} ({second_score:.2f}) are within "
                f"{_SUGGEST_MIN_MARGIN:.2f} of each other"
            ),
            detected_hue_peaks=best_hues,
        )

    return ProfileMatch(
        profile=best,
        confidence=best_score,
        reason=f"matched {best_hues}/{best.hue_count} declared hues",
        detected_hue_peaks=best_hues,
    )


def resolve(
    image_path: str | Path,
    declared: MtfProfile | None = None,
    candidates: Sequence[MtfProfile] = DECLARED_PROFILES,
) -> MtfProfile:
    """Resolve the profile for an image. Raises ProfileMismatch on conflict.

    See module docstring for the full truth table. The fail-loud
    contract: a declared profile is never silently switched, and an
    image that matches no candidate is refused rather than guessed.
    """
    suggestion = suggest_profile(image_path, candidates=candidates)

    if declared is not None:
        if suggestion.profile is None:
            raise ProfileMismatch(
                f"declared profile {declared.name!r} disagrees with image: "
                f"auto-suggest could not match any profile ({suggestion.reason})"
            )
        if suggestion.profile.name != declared.name:
            raise ProfileMismatch(
                f"declared profile {declared.name!r} disagrees with image: "
                f"auto-suggest proposed {suggestion.profile.name!r} "
                f"(confidence {suggestion.confidence:.2f}). "
                f"Never silently switch — review the chart or re-declare."
            )
        return declared

    if suggestion.profile is None:
        raise ProfileMismatch(
            f"no declared profile and auto-suggest cannot match image: {suggestion.reason}"
        )
    return suggestion.profile
