"""Rename MTF files from numeric to named suffixes (#1017, ADR-033).

ADR-033 names canonical MTF charts by chart type and (for zooms) focal
length: `-mtf-diffraction.png`, `-mtf-geometric.png`,
`-mtf-diffraction-wide.png`, and so on. Numeric suffixes (`-mtf-1`,
`-mtf-2`) carry no semantic information and are a transitional scheme
from before the convention landed.

This module produces a deterministic rename plan from the labels the
maintainer has already written in each `analysis.md` MTF charts list,
then applies it.

Input grammar (per ADR-033 "Existing folders"):

    MTF charts:

    - [<slug>-mtf-1.png](<slug>-mtf-1.png) -- diffraction MTF
    - [<slug>-mtf-2.png](<slug>-mtf-2.png) -- geometrical MTF

The script:

1. Walks every folder under `docs/optical-specs/` (or the one named on
   the command line).
2. Reads `analysis.md` and parses the MTF charts list above.
3. Maps each numeric file to its canonical name based on the label
   (`diffraction MTF` → `-mtf-diffraction.png`, etc.).
4. Includes sidecars in the plan: each `.png` carries its `.svg`,
   `-overlay.png`, and `-review.html` companions to the new stem.
5. Updates the `analysis.md` link list to point at the renamed files.
6. Rewrites `chart_path=...` string literals in
   `tools/mtfdigitizer/referenceset/charts.py` so the registry tracks
   the new paths.

Commands:

    py -m mtfdigitizer.rename --dry-run         # print plan, no writes
    py -m mtfdigitizer.rename --apply           # execute the plan
    py -m mtfdigitizer.rename <slug> --dry-run  # one folder
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
OPTICAL_SPECS = REPO_ROOT / "docs" / "optical-specs"
CHARTS_PY = REPO_ROOT / "tools" / "mtfdigitizer" / "referenceset" / "charts.py"


# Label → canonical suffix. Only labels that map deterministically to
# ADR-033 named suffixes are accepted. Anything else fails loud so the
# maintainer fixes the label rather than the script guessing.
LABEL_SUFFIX: dict[str, str] = {
    "diffraction mtf": "diffraction",
    "geometrical mtf": "geometric",
    "geometric mtf": "geometric",
}


# Focal-length parenthetical → filename suffix segment. Zooms encode
# the focal length in the label as "(wide)", "(tele)", or "(NNmm)"
# (per ADR-033). The script transcribes this verbatim to the filename.
_FOCAL_NAMED = {"wide", "tele"}
_FOCAL_NUMERIC = re.compile(r"^(\d+)mm$")


# Match a markdown link line in the MTF charts list:
#   - [<text>](<href>) <dash> <label>
# Captures (text, href, label). The separator is the U+2014 em-dash
# used throughout analysis.md, or a double ASCII hyphen as a
# round-trip-friendly alternative. Bare ASCII hyphen is rejected
# because the bullet "- " would match it. The trailing single-chart
# no-qualifier case is handled upstream of this regex.
_DASH = "(?:—|--)"
_LINK_LINE = re.compile(
    "^\\s*-\\s*\\[(?P<text>[^\\]]+)\\]\\((?P<href>[^)]+)\\)\\s*" + _DASH + "\\s*(?P<label>.+?)\\s*$"
)


@dataclass(frozen=True)
class Rename:
    """One file move: old → new, both relative to repo root."""

    old: Path
    new: Path


@dataclass(frozen=True)
class FolderPlan:
    """All renames for one lens folder, plus the analysis.md update."""

    slug: str
    folder: Path
    renames: tuple[Rename, ...]
    analysis_old: str
    analysis_new: str


class RenameError(Exception):
    """The maintainer must fix something before the rename can run."""


def _parse_analysis_md(text: str, slug: str) -> dict[str, str]:
    """Return `{numeric_basename: canonical_label}` for one analysis.md.

    Reads the bullet list under the first "MTF charts:" heading and
    returns one entry per numeric-suffixed file. Files already in
    canonical form (or with unknown labels) are not included — the
    caller fails loud if any old-scheme file on disk is missing from
    the map.
    """
    mapping: dict[str, str] = {}
    in_list = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.lower().startswith("mtf charts:"):
            in_list = True
            continue
        if not in_list:
            continue
        # The list ends at the first blank-after-list line or a new
        # heading. A blank line inside the list (rare) would be
        # ambiguous, so we treat any blank as the list terminator.
        if not line.strip():
            if mapping:
                break
            continue
        if line.lstrip().startswith("#"):
            break
        match = _LINK_LINE.match(line)
        if not match:
            # A bullet that doesn't parse means the convention is broken
            # for this folder — fail loud rather than silently skipping.
            if line.lstrip().startswith("-"):
                raise RenameError(
                    f"{slug}: cannot parse MTF charts line: {line!r}"
                )
            continue
        href = match.group("href").strip()
        label = match.group("label").strip().lower()
        label_head, focal = _split_label(label)
        chart_suffix = LABEL_SUFFIX.get(label_head)
        if chart_suffix is None:
            raise RenameError(
                f"{slug}: unrecognised MTF chart label {label!r} for {href!r}; "
                f"expected one of {sorted(LABEL_SUFFIX)}"
            )
        if focal is None:
            suffix = chart_suffix
        else:
            focal_segment = _focal_to_segment(focal, label, slug, href)
            suffix = f"{chart_suffix}-{focal_segment}" if focal_segment else chart_suffix
        basename = Path(href).name
        mapping[basename] = suffix
    return mapping


def _split_label(label: str) -> tuple[str, str | None]:
    """Split `"diffraction mtf (wide)"` into `("diffraction mtf", "wide")`.

    Returns `(head, None)` when there is no parenthetical. The parenthetical
    is preserved as a focal qualifier and validated by `_focal_to_segment`;
    parentheticals that turn out not to be focal qualifiers (e.g. the
    legacy "(10/30 lp/mm)" frequency annotation on prime charts) are
    handled by the focal validator, which falls back to dropping the
    qualifier for known non-focal annotations.
    """
    head, sep, tail = label.partition("(")
    if not sep:
        return head.strip(), None
    qualifier = tail.rsplit(")", maxsplit=1)[0].strip()
    return head.strip(), qualifier or None


def _focal_to_segment(focal: str, label: str, slug: str, href: str) -> str:
    """Map a focal-length qualifier to its filename segment.

    Accepts `wide`, `tele`, or `NNmm` (numeric, per ADR-033). Rejects
    anything else loud so the maintainer fixes the label. Known
    non-focal parentheticals (frequency annotations like `10/30 lp/mm`)
    are silently treated as no-focal — they are not zoom qualifiers.
    """
    if focal in _FOCAL_NAMED:
        return focal
    numeric = _FOCAL_NUMERIC.match(focal)
    if numeric is not None:
        return f"{numeric.group(1)}mm"
    if _is_non_focal_annotation(focal):
        # The parser cannot distinguish "(10/30 lp/mm)" from a focal
        # qualifier without context. Treat known frequency / spec
        # annotations as no-focal so legacy prime labels keep parsing.
        return ""
    raise RenameError(
        f"{slug}: unrecognised focal-length qualifier {focal!r} in label "
        f"{label!r} for {href!r}; expected wide / tele / NNmm"
    )


def _is_non_focal_annotation(qualifier: str) -> bool:
    """True for parentheticals that annotate frequency, not focal length."""
    return "lp/mm" in qualifier or "/mm" in qualifier


def _sidecars_for(png_path: Path) -> list[Path]:
    """Return existing sidecar files that travel with `png_path`.

    A numeric MTF file may carry up to three siblings derived from its
    stem: `.svg` (vector source), `-overlay.png` (eye-check artifact),
    and `-review.html` (interactive review). All four share the same
    base stem and rename in lockstep.
    """
    stem = png_path.stem  # e.g. "sigma-56mm-...-mtf-1"
    parent = png_path.parent
    candidates = [
        parent / f"{stem}.svg",
        parent / f"{stem}-overlay.png",
        parent / f"{stem}-review.html",
    ]
    return [c for c in candidates if c.exists()]


def _plan_for_folder(folder: Path) -> FolderPlan | None:
    """Build the rename plan for one lens folder.

    Returns None when the folder has no numeric-suffix files to rename
    (already in canonical form, or no MTF charts at all). Raises
    `RenameError` when analysis.md disagrees with what's on disk.
    """
    slug = folder.name
    analysis = folder / "analysis.md"
    if not analysis.exists():
        return None

    numeric_files = sorted(
        p for p in folder.glob(f"{slug}-mtf-*.png") if _is_numeric_stem(p, slug)
    )
    if not numeric_files:
        return None

    text = analysis.read_text(encoding="utf-8")
    label_map = _parse_analysis_md(text, slug)
    if not label_map:
        raise RenameError(
            f"{slug}: numeric MTF files exist on disk but analysis.md has "
            f"no MTF charts list — add the labelled list per ADR-033 first"
        )

    renames: list[Rename] = []
    analysis_replacements: dict[str, str] = {}
    seen_suffixes: dict[str, Path] = {}

    for old_png in numeric_files:
        basename = old_png.name
        suffix = label_map.get(basename)
        if suffix is None:
            raise RenameError(
                f"{slug}: {basename} is on disk but missing from "
                f"analysis.md MTF charts list — add the labelled link first"
            )
        # Collisions inside one folder (two files map to the same suffix)
        # signal a labelling error; otherwise the rename would clobber.
        if suffix in seen_suffixes:
            raise RenameError(
                f"{slug}: {basename} and {seen_suffixes[suffix].name} "
                f"both map to suffix {suffix!r}"
            )
        seen_suffixes[suffix] = old_png

        new_png = old_png.with_name(f"{slug}-mtf-{suffix}.png")
        renames.append(Rename(old=old_png, new=new_png))
        analysis_replacements[basename] = new_png.name

        for sidecar in _sidecars_for(old_png):
            new_sidecar = _renamed_sidecar(sidecar, old_png.stem, new_png.stem)
            renames.append(Rename(old=sidecar, new=new_sidecar))
            analysis_replacements[sidecar.name] = new_sidecar.name

    analysis_new = _rewrite_analysis(text, analysis_replacements)
    return FolderPlan(
        slug=slug,
        folder=folder,
        renames=tuple(renames),
        analysis_old=text,
        analysis_new=analysis_new,
    )


def _is_numeric_stem(path: Path, slug: str) -> bool:
    """True when `path.stem` looks like `<slug>-mtf-<N>` with N integer.

    Filters out `<slug>-mtf-1-overlay.png`, `<slug>-mtf.png` (single
    chart), and `<slug>-mtf-diffraction.png` (already canonical).
    """
    prefix = f"{slug}-mtf-"
    if not path.stem.startswith(prefix):
        return False
    tail = path.stem[len(prefix):]
    return tail.isdigit()


def _renamed_sidecar(sidecar: Path, old_stem: str, new_stem: str) -> Path:
    """Replace the old stem inside the sidecar name with the new stem."""
    return sidecar.with_name(sidecar.name.replace(old_stem, new_stem, 1))


def _rewrite_analysis(text: str, name_map: dict[str, str]) -> str:
    """Replace every `name_map` key in the analysis.md text with its new name.

    Plain string replacement is safe here because the keys are full file
    basenames including the slug prefix — collisions with prose are not
    possible.
    """
    out = text
    for old_name, new_name in name_map.items():
        out = out.replace(old_name, new_name)
    return out


def _update_charts_py(name_map: dict[str, str], apply: bool) -> int:
    """Rewrite `chart_path="..."` literals in referenceset/charts.py.

    `name_map` keys are old basenames; values are new basenames. Returns
    the count of substitutions made. When `apply` is False, leaves the
    file untouched and only reports.
    """
    text = CHARTS_PY.read_text(encoding="utf-8")
    new_text = text
    n_changes = 0
    for old_name, new_name in name_map.items():
        # Only touch lines that look like chart_path="...".
        pattern = re.compile(
            r'(chart_path=")([^"]*?' + re.escape(old_name) + r')(")'
        )
        def _sub(match: re.Match[str]) -> str:
            nonlocal n_changes
            n_changes += 1
            return match.group(1) + match.group(2).replace(old_name, new_name) + match.group(3)
        new_text = pattern.sub(_sub, new_text)
    if apply and new_text != text:
        CHARTS_PY.write_text(new_text, encoding="utf-8")
    return n_changes


def _apply_plan(plan: FolderPlan) -> None:
    """Execute one folder's renames + write the updated analysis.md."""
    for rename in plan.renames:
        if not rename.old.exists():
            raise RenameError(
                f"{plan.slug}: planned to rename {rename.old} but file is gone"
            )
        if rename.new.exists():
            raise RenameError(
                f"{plan.slug}: destination {rename.new} already exists"
            )
    for rename in plan.renames:
        rename.old.rename(rename.new)
    (plan.folder / "analysis.md").write_text(plan.analysis_new, encoding="utf-8")


