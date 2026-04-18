/**
 * Format a shutter speed in seconds to a human-readable string.
 *
 * - Hours: `2h`
 * - Minutes: `5m`
 * - Seconds: `30s`
 * - Fractions: `1/250`
 */
function formatShutter(seconds: number): string {
  if (seconds >= 3600) return `${Math.round(seconds / 3600)}h`;
  if (seconds >= 60) return `${Math.round(seconds / 60)}m`;
  if (seconds >= 1) return `${Math.round(seconds)}s`;
  const denom = Math.round(1 / seconds);
  return `1/${denom}`;
}

function formatFL(focalLengthMin: number, focalLengthMax: number): string {
  if (focalLengthMin === focalLengthMax) {
    return `${focalLengthMin}mm`;
  }
  return `${focalLengthMin}-${focalLengthMax}mm`;
}

export { formatShutter, formatFL };
