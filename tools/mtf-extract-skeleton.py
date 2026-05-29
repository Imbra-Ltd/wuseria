"""Skeletonization-based MTF curve extraction (spike #727).

Pipeline:
  1. Color isolation — extract each curve by color into a binary mask
  2. Skeletonization — reduce each curve to a 1px-wide skeleton
  3. Connected components — classify solid vs dashed by fragment width
  4. Y readout — read curve values at grid positions

Samyang: 4 distinct colors, no S/M ambiguity — dilate + skeletonize + read.
Sigma: 2 colors (red/blue), solid/dashed share color — skeletonize without
       dilation, then connected components classify S vs M by fragment width.

Usage:
    py tools/mtf-extract-skeleton.py docs/mtf-charts/samyang-35mm-f1-2.png
    py tools/mtf-extract-skeleton.py docs/mtf-charts/sigma-56mm-f1-4-dc-dn-c.png
    py tools/mtf-extract-skeleton.py --compare docs/mtf-charts/samyang-35mm-f1-2.png
"""

import sys
import glob
import os
import re
import cv2
import numpy as np
from PIL import Image
from skimage.morphology import skeletonize


# ---------------------------------------------------------------------------
# Chart type detection
# ---------------------------------------------------------------------------

# Minimum fraction of image pixels a signature color must cover before we
# trust a family classification. Size-relative so the same thresholds hold
# regardless of chart resolution (a cropped or high-DPI chart shifts absolute
# counts but not the fraction). Tuned against the reference Sigma/Samyang
# charts, whose signature colors cover well above these floors.
SIGMA_BLUE_MIN_FRACTION = 1.5e-4   # ~100px in a 600x900 chart
SAMYANG_PINK_MIN_FRACTION = 7.5e-5  # ~50px in a 600x900 chart


def detect_chart_type(img):
    """Detect the MTF chart family: 'sigma' (red/blue) or 'samyang' (4-color).

    Returns 'unknown' when neither family's signature colors are present in
    sufficient quantity. Callers MUST handle 'unknown' explicitly — this tool
    only knows how to trace Sigma and Samyang charts, and running any other
    brand through the wrong color masks produces silent garbage rather than an
    error (the masks match almost nothing and the curves read as zeros). Other
    brands must teach the tool their chart family before they can be traced.

    Uses numpy for a fast full-image scan — the curves may be concentrated in
    a small vertical band that sparse sampling misses. Thresholds are fractions
    of total pixels so they hold across chart resolutions.
    """
    arr = np.array(img)
    r, g, b = arr[:, :, 0].astype(int), arr[:, :, 1].astype(int), arr[:, :, 2].astype(int)
    total = arr.shape[0] * arr.shape[1]

    blue_fraction = float(np.sum((b > 160) & (r < 130) & ((b - r) > 60))) / total
    pink_fraction = float(np.sum(
        (r > 180) & (g > 80) & (b > 80) &
        ((r - g) > 30) & ((r - b) > 20) & (g < 190)
    )) / total

    if blue_fraction > SIGMA_BLUE_MIN_FRACTION:
        return "sigma"
    if pink_fraction > SAMYANG_PINK_MIN_FRACTION:
        return "samyang"
    return "unknown"


# ---------------------------------------------------------------------------
# Image loading
# ---------------------------------------------------------------------------

def load_on_white(path):
    img = Image.open(path)
    if img.mode == "P":
        img = img.convert("RGBA")
    bg = Image.new("RGB", img.size, (255, 255, 255))
    if img.mode == "RGBA":
        bg.paste(img, mask=img.split()[3])
    else:
        bg.paste(img)
    return bg


def img_to_array(img):
    return np.array(img)


# ---------------------------------------------------------------------------
# Color masks — Samyang (4 distinct colors)
# ---------------------------------------------------------------------------

def samyang_mask_dark_red(arr):
    """10 lp/mm Sagittal — saturated dark red (~197,1,51)."""
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    return (r > 160) & (g < 100) & (b < 120) & ((r.astype(int) - g.astype(int)) > 70)


def samyang_mask_pink(arr):
    """10 lp/mm Meridional — lighter pink (~225,127,152)."""
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    return ((r > 180) & (g > 80) & (b > 80) &
            ((r.astype(int) - g.astype(int)) > 30) &
            ((r.astype(int) - b.astype(int)) > 20) &
            (g < 190))


def samyang_mask_dark_gray(arr):
    """30 lp/mm Sagittal — dark gray (~102)."""
    r, g, b = arr[:, :, 0].astype(int), arr[:, :, 1].astype(int), arr[:, :, 2].astype(int)
    avg = (r + g + b) / 3
    spread = np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b)
    not_red = ~samyang_mask_dark_red(arr)
    not_pink = ~samyang_mask_pink(arr)
    return (avg >= 85) & (avg <= 120) & (spread < 20) & not_red & not_pink


