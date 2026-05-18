"""Extract MTF curve data from Samyang manufacturer PNG charts by pixel color scanning.

Samyang charts use 4 distinct colors (no solid/dashed distinction needed):
  - Dark red (~197,1,51):   10 lp/mm Sagittal (contrast10S)
  - Pink (~225,127,152):    10 lp/mm Meridional (contrast10M)
  - Dark gray (~102):       30 lp/mm Sagittal (resolution30S)
  - Light gray (~178):      30 lp/mm Meridional (resolution30M)

Each image contains TWO stacked plots: MAX. aperture (top) and F8 (bottom).
Grid spacing is auto-detected (2mm, 3mm, or 5mm depending on lens).

Approach: trace each curve across the entire plot width by finding all matching
pixels, then interpolate values at grid positions. This handles steeply sloped
curves that strip-scanning misses.

Usage:
    py tools/mtf-extract-samyang.py docs/mtf-charts/samyang-35mm-f1-2.png
    py tools/mtf-extract-samyang.py docs/mtf-charts/samyang-*.png
"""

import sys
import glob
import os
import re
from PIL import Image


# ---------------------------------------------------------------------------
# Color detection — 4 distinct colors for Samyang
# ---------------------------------------------------------------------------

def is_dark_red(r, g, b):
    """10 lp/mm Sagittal — saturated dark red (~197,1,51)."""
    return r > 160 and g < 100 and b < 120 and r - g > 70

def is_pink(r, g, b):
    """10 lp/mm Meridional — lighter pink/red (~225,127,152)."""
    return r > 180 and g > 80 and b > 80 and r - g > 30 and r - b > 20 and g < 190

def is_dark_gray(r, g, b):
    """30 lp/mm Sagittal — dark gray (~102). Tight band to exclude anti-aliased edges."""
    if is_dark_red(r, g, b) or is_pink(r, g, b):
        return False
    avg = (r + g + b) / 3
    spread = max(r, g, b) - min(r, g, b)
    return 85 <= avg <= 120 and spread < 20

def is_light_gray(r, g, b):
    """30 lp/mm Meridional — medium gray (~178). Tight band to exclude AA edges."""
    if is_dark_red(r, g, b) or is_pink(r, g, b):
        return False
    avg = (r + g + b) / 3
    spread = max(r, g, b) - min(r, g, b)
    return 160 <= avg <= 195 and spread < 20

def is_any_dark(r, g, b):
    """Any non-white pixel for axis detection (strict)."""
    return r < 240 and g < 240 and b < 240

def is_grid(r, g, b):
    """Faint grid line pixel — Samyang grids are ~(243,243,243)."""
    return r < 250 and g < 250 and b < 250


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


# ---------------------------------------------------------------------------
# Split image into two plots (MAX aperture + F8)
# ---------------------------------------------------------------------------

def find_plot_split(img):
    """Find the y-coordinate that splits the two plots."""
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


# ---------------------------------------------------------------------------
# Axis and grid detection (per plot region)
# ---------------------------------------------------------------------------

def find_axis_and_plot(img, y_min, y_max):
    """Find the left axis x-position and plot top/bottom within a region."""
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
    """Find x-positions of vertical grid lines."""
    w = img.size[0]
    p = img.load()

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


def detect_grid_step(grid_xs):
    """Auto-detect grid step in mm from pixel spacing and grid count.

    Samyang uses 2mm, 3mm, or 5mm grid spacing. Detection heuristic:
    - Wide pixel spacing (>=80px per step) → 5mm (full-frame/tele lenses)
    - Narrow spacing (<80px) with 7+ grids → 2mm (APS-C standard)
    - Narrow spacing (<80px) with 5-6 grids → 3mm (APS-C wide)
    """
    n = len(grid_xs)
    if n < 2:
        return 2.0

    avg_spacing = (grid_xs[-1] - grid_xs[0]) / (n - 1)

    # Samyang pixel spacings: ~62px→2mm, ~86px→3mm, ~100px→5mm
    if avg_spacing >= 93:
        return 5.0
    elif avg_spacing >= 73:
        return 3.0
    else:
        return 2.0


