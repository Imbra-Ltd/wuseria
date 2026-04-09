interface ChipGroupProps {
  label: string;
  value: string;
  options: { label: string; value: string }[];
  onChange: (value: string) => void;
  styles: Record<string, string>;
}

function ChipGroup({ label, value, options, onChange, styles }: ChipGroupProps) {
  return (
    <div className={styles.chipGroup}>
      <span className={styles.chipLabel}>{label}</span>
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          className={`${styles.chip} ${value === opt.value ? styles.chipOn : ""}`}
          onClick={() => onChange(opt.value)}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

export { ChipGroup };
export type { ChipGroupProps };