def samyang_mask_light_gray(arr):
    """30 lp/mm Meridional — medium gray (~178)."""
    r, g, b = arr[:, :, 0].astype(int), arr[:, :, 1].astype(int), arr[:, :, 2].astype(int)
    avg = (r + g + b) / 3
    spread = np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b)
    not_red = ~samyang_mask_dark_red(arr)
    not_pink = ~samyang_mask_pink(arr)
    return (avg >= 160) & (avg <= 195) & (spread < 20) & not_red & not_pink


# ---------------------------------------------------------------------------
# Color masks — Sigma (red and blue, solid + dashed share color)
# ---------------------------------------------------------------------------

def sigma_mask_red(arr):
    """10 lp/mm (both S and M) — red."""
    r, g, b = arr[:, :, 0].astype(int), arr[:, :, 1].astype(int), arr[:, :, 2].astype(int)
    return (r > 160) & (g < 130) & (b < 120) & ((r - g) > 50)


def sigma_mask_blue(arr):
    """30 lp/mm (both S and M) — blue."""
    r, g, b = arr[:, :, 0].astype(int), arr[:, :, 1].astype(int), arr[:, :, 2].astype(int)
    return (b > 160) & (r < 130) & ((b - r) > 60)


# ---------------------------------------------------------------------------
# Axis and grid detection (reused from existing tools)
# ---------------------------------------------------------------------------

def is_any_dark(r, g, b):
    return r < 240 and g < 240 and b < 240


