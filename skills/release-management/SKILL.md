---
name: release-management
description: Use when planning releases, generating changelogs, managing semantic versioning, or automating release workflows. Covers conventional commits, semantic-release, changesets, and release train models.
---

# Release Management & Semantic Versioning

Comprehensive guidelines and automated workflows for managing software releases, semantic versioning, multi-package coordination, and zero-downtime deployment cutovers.

## When to Use This Skill

- Establishing automated versioning and changelog pipelines for libraries, services, and containers.
- Standardizing commit message conventions across teams with automated linting.
- Managing monorepo release coordination across interdependent packages.
- Designing branching strategies: Trunk-based delivery, Git-flow, or scheduled Release Trains.
- Publishing artifacts to registries (npm, PyPI, OCI/Docker) and GitHub Releases.
- Defining fail-safe rollback procedures and multi-audience release communication.

## Core Principles & Guidelines

1. **Semantic Versioning 2.0.0 (MAJOR.MINOR.PATCH)**:
   - `MAJOR` (X.0.0): Incompatible API or breaking behavioral changes.
   - `MINOR` (0.Y.0): Backward-compatible functionality additions.
   - `PATCH` (0.0.Z): Backward-compatible bug fixes and performance patches.
2. **Conventional Commits**: Every commit message must encode release intent:
   - `feat(auth): add OAuth2 PKCE flow` -> Bumps MINOR
   - `fix(billing): prevent double invoice generation` -> Bumps PATCH
   - `feat(api)!: drop legacy v1 endpoints` or `BREAKING CHANGE:` footer -> Bumps MAJOR
3. **Pre-Release Lifecycles**:
   - `alpha` (`1.2.0-alpha.1`): Internal development builds; unstable.
   - `beta` (`1.2.0-beta.1`): Feature-complete builds for staging / early adopters.
   - `rc` (`1.2.0-rc.1`): Release candidate frozen for final acceptance testing.
4. **Branching Models**:
   - *Trunk-Based*: Continuous integration to `main`, releasing on each merge via automated semantic tags with feature toggles.
   - *Release Train*: Time-boxed releases (e.g., weekly on Tuesday). Merge window closes, release branch cuts (`release/v2.4`), stabilization occurs, cherry-pick fixes only.
5. **Audience-Targeted Release Notes**:
   - *Engineers/Integrators*: Breaking changes, schema diffs, deprecation warnings, migration code snippets.
   - *End Users/Product Stakeholders*: User-facing value, performance improvements, UI enhancements, resolved bug descriptions.

## Implementation Patterns

### 1. Automated Conventional Commit Enforcement

Enforce commit standards before code lands using `commitlint` and Git hooks:

```javascript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test', 'build', 'ci', 'chore', 'revert']
    ],
    'scope-case': [2, 'always', 'lower-case'],
    'subject-case': [2, 'never', ['sentence-case', 'start-case', 'pascal-case', 'upper-case']],
    'body-max-line-length': [2, 'always', 120]
  }
};
```

### 2. Automated Versioning and Changelog with Semantic-Release

Configure continuous releases triggered from the CI pipeline on merge:

```json
{
  "branches": [
    "main",
    { "name": "next", "prerelease": true },
    { "name": "beta", "prerelease": true }
  ],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    [
      "@semantic-release/changelog",
      { "changelogFile": "CHANGELOG.md" }
    ],
    [
      "@semantic-release/npm",
      { "npmPublish": true }
    ],
    [
      "@semantic-release/github",
      {
        "assets": [{ "path": "dist/*.tgz", "label": "Package Distribution" }]
      }
    ],
    [
      "@semantic-release/git",
      {
        "assets": ["CHANGELOG.md", "package.json"],
        "message": "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}"
      }
    ]
  ]
}
```

### 3. Monorepo Multi-Package Release Coordination (Changesets)

In monorepos, use Changesets to track package bumps independently or in synchronized fixed groups:

```json
// .changeset/config.json
{
  "$schema": "https://unpkg.com/@changesets/config@3.0.0/schema.json",
  "changelog": "@changesets/cli/changelog",
  "commit": false,
  "fixed": [["@my-org/core", "@my-org/client"]],
  "access": "public",
  "baseBranch": "main",
  "updateInternalDependencies": "patch",
  "ignore": ["@my-org/internal-dev-tools"]
}
```

```bash
# Developer creates changeset entry during PR:
npx changeset
# CI release workflow runs:
npx changeset version && npx changeset publish
```

### 4. Multi-Registry Artifact Publishing Pipeline (GitHub Actions)

Publish immutable, signed artifacts using OIDC trusted publishing (no long-lived tokens):

```yaml
# .github/workflows/publish.yaml
name: Publish Artifacts
on:
  push:
    tags: ['v*.*.*']

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write # Required for PyPI / npm OIDC provenance
      contents: write
      packages: write
    steps:
      - uses: actions/checkout@v4
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build and Push Docker Image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ github.ref_name }}
            ghcr.io/${{ github.repository }}:latest
          labels: org.opencontainers.image.revision=${{ github.sha }}
```

### 5. Production Rollback and Emergency Procedures

Execute non-destructive rollbacks when regressions bypass staging:

```text
Step 1: Freeze deployment pipelines (disable automatic CI/CD triggers).
Step 2: Check database migration backward compatibility:
        - Expand/Contract: Ensure schema changes support both N and N-1 application versions.
Step 3: Route ingress/load balancer traffic back to previous stable deployment revision.
Step 4: If hotfix is required on release branch:
        git checkout -b hotfix/v2.4.1 v2.4.0
        git cherry-pick <commit-sha>
        git tag -s v2.4.1 -m "fix: resolve critical payment deadlock"
Step 5: Cherry-pick hotfix back into main branch to prevent regression.
```

## Anti-Patterns to Avoid

- **Manual Tagging**: Creating release tags (`v1.0.0`) manually on local developer machines without cryptographic signing or CI automation.
- **Floating Tags in Production**: Deploying containers using `:latest` or mutable tags. Deployments must use immutable SHAs or exact semver tags (`:v1.4.2`).
- **Breaking Changes in Minor/Patch**: Introducing subtle API field removals, signature modifications, or behavioral changes without bumping the `MAJOR` version.
- **Destructive Database Rollbacks**: Running down-migrations (`db:rollback`) in production that drop tables or columns containing active tenant data.
- **Combined Developer & Customer Release Notes**: Emitting raw git commit hashes and refactoring PRs directly to business users without translation into functional updates.

## Verification Checklist

- [ ] Commit linting fails in PR checks if commit messages do not follow Conventional Commits.
- [ ] Releases are tagged cryptographically with GPG or GitHub OIDC provenance.
- [ ] Changelogs are automatically updated and committed or posted to GitHub Releases.
- [ ] Database migrations follow expand/contract patterns so rollback to previous binary causes no downtime.
- [ ] Monorepo packages bump dependent package version constraints automatically.
- [ ] Pre-releases (`alpha`, `beta`, `rc`) are published to separate registry distribution tags (e.g., `npm publish --tag beta`).
- [ ] Rollback runbook is tested and documented with explicit RTO (Recovery Time Objective).
