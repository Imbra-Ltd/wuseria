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

## 2. Data operations

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
(lab/field) and trust (1-3) ratings. Top sources:

| Trust 3 | Methodology |
|---------|-------------|
| LensRentals | Lab — optical bench MTF |
| LensTip | Lab — Imatest MTF charts |
| OpticalLimits | Lab — Imatest MTF |
| Dustin Abbott | Field — systematic + lab hybrid |
| DPReview | Field — comprehensive |
| Phillip Reeve | Field — manual focus specialist |

**Do not use:** Ken Rockwell — not a trusted data source.

### 2.6 Score a lens

Prerequisite: the lens must have reviews from at least one trust 3
source. See ADR-014 for the full rubric and reference scorings.

**Step 1 — Identify sources**

Search for LensTip, OpticalLimits, and Dustin Abbott reviews of
the lens. Check if the optical formula changed between versions
(e.g. XF 27mm f/2.8 R WR uses the same optics as the original).

**Step 2 — Collect data per field**

Run targeted per-field searches — one search per optical field, not
one broad query. For slow sites (LensTip), search snippets return
cached data even when direct fetch times out.

Fields to collect (all 0-2 scale, 0.5 steps):

| Field | Source type | How to score |
|-------|-----------|--------------|
| centerStopped | lpmm at sweet spot | % of sensor max (see ADR-014) |
| cornerStopped | lpmm at sweet spot | % of sensor max |
| centerWideOpen | lpmm at max aperture | % of sensor max |
| cornerWideOpen | lpmm at max aperture | % of sensor max (often missing) |
| astigmatism | % S/T difference | < 5% = 2.0, 5-10% = 1.5, etc. |
| coma | Point-source test only | Qualitative word mapping |
| sphericalAberration | Focus shift test | Qualitative word mapping |
| longitudinalCA | Colour fringing test | Qualitative word mapping |
| lateralCA | % at 70% from center | LensTip scale (< 0.04% = 2.0) |
| distortion | % RAW uncorrected | < 0.3% = 2.0, 0.3-1.0% = 1.5, etc. |
| vignettingWideOpen | EV at max aperture, RAW | < 0.5 = 2.0, 0.5-1.0 = 1.5, etc. |
| vignettingStopped | EV at f/5.6-f/8, RAW | Same scale |
| bokeh | Qualitative assessment | Word mapping |
| flareResistance | Qualitative assessment | Word mapping |

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
2. Add reference scoring table to ADR-014, sorted by focal length
3. Run `npm run check:all` to verify

**Step 6 — Verify**

Check that the scored lens appears in the Genre Guide for relevant
genres (once genre formulas are implemented).

### 2.7 Lighthouse CI

Lighthouse runs automatically on every PR against 4 key pages
(`/`, `/lenses/`, `/cameras/`, `/genre/`). Configuration is in
`lighthouserc.json`.

| Category | Threshold | Level |
|----------|-----------|-------|
| Performance | >= 80 | error |
| Accessibility | >= 90 | warn |
| SEO | >= 90 | warn |
| Best Practices | >= 90 | warn |

Results are uploaded as GitHub Actions artifacts. To run locally:

```bash
npm run build
npx @lhci/cli autorun --config lighthouserc.json
```

## 3. Maintenance

### 3.1 Update quality conventions

```bash
git submodule update --remote docs/solid-ai-templates
git add docs/solid-ai-templates
git commit -m "chore: bump solid-ai-templates submodule"
```

### 3.2 Update architecture decisions

1. Create an ADR in `docs/decisions/` using the format: context, decision, alternatives, consequences
2. ADRs are immutable once merged — create a new ADR to supersede an old one

### 3.3 Run the prototype

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

## 4. Release and deploy

### 4.1 Release

```bash
git checkout -b chore/release-vA.B.C
# Bump version in package.json to A.B.C
git add package.json
git commit -m "chore: release vA.B.C"
git push -u origin chore/release-vA.B.C
gh pr create --title "chore: release vA.B.C" --body "Release vA.B.C"
gh pr merge --merge
git checkout main && git pull
git tag vA.B.C && git push origin vA.B.C
git branch -d chore/release-vA.B.C
git push origin --delete chore/release-vA.B.C
```

### 4.2 Deploy

Deployment is automated via GitHub Actions on push to `main`. No manual steps
required.