# ---------------------------------------------------------------------------
# Curve tracing — find ALL pixels of a color, build x->y mapping
# ---------------------------------------------------------------------------

def trace_curve(img, ax_x, y_top, y_bot, color_fn):
    """Find all pixels matching color_fn and return x -> y_centroid mapping.

    For each x position, collects all matching y values and returns the
    centroid. Skips axis pixels (x <= ax_x + 2).
    """
    w = img.size[0]
    p = img.load()

    # Collect all matching pixels, grouped by x
    x_to_ys = {}
    for x in range(ax_x + 3, w):
        ys = []
        for y in range(y_top, y_bot + 1):
            if color_fn(*p[x, y]):
                ys.append(y)
        if ys:
            # Cluster into groups (handle multiple curve lines at same x)
            groups = []
            current = [ys[0]]
            for y in ys[1:]:
                if y - current[-1] <= 3:
                    current.append(y)
                else:
                    groups.append(current)
                    current = [y]
            groups.append(current)

            # Take centroid of each group
            centroids = [sum(g) / len(g) for g in groups if len(g) >= 1]
            x_to_ys[x] = centroids

    return x_to_ys


def interpolate_curve_at(x_to_ys, target_x, y_top, y_bot):
    """Get the curve y-value at a specific x by interpolation.

    When there are multiple curve branches (clusters) at nearby x positions,
    uses the closest x and picks the branch that forms a smooth trajectory.

    Returns MTF value (0-1) or None.
    """
    # Find closest x values with data
    xs_with_data = sorted(x_to_ys.keys())
    if not xs_with_data:
        return None

    def pick_y(centroids):
        """Pick the best centroid when multiple clusters exist.

        For curves with a single cluster, return it directly.
        For multiple clusters, take the one with the lowest y (highest MTF)
        — the topmost branch is more likely to be the actual curve at that x.
        """
        if len(centroids) == 1:
            return centroids[0]
        return min(centroids)

    # Find bracketing x values
    left_x = None
    right_x = None
    for x in xs_with_data:
        if x <= target_x:
            left_x = x
        if x >= target_x and right_x is None:
            right_x = x

    # Use exact or nearest
    if left_x is not None and abs(left_x - target_x) <= 5:
        y = pick_y(x_to_ys[left_x])
        return round(1.0 - (y - y_top) / (y_bot - y_top), 4)

    if right_x is not None and abs(right_x - target_x) <= 5:
        y = pick_y(x_to_ys[right_x])
        return round(1.0 - (y - y_top) / (y_bot - y_top), 4)

    # Interpolate between left and right
    if left_x is not None and right_x is not None:
        gap = right_x - left_x
        if gap > 100:
            return None
        t = (target_x - left_x) / gap
        left_y = pick_y(x_to_ys[left_x])
        right_y = pick_y(x_to_ys[right_x])
        y = left_y + t * (right_y - left_y)
        return round(1.0 - (y - y_top) / (y_bot - y_top), 4)

    # Only one side available
    if left_x is not None and abs(left_x - target_x) <= 20:
        y = pick_y(x_to_ys[left_x])
        return round(1.0 - (y - y_top) / (y_bot - y_top), 4)
    if right_x is not None and abs(right_x - target_x) <= 20:
        y = pick_y(x_to_ys[right_x])
        return round(1.0 - (y - y_top) / (y_bot - y_top), 4)

    return None


# ---------------------------------------------------------------------------
# Edge scanning
# ---------------------------------------------------------------------------

def find_curve_edge(x_to_ys):
    """Find the rightmost x where the curve has data."""
    if not x_to_ys:
        return 0
    return max(x_to_ys.keys())


# ---------------------------------------------------------------------------
# Process a single plot region
# ---------------------------------------------------------------------------