def find_axis_and_plot(img, y_min, y_max):
    w = img.size[0]
    p = img.load()

    best_x, best_count = 0, 0
    for x in range(w // 4):
        count = sum(1 for y in range(y_min, y_max) if is_any_dark(*p[x, y]))
        if count > best_count:
            best_count = count
            best_x = x

    runs = []
    in_run = False
    start = 0
    for y in range(y_min, y_max):
        if is_any_dark(*p[best_x, y]):
            if not in_run:
                in_run = True
                start = y
        else:
            if in_run:
                in_run = False
                runs.append((start, y - 1))
    if in_run:
        runs.append((start, y_max - 1))

    runs.sort(key=lambda r: -(r[1] - r[0]))
    if not runs:
        return best_x, y_min, y_max
    y_top, y_bot = runs[0]
    return best_x, y_top, y_bot


def find_vertical_grids(img, ax_x, y_top, y_bot):
    w = img.size[0]
    p = img.load()

    def is_grid(r, g, b):
        return r < 250 and g < 250 and b < 250

    col_density = []
    for x in range(ax_x, w):
        count = sum(1 for y in range(y_top, y_bot, 3) if is_grid(*p[x, y]))
        col_density.append((x, count))

    if not col_density:
        return []

    max_density = max(d[1] for d in col_density)
    threshold = max_density * 0.12

    peaks = []
    in_peak = False
    peak_data = []
    for x, count in col_density:
        if count > threshold:
            if not in_peak:
                in_peak = True
                peak_data = []
            peak_data.append((x, count))
        else:
            if in_peak:
                in_peak = False
                total_w = sum(c for _, c in peak_data)
                centroid = sum(x * c for x, c in peak_data) / total_w
                peaks.append((int(centroid), max(c for _, c in peak_data)))
    if in_peak:
        total_w = sum(c for _, c in peak_data)
        centroid = sum(x * c for x, c in peak_data) / total_w
        peaks.append((int(centroid), max(c for _, c in peak_data)))

    filtered = []
    for px, density in peaks:
        if filtered and px - filtered[-1][0] < 40:
            if density > filtered[-1][1]:
                filtered[-1] = (px, density)
        else:
            filtered.append((px, density))

    grid_xs = [px for px, _ in filtered]

    if len(grid_xs) >= 3:
        spacings = [grid_xs[i + 1] - grid_xs[i] for i in range(len(grid_xs) - 1)]
        avg = sum(spacings[:-1]) / len(spacings[:-1]) if len(spacings) > 1 else spacings[0]
        if len(spacings) > 1 and abs(spacings[-1] - avg) > avg * 0.3:
            grid_xs = grid_xs[:-1]

    return grid_xs


def find_plot_split(img):
    """Find the y-coordinate that splits two stacked plots (Samyang)."""
    w, h = img.size
    p = img.load()

    x_lo = w // 4
    x_hi = 3 * w // 4
    row_density = []
    for y in range(h):
        count = 0
        for x in range(x_lo, x_hi, 2):
            r, g, b = p[x, y]
            if r < 250 or g < 250 or b < 250:
                count += 1
        row_density.append(count)

    mid_start = h // 4
    mid_end = 3 * h // 4

    best_gap_start = mid_start
    best_gap_len = 0
    gap_start = None

    for y in range(mid_start, mid_end):
        if row_density[y] < 3:
            if gap_start is None:
                gap_start = y
        else:
            if gap_start is not None:
                gap_len = y - gap_start
                if gap_len > best_gap_len:
                    best_gap_len = gap_len
                    best_gap_start = gap_start
                gap_start = None
    if gap_start is not None:
        gap_len = mid_end - gap_start
        if gap_len > best_gap_len:
            best_gap_len = gap_len
            best_gap_start = gap_start

    return best_gap_start + best_gap_len // 2


def detect_grid_step(grid_xs):
    """Auto-detect grid step in mm (Samyang: 2/3/5mm)."""
    n = len(grid_xs)
    if n < 2:
        return 2.0
    avg_spacing = (grid_xs[-1] - grid_xs[0]) / (n - 1)
    if avg_spacing >= 93:
        return 5.0
    elif avg_spacing >= 73:
        return 3.0
    else:
        return 2.0


def detect_sigma_grid_step(grid_xs):
    """Auto-detect grid step for Sigma charts.

    Sigma uses two formats:
    - APS-C: 6 grids, 2.5mm step, 0-12.5mm range (~470px between grids)
    - Full-frame: 5 grids, 5mm step, 0-20mm range (~615px between grids)

    Pixel spacing threshold: 500px separates the two formats reliably.
    """
    n = len(grid_xs)
    if n < 2:
        return 2.5
    avg_spacing = (grid_xs[-1] - grid_xs[0]) / (n - 1)
    if avg_spacing > 500:
        return 5.0
    return 2.5


# ---------------------------------------------------------------------------
# Core: skeletonize a binary mask and extract y-values
# ---------------------------------------------------------------------------

def dilate_mask(mask, iterations=1):
    """Dilate binary mask to connect anti-aliased fragments."""
    from scipy.ndimage import binary_dilation
    struct = np.ones((3, 3), dtype=bool)
    return binary_dilation(mask, structure=struct, iterations=iterations)


def skeleton_to_curve(skeleton, x_start, x_end, y_top, y_bot):
    """Extract y-value at each x from a skeletonized binary image.

    For each x column, find skeleton pixels in the plot region and return
    their centroid. When multiple disconnected skeleton branches exist at
    the same x (e.g. from dashed lines), cluster them and return all branches.

    Returns dict: x -> list of y centroids (one per branch).
    """
    x_to_branches = {}
    for x in range(max(0, x_start), min(skeleton.shape[1], x_end + 1)):
        ys = np.where(skeleton[y_top:y_bot + 1, x])[0] + y_top
        if len(ys) == 0:
            continue

        # Cluster y values into branches (gap > 3px = separate branch)
        branches = []
        current = [ys[0]]
        for y in ys[1:]:
            if y - current[-1] <= 3:
                current.append(y)
            else:
                branches.append(current)
                current = [y]
        branches.append(current)

        centroids = [sum(b) / len(b) for b in branches]
        x_to_branches[x] = centroids

    return x_to_branches


def pick_continuous_curve(branches_map, x_positions, y_top, y_bot):
    """From a branches map (x -> [y1, y2, ...]), pick the single continuous curve.

    Uses left-to-right continuity: at each x, pick the branch closest to
    the previous y value. This resolves multi-branch ambiguity from dashed
    lines or noise.
    """
    x_to_y = {}
    prev_y = None

    # Process all x values in order
    all_xs = sorted(branches_map.keys())
    for x in all_xs:
        centroids = branches_map[x]
        if prev_y is not None:
            best = min(centroids, key=lambda c: abs(c - prev_y))
        else:
            best = min(centroids)  # topmost = highest MTF
        x_to_y[x] = best
        prev_y = best

    return x_to_y


def split_solid_dashed_cc(skeleton_uint8, y_top, y_bot, x_start, label=""):
    """Split a skeleton into solid (S) and dashed (M) curves using connected components.

    After skeletonization WITHOUT dilation, solid lines remain as one or a few
    large connected components spanning most of the x-axis. Dashed lines break
    into many small fragments. cv2.connectedComponentsWithStats classifies them
    by bounding box width.

    Returns (solid_curve, dashed_curve) as x -> y dicts.
    """
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        skeleton_uint8, connectivity=8
    )

    if num_labels <= 1:
        return {}, None

    # Collect component info (skip background label 0)
    components = []
    for i in range(1, num_labels):
        width = stats[i, cv2.CC_STAT_WIDTH]
        area = stats[i, cv2.CC_STAT_AREA]
        x_min = stats[i, cv2.CC_STAT_LEFT]
        y_min_c = stats[i, cv2.CC_STAT_TOP]
        components.append({
            "label": i, "width": width, "area": area,
            "x_min": x_min, "y_min": y_min_c,
        })

    # Find the widest component — this anchors our threshold
    max_width = max(c["width"] for c in components)

    # Solid components span a large fraction of the plot width.
    # Dashed fragments are narrow. Threshold: 15% of the widest component.
    width_threshold = max(max_width * 0.15, 30)

    solid_components = [c for c in components if c["width"] > width_threshold]
    dashed_components = [c for c in components if c["width"] <= width_threshold]

    solid_area = sum(c["area"] for c in solid_components)
    dashed_area = sum(c["area"] for c in dashed_components)

    if label:
        print(f"    {label}: {len(solid_components)} solid components "
              f"({solid_area}px), {len(dashed_components)} dashed fragments "
              f"({dashed_area}px), threshold={width_threshold:.0f}px")

    def components_to_curve(comp_list):
        """Pool component pixels into an x -> y mapping.

        Every component in comp_list belongs to the same logical curve (the
        caller splits solid from dashed before calling), so at each x we take
        the unweighted mean of all skeleton pixels there — that is the line's
        own thickness, correctly centroided.

        We must NOT cap or pairwise-average across a 5px window the way the
        old code did (B3). Its `(curve[x] + y) / 2` running average was
        order-dependent (the result depended on pixel iteration order, not the
        true centroid), and its `< 5` guard silently dropped any pixel more
        than 5px from the first one seen at that x — discarding real data on
        steep segments. Pooling all pixels and taking their unweighted mean is
        order-independent and keeps every pixel of the curve.
        """
        ys_by_x = {}
        for c in comp_list:
            component_mask = (labels == c["label"])
            ys, xs = np.where(component_mask)
            for x, y in zip(xs, ys):
                if y_top <= y <= y_bot and x >= x_start:
                    ys_by_x.setdefault(int(x), []).append(float(y))
        return {x: sum(vals) / len(vals) for x, vals in ys_by_x.items()}

    solid_curve = components_to_curve(solid_components)
    dashed_curve = components_to_curve(dashed_components) if dashed_components else None

    return solid_curve, dashed_curve


