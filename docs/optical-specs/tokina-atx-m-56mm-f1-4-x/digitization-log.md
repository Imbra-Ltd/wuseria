# Digitization log: tokina-atx-m-56mm-f1-4-x

This lens has one reference panel.

**Legend.**

- **EYE** — eye-read ground truth from the chart, set by a maintainer in `tools/mtfdigitizer/referenceset/charts.py`.
- **EX** — what the extractor computed for the same sample point.
- **Δ** — `|EX − EYE|`; the calibration tolerance band is ±0.05.
- **sister-fill** — count of samples filled from the sister curve.
- **·** in a sparkline — EYE marked the value as None at that point.

See `tools/mtfdigitizer/README.md` for the dispatch algorithm (per-hue Viterbi shortest path + raw-centroid snap + sister fallback + center symmetry).

## Panel

- **Chart:** `docs/optical-specs/tokina-atx-m-56mm-f1-4-x/tokina-atx-m-56mm-f1-4-x-mtf.png`
- **Style family:** `2color-frequency`
- **Dispatch profile:** `tokina-2color-frequency`
- **Plot box (pixels):** x=[338, 1668], y=[188, 1006]
- **Image height:** 14.0 mm

### Sample grid (EYE vs EX)

| Field         | paired | med \|Δ\| | p95 \|Δ\| | sister-fill |
| ------------- | ------ | --------- | --------- | ----------- |
| contrast10S   | 11/11  | 0.022     | 0.054     | 1/11        |
| contrast10M   | 11/11  | 0.020     | 0.089     | 0/11        |
| resolution30S | 11/11  | 0.028     | 0.096     | 1/11        |
| resolution30M | 11/11  | 0.020     | 0.211     | 0/11        |

```
  EX   contrast10S    ▇▇▇▇▇▇▇▇▆▆▆  (0.91 → 0.70)
  EYE  contrast10S    █▇▇█▇▇▇▆▆▆▆
  EX   contrast10M    ▇▇▇▇▇▇▇▇▇▇▆  (0.91 → 0.70)
  EYE  contrast10M    █▇▇▇▇▇▇▇▇▆▅
  EX   resolution30S  ▆▆▆▅▅▅▅▄▄▄▄  (0.69 → 0.44)
  EYE  resolution30S  ▆▆▅▆▅▆▅▅▄▄▄
  EX   resolution30M  ▆▆▅▅▅▅▅▅▅▅▃  (0.69 → 0.35)
  EYE  resolution30M  ▆▆▅▅▅▅▅▅▅▄▂
```

| frac | contrast10S EYE | contrast10S EX | contrast10S Δ | contrast10M EYE | contrast10M EX | contrast10M Δ | resolution30S EYE | resolution30S EX | resolution30S Δ | resolution30M EYE | resolution30M EX | resolution30M Δ |
| ---- | --------------- | -------------- | ------------- | --------------- | -------------- | ------------- | ----------------- | ---------------- | --------------- | ----------------- | ---------------- | --------------- |
| 0.0  | 0.93            | 0.91           | 0.020         | 0.93            | 0.91           | 0.020         | 0.72              | 0.69             | 0.028           | 0.70              | 0.69             | 0.008           |
| 0.1  | 0.90            | 0.91           | 0.005         | 0.90            | 0.90           | 0.004         | 0.65              | 0.68             | 0.031           | 0.65              | 0.67             | 0.020           |
| 0.2  | 0.88            | 0.89           | 0.010         | 0.88            | 0.87           | 0.005         | 0.60              | 0.66             | 0.057           | 0.62              | 0.61             | 0.013           |
| 0.3  | 0.93            | 0.90           | 0.026         | 0.90            | 0.86           | 0.040         | 0.65              | 0.64             | 0.012           | 0.58              | 0.57             | 0.007           |
| 0.4  | 0.87            | 0.87           | 0.005         | 0.89            | 0.87           | 0.020         | 0.62              | 0.62             | 0.000           | 0.55              | 0.58             | 0.031           |
| 0.5  | 0.86            | 0.86           | 0.003         | 0.87            | 0.86           | 0.008         | 0.65              | 0.62             | 0.030           | 0.55              | 0.59             | 0.040           |
| 0.6  | 0.85            | 0.87           | 0.022         | 0.88            | 0.85           | 0.028         | 0.63              | 0.57             | 0.056           | 0.55              | 0.57             | 0.020           |
| 0.7  | 0.78            | 0.82           | 0.036         | 0.85            | 0.86           | 0.010         | 0.55              | 0.47             | 0.085           | 0.55              | 0.54             | 0.013           |
| 0.8  | 0.72            | 0.76           | 0.040         | 0.80            | 0.87           | 0.074         | 0.45              | 0.44             | 0.011           | 0.52              | 0.55             | 0.027           |
| 0.9  | 0.70            | 0.75           | 0.052         | 0.75            | 0.84           | 0.087         | 0.43              | 0.44             | 0.007           | 0.45              | 0.53             | 0.083           |
| 1.0  | 0.65            | 0.70           | 0.046         | 0.62            | 0.70           | 0.083         | 0.45              | 0.44             | 0.005           | 0.18              | 0.35             | 0.175           |

### Center / edge summary

| Field         | center (0.0) | edge (0.9) | corner (1.0) |
| ------------- | ------------ | ---------- | ------------ |
| contrast10S   | 0.91         | 0.75       | 0.70         |
| contrast10M   | 0.91         | 0.84       | 0.70         |
| resolution30S | 0.69         | 0.44       | 0.44         |
| resolution30M | 0.69         | 0.53       | 0.35         |

### Shape metrics

| Field         | peak frac | peak value | half-falloff frac |
| ------------- | --------- | ---------- | ----------------- |
| contrast10S   | 0.0       | 0.91       | —                 |
| contrast10M   | 0.0       | 0.91       | —                 |
| resolution30S | 0.0       | 0.69       | —                 |
| resolution30M | 0.0       | 0.69       | —                 |
