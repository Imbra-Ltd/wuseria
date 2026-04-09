# Playbook

Operational reference for common tasks.

## Add a new lens

1. Add an entry to `src/data/lenses.ts` following the `Lens` interface
2. All boolean fields use `is`/`has` prefix (e.g. `hasAutofocus`, `isWeatherSealed`)
3. Price in USD, rounded to nearest $250
4. Run `npm run lint` to verify

## Add a new camera

1. Add an entry to `src/data/cameras.ts` following the `Camera` interface
2. Same boolean naming and price conventions as lenses
3. Run `npm run lint` to verify

## Add a new accessory

1. Choose the correct sub-interface in `src/types/accessory.ts` by `category`
2. Add an entry to `src/data/accessories.ts` (when created)
3. If no existing category fits, add a `GenericAccessory` entry

## Update quality conventions

1. Update the submodule: `git submodule update --remote docs/solid-ai-templates`
2. Review changes and commit the updated submodule pointer

## Update architecture decisions

1. Create an ADR in `docs/decisions/` using the format: context, decision, alternatives, consequences
2. Reference the ADR from `docs/architecture.md` if relevant

## Deploy

Deployment is automated via GitHub Actions on push to `main`. No manual steps required.