def _print_plan(plan: FolderPlan) -> None:
    print(f"\n{plan.slug}:")
    for rename in plan.renames:
        old_rel = rename.old.relative_to(REPO_ROOT)
        new_rel = rename.new.relative_to(REPO_ROOT)
        print(f"  {old_rel.as_posix()}")
        print(f"    -> {new_rel.as_posix()}")
    if plan.analysis_old != plan.analysis_new:
        print(f"  analysis.md: updated")


def _collect_plans(slug: str | None) -> list[FolderPlan]:
    """Walk optical-specs and build a plan per matching folder.

    When `slug` is given, only that folder is considered. Otherwise
    every direct subdirectory of `docs/optical-specs/` is walked.
    Folders with no numeric-suffix files (or no analysis.md) are
    silently skipped.
    """
    if slug is not None:
        folders = [OPTICAL_SPECS / slug]
        if not folders[0].is_dir():
            raise RenameError(f"folder not found: docs/optical-specs/{slug}")
    else:
        folders = sorted(p for p in OPTICAL_SPECS.iterdir() if p.is_dir())

    plans: list[FolderPlan] = []
    errors: list[str] = []
    for folder in folders:
        try:
            plan = _plan_for_folder(folder)
        except RenameError as exc:
            errors.append(str(exc))
            continue
        if plan is not None:
            plans.append(plan)
    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        raise RenameError(f"{len(errors)} folder(s) failed validation; nothing applied")
    return plans


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "slug",
        nargs="?",
        help="restrict the rename to one folder under docs/optical-specs/. "
        "Omit to walk every folder.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="print the rename plan and exit. No files are touched.",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help="execute the rename plan: move files, update analysis.md, "
        "rewrite referenceset/charts.py chart_path literals.",
    )
    args = parser.parse_args(argv)

    try:
        plans = _collect_plans(args.slug)
    except RenameError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not plans:
        print("no numeric-suffix MTF files to rename")
        return 0

    for plan in plans:
        _print_plan(plan)

    # Aggregate name map for charts.py (all folders' basenames are unique
    # because each carries the lens slug as prefix).
    name_map: dict[str, str] = {}
    for plan in plans:
        for rename in plan.renames:
            name_map[rename.old.name] = rename.new.name

    if args.dry_run:
        n_charts = _update_charts_py(name_map, apply=False)
        print(f"\nreferenceset/charts.py: {n_charts} chart_path literal(s) would be rewritten")
        print(f"\ndry run: {len(plans)} folder(s), {sum(len(p.renames) for p in plans)} file(s) would move")
        return 0

    for plan in plans:
        try:
            _apply_plan(plan)
        except RenameError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
    n_charts = _update_charts_py(name_map, apply=True)
    print(f"\napplied: {len(plans)} folder(s), {sum(len(p.renames) for p in plans)} file(s) moved, "
          f"{n_charts} chart_path literal(s) rewritten in charts.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
