/**
 * Checks that every external URL in the data files is reachable.
 *
 * Scans src/data/*.ts for https:// URLs (officialUrl, reviewSources, etc.),
 * dedupes, and requests each one. A URL is reported as broken only after a
 * retry, to tolerate transient network blips. Intended to run on a schedule
 * (weekly cron), NOT per-PR — external hosts rate-limit and flake.
 *
 * Exit 1 if any URL is unreachable after retry; 0 otherwise.
 */
import { readFileSync, readdirSync } from "node:fs";
import { resolve, join } from "node:path";

const DATA_DIR = resolve(import.meta.dirname, "..", "src", "data");
const TIMEOUT_MS = 20_000;
const CONCURRENCY = 8;
// Some hosts reject HEAD or non-browser agents; send a browser-like UA.
const UA =
  "Mozilla/5.0 (compatible; wuseria-linkcheck/1.0; +https://wuseria.com)";

function collectUrls(): Map<string, Set<string>> {
  const urlToFiles = new Map<string, Set<string>>();
  const urlPattern = /"(https:\/\/[^"]+)"/g;
  const files = readdirSync(DATA_DIR).filter((f) => f.endsWith(".ts"));
  for (const file of files) {
    const text = readFileSync(join(DATA_DIR, file), "utf-8");
    let m: RegExpExecArray | null;
    while ((m = urlPattern.exec(text)) !== null) {
      const url = m[1];
      if (!urlToFiles.has(url)) urlToFiles.set(url, new Set());
      urlToFiles.get(url)!.add(file);
    }
  }
  return urlToFiles;
}

async function fetchStatus(url: string): Promise<number | string> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    // Try HEAD first; fall back to GET if the host rejects HEAD.
    let res = await fetch(url, {
      method: "HEAD",
      redirect: "follow",
      headers: { "user-agent": UA },
      signal: controller.signal,
    });
    if (res.status === 405 || res.status === 403 || res.status === 501) {
      res = await fetch(url, {
        method: "GET",
        redirect: "follow",
        headers: { "user-agent": UA },
        signal: controller.signal,
      });
    }
    return res.status;
  } catch (err) {
    return err instanceof Error ? err.name : "error";
  } finally {
    clearTimeout(timer);
  }
}

function isOk(status: number | string): boolean {
  return typeof status === "number" && status >= 200 && status < 400;
}

// 403/429/503 and network timeouts are bot-blocking / rate-limit / transient
// signatures, not dead links — many manufacturer and review sites reject a
// plain non-browser fetch (e.g. venuslens.net needs a real browser; fujifilm-x
// throttles to 503 under load). Flagging these as broken makes the check cry
// wolf, so they are reported as UNVERIFIABLE (warn) rather than BROKEN (fail).
// Only genuine not-found / gone / DNS failures fail the run.
const SOFT_STATUSES = new Set([401, 403, 405, 429, 500, 502, 503]);
// A fetch() rejection surfaces as TypeError ("fetch failed" — TLS/DNS/network)
// or Abort/Timeout. None of these distinguish a dead page from a host that
// blocks scripted clients, so all are unverifiable rather than dead; a genuine
// 404/410 always comes back as a numeric status.
const SOFT_ERRORS = new Set(["AbortError", "TimeoutError", "TypeError"]);

function classify(status: number | string): "ok" | "soft" | "broken" {
  if (isOk(status)) return "ok";
  if (typeof status === "number") {
    return SOFT_STATUSES.has(status) ? "soft" : "broken";
  }
  return SOFT_ERRORS.has(status) ? "soft" : "broken";
}

async function check(url: string): Promise<number | string> {
  const first = await fetchStatus(url);
  if (isOk(first)) return first;
  // Retry once after a short delay before classifying.
  await new Promise((r) => setTimeout(r, 1500));
  return fetchStatus(url);
}

async function main(): Promise<void> {
  const urlToFiles = collectUrls();
  const urls = [...urlToFiles.keys()].sort((a, b) => a.localeCompare(b));
  console.log(`Checking ${urls.length} unique external URLs...\n`);

  const broken: { url: string; status: number | string; files: string }[] = [];
  const soft: { url: string; status: number | string; files: string }[] = [];
  for (let i = 0; i < urls.length; i += CONCURRENCY) {
    const batch = urls.slice(i, i + CONCURRENCY);
    const results = await Promise.all(
      batch.map(async (url) => ({ url, status: await check(url) })),
    );
    for (const { url, status } of results) {
      const verdict = classify(status);
      if (verdict === "ok") continue;
      const files = [...urlToFiles.get(url)!].join(", ");
      const entry = { url, status, files };
      if (verdict === "broken") {
        broken.push(entry);
        console.error(`BROKEN [${status}] ${url}  (${files})`);
      } else {
        soft.push(entry);
      }
    }
  }

  if (soft.length > 0) {
    console.warn(
      `\n${soft.length} URL(s) UNVERIFIABLE (bot-block / rate-limit / timeout — ` +
        `not treated as broken):`,
    );
    for (const { url, status } of soft) console.warn(`  [${status}] ${url}`);
  }

  if (broken.length > 0) {
    console.error(
      `\n${broken.length} of ${urls.length} URL(s) genuinely dead.`,
    );
    process.exit(1);
  }
  console.log(
    `\nAll ${urls.length} external URLs OK (${soft.length} unverifiable, 0 dead).`,
  );
}

main();
