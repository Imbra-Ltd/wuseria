import { lenses } from "../src/data/lenses";

const scored = lenses.filter(
  (l) => (l as unknown as Record<string, unknown>).centerStopped != null,
);

for (const l of scored) {
  const lens = l as unknown as Record<string, unknown>;
  const line = [
    String(lens.model).padEnd(40),
    "cS=" + String((lens.centerStopped as number | undefined) ?? "-").padEnd(5),
    "crS=" +
      String((lens.cornerStopped as number | undefined) ?? "-").padEnd(5),
    "cWO=" +
      String((lens.centerWideOpen as number | undefined) ?? "-").padEnd(5),
  ].join(" ");
  process.stdout.write(line + "\n");
}
