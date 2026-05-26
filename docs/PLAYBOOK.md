# Playbook

Operational reference for common tasks.

## 1. Git workflow

### 1.1 Start a new feature

```bash
git checkout main && git pull
git checkout -b feat/description
```

### 1.2 Commit changes

```bash
npm run lint
git add <files>
git commit -m "feat: description"
```

Commit prefixes: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `style:`,
`test:`. Subject line under 80 characters, imperative mood.

### 1.3 Create a pull request

```bash
git push -u origin feat/description
gh pr create --title "feat: description" --body "## Summary\n- ..."
```

### 1.4 Merge and clean up

```bash
gh pr merge <number> --merge
git checkout main && git pull
git branch -d feat/description
git push origin --delete feat/description
```

### 1.5 List open issues

```bash
gh issue list --state open
gh issue list --label epic --state open
```

### 1.6 Close an issue from a PR

Reference the issue in the PR body with `Closes #<number>`. GitHub closes it
automatically on merge.

## 2. Domain operations

### 2.1 Add a new lens

1. Add an entry to `src/data/lenses.ts` following the `Lens` interface
2. All boolean fields use `is`/`has` prefix (e.g. `hasAutofocus`, `isWeatherSealed`)
3. Price in USD, rounded to nearest $250
4. Only fill optical quality fields if data comes from a trusted source (see 2.4)
5. Leave optical fields empty for lenses without trusted data — they will
   appear in the Lens Explorer but be excluded from the Genre Guide
6. Run `npm run lint` to verify

### 2.2 Add a new camera

1. Add an entry to `src/data/cameras.ts` following the `Camera` interface
2. Same boolean naming and price conventions as lenses
3. Run `npm run lint` to verify

### 2.3 Add a new accessory

1. Choose the correct sub-interface in `src/types/accessory.ts` by `category`
2. Add an entry to `src/data/accessories.ts` (when created)
3. If no existing category fits, add a `GenericAccessory` entry

### 2.4 Scoring data policy

Only score lenses that have optical data from trusted review sources. Do not
guess or estimate optical quality — showing nothing is better than showing
wrong data.

- **Lens Explorer** — shows all lenses, sortable by specs. No scoring needed.
- **Genre Guide** — shows only lenses with optical data. Lenses with empty
  optical fields are excluded entirely.
- Scoring functions return `null` when optical fields are missing.

### 2.5 Trusted review sources

See `src/data/reviews.ts` for the full directory with methodology
(lab/field) and trust (1-3) ratings. Trust-3 sources:

| Trust 3             | Methodology                     |
| ------------------- | ------------------------------- |
| LensRentals         | Lab — optical bench MTF         |
| LensTip             | Lab — Imatest MTF charts        |
| OpticalLimits       | Lab — Imatest MTF               |
| DxOMark             | Lab — perceptual megapixel      |
| The Digital Picture | Lab — ISO 12233 chart           |
| ePHOTOzine          | Lab — Imatest MTF               |
| ColorFoto           | Lab — proprietary bench         |
| Dustin Abbott       | Field — systematic + lab hybrid |
| DPReview            | Field — comprehensive           |
| Phillip Reeve       | Field — manual focus specialist |
| Lloyd Chambers      | Field — systematic high-res     |
| Lonely Speck        | Field — astrophotography        |

**Do not use:** Ken Rockwell — not a trusted data source.

### 2.6 Score a lens

Prerequisite: the lens must have reviews from at least one trust 3
source. See ADR-014 for the full rubric and reference scorings.

**Step 1 — Identify sources**

Search ALL trust-3 sources for the lens before proceeding:

- Lab (trust 3): LensRentals, LensTip, OpticalLimits, DxOMark, The Digital Picture, ePHOTOzine, ColorFoto
- Field (trust 3): Dustin Abbott, DPReview, Phillip Reeve, Lloyd Chambers, Lonely Speck

Do not skip sources — missing one can leave scoreable fields empty
(e.g. Dustin Abbott provided astigmatism + bokeh data for the
Viltrox 9mm that two other sources missed).

Check if the optical formula changed between versions
(e.g. XF 27mm f/2.8 R WR uses the same optics as the original).

**Step 2 — Collect data per field**

Run targeted per-field searches — one search per optical field, not
one broad query. For slow sites (LensTip), search snippets return
cached data even when direct fetch times out.

Fields to collect (all 0-2 scale, 0.5 steps):

