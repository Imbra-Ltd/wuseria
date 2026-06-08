import { existsSync, readdirSync, statSync } from "node:fs";
import { join, resolve } from "node:path";
import { describe, it, expect } from "vitest";
import { lenses } from "./lenses";
import { mtfReadings } from "./mtf-readings";
import { toSlug } from "../utils/slug";

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

  it("every entry has a source URL", () => {
    for (const [slug, data] of entries) {
      expect(data.source, `${slug}: missing source`).toMatch(/^https?:\/\//);
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
// commit time — three bugs that landed in S122 (#1060 t-s vs ts slug,
// #1061 anchor lenses with disk data but no readings entry, #1062 60
// auto-derived 404 source URLs) would have been caught here.
describe("mtf-readings ↔ lenses.ts coverage", () => {
  const lensSlugs = new Set(lenses.map((l) => toSlug(`${l.brand} ${l.model}`)));
  const readingSlugs = Object.keys(mtfReadings);

  it("every mtfReadings key matches a lens via toSlug(brand model)", () => {
    const orphans = readingSlugs.filter((slug) => !lensSlugs.has(slug));
    expect(
      orphans,
      `mtfReadings keys with no matching lens (slug drift?): ${orphans.join(", ")}`,
    ).toEqual([]);
  });

  it("every mtfReadings entry's source URL parses", () => {
    for (const [slug, data] of Object.entries(mtfReadings)) {
      expect(
        () => new URL(data.source),
        `${slug}: source URL does not parse: ${data.source}`,
      ).not.toThrow();
    }
  });
});

// Shared walker — tests run with cwd = repo root.
const opticalSpecsDir = resolve(process.cwd(), "docs/optical-specs");

// Directories with a leading underscore are staging areas for
// pre-collected materials (e.g. `_pending-mitakon-cine/`) and are
// intentionally not lens slugs — exclude them from slug-shape checks.
const lensSpecDirs: string[] = readdirSync(opticalSpecsDir).filter((entry) => {
  if (entry.startsWith("_")) return false;
  return statSync(join(opticalSpecsDir, entry)).isDirectory();
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
    // Both share the 100mm-macro chart; emit blocked by extractor
    // freq30S zero-leak bug #1090. Remove after the extractor fix
    // lands and the 2 entries are emitted.
    "ttartisan-100mm-f2-8-macro-2x-gfx",
    "ttartisan-100mm-f2-8-macro-2x-tilt-shift",
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

// Directory-name invariant (#1069). Every `docs/optical-specs/<dir>`
// must match `toSlug(lens.brand + " " + lens.model)` for some lens in
// `lenses.ts`. Catches the S123 (#1063, #1066) class of bug where a
// scaffolder wrote `-t-s-` directories because the brand tooling did
// not match `toSlug`'s `/` → `` → `-` collapse for `T/S` → `ts`.
describe("docs/optical-specs directory-name invariant", () => {
  const lensSlugs = new Set(lenses.map((l) => toSlug(`${l.brand} ${l.model}`)));

  // Directories whose lens entry has not been added to `lenses.ts`
  // yet. Pre-existing as of #1069 landing; remove an entry when the
  // matching lens is added (or remove the directory if the lens was
  // surveyed and rejected). Tracked via #1085.
  const KNOWN_PENDING_LENS_ENTRY = new Set<string>([
    "thingyfy-pinhole-pro-x",
    "zeiss-touit-12mm-f2-8",
    "zeiss-touit-32mm-f1-8",
    "zeiss-touit-50mm-f2-8-macro",
  ]);

  it("every optical-specs directory matches a lens via toSlug", () => {
    const orphans = lensSpecDirs
      .filter((dir) => !lensSlugs.has(dir))
      .filter((dir) => !KNOWN_PENDING_LENS_ENTRY.has(dir));
    expect(
      orphans,
      `optical-specs directories with no matching lens (slug drift?): ${orphans.join(", ")}`,
    ).toEqual([]);
  });
});
