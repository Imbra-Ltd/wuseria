"""Extract MTF curve data from Sigma manufacturer PNG charts by pixel color scanning.

Auto-detects plot area, scans wide strips, and uses curve-following gap
detection to reliably distinguish solid (S) from dashed (M) lines — even
through crossings.

Charts live per-lens under docs/optical-specs/<slug>/ (ADR-033) as
mtf-chart.png. Superseded by mtf-extract-skeleton.py.

Usage:
    py tools/mtf-extract-sigma.py docs/optical-specs/sigma-16mm-f1-4-dc-dn-c/mtf-chart.png
    py tools/mtf-extract-sigma.py docs/optical-specs/sigma-56mm-f1-4-dc-dn-c/mtf-chart.png
"""

import sys
from PIL import Image


# ---------------------------------------------------------------------------
# Color detection
# ---------------------------------------------------------------------------

def is_red(r, g, b):
    return r > 160 and g < 130 and b < 120 and r - g > 50


def is_blue(r, g, b):
    return b > 160 and r < 130 and b - r > 60


def is_dark(r, g, b):
    if is_red(r, g, b) or is_blue(r, g, b):
        return False
    return r < 240 and g < 240 and b < 240


# ---------------------------------------------------------------------------
# Image loading and calibration
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


def find_axis_and_plot(img):
    w, h = img.size
    p = img.load()

    best_x, best_count = 0, 0
    for x in range(w // 4):
        count = sum(1 for y in range(h) if is_dark(*p[x, y]))
        if count > best_count:
            best_count = count
            best_x = x

    def is_nonwhite(r, g, b):
        return r < 250 or g < 250 or b < 250

    runs = []
    in_run = False
    start = 0
    for y in range(h):
        if is_nonwhite(*p[best_x, y]):
            if not in_run:
                in_run = True
                start = y
        else:
            if in_run:
                in_run = False
                runs.append((start, y - 1))
    if in_run:
        runs.append((start, h - 1))

    runs.sort(key=lambda r: -(r[1] - r[0]))
    y_top, y_bot = runs[0]
    return best_x, y_top, y_bot


def find_vertical_grids(img, ax_x, y_top, y_bot):
    w = img.size[0]
    p = img.load()

    col_density = []
    for x in range(ax_x, w):
        count = sum(1 for y in range(y_top, y_bot, 3) if is_dark(*p[x, y]))
        col_density.append((x, count))

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


# ---------------------------------------------------------------------------
# Wide strip scanning
# ---------------------------------------------------------------------------

STRIP_HALF = 30


def scan_strip(img, x_center, y_top, y_bot, color_fn):
    w = img.size[0]
    p = img.load()
    hits = set()
    x_lo = max(0, x_center - STRIP_HALF)
    x_hi = min(w - 1, x_center + STRIP_HALF)

    for y in range(y_top, y_bot + 1):
        for x in range(x_lo, x_hi + 1):
            if color_fn(*p[x, y]):
                hits.add(y)
                break

    return sorted(hits)


def cluster_groups(hits, gap=12):
    if not hits:
        return []
    groups = [[hits[0]]]
    for y in hits[1:]:
        if y - groups[-1][-1] <= gap:
            groups[-1].append(y)
        else:
            groups.append([y])
    return [g for g in groups if len(g) >= 2]


# ---------------------------------------------------------------------------
# Curve-following gap detection for S/M classification
# ---------------------------------------------------------------------------

def trace_curve_gaps(img, x_center, y_center, color_fn, span=100, search=8):
    """Follow the curve from x_center outward, checking for color at each x.

    At each x, search vertically around the last-found y (following the curve).
    A solid line stays present at most x positions (~70%+).
    A dashed line has intermittent gaps (~35-55% fill, 3+ gap transitions).

    Returns (gap_transitions, fill_fraction).
    """
    p = img.load()
    w, h = img.size
    last_y = int(y_center)
    hits = 0
    total = 0
    gap_transitions = 0
    was_hit = True

    for dx in range(-span, span + 1):
        px = x_center + dx
        if px < 0 or px >= w:
            continue

        found = False
        for dy in range(-search, search + 1):
            py = last_y + dy
            if 0 <= py < h:
                r, g, b = p[px, py]
                if color_fn(r, g, b):
                    last_y = py
                    found = True
                    break

        total += 1
        if found:
            hits += 1
            if not was_hit:
                gap_transitions += 1
            was_hit = True
        else:
            if was_hit and total > 1:
                gap_transitions += 1
            was_hit = False

    fill = hits / total if total > 0 else 0
    return gap_transitions, fill


def classify_sm(img, x_center, groups, color_fn, yval_fn):
    """Classify clusters as S (solid) or M (dashed) using curve-following gaps.

    Returns (s_value, m_value). m_value is None if only 1 cluster.
    """
    if not groups:
        return None, None

    entries = []
    for g in groups:
        centroid = sum(g) / len(g)
        val = yval_fn(centroid)
        gt, fill = trace_curve_gaps(img, x_center, centroid, color_fn)
        is_solid = gt <= 2 and fill > 0.6
        entries.append((val, is_solid, gt, fill))

    if len(entries) == 1:
        return entries[0][0], None

    # Separate solid and dashed
    solids = [e for e in entries if e[1]]
    dashed = [e for e in entries if not e[1]]

    if len(solids) == 1 and len(dashed) == 1:
        return solids[0][0], dashed[0][0]

    # Fallback: if classification is ambiguous, use fill ratio
    entries.sort(key=lambda e: -e[3])  # highest fill = solid
    return entries[0][0], entries[1][0]


def interpolate_missing(s_vals, m_vals):
    """Fill in missing M values from neighbors.

    Where the dashed M line merges into the solid S line (a single detected
    cluster), the two genuinely coincide, so M = S there. This applies to both
    the center positions before the first detected M and to the trailing edge
    after the last one.

    Earlier this function manufactured a center astigmatism gap with a magic
    `gap_at_first * (0.6 + 0.4*t)` taper (B4 from the #726 audit) — an
    unjustified shrinking gap with no basis in the chart. At the optical center
    sagittal and meridional are identical (gap = 0), so M = S is the correct
    fill. This matches the live skeleton tool's interpolate_missing_m.
    """
    result = list(m_vals)
    n = len(result)

    first_m = next((i for i in range(n) if result[i] is not None), None)
    if first_m is None:
        return result

    # Center positions before the first detected M: S and M coincide → M = S.
    for i in range(first_m):
        if s_vals[i] is not None:
            result[i] = s_vals[i]

    # Fill interior gaps by linear interpolation; trailing edge gaps fall back
    # to M = S (S and M coincide where the dashed line was not separable).
    for i in range(n):
        if result[i] is None and s_vals[i] is not None:
            left = next((j for j in range(i - 1, -1, -1) if result[j] is not None), None)
            right = next((j for j in range(i + 1, n) if result[j] is not None), None)
            if left is not None and right is not None:
                t = (i - left) / (right - left)
                result[i] = round(result[left] + t * (result[right] - result[left]), 3)
            elif left is not None:
                result[i] = s_vals[i]

    return result


# ---------------------------------------------------------------------------
# Edge scanning (beyond last grid line)
# ---------------------------------------------------------------------------

def find_curve_edge(img, y_top, y_bot, color_fn):
    """Find the rightmost x where color pixels exist."""
    w = img.size[0]
    p = img.load()
    max_x = 0
    for x in range(w - 1, w // 2, -1):
        for y in range(y_top, y_bot):
            if color_fn(*p[x, y]):
                return x
    return w - 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: py tools/mtf-extract.py <image.png>")
        sys.exit(1)

    path = sys.argv[1]
    img = load_on_white(path)
    w, h = img.size
    print(f"Image: {path} ({w}x{h})")

    ax_x, y_top, y_bot = find_axis_and_plot(img)
    grid_xs = find_vertical_grids(img, ax_x, y_top, y_bot)
    n = len(grid_xs)

    print(f"Axis: x={ax_x}, plot: y={y_top}..{y_bot} ({y_bot - y_top}px)")
    print(f"Grids ({n}): {grid_xs}")

    x_step = 2.5
    x_left = grid_xs[0]
    x_right = grid_xs[-1]
    x_max_mm = x_step * (n - 1)
    px_per_mm = (x_right - x_left) / x_max_mm

    def xpix(mm):
        return int(x_left + mm * px_per_mm)

    def yval(y):
        return round(1.0 - (y - y_top) / (y_bot - y_top), 4)

    # Build position list: grid positions + edge
    positions = [round(i * x_step, 1) for i in range(n)]

    # Check if curves extend beyond last grid
    edge_red_x = find_curve_edge(img, y_top, y_bot, is_red)
    edge_mm = round((edge_red_x - x_left) / px_per_mm, 1)
    if edge_mm > positions[-1] + 0.5:
        # Add edge position rounded to nearest 0.5mm
        edge_pos = round(edge_mm * 2) / 2
        positions.append(edge_pos)
        print(f"Edge detected at ~{edge_mm}mm, adding position {edge_pos}mm")

    # Scan all positions
    print()
    print(f"{'Pos':>5}  {'10S':>6}  {'10M':>6}  {'30S':>6}  {'30M':>6}  {'10M?':>4}  {'30M?':>4}")
    print("-" * 55)

    all_s10 = []
    all_m10 = []
    all_s30 = []
    all_m30 = []

    for pos in positions:
        xp = xpix(pos)

        red_hits = scan_strip(img, xp, y_top, y_bot, is_red)
        blue_hits = scan_strip(img, xp, y_top, y_bot, is_blue)

        red_groups = cluster_groups(red_hits)
        blue_groups = cluster_groups(blue_hits)

        s10, m10 = classify_sm(img, xp, red_groups, is_red, yval)
        s30, m30 = classify_sm(img, xp, blue_groups, is_blue, yval)

        all_s10.append(round(s10, 3) if s10 is not None else None)
        all_m10.append(round(m10, 3) if m10 is not None else None)
        all_s30.append(round(s30, 3) if s30 is not None else None)
        all_m30.append(round(m30, 3) if m30 is not None else None)

    # Interpolate missing M values
    m10_filled = interpolate_missing(all_s10, all_m10)
    m30_filled = interpolate_missing(all_s30, all_m30)

    for i, pos in enumerate(positions):
        def fmt(v):
            return f"{v:.3f}" if v is not None else "  --- "

        m10_flag = "*" if all_m10[i] is None and m10_filled[i] is not None else " "
        m30_flag = "*" if all_m30[i] is None and m30_filled[i] is not None else " "

        print(
            f"{pos:5.1f}  "
            f"{fmt(all_s10[i])}  {fmt(m10_filled[i])}  "
            f"{fmt(all_s30[i])}  {fmt(m30_filled[i])}  "
            f"  {m10_flag}     {m30_flag}"
        )

    print()
    print("(* = M interpolated from neighbors)")
    print()
    print("// TypeScript readings:")
    for i, pos in enumerate(positions):
        s10 = all_s10[i]
        m10 = m10_filled[i] if m10_filled[i] is not None else s10
        s30 = all_s30[i]
        m30 = m30_filled[i] if m30_filled[i] is not None else s30

        if s10 is None:
            continue

        print(
            f"          {{ position: {pos}, "
            f"contrast10S: {round(s10, 2)}, contrast10M: {round(m10, 2)}, "
            f"resolution30S: {round(s30, 2)}, resolution30M: {round(m30, 2)} }},"
        )


if __name__ == "__main__":
    main()
