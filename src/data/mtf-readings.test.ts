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

  it("all values are in 0-1 range", () => {
    for (const [slug, data] of entries) {
      const readings = data.charts.flatMap((c) => c.readings);
      for (const r of readings) {
        const fields = [
          r.contrast10S,
          r.contrast10M,
          r.resolution30S,
          r.resolution30M,
        ];
        for (const val of fields) {
          expect(
            val,
            `${slug} pos ${r.position}: out of range`,
          ).toBeGreaterThanOrEqual(0);
          expect(
            val,
            `${slug} pos ${r.position}: out of range`,
          ).toBeLessThanOrEqual(1);
        }
      }
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
  it("centre (position 0) MTF is never zero", () => {
    for (const [slug, data] of entries) {
      for (const chart of data.charts) {
        const centre = chart.readings.find((r) => r.position === 0);
        if (!centre) continue;
        const fields = {
          contrast10S: centre.contrast10S,
          contrast10M: centre.contrast10M,
          resolution30S: centre.resolution30S,
          resolution30M: centre.resolution30M,
        };
        for (const [field, val] of Object.entries(fields)) {
          expect(
            val,
            `${slug} ${chart.aperture}: centre ${field} is 0 (undetected curve?)`,
          ).toBeGreaterThan(0);
        }
      }
    }
  });
});
