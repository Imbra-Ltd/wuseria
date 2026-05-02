import styles from "../GenreGuide/GenreGuide.module.css";

// =============================================================================
// FIELD VALUE — 0-2 scale with traffic-light color
// =============================================================================

function FieldVal({ value }: { value: number | undefined }) {
  if (value == null) return <span className={styles.markDash}>&ndash;</span>;
  const cls =
    value >= 1.5
      ? styles.fieldViable // green — good optical performance
      : value >= 1.0
        ? styles.fieldMarginal // amber — acceptable
        : styles.fieldOver; // red — poor
  return <span className={`${cls} ${styles.fieldMono}`}>{value}</span>;
}

// =============================================================================
// MARK PIPS — visual dots for genre marks (0-5 scale)
// =============================================================================

function MarkPips({ mark }: { mark: number | null }) {
  if (mark == null) return <span className={styles.markDash}>&ndash;</span>;
  const full = Math.floor(mark);
  const half = mark % 1 >= 0.5;
  const pips: React.ReactNode[] = [];
  for (let i = 0; i < full; i++) {
    pips.push(<span key={i} className={`${styles.pip} ${styles.pipFull}`} />);
  }
  if (half) {
    pips.push(
      <span key="half" className={`${styles.pip} ${styles.pipHalf}`} />,
    );
  }
  return (
    <span className={styles.markDots} aria-label={`Mark ${mark} of 5`}>
      {pips}
    </span>
  );
}

// =============================================================================
// PICK STAR — editorial pick indicator
// =============================================================================

function PickStar({ isPick }: { isPick: boolean }) {
  if (!isPick) return null;
  return (
    <span className={styles.topStar} aria-label="Editor pick">
      ★
    </span>
  );
}

export { MarkPips, PickStar, FieldVal };
