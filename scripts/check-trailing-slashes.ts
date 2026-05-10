import { readFileSync, readdirSync, existsSync } from "node:fs";
import { resolve, join } from "node:path";

const DIST = resolve(import.meta.dirname, "..", "dist");

if (!existsSync(DIST)) {
  console.error("dist/ not found — run `npm run build` first.");
  process.exit(1);
}

const files = readdirSync(DIST, { recursive: true })
  .map(String)
  .filter((f) => f.endsWith(".html"));

const hrefPattern = /href="(\/[^"]*?)"/g;
const IGNORED_EXTENSIONS =
  /\.(xml|css|js|json|svg|png|jpg|jpeg|webp|ico|txt|pdf|woff2?)$/i;

let violations = 0;

for (const file of files) {
  const html = readFileSync(join(DIST, file), "utf-8");
  let match: RegExpExecArray | null;

  while ((match = hrefPattern.exec(html)) !== null) {
    const href = match[1];

    if (
      href.includes("#") ||
      href.includes("?") ||
      IGNORED_EXTENSIONS.test(href)
    ) {
      continue;
    }

    if (!href.endsWith("/")) {
      console.error(`${file}: href="${href}" missing trailing slash`);
      violations++;
    }
  }
}

if (violations > 0) {
  console.error(`\n${violations} internal link(s) missing trailing slash.`);
  process.exit(1);
} else {
  console.log(
    `Checked ${files.length} HTML files — all internal links have trailing slashes.`,
  );
}
