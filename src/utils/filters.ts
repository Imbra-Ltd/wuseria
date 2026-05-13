/** Shared filter utilities for explorer components. */

function passesBooleanFilter(
  filter: string,
  value: boolean | undefined,
): boolean {
  if (filter === "yes") return !!value;
  if (filter === "no") return !value;
  return true;
}

function passesExactFilter(value: string, filter: string): boolean {
  return !filter || value === filter;
}

function passesMaxFilter(value: number, filter: string): boolean {
  if (!filter) return true;
  return value <= parseFloat(filter);
}

function passesMinFilter(value: number | undefined, filter: string): boolean {
  if (!filter) return true;
  return value != null && value >= Number(filter);
}

function passesRangeFilter(
  value: number,
  filter: string,
  ranges: Record<string, [number, number]>,
): boolean {
  if (!filter) return true;
  const range = ranges[filter];
  if (!range) return true;
  const [min, max] = range;
  return value >= min && value <= max;
}

function passesStatusFilter(
  filter: string,
  isDiscontinued: boolean | undefined,
): boolean {
  if (filter === "available") return !isDiscontinued;
  if (filter === "discontinued") return !!isDiscontinued;
  return true;
}

function passesSearchFilter(text: string, query: string): boolean {
  const q = query.trim();
  if (!q) return true;
  return text.toLowerCase().includes(q.toLowerCase());
}

export {
  passesBooleanFilter,
  passesExactFilter,
  passesMaxFilter,
  passesMinFilter,
  passesRangeFilter,
  passesStatusFilter,
  passesSearchFilter,
};
