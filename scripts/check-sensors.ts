import { lenses } from "../src/data/lenses";

const scored = lenses.filter(
  (l) => (l as unknown as Record<string, unknown>).centerStopped != null,
);

for (const l of scored) {
  const lens = l as unknown as Record<string, unknown>;
  const line = [
    String(lens.model).padEnd(40),
    "cS=" + String(lens.centerStopped ?? "-").padEnd(5),
    "crS=" + String(lens.cornerStopped ?? "-").padEnd(5),
    "cWO=" + String(lens.centerWideOpen ?? "-").padEnd(5),
  ].join(" ");
  process.stdout.write(line + "\n");
}
