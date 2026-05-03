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

function ariaSortValue(
  currentKey: string,
  sortKey: string,
  direction: "asc" | "desc" | boolean,
): "ascending" | "descending" | "none" {
  if (currentKey !== sortKey) return "none";
  if (direction === "asc" || direction === true) return "ascending";
  return "descending";
}

function sortIndicatorChar(
  currentKey: string,
  sortKey: string,
  direction: "asc" | "desc" | boolean,
): string {
  if (currentKey !== sortKey) return "\u2195";
  if (direction === "asc" || direction === true) return "\u2191";
  return "\u2193";
}

export type { ColumnAlign };
export { makeAlignClasses, ariaSortValue, sortIndicatorChar };
