import { createHash } from "node:crypto";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join, resolve } from "node:path";
import { describe, it, expect } from "vitest";
import { lenses } from "./lenses";
import accessories from "./accessories";
import { mtfReadings } from "./mtf-readings";
import { toDataSlug } from "../utils/slug";

// The brandkit `slug_prefix` override map (ADR-056) lives in
// `src/utils/slug.ts` (`toDataSlug`) — shared with the lens page's
// mtfReadings lookup so the invariant here and the render path can
// never disagree on a brand's data slug.

describe("mtf-readings data integrity", () => {
  const entries = Object.entries(mtfReadings);

  it("has at least one entry", () => {
    expect(entries.length).toBeGreaterThan(0);
  });

  it("all slugs are lowercase kebab-case", () => {
    for (const [slug] of entries) {
      expect(slug, `Invalid slug: ${slug}`).toMatch(/^[a-z0-9-]+$/);
    }
  });

  it("every entry has at least one chart", () => {
    for (const [slug, data] of entries) {
      expect(data.charts.length, `${slug}: no charts`).toBeGreaterThan(0);
    }
  });

  it("every chart has an aperture string", () => {
    for (const [slug, data] of entries) {
      for (const chart of data.charts) {
        expect(chart.aperture, `${slug}: missing aperture`).toMatch(/^f\/\d/);
      }
    }
  });

  // ADR-053 + #1134: per-pass confidence.
  it("every chart has confidence HIGH or LOW", () => {
    for (const [slug, data] of entries) {
      for (const chart of data.charts) {
        expect(
          chart.confidence,
          `${slug} ${chart.aperture}: confidence must be 'HIGH' or 'LOW'`,
        ).toMatch(/^(HIGH|LOW)$/);
      }
    }
  });

  it("LOW charts carry a non-empty confidenceReason; HIGH charts omit it", () => {
    for (const [slug, data] of entries) {
      for (const chart of data.charts) {
        if (chart.confidence === "LOW") {
          expect(
            chart.confidenceReason,
            `${slug} ${chart.aperture}: LOW must have confidenceReason`,
          ).toMatch(/\S/);
        } else {
          expect(
            chart.confidenceReason,
            `${slug} ${chart.aperture}: HIGH must omit confidenceReason`,
          ).toBeUndefined();
        }
      }
    }
  });

  it("readings are sorted by position (ascending)", () => {
    for (const [slug, data] of entries) {
      for (const chart of data.charts) {
        const positions = chart.readings.map((r) => r.position);
        const sorted = [...positions].sort((a, b) => a - b);
        expect(
          positions,
          `${slug} ${chart.aperture}: unsorted positions`,
        ).toEqual(sorted);
      }
    }
  });

  it("all non-null values are in 0-1 range", () => {
    // Flatten to (slug, position, value) triples so the assertion loop
    // stays at one level — keeps cognitive complexity under the lint cap.
    type Sample = { slug: string; position: number; value: number };
    const samples: Sample[] = entries.flatMap(([slug, data]) =>
      data.charts.flatMap((c) =>
        c.readings.flatMap((r) =>
          Object.values(r.samples)
            .flatMap((sm) => [sm.S, sm.M])
            .filter((v): v is number => v != null)
            .map((value) => ({ slug, position: r.position, value })),
        ),
      ),
    );

    for (const s of samples) {
      expect(
        s.value,
        `${s.slug} pos ${s.position}: out of range`,
      ).toBeGreaterThanOrEqual(0);
      expect(
        s.value,
        `${s.slug} pos ${s.position}: out of range`,
      ).toBeLessThanOrEqual(1);
    }
  });

  it("first reading starts at position 0 (center)", () => {
    for (const [slug, data] of entries) {
      for (const chart of data.charts) {
        expect(
          chart.readings[0].position,
          `${slug} ${chart.aperture}: first position not center`,
        ).toBe(0);
      }
    }
  });

  // A lens with literally zero MTF at the optical centre is physically
  // impossible — a centre reading of 0 means a curve was not detected and got
  // emitted as 0 by the old extractor (the B2 zero-artifact found in the #726
  // verify pass). Edge readings may legitimately approach 0, so this guard is
  // scoped to position 0 only.
  //
  // null is allowed: the digitizer (B2 contract) returns null when no curve
  // was found at a sample position. That's honest absence-of-data; only an
  // emitted 0 indicates a buggy "found curve at MTF=0" reading.
  it("focalLength, when set, is a positive integer in mm", () => {
    for (const [slug, data] of entries) {
      for (const chart of data.charts) {
        if (chart.focalLength == null) continue;
        expect(
          chart.focalLength,
          `${slug} ${chart.aperture}: focalLength must be positive`,
        ).toBeGreaterThan(0);
        expect(
          Number.isInteger(chart.focalLength),
          `${slug} ${chart.aperture}: focalLength must be an integer mm`,
        ).toBe(true);
      }
    }
  });

  it("focalLength is set on all-or-none charts within an entry", () => {
    // Multi-chart entries can be either: (a) one prime with multiple
    // apertures (MAX + F8 panels — same focal length, no focalLength
    // needed); or (b) a zoom with one panel per published focal length.
    // What MUST hold is consistency within an entry: either every chart
    // sets focalLength (a zoom) or none does (a prime).
    for (const [slug, data] of entries) {
      const withFocal = data.charts.filter((c) => c.focalLength != null).length;
      const withoutFocal = data.charts.length - withFocal;
      expect(
        withFocal === 0 || withoutFocal === 0,
        `${slug}: charts must all set focalLength (zoom) or all omit it (prime); got ${withFocal} with, ${withoutFocal} without`,
      ).toBe(true);
    }
  });

  it("centre (position 0) MTF is never zero", () => {
    type CentreField = {
      slug: string;
      aperture: string;
      field: string;
      value: number;
    };
    const centreFields: CentreField[] = entries.flatMap(([slug, data]) =>
      data.charts.flatMap((chart) => {
        const centre = chart.readings.find((r) => r.position === 0);
        if (!centre) return [];
        const out: CentreField[] = [];
        for (const [freq, sm] of Object.entries(centre.samples)) {
          if (sm.S != null) {
            out.push({
              slug,
              aperture: chart.aperture,
              field: `${freq}S`,
              value: sm.S,
            });
          }
          if (sm.M != null) {
            out.push({
              slug,
              aperture: chart.aperture,
              field: `${freq}M`,
              value: sm.M,
            });
          }
        }
        return out;
      }),
    );

    for (const c of centreFields) {
      expect(
        c.value,
        `${c.slug} ${c.aperture}: centre ${c.field} is 0 (undetected curve?)`,
      ).toBeGreaterThan(0);
    }
  });

  // ADR-042 invariant: within one MtfChart, every reading row carries
  // the same set of frequency keys in `samples`. A divergence indicates
  // either a malformed dataset or a curator error mid-chart. Cross-chart
  // differences (prime + zoom on the same lens) are allowed — only
  // within-chart consistency is enforced.
  it("samples key set is consistent across rows within a chart", () => {
    for (const [slug, data] of entries) {
      for (const chart of data.charts) {
        const expectedKeys = Object.keys(chart.readings[0].samples)
          .map(Number)
          .sort((a, b) => a - b)
          .join(",");
        for (const r of chart.readings) {
          const rowKeys = Object.keys(r.samples)
            .map(Number)
            .sort((a, b) => a - b)
            .join(",");
          expect(
            rowKeys,
            `${slug} ${chart.aperture} pos ${r.position}: row frequencies ${rowKeys} differ from chart ${expectedKeys}`,
          ).toBe(expectedKeys);
        }
      }
    }
  });
});