| Field               | Source type             | How to score                       |
| ------------------- | ----------------------- | ---------------------------------- |
| centerStopped       | lpmm at sweet spot      | % of sensor max (see ADR-014)      |
| cornerStopped       | lpmm at sweet spot      | % of sensor max                    |
| centerWideOpen      | lpmm at max aperture    | % of sensor max                    |
| cornerWideOpen      | lpmm at max aperture    | % of sensor max (often missing)    |
| astigmatism         | % S/T difference        | < 5% = 2.0, 5-10% = 1.5, etc.      |
| coma                | Point-source test only  | Qualitative word mapping           |
| sphericalAberration | Focus shift test        | Qualitative word mapping           |
| longitudinalCA      | Colour fringing test    | Qualitative word mapping           |
| lateralCA           | % at 70% from center    | LensTip scale (< 0.04% = 2.0)      |
| distortion          | % RAW uncorrected       | < 0.3% = 2.0, 0.3-1.0% = 1.5, etc. |
| vignettingWideOpen  | EV at max aperture, RAW | < 0.5 = 2.0, 0.5-1.0 = 1.5, etc.   |
| vignettingStopped   | EV at f/5.6-f/8, RAW    | Same scale                         |
| bokeh               | Qualitative assessment  | Word mapping                       |
| flareResistance     | Qualitative assessment  | Word mapping                       |

Red flags: fast lenses (f/2 or wider) should have longitudinalCA,
sphericalAberration, and coma data. Wide-angle lenses should have
lateralCA and distortion data. If a field that should be significant
is missing, search specifically before accepting undefined.

**Step 3 — Apply rubric**

For each field, apply the threshold from ADR-014. Use only discrete
values: 0, 0.5, 1.0, 1.5, 2.0. When sources disagree, use the
highest-trust source. When ambiguous, round conservative (lower).

If a field has no data from any source, leave it undefined. Do not
infer from related fields or optical construction alone.

**Step 4 — Fallback sources (only when no lab/field data exists)**

- Official MTF chart → astigmatism only (S/M divergence)
- Optical construction + zero complaints → sphericalAberration,
  CA (not coma, bokeh, or flare)

**Step 5 — Write the data**

1. Add optical fields + `sweetSpotAperture` + `reviewSources` to the
   lens entry in `src/data/lenses.ts`
2. Add reference scoring table to `docs/optical-specs/<slug>/scoring-log.md`
3. If astigmatism was scored from an official MTF chart, save the chart
   image and a companion `.md` analysis in `docs/mtf-charts/`
4. Run `npm run validate` to verify

**Step 6 — Verify**

Check that the scored lens appears in the Genre Guide for relevant
genres (once genre formulas are implemented).

### 2.7 Utility scripts

**Fetch a web page (four-tier auto-escalation):**

```bash
py tools/fetch-page.py <url>              # auto mode: urllib → Playwright → Nodriver → UC
py tools/fetch-page.py <url> --html       # raw HTML output
py tools/fetch-page.py <url> --js         # force Playwright (JS-rendered pages)
py tools/fetch-page.py <url> --nodriver   # force Nodriver (headed Chrome, bot bypass)
py tools/fetch-page.py <url> --uc         # force SeleniumBase UC (headless fallback)
py tools/fetch-page.py <url> --no-cache   # bypass cache, fetch fresh
py tools/fetch-page.py --batch urls.txt --nodriver --output-dir out/  # batch mode
```

Responses are cached in `.cache/fetch/`. See `tools/FETCH-PAGE.md` for details.

**Audit spec field coverage per brand:**

```bash
npx tsx scripts/audit-brand.ts              # all brands summary
npx tsx scripts/audit-brand.ts Fujifilm     # single brand detail
```

**Fetch Fujifilm optical specs, images, and coatings (Playwright):**

```bash
py tools/fujifilm/fetch_specs.py                    # fetch all missing data
py tools/fujifilm/fetch_specs.py --dry-run           # list what would be fetched
py tools/fujifilm/fetch_specs.py --filter gf         # filter by model substring
py tools/fujifilm/fetch_specs.py --specs-only        # only extract specs text
py tools/fujifilm/fetch_specs.py --images-only       # only download images
py tools/fujifilm/fetch_specs.py --coatings-only     # only extract coatings
py tools/fujifilm/audit.py                           # audit data completeness
py tools/fujifilm/audit.py --missing                 # show only incomplete lenses
```

