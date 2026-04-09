# Playbook

Operational reference for common tasks.

## Start a new feature

```bash
git checkout main && git pull
git checkout -b feat/description
```

## Commit changes

```bash
npm run lint
git add <files>
git commit -m "feat: description"
```

Commit prefixes: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `style:`,
`test:`. Subject line under 80 characters, imperative mood.

## Create a pull request

```bash
git push -u origin feat/description
gh pr create --title "feat: description" --body "## Summary\n- ..."
```

## Merge and clean up

```bash
gh pr merge <number> --merge
git checkout main && git pull
git branch -d feat/description
git push origin --delete feat/description
```

## Add a new lens

1. Add an entry to `src/data/lenses.ts` following the `Lens` interface
2. All boolean fields use `is`/`has` prefix (e.g. `hasAutofocus`, `isWeatherSealed`)
3. Price in USD, rounded to nearest $250
4. Only fill optical quality fields if data comes from a trusted source (see below)
5. Leave optical fields empty for lenses without trusted data — they will
   appear in the Lens Explorer but be excluded from the Genre Guide
6. Run `npm run lint` to verify

## Scoring data policy

Only score lenses that have optical data from trusted review sources. Do not
guess or estimate optical quality — showing nothing is better than showing
wrong data.

- **Lens Explorer** — shows all lenses, sortable by specs. No scoring needed.
- **Genre Guide** — shows only lenses with optical data. Lenses with empty
  optical fields are excluded entirely.
- Scoring functions return `null` when optical fields are missing.

## Trusted review sources

Ordered by measurement rigour (see `src/types/review.ts`):

1. LensRentals — optical bench MTF
2. Lenstip — lab MTF charts
3. Opticallimits — lab MTF
4. DxOMark — sensor + lens measurements
5. The Digital Picture — ISO chart comparisons
6. Dustin Abbott — field + lab
7. Imaging Resource — lab resolution/noise
8. ePHOTOzine — lab MTF
9. DPReview — comprehensive (archived)
10. Phillip Reeve — manual focus specialist

**Do not use:** Ken Rockwell — not a trusted data source. Listed in
`docs/bookmarks.md` as a competitor reference only (he ranks for per-lens
queries we want to target).

## Add a new camera

1. Add an entry to `src/data/cameras.ts` following the `Camera` interface
2. Same boolean naming and price conventions as lenses
3. Run `npm run lint` to verify

## Add a new accessory

1. Choose the correct sub-interface in `src/types/accessory.ts` by `category`
2. Add an entry to `src/data/accessories.ts` (when created)
3. If no existing category fits, add a `GenericAccessory` entry

## Update quality conventions

```bash
git submodule update --remote docs/solid-ai-templates
git add docs/solid-ai-templates
git commit -m "chore: bump solid-ai-templates submodule"
```

## Update architecture decisions

1. Create an ADR in `docs/decisions/` using the format: context, decision, alternatives, consequences
2. Reference the ADR from `docs/architecture.md` if relevant

## Run the prototype

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

## Release

```bash
git checkout -b chore/release-vA.B.C
git commit --allow-empty -m "chore: release vA.B.C"
git push -u origin chore/release-vA.B.C
gh pr create --title "chore: release vA.B.C" --body "Release vA.B.C"
gh pr merge --merge
git checkout main && git pull
git tag vA.B.C && git push origin vA.B.C
git branch -d chore/release-vA.B.C
git push origin --delete chore/release-vA.B.C
```

## Deploy

Deployment is automated via GitHub Actions on push to `main`. No manual steps required.

## List open issues

```bash
gh issue list --state open
gh issue list --label epic --state open
```

## Close an issue from a PR

Reference the issue in the PR body with `Closes #<number>`. GitHub closes it
automatically on merge.
