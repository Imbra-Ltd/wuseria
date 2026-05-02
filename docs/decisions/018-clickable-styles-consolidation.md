# ADR-018: Clickable element style consolidation

**Status:** Accepted
**Date:** 2026-05-01

## Context

The codebase has 12 distinct clickable element styles spread across multiple
CSS Module files. Three explorer modules (LensExplorer, CameraExplorer,
AccessoriesExplorer) contain near-identical CSS for chips, filters, sort
buttons, clear buttons, and show-all buttons. Focus states are inconsistent
— some elements have `focus-visible`, some do not.

Two visual systems coexist:

1. **Accent-primary** — chips, genre tabs, clear buttons, scene items.
   Active state uses accent background with dark text.
2. **Link-primary** — link buttons, back links, learn-more links.
   Uses blue link color with accent borders on hover.

Both systems are intentional and serve different purposes: accent-primary
for in-page actions (filter, sort, select), link-primary for navigation
to other pages.

### Inventory

| Element         | Classes                                        | Duplicated across         |
| --------------- | ---------------------------------------------- | ------------------------- |
| Chip groups     | `.chip`, `.chipOn`, `.chipGroup`, `.chipLabel` | 3 explorers + GenreGuide  |
| Sort buttons    | `.sortButton`, `.sortIndicator`                | 3 explorers + GenreGuide  |
| Clear buttons   | `.clearButton`                                 | 3 explorers               |
| Filter selects  | `.filterSelect`, `.filterActive`               | 3 explorers               |
| Search input    | `.searchInput`                                 | 3 explorers               |
| Show all button | `.showAllButton`                               | 3 explorers               |
| Genre tabs      | `.genreTab`, `.genreTabActive`                 | GenreGuide only           |
| Scene list      | `.sceneItem`, `.sceneItemActive`               | GenreGuide only           |
| Link buttons    | `.link-button`                                 | 3 detail pages (scoped)   |
| Genre cards     | `.genre-card`                                  | Lens detail page (scoped) |
| Learn more      | `.learnMoreBtn`                                | GenreGuide only           |
| Back links      | `.back-link`                                   | 3 detail pages (scoped)   |

## Decision

1. **Extract shared interactive styles** into
   `src/components/interactive/shared/shared.module.css`. This module
   holds styles that are identical across multiple explorer components:
   chips, sort buttons, clear buttons, filter selects, search inputs,
   show-all buttons.

2. **Keep two button families.** Accent-primary for in-page actions,
   link-primary for navigation. Do not merge them into one.

3. **Standardize focus-visible** on all interactive elements:
   `outline: 2px solid var(--color-accent); outline-offset: 2px`.

4. **Keep GenreGuide-specific styles in GenreGuide.module.css.** Genre
   tabs, scene items, and learn-more links are unique to that component
   and do not benefit from extraction.

5. **Keep Astro scoped styles on detail pages.** Link buttons, genre
   cards, and back links are page-level styles in `.astro` files and
   are not duplicated enough to warrant extraction.

6. **Import shared styles via CSS Module composition.** Explorer
   components import class names from `shared.module.css` and pass
   them via the existing `styles` prop pattern.

## Alternatives considered

### Global utility classes in `global.css`

Add `.btn`, `.btn-accent`, `.chip` etc. to the global stylesheet.
Rejected: breaks the CSS Modules convention established in the project.
Global class names risk collisions and make it harder to trace which
component uses which style.

### Design tokens only

Keep styles in each module file but standardize spacing, colors, and
sizing via additional CSS custom properties. Rejected: does not
eliminate the 600+ lines of duplicated CSS across explorer modules.
The duplication is the primary problem.

## Consequences

- Explorer CSS module files shrink significantly (estimated ~100 lines
  each removed).
- New shared module becomes a dependency for all explorer components.
- ChipGroup component (already in `shared/`) can import its own styles
  from the shared module instead of receiving them as props.
- Future explorer components get consistent styles by importing the
  shared module.
- All interactive elements gain consistent keyboard focus indicators.