// Coverage assertions (#1068). Catch key drift between `lenses.ts`,
// `mtf-readings.ts`, and the on-disk `docs/optical-specs/` charts at
// commit time — bugs in S122 (#1060 t-s vs ts slug, #1061 anchor lenses
// with disk data but no readings entry) would have been caught here.
// The #1062/#1339 drift class is now eliminated structurally: the
// attribution URL derives from `lenses.ts.officialUrl` instead of a
// duplicated field (#1341).
describe("mtf-readings ↔ lenses.ts coverage", () => {
  const lensSlugs = new Set(lenses.map((l) => toDataSlug(l.brand, l.model)));
  const readingSlugs = Object.keys(mtfReadings);

  it("every mtfReadings key matches a lens via toDataSlug(brand, model)", () => {
    const orphans = readingSlugs.filter((slug) => !lensSlugs.has(slug));
    expect(
      orphans,
      `mtfReadings keys with no matching lens (slug drift?): ${orphans.join(", ")}`,
    ).toEqual([]);
  });
});

// Shared walker — tests run with cwd = repo root.
const opticalSpecsDir = resolve(process.cwd(), "docs/optical-specs");

// Directories with a leading underscore are staging areas for
// pre-collected materials (e.g. `_pending-mitakon-cine/`) and are
// intentionally not lens slugs — exclude them from slug-shape checks.
//
// Directories whose only content is `diagnostic/` (ADR-050: per-stage
// digitizer bundle, gitignored) are local-only artifacts from a
// `mtfdigitizer diagnose` run on a slug that does not exist as a
// lens. They appear on disk but never in git; excluding them keeps
// `npm test` deterministic across machines (#1183).
const lensSpecDirs: string[] = readdirSync(opticalSpecsDir).filter((entry) => {
  if (entry.startsWith("_")) return false;
  const full = join(opticalSpecsDir, entry);
  if (!statSync(full).isDirectory()) return false;
  const trackedEntries = readdirSync(full).filter((e) => e !== "diagnostic");
  return trackedEntries.length > 0;
});