# ---------------------------------------------------------------------------
# Interpolate curve values at grid positions
# ---------------------------------------------------------------------------

# Largest x-gap (px) between two detected curve points across which we trust a
# linear interpolation. Beyond this the curve has no nearby data and we report
# the position as missing rather than guessing — see MAX_EXACT_MATCH_PX.
MAX_INTERP_GAP_PX = 100
# An x within this distance of a detected point is treated as that point.
MAX_EXACT_MATCH_PX = 3


def interpolate_at(curve_map, target_x, y_top, y_bot):
    """Get MTF value at target_x from a curve map (x -> y).

    Returns the MTF value (0-1), or None when the curve has no usable data at
    target_x. A point is usable only if it is within MAX_EXACT_MATCH_PX of
    target_x, or target_x falls between two detected points no more than
    MAX_INTERP_GAP_PX apart. We deliberately do NOT fall back to the nearest
    detected point when bracketing fails (B2): that reports a neighbor's
    reading as if measured at target_x, fabricating data exactly where the
    curve is occluded or runs off the plot. Missing reads are filled honestly
    downstream (occlusion fill, M=S at center) — a fabricated read is not.
    """
    if not curve_map:
        return None

    xs = sorted(curve_map.keys())
    if not xs:
        return None

    def to_mtf(y):
        return round(1.0 - (y - y_top) / (y_bot - y_top), 4)

    # Exact or very close match
    for x in xs:
        if abs(x - target_x) <= MAX_EXACT_MATCH_PX:
            return to_mtf(curve_map[x])

    # Find bracketing points
    left_x = None
    right_x = None
    for x in xs:
        if x <= target_x:
            left_x = x
        if x >= target_x and right_x is None:
            right_x = x

    # Interpolate only when target_x is bracketed by points close enough to
    # trust a straight line between them.
    if left_x is not None and right_x is not None:
        gap = right_x - left_x
        if gap <= MAX_INTERP_GAP_PX:
            t = (target_x - left_x) / gap
            y = curve_map[left_x] + t * (curve_map[right_x] - curve_map[left_x])
            return to_mtf(y)

    return None


