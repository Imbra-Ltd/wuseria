import styles from "../GenreGuide/GenreGuide.module.css";

// =============================================================================
// FIELD VALUE — 0-2 scale with traffic-light color
// =============================================================================

function fieldValClass(value: number): string {
  if (value >= 1.5) return styles.fieldViable; // green — good optical performance
  if (value >= 1.0) return styles.fieldMarginal; // amber — acceptable
  return styles.fieldOver; // red — poor
}

function FieldVal({ value }: { value: number | undefined }) {
  if (value == null) return <span className={styles.markDash}>&ndash;</span>;
  return (
    <span className={`${fieldValClass(value)} ${styles.fieldMono}`}>
      {value}
    </span>
  );
}

// =============================================================================
// MARK PIPS — visual dots for genre marks (0-5 scale)
// =============================================================================

function MarkPips({ mark }: { mark: number | null }) {
  if (mark == null) return <span className={styles.markDash}>&ndash;</span>;
  const full = Math.floor(mark);
  const half = mark % 1 >= 0.5;
  const filled = full + (half ? 1 : 0);
  const pips: React.ReactNode[] = [];
  for (let i = 0; i < full; i++) {
    pips.push(<span key={i} className={`${styles.pip} ${styles.pipFull}`} />);
  }
  if (half) {
    pips.push(
      <span key="half" className={`${styles.pip} ${styles.pipHalf}`} />,
    );
  }
  for (let i = filled; i < 5; i++) {
    pips.push(<span key={`empty-${i}`} className={styles.pip} />);
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