describe("docs/optical-specs ↔ mtf-readings coverage", () => {
  // A lens directory has "production data on disk" when it contains a
  // `digitization-log.md` — the production extractor writes that file
  // only on `--accept`. Charts that exist as raw PNGs but never went
  // through `--accept` are work-in-progress and do not require an
  // mtfReadings entry yet.
  const dirsWithLog: string[] = lensSpecDirs.filter((entry) =>
    existsSync(join(opticalSpecsDir, entry, "digitization-log.md")),
  );

  // Lenses where the chart was accepted (`--accept` written the log)
  // but the readings have not yet been emitted to `mtfReadings`.
  // Pre-existing as of #1068 landing — three early-anchor lenses
  // surveyed before the bulk-emit pipeline was wired. Remove an entry
  // when its readings are emitted; the test will then enforce
  // continued presence.
  const KNOWN_PENDING_EMIT = new Set<string>([
    "7artisans-50mm-f1-2-mark-ii",
    "sigma-30mm-f1-4-dc-dn-c",
    "tokina-atx-m-23mm-f1-4-x",
  ]);

  it("every accepted-extraction directory has a mtfReadings entry", () => {
    const missing = dirsWithLog
      .filter((slug) => !(slug in mtfReadings))
      .filter((slug) => !KNOWN_PENDING_EMIT.has(slug));
    expect(
      missing,
      `directories with digitization-log.md but no mtfReadings entry: ${missing.join(", ")}`,
    ).toEqual([]);
  });
});

// Eye-read overrides applied directly in mtf-readings.ts when the
// extractor disagrees with maintainer-verified truth. Each entry locks
// a single cell so a future `emit_*` re-run cannot silently revert it
// (#1202). When the underlying extractor is fixed, remove the
// corresponding entry here in the same PR.
//
// The af-35 entry is declared PERMANENT by ADR-073 (spike #1224 dead
// end). The right-corner M30 reading is the maintainer's eye-read
// extrapolation of the curve's last visible value past the chart's
// fade region; anchor-signal repair was evaluated and ruled out as a
// lever (band-overlap geometry is independent of seed quality). The
// extractor will not produce 0.58 on its own at this cell — the
// override carries the shipped reading.
const EYE_READ_OVERRIDES = [
  {
    slug: "ttartisan-af-35mm-f1-8",
    aperture: "f/1.8",
    position: 12.6,
    frequency: 30,
    field: "M" as const,
    expected: 0.58,
    issue: "#1201 / #1202 / ADR-073 (permanent)",
  },
];

describe("mtf-readings eye-read overrides", () => {
  for (const o of EYE_READ_OVERRIDES) {
    it(`${o.slug} ${o.aperture} pos ${o.position} ${o.frequency}${o.field} stays at ${o.expected} (${o.issue})`, () => {
      const entry = mtfReadings[o.slug];
      expect(entry, `${o.slug}: missing from mtfReadings`).toBeDefined();
      const chart = entry.charts.find((c) => c.aperture === o.aperture);
      expect(chart, `${o.slug}: missing chart ${o.aperture}`).toBeDefined();
      const reading = chart!.readings.find((r) => r.position === o.position);
      expect(
        reading,
        `${o.slug} ${o.aperture}: missing position ${o.position}`,
      ).toBeDefined();
      const sm = reading!.samples[o.frequency];
      expect(
        sm,
        `${o.slug} ${o.aperture} pos ${o.position}: missing frequency ${o.frequency}`,
      ).toBeDefined();
      expect(
        sm[o.field],
        `${o.slug} ${o.aperture} pos ${o.position} ${o.frequency}${o.field}: eye-read override drifted from ${o.expected} (extractor likely overwrote it — see ${o.issue})`,
      ).toBe(o.expected);
    });
  }
});