# ---------------------------------------------------------------------------
# Occlusion fill for Samyang (4-color z-order overlap)
# ---------------------------------------------------------------------------

def fill_occluded_samyang(readings):
    """Fill missing values caused by z-order occlusion in Samyang charts.

    When two curves share the same y-position in the PNG, the top-drawn color
    hides the bottom one. Sibling pairs that can occlude each other:
      - 10S (dark red) ↔ 10M (pink) — same frequency, different direction
      - 30S (dark gray) ↔ 30M (light gray) — same frequency, different direction

    Strategy: if one sibling is missing but the other is present, copy the
    sibling's value. This is only valid when the curves genuinely overlap
    (same y-position), which is the exact condition that causes occlusion.

    Also fills cross-frequency occlusion: 30S/30M can be hidden by 10S/10M
    when all four curves converge near the same value (common at center
    positions on F8 plots).
    """
    result = [dict(r) for r in readings]

    for r in result:
        s10 = r["contrast10S"]
        m10 = r["contrast10M"]
        s30 = r["resolution30S"]
        m30 = r["resolution30M"]

        # Same-frequency sibling fill: 10S ↔ 10M
        if s10 is None and m10 is not None:
            r["contrast10S"] = m10
        elif m10 is None and s10 is not None:
            r["contrast10M"] = s10

        # Same-frequency sibling fill: 30S ↔ 30M
        if s30 is None and m30 is not None:
            r["resolution30S"] = m30
        elif m30 is None and s30 is not None:
            r["resolution30M"] = s30

        # Cross-frequency fill: all four curves converge at the same value.
        # Re-read after sibling fill.
        s10_now = r["contrast10S"]
        m10_now = r["contrast10M"]
        s30_now = r["resolution30S"]
        m30_now = r["resolution30M"]

        # 30 lp/mm both missing, 10 lp/mm present → 30 hidden under 10
        if s30_now is None and m30_now is None and (s10_now or m10_now):
            val = s10_now or m10_now
            r["resolution30S"] = val
            r["resolution30M"] = val

        # 10 lp/mm both missing, 30 lp/mm present → all four overlapping
        # (10 lp/mm ≥ 30 lp/mm, so at convergence they share the same value)
        if s10_now is None and m10_now is None and (s30_now or m30_now):
            r["contrast10S"] = s30_now or m30_now
            r["contrast10M"] = m30_now or s30_now

    return result


# ---------------------------------------------------------------------------
# Process Samyang chart (4 colors, 2 stacked plots)
# ---------------------------------------------------------------------------

def process_samyang_plot(img, arr, y_min, y_max, label):
    """Extract MTF readings from one Samyang plot region using skeletonization."""
    ax_x, y_top, y_bot = find_axis_and_plot(img, y_min, y_max)
    grid_xs = find_vertical_grids(img, ax_x, y_top, y_bot)
    n = len(grid_xs)

    if n < 2:
        print(f"  [{label}] WARNING: only {n} grid lines found, skipping")
        return None, [], []

    x_step = detect_grid_step(grid_xs)
    x_left = grid_xs[0]
    x_right = grid_xs[-1]
    x_max_mm = x_step * (n - 1)
    px_per_mm = (x_right - x_left) / x_max_mm

    print(f"  [{label}] axis={ax_x}, plot y={y_top}..{y_bot} ({y_bot - y_top}px)")
    print(f"  [{label}] grids ({n}): {grid_xs}, step={x_step}mm, max={x_max_mm}mm")

    # Crop array to plot region for mask generation
    plot_arr = arr.copy()

    # Generate color masks
    mask_10s = samyang_mask_dark_red(plot_arr)
    mask_10m = samyang_mask_pink(plot_arr)
    mask_30s = samyang_mask_dark_gray(plot_arr)
    mask_30m = samyang_mask_light_gray(plot_arr)

    # Restrict to plot region
    for mask in [mask_10s, mask_10m, mask_30s, mask_30m]:
        mask[:y_top, :] = False
        mask[y_bot + 1:, :] = False
        mask[:, :ax_x + 2] = False

    # Dilate to connect anti-aliased fragments, then skeletonize
    curves = {}
    for name, mask in [("10S", mask_10s), ("10M", mask_10m),
                       ("30S", mask_30s), ("30M", mask_30m)]:
        pixel_count = np.sum(mask)
        if pixel_count < 10:
            print(f"  [{label}] {name}: only {pixel_count} pixels, skipping")
            curves[name] = {}
            continue

        dilated = dilate_mask(mask, iterations=1)
        skel = skeletonize(dilated)
        skel_pixels = np.sum(skel)
        print(f"  [{label}] {name}: {pixel_count} color pixels -> {skel_pixels} skeleton pixels")

        branches = skeleton_to_curve(skel, ax_x + 3, img.size[0], y_top, y_bot)
        curve = pick_continuous_curve(branches, range(ax_x + 3, img.size[0]), y_top, y_bot)
        curves[name] = curve

    # Build position list
    positions = [round(i * x_step, 1) for i in range(n)]

    # Check for edge extension
    if curves["10S"]:
        edge_x = max(curves["10S"].keys())
        edge_mm = round((edge_x - x_left) / px_per_mm, 1)
        if edge_mm > positions[-1] + x_step * 0.3:
            edge_pos = round(edge_mm * 2) / 2
            positions.append(edge_pos)
            print(f"  [{label}] edge at ~{edge_mm}mm, adding position {edge_pos}mm")

    # Read values at grid positions
    readings = []
    for pos in positions:
        xp = int(x_left + pos * px_per_mm)
        readings.append({
            "position": pos,
            "contrast10S": interpolate_at(curves["10S"], xp, y_top, y_bot),
            "contrast10M": interpolate_at(curves["10M"], xp, y_top, y_bot),
            "resolution30S": interpolate_at(curves["30S"], xp, y_top, y_bot),
            "resolution30M": interpolate_at(curves["30M"], xp, y_top, y_bot),
        })

    # Fill occluded values — when curves overlap in the PNG, the top layer
    # hides the one underneath. Sibling pairs: 10S↔10M, 30S↔30M.
    readings = fill_occluded_samyang(readings)

    return x_step, positions, readings