def process_plot(img, y_min, y_max, label):
    """Extract MTF readings from one plot region."""
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

    # Trace all 4 curves across the entire plot
    print(f"  [{label}] tracing curves...")
    curve_10s = trace_curve(img, ax_x, y_top, y_bot, is_dark_red)
    curve_10m = trace_curve(img, ax_x, y_top, y_bot, is_pink)
    curve_30s = trace_curve(img, ax_x, y_top, y_bot, is_dark_gray)
    curve_30m = trace_curve(img, ax_x, y_top, y_bot, is_light_gray)

    print(f"  [{label}] pixels: 10S={len(curve_10s)}, 10M={len(curve_10m)}, "
          f"30S={len(curve_30s)}, 30M={len(curve_30m)}")

    def xpix(mm):
        return int(x_left + mm * px_per_mm)

    # Build position list
    positions = [round(i * x_step, 1) for i in range(n)]

    # Check for curves extending beyond last grid
    edge_x = find_curve_edge(curve_10s)
    if edge_x > 0:
        edge_mm = round((edge_x - x_left) / px_per_mm, 1)
        if edge_mm > positions[-1] + x_step * 0.3:
            edge_pos = round(edge_mm * 2) / 2
            positions.append(edge_pos)
            print(f"  [{label}] edge at ~{edge_mm}mm, adding position {edge_pos}mm")

    # Interpolate all 4 curves at each position
    readings = []
    for pos in positions:
        xp = xpix(pos)
        s10 = interpolate_curve_at(curve_10s, xp, y_top, y_bot)
        m10 = interpolate_curve_at(curve_10m, xp, y_top, y_bot)
        s30 = interpolate_curve_at(curve_30s, xp, y_top, y_bot)
        m30 = interpolate_curve_at(curve_30m, xp, y_top, y_bot)

        readings.append({
            "position": pos,
            "contrast10S": s10,
            "contrast10M": m10,
            "resolution30S": s30,
            "resolution30M": m30,
        })

    return x_step, positions, readings


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
        if s10 is None:
            continue
        if m10 is None:
            m10 = s10
        if m30 is None:
            m30 = s30 if s30 is not None else 0
        if s30 is None:
            s30 = 0
        print(
            f"          {{ position: {r['position']}, "
            f"contrast10S: {round(s10, 2)}, contrast10M: {round(m10, 2)}, "
            f"resolution30S: {round(s30, 2)}, resolution30M: {round(m30, 2)} }},"
        )
    print(f"        ],")
    print(f"      }},")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def process_file(path):
    img = load_on_white(path)
    w, h = img.size
    print(f"\nImage: {path} ({w}x{h})")

    split_y = find_plot_split(img)
    print(f"Plot split at y={split_y}")

    # Process top plot (MAX. aperture)
    print()
    step1, pos1, readings1 = process_plot(img, 0, split_y, "MAX")
    if readings1:
        print_table(pos1, readings1)

    # Process bottom plot (F8)
    print()
    step2, pos2, readings2 = process_plot(img, split_y, h, "F8")
    if readings2:
        print_table(pos2, readings2)

    # Output TypeScript
    print()
    print("// TypeScript readings:")

    name = os.path.splitext(os.path.basename(path))[0]
    match = re.search(r'-f(\d+(?:-\d+)?)', name)
    if match:
        apt = match.group(1).replace("-", ".")
        aperture_label = f"f/{apt}"
    else:
        aperture_label = "f/?"

    if readings1:
        print_typescript(aperture_label, readings1)
    if readings2:
        print_typescript("f/8", readings2)


def main():
    if len(sys.argv) < 2:
        print("Usage: py tools/mtf-extract-samyang.py <image.png> [image2.png ...]")
        print("       py tools/mtf-extract-samyang.py docs/mtf-charts/samyang-*.png")
        sys.exit(1)

    files = []
    for arg in sys.argv[1:]:
        expanded = glob.glob(arg)
        if expanded:
            files.extend(expanded)
        else:
            files.append(arg)

    for path in sorted(files):
        process_file(path)


if __name__ == "__main__":
    main()
