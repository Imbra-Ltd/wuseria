import styles from "./GenreGuide.module.css";

interface FilterSelectProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  allLabel?: string;
  options: { label: string; value: string | number }[];
}

function FilterSelect({
  label,
  value,
  onChange,
  allLabel = "Any",
  options,
}: FilterSelectProps) {
  return (
    <div className={styles.controlGroup}>
      <span className={styles.controlLabel}>{label}</span>
      <select
        className={styles.controlSelect}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">{allLabel}</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}

const MIN_THRESHOLDS = [2.0, 1.5, 1.0].map((v) => ({
  label: `\u2265 ${v}`,
  value: v,
}));
const APERTURE_THRESHOLDS = [1.4, 2.0, 2.8, 4.0].map((v) => ({
  label: `\u2264 f/${v}`,
  value: v,
}));
const MARK_THRESHOLDS = [5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5, 1].map((v) => ({
  label: `\u2265 ${v}`,
  value: v,
}));
const WEIGHT_THRESHOLDS = [200, 300, 500, 800, 1500].map((v) => ({
  label: `\u2264 ${v}g`,
  value: v,
}));
const PRICE_THRESHOLDS = [500, 1000, 1500, 2000, 4000].map((v) => ({
  label: `\u2264 ~$${v}`,
  value: v,
}));

export {
  FilterSelect,
  MIN_THRESHOLDS,
  APERTURE_THRESHOLDS,
  MARK_THRESHOLDS,
  WEIGHT_THRESHOLDS,
  PRICE_THRESHOLDS,
};