# ---------------------------------------------------------------------------
# M-value interpolation for overlapping regions
# ---------------------------------------------------------------------------

def interpolate_missing_m(readings):
    """Fill missing M values where S and M curves overlap.

    At center positions where solid and dashed lines coincide, the dashed
    fragments merge into the solid component during skeletonization, leaving
    M undetected. Strategy:

    1. Find the first position where M is detected.
    2. For positions before that: set M = S (curves are coincident at center).
    3. For interior gaps: linear interpolation between nearest detected M values.

    Applies independently to 10 lp/mm and 30 lp/mm pairs.
    """
    result = [dict(r) for r in readings]
    n = len(result)

    for s_key, m_key in [("contrast10S", "contrast10M"),
                         ("resolution30S", "resolution30M")]:
        s_vals = [r[s_key] for r in result]
        m_vals = [r[m_key] for r in result]

        # Find first and last detected M
        first_m = next((i for i in range(n) if m_vals[i] is not None), None)
        last_m = next((i for i in range(n - 1, -1, -1) if m_vals[i] is not None), None)

        if first_m is None:
            # No M detected at all — set M = S everywhere
            for i in range(n):
                if s_vals[i] is not None:
                    result[i][m_key] = s_vals[i]
            continue

        # Fill positions before first detected M with M = S
        for i in range(first_m):
            if s_vals[i] is not None and m_vals[i] is None:
                result[i][m_key] = s_vals[i]

        # Fill interior gaps by linear interpolation
        for i in range(first_m + 1, (last_m or n)):
            if m_vals[i] is None and s_vals[i] is not None:
                left = next((j for j in range(i - 1, -1, -1) if m_vals[j] is not None), None)
                right = next((j for j in range(i + 1, n) if m_vals[j] is not None), None)
                if left is not None and right is not None:
                    t = (i - left) / (right - left)
                    result[i][m_key] = round(
                        m_vals[left] + t * (m_vals[right] - m_vals[left]), 4
                    )
                elif left is not None:
                    result[i][m_key] = s_vals[i]

    return result


# ---------------------------------------------------------------------------
# Process Sigma chart (2 colors, solid/dashed, single plot)
# ---------------------------------------------------------------------------

