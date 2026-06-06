"""MTF chart profile abstraction + advisory auto-suggest (#934, ADR-038 §1).

A *profile* is a declaration of a chart's visual dialect along three axes:

- **Color axis** — how many distinct hues carry curves, and their HSV ranges.
- **Style axis** — within a hue, how to split S/M (`SPLIT_BY_DASH` for solid
  vs dashed, `HUE_IS_CURVE` when each hue already is one curve).
- **Frequency count** — 2 (mainstream 10+30) or 3 (e.g. Zeiss press kit
  10/20/40); declaring 2 refuses 3-frequency charts.

Profiles are *declared*. An advisory auto-suggest inspects an image and
proposes one, but never silently overrides a declared profile — when a
declared profile and the image disagree, that is a fail-loud event
(generalizing PR #931's B1 gate).

Public surface:

- `MtfProfile`, `HueRange`, `StyleAxis`, `HueMeaning`
- `ProfileMatch` — auto-suggest result
- `ProfileMismatch` — raised by `resolve()` on disagreement or no match
- `suggest_profile(image, candidates) -> ProfileMatch`
- `resolve(image, declared, candidates) -> MtfProfile`
- `SIGMA_2COLOR_SOLID_DASHED`, `SAMYANG_4COLOR_ALL_SOLID`,
  `SEVENARTISANS_2COLOR_SAMECOLOR_DASHED`, `TOKINA_2COLOR_FREQUENCY`,
  `TOKINA_2COLOR_FREQUENCY_CC_RANK`, `VILTROX_BW_DASHED_F12` — declared
  profiles
- `DECLARED_PROFILES` — tuple of all currently-declared profiles
"""

from .types import (
    HueMeaning,
    HueRange,
    MtfProfile,
    ProfileMatch,
    ProfileMismatch,
    StyleAxis,
)
from .declared import (
    DECLARED_PROFILES,
    FUJIFILM_PERMFREQ_2COLOR_SOLID_DASHED,
    SAMYANG_4COLOR_ALL_SOLID,
    SEVENARTISANS_2COLOR_SAMECOLOR_DASHED,
    SIGMA_2COLOR_SOLID_DASHED,
    TOKINA_2COLOR_FREQUENCY,
    TOKINA_2COLOR_FREQUENCY_CC_RANK,
    VILTROX_BW_DASHED_F12,
)
from .suggest import resolve, suggest_profile

__all__ = [
    "DECLARED_PROFILES",
    "FUJIFILM_PERMFREQ_2COLOR_SOLID_DASHED",
    "HueMeaning",
    "HueRange",
    "MtfProfile",
    "ProfileMatch",
    "ProfileMismatch",
    "SAMYANG_4COLOR_ALL_SOLID",
    "SEVENARTISANS_2COLOR_SAMECOLOR_DASHED",
    "SIGMA_2COLOR_SOLID_DASHED",
    "StyleAxis",
    "TOKINA_2COLOR_FREQUENCY",
    "TOKINA_2COLOR_FREQUENCY_CC_RANK",
    "VILTROX_BW_DASHED_F12",
    "resolve",
    "suggest_profile",
]
