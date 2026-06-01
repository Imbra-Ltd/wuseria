# Digitization log: tokina-atx-m-33mm-f1-4-x

This lens has one reference panel.

See `tools/mtfdigitizer/README.md` for the dispatch algorithm (per-hue Viterbi shortest path + raw-centroid snap + sister fallback + center symmetry).

## Panel

- **Chart:** `docs/optical-specs/tokina-atx-m-33mm-f1-4-x/tokina-atx-m-33mm-f1-4-x-mtf.png`
- **Style family:** `2color-frequency`
- **Dispatch profile:** `tokina-2color-frequency`
- **Plot box (pixels):** x=[182, 1338], y=[144, 855]
- **Image height:** 14.0 mm

### Sample grid (GT vs extracted)

| Field         | paired | med \|Δ\| | p95 \|Δ\| | sister-fill |
| ------------- | ------ | --------- | --------- | ----------- |
| contrast10S   | 11/11  | 0.036     | 0.070     | 0/11        |
| contrast10M   | 11/11  | 0.032     | 0.098     | 0/11        |
| resolution30S | 11/11  | 0.012     | 0.142     | 0/11        |
| resolution30M | 11/11  | 0.030     | 0.153     | 0/11        |

| frac | contrast10S GT | contrast10S EX | contrast10S Δ | contrast10M GT | contrast10M EX | contrast10M Δ | resolution30S GT | resolution30S EX | resolution30S Δ | resolution30M GT | resolution30M EX | resolution30M Δ |
| ---- | -------------- | -------------- | ------------- | -------------- | -------------- | ------------- | ---------------- | ---------------- | --------------- | ---------------- | ---------------- | --------------- |
| 0.0  | 0.95           | 0.92           | 0.028         | 0.95           | 0.92           | 0.028         | 0.72             | 0.71             | 0.010           | 0.72             | 0.71             | 0.010           |
| 0.1  | 0.96           | 0.92           | 0.045         | 0.94           | 0.92           | 0.022         | 0.69             | 0.69             | 0.003           | 0.67             | 0.69             | 0.019           |
| 0.2  | 0.93           | 0.91           | 0.021         | 0.96           | 0.90           | 0.059         | 0.71             | 0.68             | 0.032           | 0.62             | 0.65             | 0.030           |
| 0.3  | 0.95           | 0.91           | 0.041         | 0.95           | 0.94           | 0.013         | 0.72             | 0.69             | 0.026           | 0.58             | 0.65             | 0.069           |
| 0.4  | 0.91           | 0.91           | 0.004         | 0.92           | 0.90           | 0.017         | 0.71             | 0.70             | 0.010           | 0.55             | 0.58             | 0.033           |
| 0.5  | 0.92           | 0.90           | 0.021         | 0.90           | 0.87           | 0.032         | 0.65             | 0.66             | 0.012           | 0.50             | 0.52             | 0.021           |
| 0.6  | 0.91           | 0.87           | 0.041         | 0.85           | 0.87           | 0.020         | 0.55             | 0.56             | 0.011           | 0.45             | 0.49             | 0.036           |
| 0.7  | 0.92           | 0.86           | 0.064         | 0.80           | 0.84           | 0.038         | 0.50             | 0.51             | 0.012           | 0.42             | 0.44             | 0.024           |
| 0.8  | 0.87           | 0.86           | 0.005         | 0.74           | 0.81           | 0.065         | 0.57             | 0.53             | 0.038           | 0.45             | 0.46             | 0.012           |
| 0.9  | 0.81           | 0.86           | 0.049         | 0.67           | 0.76           | 0.089         | 0.55             | 0.56             | 0.007           | 0.41             | 0.49             | 0.079           |
| 1.0  | 0.76           | 0.80           | 0.036         | 0.60           | 0.66           | 0.064         | 0.30             | 0.41             | 0.112           | 0.30             | 0.43             | 0.132           |

### Center / edge summary

| Field         | center (0.0) | edge (0.9) | corner (1.0) |
| ------------- | ------------ | ---------- | ------------ |
| contrast10S   | 0.92         | 0.86       | 0.80         |
| contrast10M   | 0.92         | 0.76       | 0.66         |
| resolution30S | 0.71         | 0.56       | 0.41         |
| resolution30M | 0.71         | 0.49       | 0.43         |

### Shape metrics

| Field         | peak frac | peak value | half-falloff frac |
| ------------- | --------- | ---------- | ----------------- |
| contrast10S   | 0.0       | 0.92       | —                 |
| contrast10M   | 0.3       | 0.94       | —                 |
| resolution30S | 0.0       | 0.71       | —                 |
| resolution30M | 0.0       | 0.71       | —                 |