**Fetch Samyang optical specs, MTF charts, and construction diagrams (urllib):**

```bash
py tools/samyang/fetch_specs.py                    # fetch all (specs + images)
py tools/samyang/fetch_specs.py --dry-run           # list lenses without fetching
py tools/samyang/fetch_specs.py --filter 12mm       # filter by model substring
py tools/samyang/fetch_specs.py --specs-only        # only extract specs text
py tools/samyang/fetch_specs.py --images-only       # only download images
py tools/samyang/audit.py                           # audit data completeness
py tools/samyang/audit.py --missing                 # show only incomplete lenses
```

**Fetch Samyang MTF charts:**

```bash
py scripts/fetch-samyang-mtf.py             # fetch all to docs/mtf-charts/
py scripts/fetch-samyang-mtf.py --seq 351   # fetch one by product seq
py scripts/fetch-samyang-mtf.py --dry-run   # list without downloading
py scripts/fetch-samyang-mtf.py --temp      # download to temp/ (testing)
```

**Fetch Sigma optical specs, MTF charts, and construction diagrams (urllib):**

```bash
py tools/sigma/fetch_specs.py                    # fetch all (specs + images)
py tools/sigma/fetch_specs.py --dry-run           # list lenses without fetching
py tools/sigma/fetch_specs.py --filter 12mm       # filter by model substring
py tools/sigma/fetch_specs.py --specs-only        # only extract specs text
py tools/sigma/fetch_specs.py --images-only       # only download images
py tools/sigma/audit.py                           # audit data completeness
py tools/sigma/audit.py --missing                 # show only incomplete lenses
```

**Fetch Viltrox optical specs and download images (Shopify JSON + HTML scraping):**

```bash
py tools/viltrox/fetch_specs.py                    # fetch all specs from Shopify API
py tools/viltrox/fetch_specs.py --dry-run           # list lenses without fetching
py tools/viltrox/fetch_specs.py --filter 13mm       # filter by model substring
py tools/viltrox/download_images.py                 # download all theme images to cache
py tools/viltrox/download_images.py --dry-run       # list image URLs only
py tools/viltrox/download_images.py --filter 27mm   # filter by model substring
py tools/viltrox/audit.py                           # audit data completeness
py tools/viltrox/audit.py --missing                 # show only incomplete lenses
```

**Fetch Tamron optical specs (urllib, dual-page parsing — main + /spec.html):**

```bash
py tools/tamron/fetch_specs.py                    # fetch all specs + images
py tools/tamron/fetch_specs.py --dry-run           # list lenses without fetching
py tools/tamron/fetch_specs.py --filter 17-70mm    # filter by model substring
py tools/tamron/audit.py                           # audit data completeness
py tools/tamron/audit.py --missing                 # show only incomplete lenses
```

**Fetch Tokina optical specs (urllib, alt-text scraping):**

```bash
py tools/tokina/fetch_specs.py                    # fetch all specs + images
py tools/tokina/fetch_specs.py --dry-run           # list lenses without fetching
py tools/tokina/fetch_specs.py --filter 23mm       # filter by model substring
py tools/tokina/audit.py                           # audit data completeness
py tools/tokina/audit.py --missing                 # show only incomplete lenses
```

**Fetch Carl Zeiss Touit PDF datasheets (discontinued lenses, no live pages):**

```bash
py tools/zeiss/fetch_specs.py                     # download all PDF datasheets
py tools/zeiss/fetch_specs.py --dry-run            # list lenses without downloading
py tools/zeiss/fetch_specs.py --filter 12mm        # filter by model substring
py tools/zeiss/audit.py                            # audit data completeness
py tools/zeiss/audit.py --missing                  # show only incomplete lenses
```

Note: Zeiss MTF charts and construction diagrams must be extracted manually from the downloaded PDFs.

**Fetch TTartisan optical specs (urllib, spec table + prose parsing):**

```bash
py tools/ttartisan/fetch_specs.py                    # fetch all specs + images
py tools/ttartisan/fetch_specs.py --dry-run           # list lenses without fetching
py tools/ttartisan/fetch_specs.py --filter 23mm       # filter by model substring
py tools/ttartisan/fetch_specs.py --specs-only        # only extract specs text
py tools/ttartisan/fetch_specs.py --images-only       # only download images
py tools/ttartisan/audit.py                           # audit data completeness
py tools/ttartisan/audit.py --missing                 # show only incomplete lenses
```