def process_sigma(img, arr):
    """Extract MTF readings from a Sigma chart.

    Pipeline: color mask (no dilation) -> skeletonize -> connected components
    -> classify solid/dashed by fragment width -> reassemble curves -> read values.

    Sigma PNGs are palette-based with no anti-aliasing, so no dilation is needed.
    This preserves dash gaps for accurate S/M classification.
    """
    ax_x, y_top, y_bot = find_axis_and_plot(img, 0, img.size[1])
    grid_xs = find_vertical_grids(img, ax_x, y_top, y_bot)
    n = len(grid_xs)

    print(f"  Axis: x={ax_x}, plot: y={y_top}..{y_bot} ({y_bot - y_top}px)")
    print(f"  Grids ({n}): {grid_xs}")

    if n < 2:
        print("  WARNING: insufficient grid lines")
        return

    x_left = grid_xs[0]
    x_right = grid_xs[-1]
    x_step = detect_sigma_grid_step(grid_xs)
    x_max_mm = x_step * (n - 1)
    px_per_mm = (x_right - x_left) / x_max_mm
    print(f"  Grid step: {x_step}mm, range: 0-{x_max_mm}mm")

    # Generate color masks
    mask_red = sigma_mask_red(arr)
    mask_blue = sigma_mask_blue(arr)

    # Restrict to plot region
    for mask in [mask_red, mask_blue]:
        mask[:y_top, :] = False
        mask[y_bot + 1:, :] = False
        mask[:, :ax_x + 2] = False

    # Skeletonize each color WITHOUT dilation — preserves dash gaps
    results = {}
    for name, mask in [("red(10)", mask_red), ("blue(30)", mask_blue)]:
        pixel_count = int(np.sum(mask))
        skel = skeletonize(mask)
        skel_uint8 = skel.astype(np.uint8) * 255
        skel_pixels = int(np.sum(skel))
        print(f"  {name}: {pixel_count} color pixels -> {skel_pixels} skeleton pixels")

        # Connected components classify solid vs dashed by fragment width
        solid, dashed = split_solid_dashed_cc(
            skel_uint8, y_top, y_bot, ax_x + 3, label=name
        )
        results[name] = (solid, dashed)

    solid_10, dashed_10 = results["red(10)"]
    solid_30, dashed_30 = results["blue(30)"]

    # Build positions
    positions = [round(i * x_step, 1) for i in range(n)]

    # Edge detection
    edge_curve = solid_10 or dashed_10
    if edge_curve:
        edge_x = max(edge_curve.keys())
        edge_mm = round((edge_x - x_left) / px_per_mm, 1)
        if edge_mm > positions[-1] + 0.5:
            edge_pos = round(edge_mm * 2) / 2
            positions.append(edge_pos)
            print(f"  Edge at ~{edge_mm}mm, adding position {edge_pos}mm")

    # Read raw values
    raw_readings = []
    for pos in positions:
        xp = int(x_left + pos * px_per_mm)
        raw_readings.append({
            "position": pos,
            "contrast10S": interpolate_at(solid_10, xp, y_top, y_bot),
            "contrast10M": interpolate_at(dashed_10, xp, y_top, y_bot) if dashed_10 else None,
            "resolution30S": interpolate_at(solid_30, xp, y_top, y_bot),
            "resolution30M": interpolate_at(dashed_30, xp, y_top, y_bot) if dashed_30 else None,
        })

    # Interpolate missing M values — where S and M overlap at center, dashed
    # fragments merge into the solid component so M is undetected. Fill M from
    # S (curves are coincident) or interpolate from nearest detected M values.
    readings = interpolate_missing_m(raw_readings)

    return positions, readings


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def print_table(positions, readings):
    print(f"  {'Pos':>5}  {'10S':>6}  {'10M':>6}  {'30S':>6}  {'30M':>6}")
    print("  " + "-" * 38)
    for r in readings:
        def fmt(v):
            return f"{v:.3f}" if v is not None else "  --- "
        print(
            f"  {r['position']:5.1f}  "
            f"{fmt(r['contrast10S'])}  {fmt(r['contrast10M'])}  "
            f"{fmt(r['resolution30S'])}  {fmt(r['resolution30M'])}"
        )


def print_typescript(aperture_label, readings):
    print(f"      {{")
    print(f'        aperture: "{aperture_label}",')
    print(f"        readings: [")
    for r in readings:
        s10 = r["contrast10S"]
        m10 = r["contrast10M"]
        s30 = r["resolution30S"]
        m30 = r["resolution30M"]
        if s10 is None and m10 is None and s30 is None and m30 is None:
            continue
        if s10 is None:
            s10 = m10 if m10 is not None else 0
        if m10 is None:
            m10 = s10
        if m30 is None:
            m30 = s30 if s30 is not None else 0
        if s30 is None:
            s30 = m30 if m30 is not None else 0
        print(
            f"          {{ position: {r['position']}, "
            f"contrast10S: {round(s10, 2)}, contrast10M: {round(m10, 2)}, "
            f"resolution30S: {round(s30, 2)}, resolution30M: {round(m30, 2)} }},"
        )
    print(f"        ],")
    print(f"      }},")


# ---------------------------------------------------------------------------
# Comparison mode — run both old and new, show diffs
# ---------------------------------------------------------------------------

