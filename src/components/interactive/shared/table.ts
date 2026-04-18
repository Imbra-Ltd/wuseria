type ColumnAlign = "left" | "right" | "center";

function makeAlignClasses(
  styles: Record<string, string>,
): Record<ColumnAlign, string | undefined> {
  return {
    left: undefined,
    right: styles.cellRight,
    center: styles.cellCenter,
  };
}

export type { ColumnAlign };
export { makeAlignClasses };