Note: TTartisan pages use two site patterns — main site (ttartisan.com) with
query-param routing and Shopify store (ttartisan.store). Some pages embed
Shopify CDN images not detectable by the scraper. Some older pages use
legacy timestamp URLs instead of named Specification-\*.webp files.
Construction diagrams are authoritative for special elements — page text
often omits glass types that diagrams show.

**Fetch Venus Laowa optical specs (SeleniumBase UC mode — Cloudflare bypass):**

```bash
py tools/venus/fetch_specs.py                    # fetch all specs + images
py tools/venus/fetch_specs.py --dry-run           # list lenses without fetching
py tools/venus/fetch_specs.py --filter 10mm       # filter by model substring
py tools/venus/fetch_specs.py --specs-only        # only extract specs text
py tools/venus/fetch_specs.py --images-only       # only download images
py tools/venus/audit.py                           # audit data completeness
py tools/venus/audit.py --missing                 # show only incomplete lenses
```

Note: venuslens.net uses Cloudflare Turnstile which blocks plain urllib and
Playwright. Requires `py -m pip install seleniumbase` (installs Undetected
Chrome driver). Runs headed (non-headless) — a browser window will open
briefly per page. Some construction diagrams use Chinese filenames not
detectable by the tool; manual page inspection may find additional images.

**Extract MTF readings from chart PNGs:**

Skeleton tool (recommended — requires Python + scikit-image + opencv-python):

```bash
py tools/mtf-extract-skeleton.py docs/mtf-charts/samyang-35mm-f1-2.png
py tools/mtf-extract-skeleton.py docs/mtf-charts/sigma-56mm-f1-4-dc-dn-c.png
py tools/mtf-extract-skeleton.py docs/mtf-charts/samyang-*.png   # batch
```

Auto-detects chart type (Samyang 4-color / Sigma solid+dashed). Uses
color isolation → skeletonization → connected components for S/M
classification. Handles occlusion fill, auto grid step detection (APS-C
2.5mm / full-frame 5mm), and M-value interpolation. Copy the TypeScript
output into `src/data/mtf-readings.ts`.

Comparison mode (Samyang only — validates against old pixel-scan tool):

```bash
py tools/mtf-extract-skeleton.py --compare docs/mtf-charts/samyang-35mm-f1-2.png
```

Legacy tools (Pillow only, no scikit-image needed):

```bash
py tools/mtf-extract-samyang.py docs/mtf-charts/samyang-35mm-f1-2.png
py tools/mtf-extract-sigma.py docs/mtf-charts/sigma-16mm-f1-4-dc-dn-c.png
```

**List unscored lenses:**

```bash
npx tsx scripts/list-unscored.ts           # list all lenses without optical scores
```

**Compute genre marks:**

```bash
npx tsx scripts/compute-marks.ts print      # print all computed marks
npx tsx scripts/compute-marks.ts patch       # patch lenses.ts with marks
```

### 2.8 Fill and verify tech specs per brand

#### Phase 1 — Prepare

