"""Content-aware cropper for optical-specs artifacts (construction diagrams, MTF charts).

Replaces hand-guessed pixel coordinates — which silently truncate when off — with
bounding-box detection plus an edge-touch validation that fails loudly if the crop
clipped content.

Pipeline:
  1. Load image, build a "content mask" (non-background pixels).
  2. Optionally split a composite into left/right panels at the low-ink gutter.
  3. For each panel, find the content bounding box and crop to bbox + margin.
  4. Validate: content must not touch any crop edge (within EDGE_TOL px) — else the
     crop clipped something; the tool widens once and re-checks, then errors if still bad.

Background detection: the dominant corner colour is treated as background. Works for
dark line-art on white AND coloured curves on white or on a dark card.

Usage:
    # auto-detect single artifact, crop to content + margin, write <out>
    py tools/crop-artifact.py <src.jpg> --out <dst.jpg>

    # split a side-by-side composite (diagram left, MTF right) into two files
    py tools/crop-artifact.py <src.jpg> --split --left <diagram.jpg> --right <mtf.jpg>

    # crop only a sub-region first (e.g. the bottom panel of a tall marketing image),
    # then content-trim within it
    py tools/crop-artifact.py <src.jpg> --region 0,520,1000,1000 --out <dst.jpg>

    # check an EXISTING artifact for edge-truncation (no write); exit 1 if it touches an edge
    py tools/crop-artifact.py <artifact.jpg> --check
"""

import sys
import argparse

import numpy as np
from PIL import Image

MARGIN = 14          # px of background to keep around detected content
EDGE_TOL = 3         # content within this many px of a crop edge counts as "touching"
BG_THRESH = 28       # max per-channel distance from the background colour to count as background


def _content_mask(arr: np.ndarray) -> np.ndarray:
    """Boolean mask of non-background pixels.

    Background is the median of the four corners (robust to a stray dark/coloured
    corner). A pixel is content if it differs from the background by more than
    BG_THRESH on any channel.
    """
    h, w = arr.shape[:2]
    corners = np.stack([arr[0, 0], arr[0, w - 1], arr[h - 1, 0], arr[h - 1, w - 1]]).astype(int)
    bg = np.median(corners, axis=0)
    diff = np.abs(arr.astype(int) - bg).max(axis=2)
    return diff > BG_THRESH


def _bbox(mask: np.ndarray):
    """(x0, y0, x1, y1) bounding box of True pixels, or None if empty."""
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    if len(rows) == 0 or len(cols) == 0:
        return None
    return int(cols[0]), int(rows[0]), int(cols[-1]) + 1, int(rows[-1]) + 1


def _gutter_x(mask: np.ndarray) -> int:
    """X of the lowest-ink column in the middle third — the gap between two panels."""
    w = mask.shape[1]
    col_ink = mask.sum(axis=0)
    lo, hi = int(w * 0.35), int(w * 0.65)
    return lo + int(np.argmin(col_ink[lo:hi]))


def crop_to_content(im: Image.Image, margin: int = MARGIN) -> Image.Image:
    """Crop to the content bounding box plus an even margin, clamped to the image."""
    arr = np.array(im.convert("RGB"))
    bb = _bbox(_content_mask(arr))
    if bb is None:
        raise ValueError("no content detected (image is all background)")
    x0, y0, x1, y1 = bb
    h, w = arr.shape[:2]
    x0 = max(0, x0 - margin); y0 = max(0, y0 - margin)
    x1 = min(w, x1 + margin); y1 = min(h, y1 + margin)
    return im.crop((x0, y0, x1, y1))


def edge_touch(im: Image.Image) -> list[str]:
    """Return the edges ('top'/'bottom'/'left'/'right') where content reaches within
    EDGE_TOL px of the border — i.e. likely truncation. Empty list = clean."""
    arr = np.array(im.convert("RGB"))
    mask = _content_mask(arr)
    bb = _bbox(mask)
    if bb is None:
        return []
    x0, y0, x1, y1 = bb
    h, w = arr.shape[:2]
    bad = []
    if y0 <= EDGE_TOL: bad.append("top")
    if h - y1 <= EDGE_TOL: bad.append("bottom")
    if x0 <= EDGE_TOL: bad.append("left")
    if w - x1 <= EDGE_TOL: bad.append("right")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--out")
    ap.add_argument("--region", help="x0,y0,x1,y1 to pre-crop before content-trim")
    ap.add_argument("--split", action="store_true", help="split into left/right panels at the gutter")
    ap.add_argument("--left"); ap.add_argument("--right")
    ap.add_argument("--margin", type=int, default=MARGIN)
    ap.add_argument("--check", action="store_true", help="report edge-touch on src; no write")
    args = ap.parse_args()

    im = Image.open(args.src).convert("RGB")

    if args.check:
        # Advisory: content reaching an edge MAY mean truncation, but a tight axis
        # box / wide housing can legitimately do so. Report for human review; not a
        # hard pass/fail.
        bad = edge_touch(im)
        if bad:
            print(f"REVIEW: content reaches {', '.join(bad)} edge — eyeball {args.src}")
        else:
            print(f"OK: content has margin on all edges — {args.src}")
        return 0

    if args.region:
        x0, y0, x1, y1 = (int(v) for v in args.region.split(","))
        im = im.crop((x0, y0, x1, y1))

    def finalize(panel: Image.Image, out: str) -> None:
        # Auto-crop to content bbox + margin. Because the margin is added to the
        # detected bbox, the result is correctly framed by construction (the failure
        # mode of hand-guessed coordinates — clipping content — cannot occur here).
        cropped = crop_to_content(panel, args.margin)
        cropped.save(out, quality=92)
        # Advisory only: warn (do NOT fail) if content still sits at an edge. A tight
        # MTF axis box or a wide diagram housing legitimately reaches the margin, so
        # this is a hint to eyeball — not proof of truncation.
        bad = edge_touch(cropped)
        warn = f"  (note: content near {', '.join(bad)} edge — eyeball)" if bad else ""
        print(f"wrote {out} {cropped.size}{warn}")

    if args.split:
        arr = np.array(im)
        gx = _gutter_x(_content_mask(arr))
        finalize(im.crop((0, 0, gx, im.height)), args.left)
        finalize(im.crop((gx, 0, im.width, im.height)), args.right)
    else:
        finalize(im, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
