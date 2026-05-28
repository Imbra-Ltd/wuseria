"""Helpers for the per-lens optical-specs folders (docs/optical-specs/<slug>/).

Every brand checked for MTF charts and construction diagrams the same way
(glob `<slug>-mtf*` / `<slug>-construction*`) and built the same destination
paths for downloaded images. That logic lives here once.
"""

from pathlib import Path

_IMAGE_SUFFIXES = (".png", ".jpg", ".webp", ".svg")


def _has_image(specs_root: Path, slug: str, kind: str) -> bool:
    specs_dir = specs_root / slug
    if not specs_dir.is_dir():
        return False
    return any(
        f.suffix.lower() in _IMAGE_SUFFIXES
        for f in specs_dir.glob(f"{slug}-{kind}*")
    )


def has_mtf_chart(specs_root: Path, slug: str) -> bool:
    """True if an MTF chart image exists in the lens's specs folder."""
    return _has_image(specs_root, slug, "mtf")


def has_construction_image(specs_root: Path, slug: str) -> bool:
    """True if a construction diagram exists in the lens's specs folder."""
    return _has_image(specs_root, slug, "construction")


def image_dest(
    specs_root: Path, slug: str, kind: str, ext: str, index: int | None = None
) -> Path:
    """Destination path for a downloaded image.

    kind is "mtf" or "construction"; index disambiguates multiple charts
    (e.g. zoom lenses with several MTF charts). ext includes the leading dot.
    """
    suffix = f"-{kind}-{index}" if index is not None else f"-{kind}"
    return specs_root / slug / f"{slug}{suffix}{ext}"


def detect_ext(url: str) -> str:
    """Pick a file extension from an image URL (defaults to .jpg)."""
    lowered = url.lower()
    for ext in (".png", ".webp", ".svg"):
        if ext in lowered:
            return ext
    return ".jpg"