// Directory-name invariant (#1069). Every `docs/optical-specs/<dir>`
// must match `toSlug(brand + " " + model)` for some lens in `lenses.ts`
// or accessory in `accessories.ts` (e.g. Thingyfy Pinhole Pro X is an
// accessory but has a specs-log dir). Catches the S123 (#1063, #1066)
// class of bug where a scaffolder wrote `-t-s-` directories because the
// brand tooling did not match `toSlug`'s `/` → `` → `-` collapse for
// `T/S` → `ts`. Brand-prefix divergences (Carl Zeiss → zeiss) are
// handled via BRAND_SLUG_OVERRIDE — see ADR-056.
describe("docs/optical-specs directory-name invariant", () => {
  const lensSlugs = new Set([
    ...lenses.map((l) => toDataSlug(l.brand, l.model)),
    ...accessories.map((a) => toDataSlug(a.brand, a.model)),
  ]);

  it("every optical-specs directory matches a lens via toDataSlug", () => {
    const orphans = lensSpecDirs.filter((dir) => !lensSlugs.has(dir));
    expect(
      orphans,
      `optical-specs directories with no matching lens (slug drift?): ${orphans.join(", ")}`,
    ).toEqual([]);
  });
});

// Same-product MTF chart invariant (#1265). Two lens entries that share
// an `officialUrl` are, by construction, the same optical product sold
// in two mount variants (e.g. TTartisan 100mm Macro 2X X-mount vs
// GFX-mount — same lens, different rear adapter). The manufacturer
// publishes one MTF chart per optical design, so the primary
// `<slug>-mtf.png` source chart MUST be byte-identical across mount
// variants. The investigation behind #1265 found three TTartisan pairs
// in this state and confirmed all three have matching upstream charts —
// any future drift (e.g. someone fetches a different chart for one
// variant) is a data-quality bug.
//
// The test scopes to lens-pairs that share an `officialUrl` AND both
// have a primary MTF chart file on disk; pairs missing one side are
// out of scope (different cause).
describe("same-product MTF chart invariant", () => {
  const SPECS_ROOT = resolve(__dirname, "../../docs/optical-specs");

  function hashFile(path: string): string {
    // sha256: identity check, not security — sonarjs flags md5/sha1.
    return createHash("sha256").update(readFileSync(path)).digest("hex");
  }

  function primaryChartPath(slug: string): string {
    return join(SPECS_ROOT, slug, `${slug}-mtf.png`);
  }

  const groupsByUrl = new Map<string, string[]>();
  for (const lens of lenses) {
    if (!lens.officialUrl) continue;
    const slug = toDataSlug(lens.brand, lens.model);
    const list = groupsByUrl.get(lens.officialUrl) ?? [];
    list.push(slug);
    groupsByUrl.set(lens.officialUrl, list);
  }
  const sharedUrlGroups = [...groupsByUrl.entries()].filter(
    ([, slugs]) => slugs.length > 1,
  );

  it("lens entries sharing an officialUrl share their primary MTF chart", () => {
    const mismatches: string[] = [];
    for (const [url, slugs] of sharedUrlGroups) {
      const present = slugs.filter((s) => existsSync(primaryChartPath(s)));
      if (present.length < 2) continue;
      const hashes = present.map((s) => ({
        slug: s,
        hash: hashFile(primaryChartPath(s)),
      }));
      const distinctHashes = new Set(hashes.map((h) => h.hash));
      if (distinctHashes.size > 1) {
        const detail = hashes
          .map((h) => `${h.slug}=${h.hash.slice(0, 8)}`)
          .join(", ");
        mismatches.push(`${url}: ${detail}`);
      }
    }
    expect(
      mismatches,
      `lenses sharing officialUrl have divergent MTF charts (one mount variant was likely fetched from the wrong page — see #1265): ${mismatches.join("; ")}`,
    ).toEqual([]);
  });
});