1. **Verify the brand's full lineup** — confirm every X-mount and GFX lens
   the brand offers before researching individual specs. Cross-reference
   official catalog, retailers (B&H, Adorama), and
   [alikgriffin.com](https://alikgriffin.com/a-complete-list-of-fujifilm-x-mount-lenses/).
   Create a separate issue for any missing lenses.
2. **Audit gaps** — run `npx tsx scripts/audit-brand.ts <Brand>`
3. **Run extraction tool** if available: `py tools/<brand>/fetch_specs.py`

#### Phase 2 — Research each lens

4. **Generate research URLs** — `py tools/lookup.py "<lens name>"`
5. **Check each source** and record result in `specs-log.md` (found / not found / 404 / paywall).
   Every specs-log MUST include a row for at least these five sources:
   - Official manufacturer page
   - LensTip (`py tools/lenstip/search.py "<lens>"` resolves the page ID)
   - Radojuva
   - DPReview
   - Google Image Search (construction diagram + MTF chart)
6. **Verify** extracted data against diagrams and official pages — element/group
   counts, special elements, coatings (including protective), X-mount dimensions

#### Phase 3 — Commit per lens

7. Update `specs-log.md` FIRST — the specs-log is the primary deliverable
8. Edit `lenses.ts` — apply the verified data
9. Confirm both files updated before moving to the next lens
10. Run `npm run validate`
11. If adding `maxMagnification` to a scored lens, also add `macro` genre mark

#### Maintenance

- **Audit false negatives** — `py tools/lenstip/audit_specslog.py --fix`
- **Rebuild LensTip index** quarterly — `py tools/lenstip/build_index.py`

#### Source reference (priority order)

| Source                        | Best for                                  | Notes                                  |
| ----------------------------- | ----------------------------------------- | -------------------------------------- |
| Official manufacturer         | Dimensions, filter thread, build features | Always check first                     |
| DPReview                      | Comprehensive specs incl. magnification   | Archived but still available           |
| LensTip                       | maxMagnification on budget lenses         | Opaque numeric IDs — use the index     |
| Radojuva                      | Hands-on magnification measurements       | Multi-language, search all variants    |
| digitalkamera.de              | Dimensions                                | Rarely has magnification               |
| cameradecision.com            | Spec comparison                           | 403s on direct fetch, use Playwright   |
| Mobile01                      | Construction diagrams, Chinese brands     | Requires SeleniumBase UC               |
| Photography Life              | Spec tables, diagrams, special elements   | Predictable URL pattern                |
| Dustin Abbott / Phillip Reeve | Trust-3 field measurements                | Thorough optical analysis              |
| Duclos Lenses                 | Cinema lens specs                         | Length, weight, min focus              |
| Google Image Search           | Construction diagrams, MTF charts         | Text searches miss non-English sources |

#### Caveats

- **LensTip IDs:** URL names are ignored; only the numeric ID matters. Verify
  `Manufacturer` and `Model` on the page — wrong IDs redirect silently.
- **Image filenames:** do not filter by filename keywords — news sites use
  generic names (e.g. `APO200F14-lens.jpg` for a combined diagram + MTF).
  For pages with < 10 images, visually check all content images.
- **Mount variants:** if lenses share optical design across mounts, update
  BOTH specs-logs.
- **alikgriffin.com tables:** AJAX-loaded (Ninja Tables plugin), not in page
  HTML. Use the admin-ajax API endpoint or ask the user to paste the table.

## 3. Quality

### 3.1 Validate pipeline

The full quality gate runs all checks in sequence. Run before every commit:

```bash
npm run validate
```

Pipeline steps (exits on first failure):

| Step       | Command               | What it checks                                    |
| ---------- | --------------------- | ------------------------------------------------- |
| Lint       | `npm run lint`        | ESLint + sonarjs — code smells, unused vars       |
| Format     | `npm run format`      | Prettier — consistent style                       |
| Type check | `npm run check`       | astro check — `.astro` files and TypeScript types |
| Test       | `npm test`            | Vitest — unit + component tests with coverage     |
| Build      | `npm run build`       | Astro build — full static site generation         |
| Link check | `npm run check:links` | Trailing slash validation on internal links       |

### 3.2 Pre-commit hooks (husky + lint-staged)

Every commit is gated by `.husky/pre-commit`. Runs automatically — no manual
step needed.

**What runs:**

1. `gitleaks protect --staged` — blocks commits containing secrets (skipped if
   gitleaks is not installed locally)
2. `lint-staged` — runs per file type on staged files only:
   - `*.{ts,tsx}` — `eslint --fix` + `prettier --write`
   - `*.astro` — `prettier --write`
   - `*.{json,md,css}` — `prettier --write`

Configuration: `lint-staged` key in `package.json`, hook in `.husky/pre-commit`.

### 3.3 Formatting (Prettier)

Prettier owns all formatting — no style debates in code review. Runs at all
three quality gate layers (editor on save, pre-commit via lint-staged, CI via
`npm run format`).

```bash
npm run format              # check (CI mode, exits non-zero on diff)
npx prettier --write <file> # fix a single file
```

Configuration: `.prettierrc` + `prettier-plugin-astro` for `.astro` files.

### 3.4 Type checking (astro check)

Validates `.astro` files, TypeScript types, and content schemas. Part of the
validate pipeline.

```bash
npm run check
```

Catches type errors that ESLint and the TypeScript compiler miss in `.astro`
files — Astro's template syntax requires its own checker.

### 3.5 Testing (Vitest)

**Run tests (single run with coverage):**

```bash
npm test
```

Coverage text summary prints to the console. Threshold enforcement: statements
85%, branches 80%, functions 90%, lines 85%.

**Watch mode (development):**

```bash
npm run test:watch
```

**Generate local reports (coverage + test results):**

```bash
npm run test:report
```

Generates:

- `reports/tests/index.html` — interactive HTML test report (pass/fail, timing, filter by file)
- `reports/coverage/index.html` — interactive HTML coverage map (click into files, see uncovered lines)

Open either in a browser. The `reports/` directory is gitignored.

**Writing tests:**

- Test factories in `src/test/factories.ts` — use `makeLens`, `makeExplorerLens`,
  `makeCamera` instead of inline objects
- `makeExplorerLens` mirrors the `ExplorerLens` shape (booleans default to
  `undefined`, matching real data)
- Use `getAllByText` for explorer content (table + cards both render)
- Use `getByRole("combobox", { name: /label/i })` for select filters
- Use `screen.getAllByRole("button", { name: "Yes" })` for boolean chip filters

**Test structure:**

| File                                                                | Covers                                         |
| ------------------------------------------------------------------- | ---------------------------------------------- |
| `src/utils/scoring.test.ts`                                         | Genre scoring, OQ, helpers, field picker       |
| `src/utils/formatting.test.ts`                                      | Shutter + FL formatting                        |
| `src/utils/slug.test.ts`                                            | URL slug generation                            |
| `src/hooks/useSort.test.ts`                                         | Sort hook (strings, numbers, booleans, nulls)  |
| `src/hooks/useUrlFilters.test.ts`                                   | URL filter sync hook                           |
| `src/data/lenses.test.ts`                                           | Data validation (uniqueness, ranges, booleans) |
| `src/data/genres.test.ts`                                           | Genre config validation                        |
| `src/components/interactive/LensExplorer/LensExplorer.test.tsx`     | Lens filters + sort                            |
| `src/components/interactive/CameraExplorer/CameraExplorer.test.tsx` | Camera filters + sort                          |
| `src/components/interactive/GenreGuide/GenreGuide.test.tsx`         | Genre tabs, filters, matrices                  |
| `src/components/interactive/GenreGuide/exposure.test.ts`            | Exposure calculations                          |

### 3.6 Code quality (eslint-plugin-sonarjs + unicorn)

SonarQube-equivalent code smell detection runs via ESLint at all three quality
gate layers (editor, pre-commit, CI). Type-checked linting is enabled via
`projectService` — 67 sonarjs rules that require type information are active.
Configuration is in `eslint.config.js`.

Explicitly enabled rules:

| Rule                               | What it catches                             |
| ---------------------------------- | ------------------------------------------- |
| `cognitive-complexity`             | Functions exceeding complexity threshold    |
| `no-nested-conditional`            | Deeply nested if/switch statements          |
| `no-nested-template-literals`      | Template literals inside template literals  |
| `redundant-type-aliases`           | Type aliases that add no information        |
| `unicorn/no-zero-fractions`        | Unnecessary `.0` in numeric literals        |
| `unicorn/prefer-number-properties` | `parseInt()` instead of `Number.parseInt()` |

Also enforced via ESLint core: `max-depth: 3`, `no-console`.
Also enforced via `sonarjs.configs.recommended`: 67 type-checked rules including
`no-alphabetical-sort`, `prefer-read-only-props`, `prefer-regexp-exec`.

```bash
npm run lint
```

### 3.7 Site quality (Lighthouse)

Lighthouse runs automatically on every PR against 4 key pages
(`/`, `/lenses/`, `/cameras/`, `/genre/`). Configuration is in
`lighthouserc.json`.

| Category       | Threshold | Level |
| -------------- | --------- | ----- |
| Performance    | >= 80     | error |
| Accessibility  | >= 90     | warn  |
| SEO            | >= 90     | warn  |
| Best Practices | >= 90     | warn  |

**Run locally:**

```bash
npm run lighthouse
```

This builds the site and runs Lighthouse against all 4 pages (3 runs each).
HTML reports are written to `reports/lighthouse/` — open any `.report.html`
in a browser for full scores, diagnostics, and opportunities.

### 3.8 Link checking (lychee)

Lychee checks for broken internal links in the built site. Runs in CI on
every PR. Requires [lychee](https://github.com/lycheeverse/lychee) installed
locally (see ONBOARDING prerequisites).

```bash
npm run build
lychee --offline --no-progress --root-dir dist dist/
```

Checks all internal links in the static output. Exits non-zero on broken links.

### 3.9 Secret scanning (gitleaks)

Gitleaks scans for accidentally committed secrets. Runs in CI on every PR.
Requires [gitleaks](https://github.com/gitleaks/gitleaks) installed locally
(see ONBOARDING prerequisites).

```bash
gitleaks detect --source . --config .gitleaks.toml
```

Scans the full repo history. Exits non-zero if secrets are found.

### 3.10 Static analysis (CodeQL)

CodeQL runs automatically on every PR via `.github/workflows/codeql.yml`.
Scans JavaScript and TypeScript for security vulnerabilities and code quality
issues. No local setup needed — GitHub-native, results appear in the Security
tab.

### 3.11 Dependency updates (Dependabot)

Dependabot opens weekly PRs for outdated npm packages and GitHub Actions.
Configuration is in `.github/dependabot.yml`. PRs are labeled `chore` + `P3`.

Review Dependabot PRs:

```bash
gh pr list --author app/dependabot
```

### 3.12 Analytics verification (Umami)

Umami Cloud tracks page views with zero cookies and no consent banner.
The script loads from `cloud.umami.is` via the base layout. Run this
manual check after changes to navigation, View Transitions, or the
analytics integration.

**Prerequisites:**

- Access to https://cloud.umami.is/ (login credentials)
- Chrome DevTools (or equivalent)

**Step 1 — Script loads:**

1. Open https://wuseria.com
2. DevTools → Network → filter `script.js`
3. Refresh the page

Expected: `cloud.umami.is/script.js` returns **200 OK**, ~5-6 KB.
No console errors.

**Step 2 — Page views register:**

1. Open the Umami dashboard → select wuseria.com → Realtime view
2. Navigate through several pages: Lenses → Cameras → Genre → Wiki →
   any individual lens detail page
3. Check the dashboard

Expected: each page path appears (`/lenses/`, `/cameras/`, `/genre/`,
`/wiki/`, `/lenses/[slug]`). Count matches pages visited.

**Step 3 — No duplicate events:**

1. DevTools → Network → clear the log
2. Click one navigation link (e.g. Cameras)
3. Filter by `cloud.umami.is`

Expected: exactly **1 `send`** request per navigation. If 2+ fire
for a single click, that's a duplicate event bug.

**Step 4 — Fresh page load:**

1. Clear the Network log
2. Type `wuseria.com` in the address bar and press Enter (full load)
3. Filter by `cloud.umami.is`

Expected: `script.js` + exactly **1 `send`** request.

**Last verified:** 2026-05-03 — all checks pass.

### 3.13 Search indexing (Google Search Console)

GSC surfaces indexing issues that require code fixes (e.g. trailing slash
inconsistencies, excluded pages, crawl errors). Run this check after routing
changes, new page types, or sitemap updates — and periodically (~monthly).

**Prerequisites:**

- Access to [Google Search Console](https://search.google.com/search-console)
  for wuseria.com

**Step 1 — Coverage check:**

1. Open GSC → Pages
2. Check "Not indexed" count and reasons

Red flags: "Page with redirect", "Duplicate without user-selected canonical",
"Excluded by noindex tag", "Crawled — currently not indexed" on pages that
should be indexed.

**Step 2 — Sitemap validation:**

1. Open GSC → Sitemaps
2. Verify `sitemap-index.xml` status is "Success"
3. Compare submitted page count with expected (currently 461 pages)

If count is off, check that `@astrojs/sitemap` is generating correctly and
no pages are accidentally excluded.

**Step 3 — URL inspection:**

For new page types or routing changes, inspect a sample URL:

1. GSC → URL Inspection → paste the URL
2. Verify: "URL is on Google" or "URL can be indexed"
3. Check canonical URL matches the page URL

**Step 4 — Core Web Vitals:**

1. GSC → Core Web Vitals
2. Check for "Poor" or "Needs improvement" URLs

Any regression is a bug — cross-reference with Lighthouse (3.7) to identify
the cause.

**Last verified:** 2026-05-14 — 106/461 pages indexed (23%), no critical
coverage issues.

### 3.14 Page performance (PageSpeed Insights)

[PageSpeed Insights](https://pagespeed.web.dev/) complements Lighthouse CI
(3.7) with real-user field data from the Chrome User Experience Report (CrUX).
Local Lighthouse runs produce lab data only — PSI adds how actual visitors
experience the site. Run after layout changes, new page types, or when GSC
(3.13) flags Core Web Vitals regressions.

**Step 1 — Test key pages:**

Run these URLs through https://pagespeed.web.dev/:

1. `https://wuseria.com/`
2. `https://wuseria.com/lenses/`
3. `https://wuseria.com/genre/`
4. A sample lens detail page (e.g. `https://wuseria.com/lenses/xf-23mm-f1-4-r/`)

**Step 2 — Check field data (CrUX):**

If field data is available, verify Core Web Vitals pass:

| Metric | Good threshold |
| ------ | -------------- |
| LCP    | < 2.5s         |
| INP    | < 200ms        |
| CLS    | < 0.1          |

If field data shows "Not enough data", rely on lab data only.

**Step 3 — Review lab diagnostics:**

Check the Opportunities and Diagnostics sections for:

- Render-blocking resources
- Unused JavaScript/CSS
- Image optimization opportunities
- Layout shift sources

Any performance score below 80 is a bug — cross-reference with Lighthouse CI
(3.7) to confirm it reproduces locally before fixing.

**Last verified:** not yet baselined.

### 3.15 Technical SEO crawl (Screaming Frog)

[Screaming Frog SEO Spider](https://www.screamingfrog.co.uk/seo-spider/) is a
desktop crawler that audits the site like a search engine. Catches redirect
chains, orphan pages, canonical mismatches, and
structured data errors. Free for up to 500 URLs (site currently has 461 pages).

**Prerequisites:**

- [Screaming Frog SEO Spider](https://www.screamingfrog.co.uk/seo-spider/)
  installed locally
- Free tier limit: 500 URLs (site currently has 461 pages). When the site
  exceeds 500, either buy a license or crawl selectively by filtering to
  specific directories (e.g. `/lenses/`, `/wiki/`)

**Step 1 — Crawl the site:**

1. Open Screaming Frog
2. Enter `https://wuseria.com/`
3. Start crawl — wait for completion

**Step 2 — Check key reports:**

| Tab              | What to check                                       |
| ---------------- | --------------------------------------------------- |
| Internal         | Response codes — no 3xx chains, no 4xx/5xx          |
| Page Titles      | No missing, duplicate, or truncated titles          |
| Meta Description | No missing or duplicate descriptions                |
| H1               | Exactly one H1 per page, no duplicates across pages |
| H2               | No skipped heading levels (H1 → H3)                 |
| Canonicals       | Every page has a self-referencing canonical         |
| Structured Data  | JSON-LD validates, no errors                        |
| Images           | No missing alt text on content images               |

**Step 3 — Check for orphan pages:**

1. Crawl Analysis → Orphan Pages
2. Cross-reference with sitemap (Configuration → Spider → Crawl → check
   "Crawl linked XML Sitemaps")

Any page in the sitemap but not linked internally is an orphan — fix the
internal linking or remove from sitemap.

**Step 4 — Export issues:**

Export findings as CSV for tracking. Issues with direct code fixes (missing
meta, broken canonicals, redirect chains) are bugs.

**Last verified:** not yet baselined.

### 3.16 SEO manual test plan

Periodic checklist covering GSC, Umami, Lighthouse, structured data, and
technical SEO spot checks. See [`docs/audits/seo-test-plan.md`](audits/seo-test-plan.md).

## 4. Maintenance

### 4.1 Update quality conventions

```bash
git submodule update --remote docs/solid-ai-templates
git add docs/solid-ai-templates
git commit -m "chore: bump solid-ai-templates submodule"
```

### 4.2 Update architecture decisions

1. Create an ADR in `docs/decisions/` using the format: context, decision, alternatives, consequences
2. ADRs are immutable once merged — create a new ADR to supersede an old one

### 4.3 Run the prototype

All prototype resources live in `docs/prototype/`. To run:

```bash
cp docs/prototype/index.html index.html
cp docs/prototype/main.jsx src/main.jsx
cp docs/prototype/App.jsx src/App.jsx
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Clean up after:

```bash
rm index.html src/main.jsx src/App.jsx
```

The prototype uses old field names (pre-migration) and is kept for reference
only. Do not commit the copied files.

## 5. Release and deploy

### 5.1 Release

```bash
# From main, with clean working directory:
npm run release -- A.B.C
```

The script validates preconditions (on main, clean tree, valid semver),
bumps `package.json`, commits, pushes, and creates a PR. After the PR
merges:

```bash
git checkout main && git pull
git tag vA.B.C && git push origin vA.B.C
git branch -d chore/release-vA.B.C
git push origin --delete chore/release-vA.B.C
```

### 5.2 Deploy

Deployment is automated via GitHub Actions on push to `main`. No manual steps
required.
