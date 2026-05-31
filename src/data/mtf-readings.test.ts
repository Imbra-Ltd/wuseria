import { describe, it, expect } from "vitest";
import { mtfReadings } from "./mtf-readings";

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
          [r.contrast10S, r.contrast10M, r.resolution30S, r.resolution30M]
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
        const raw = {
          contrast10S: centre.contrast10S,
          contrast10M: centre.contrast10M,
          resolution30S: centre.resolution30S,
          resolution30M: centre.resolution30M,
        };
        return Object.entries(raw)
          .filter((entry): entry is [string, number] => entry[1] != null)
          .map(([field, value]) => ({
            slug,
            aperture: chart.aperture,
            field,
            value,
          }));
      }),
    );

    for (const c of centreFields) {
      expect(
        c.value,
        `${c.slug} ${c.aperture}: centre ${c.field} is 0 (undetected curve?)`,
      ).toBeGreaterThan(0);
    }
  });
});