def compare_samyang(path):
    """Run both extraction methods and compare results."""
    # Import the old tool's functions
    sys.path.insert(0, os.path.dirname(__file__))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "old_samyang",
        os.path.join(os.path.dirname(__file__), "mtf-extract-samyang.py")
    )
    old_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old_mod)

    img = load_on_white(path)
    arr = img_to_array(img)
    w, h = img.size

    split_y = find_plot_split(img)

    print("=" * 60)
    print(f"COMPARISON: {os.path.basename(path)}")
    print("=" * 60)

    for region, y_min, y_max, label in [(0, 0, split_y, "MAX"), (1, split_y, h, "F8")]:
        print(f"\n--- {label} aperture ---")

        # New (skeleton)
        print("\n[SKELETON]")
        new_step, new_pos, new_readings = process_samyang_plot(img, arr, y_min, y_max, label)

        # Old (pixel scan)
        print("\n[PIXEL SCAN]")
        old_step, old_pos, old_readings = old_mod.process_plot(img, y_min, y_max, label)

        if not new_readings or not old_readings:
            print("  Skipped (no data)")
            continue

        # Compare at matching positions
        print(f"\n  {'Pos':>5}  {'10S diff':>8}  {'10M diff':>8}  {'30S diff':>8}  {'30M diff':>8}")
        print("  " + "-" * 50)

        diffs = []
        for nr in new_readings:
            # Find matching old reading
            old_r = None
            for o in old_readings:
                if abs(o["position"] - nr["position"]) < 0.01:
                    old_r = o
                    break
            if old_r is None:
                continue

            row_diffs = []
            for key in ["contrast10S", "contrast10M", "resolution30S", "resolution30M"]:
                nv = nr[key]
                ov = old_r[key]
                if nv is not None and ov is not None:
                    d = nv - ov
                    row_diffs.append(d)
                    diffs.append(abs(d))
                else:
                    row_diffs.append(None)

            def fmt_diff(d):
                if d is None:
                    return "   ---  "
                sign = "+" if d >= 0 else ""
                return f"{sign}{d:7.4f}"

            print(
                f"  {nr['position']:5.1f}  "
                f"{fmt_diff(row_diffs[0])}  {fmt_diff(row_diffs[1])}  "
                f"{fmt_diff(row_diffs[2])}  {fmt_diff(row_diffs[3])}"
            )

        if diffs:
            avg = sum(diffs) / len(diffs)
            mx = max(diffs)
            print(f"\n  Mean |diff|: {avg:.4f}  Max |diff|: {mx:.4f}  N={len(diffs)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def process_file(path, compare=False):
    if compare:
        compare_samyang(path)
        return

    img = load_on_white(path)
    arr = img_to_array(img)
    w, h = img.size
    chart_type = detect_chart_type(img)
    print(f"\nImage: {path} ({w}x{h}) — detected: {chart_type}")

    if chart_type == "unknown":
        print(
            "  SKIPPED: unrecognized chart family. This tool only traces "
            "Sigma (red/blue) and Samyang (4-color) charts. Running another "
            "brand through these color masks yields silent garbage, so it is "
            "refused. Add a detector + color masks for this brand before "
            "tracing it (see #790)."
        )
        return

    if chart_type == "sigma":
        result = process_sigma(img, arr)
        if result:
            positions, readings = result
            print()
            print_table(positions, readings)
            print()
            print("// TypeScript readings:")
            print_typescript("f/?", readings)

    else:  # samyang
        split_y = find_plot_split(img)
        print(f"Plot split at y={split_y}")

        # MAX aperture
        print()
        step1, pos1, readings1 = process_samyang_plot(img, arr, 0, split_y, "MAX")
        if readings1:
            print_table(pos1, readings1)

        # F8
        print()
        step2, pos2, readings2 = process_samyang_plot(img, arr, split_y, h, "F8")
        if readings2:
            print_table(pos2, readings2)

        # TypeScript output
        print()
        print("// TypeScript readings:")
        name = os.path.splitext(os.path.basename(path))[0]
        match = re.search(r'-f(\d+(?:-\d+)?)', name)
        aperture_label = f"f/{match.group(1).replace('-', '.')}" if match else "f/?"
        if readings1:
            print_typescript(aperture_label, readings1)
        if readings2:
            print_typescript("f/8", readings2)


def main():
    if len(sys.argv) < 2:
        print("Usage: py tools/mtf-extract-skeleton.py <image.png> [image2.png ...]")
        print("       py tools/mtf-extract-skeleton.py --compare <samyang-image.png>")
        sys.exit(1)

    compare = "--compare" in sys.argv
    files = []
    for arg in sys.argv[1:]:
        if arg == "--compare":
            continue
        expanded = glob.glob(arg)
        if expanded:
            files.extend(expanded)
        else:
            files.append(arg)

    for path in sorted(files):
        process_file(path, compare=compare)


if __name__ == "__main__":
    main()
