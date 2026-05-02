#!/usr/bin/env bash
set -euo pipefail

# Usage: npm run release -- 0.5.0
# Bumps package.json, commits, pushes, creates PR, and prints next steps.

VERSION="${1:-}"

if [ -z "$VERSION" ]; then
  echo "Usage: npm run release -- <version>"
  echo "Example: npm run release -- 0.5.0"
  exit 1
fi

if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "Error: version must be semver (e.g. 1.2.3), got: $VERSION"
  exit 1
fi

CURRENT=$(node -p "require('./package.json').version")
if [ "$CURRENT" = "$VERSION" ]; then
  echo "Error: package.json is already at $VERSION"
  exit 1
fi

BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "main" ]; then
  echo "Error: must be on main branch, currently on: $BRANCH"
  exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
  echo "Error: working directory is not clean"
  exit 1
fi

echo "Releasing v$VERSION (current: $CURRENT)"

git checkout -b "chore/release-v$VERSION"
npm version "$VERSION" --no-git-tag-version
git add package.json package-lock.json
git commit -m "chore: release v$VERSION"
git push -u origin "chore/release-v$VERSION"
gh pr create --title "chore: release v$VERSION" --body "Release v$VERSION"

echo ""
echo "PR created. After merge, run:"
echo "  git checkout main && git pull"
echo "  git tag v$VERSION && git push origin v$VERSION"
echo "  git branch -d chore/release-v$VERSION"
echo "  git push origin --delete chore/release-v$VERSION"
