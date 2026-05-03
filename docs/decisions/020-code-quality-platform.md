# ADR-020: Code Quality Platform

## Status

Decided — defer adoption until multi-contributor

## Context

`base/quality.md` requires cognitive complexity ≤ 15 enforced by static analysis.
For solo development, `eslint-plugin-sonarjs` covers this. The question is whether
a full platform (SonarCloud, Codacy, CodeClimate) is needed now or later.

## Options Considered

| Criteria                   | SonarCloud                        | Codacy              | CodeClimate       |
| -------------------------- | --------------------------------- | ------------------- | ----------------- |
| Cognitive complexity       | Yes (native)                      | Yes (via engines)   | Yes (limited)     |
| Duplication detection      | Yes                               | Yes                 | Yes               |
| PR decorations             | Yes                               | Yes                 | Yes               |
| Dashboard / trends         | Best                              | Good                | Good              |
| Free for open-source       | Yes                               | Yes                 | Yes (OSS only)    |
| Free for private repos     | Up to 500 LOC new/edit per PR     | Free tier available | No                |
| GitHub Actions integration | Native action                     | Native action       | Native action     |
| Setup complexity           | Medium (sonar-project.properties) | Low (auto-detect)   | Low (auto-detect) |
| ESLint rule overlap        | High — duplicates sonarjs plugin  | Medium              | Low               |

## Decision

**Defer adoption.** Current tooling is sufficient for solo development:

- `eslint-plugin-sonarjs` enforces cognitive complexity and detects code smells
- CodeQL covers security scanning (ADR pending, added in this session)
- Vitest coverage thresholds gate test quality
- Lighthouse CI gates performance

**Adoption trigger:** When the project has 3+ regular contributors, adopt SonarCloud
(best dashboard and complexity analysis). At that point, remove `eslint-plugin-sonarjs`
to avoid duplicate analysis.

## Consequences

- No additional CI cost or complexity now
- Team onboarding will require SonarCloud setup when the trigger is met
- `eslint-plugin-sonarjs` continues as the solo-dev bridge
