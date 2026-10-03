---
name: dependency-management
description: Use when managing project dependencies, configuring automated update tools, handling CVE remediation, or establishing dependency governance policies. Covers Renovate, Dependabot, npm audit, pip-audit, and supply chain security.
---

# Dependency Management & Governance Guide

This skill provides engineering standards for managing open source dependencies, automating updates with Renovate and Dependabot, resolving transitive security vulnerabilities, enforcing license compliance, and securing software supply chains.

## When to Use This Skill
- Establishing automated dependency update pipelines (Renovate or GitHub Dependabot).
- Configuring deterministic lockfile enforcement and private artifact registries (Artifactory, GitHub Packages).
- Triaging and remediating Common Vulnerabilities and Exposures (CVEs) across dependencies.
- Managing monorepo dependency hoisting, workspace protocols, and single-version policies.
- Resolving transitive dependency conflicts via package manager override mechanisms.
- Auditing third-party licenses (SPDX) to ensure intellectual property compliance.

## Core Principles & Dependency Governance

### Version Pinning vs Version Ranges
| Target Artifact | Version Specification | Rationale |
| :--- | :--- | :--- |
| **Deployable Applications** | **Exact Pinning** (`1.4.2`) | Guarantees deterministic, reproducible production builds. Eliminates unexpected transitive breakage. |
| **Shared Libraries / SDKs** | **Permissive Ranges** (`^1.4.0` or `~1.4.0`) | Prevents diamond dependency conflicts and allows host applications to deduplicate sub-dependencies. |
| **Docker Base Images** | **Digest Pinning** (`node:20.11-alpine@sha256:...`) | Defends against mutable image tag poisoning and upstream upstream rebuilds. |

### Deterministic Lockfile Hygiene
- **Never Run `install` in CI**: Always use immutable install commands that fail if lockfiles are missing or out of sync:
  - Node.js: `npm ci` or `pnpm install --frozen-lockfile`
  - Python: `poetry install --sync` or `pip install --require-hashes -r requirements.txt`
  - Rust: `cargo build --locked`
  - Go: `go mod verify`
- **Lockfile Integrity**: Lockfiles (`package-lock.json`, `poetry.lock`, `pnpm-lock.yaml`, `Cargo.lock`) must be tracked in version control. Never resolve merge conflicts by deleting and regenerating lockfiles.

### Transitive Dependency Overrides
When an indirect sub-dependency has a vulnerability or bug, force resolution at the root level without waiting for intermediate package updates:
```json
// package.json (npm / pnpm / yarn)
{
  "overrides": {
    "semver": "^7.5.4",
    "got": "^11.8.5"
  }
}
```
For Python, maintain a root constraints file (`pip install -r requirements.txt -c constraints.txt`):
```text
# constraints.txt - force safe versions across all transitive trees
cryptography>=42.0.4
urllib3>=2.0.7
```

### Monorepo Dependency Strategies
- **Single Version Policy**: Enforce identical versions of third-party libraries across all workspace packages using catalog protocols:
  ```json
  // pnpm-workspace.yaml
  packages:
    - 'apps/*'
    - 'packages/*'
  catalog:
    typescript: ^5.4.0
    react: ^18.2.0
  ```
- **Workspace Protocol**: Reference internal monorepo packages via `"@org/ui": "workspace:*"` to ensure symlinks resolve locally without publishing intermediate tarballs.

### License Compliance (SPDX)
Classify allowed licenses via automated policy linters (e.g., `license-checker`, `fossa`):
- **Permissive (Approved)**: `MIT`, `Apache-2.0`, `BSD-2-Clause`, `BSD-3-Clause`, `ISC`
- **Weak Copyleft (Requires Legal Review)**: `LGPL-2.1`, `LGPL-3.0`, `MPL-2.0` (acceptable if dynamically linked without modifications)
- **Strong Copyleft (Prohibited for Commercial Proprietary Code)**: `GPL-2.0`, `GPL-3.0`, `AGPL-3.0`, `SSPL`

### Private Registry Setup
Authenticate private registries securely in CI using scoped namespaces and environment tokens:
```ini
# .npmrc
@mycompany:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
always-auth=true
```
```ini
# ~/.config/pip/pip.conf
[global]
index-url = https://__token__:${ARTIFACTORY_TOKEN}@artifactory.example.com/api/pypi/pypi-release/simple
trusted-host = artifactory.example.com
```

## Implementation Patterns & Concrete Examples

### 1. Production Renovate Configuration (`renovate.json`)
```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended", ":semanticCommits"],
  "timezone": "UTC",
  "schedule": ["before 6am on monday"],
  "prConcurrentLimit": 10,
  "packageRules": [
    {
      "matchUpdateTypes": ["minor", "patch"],
      "matchCurrentVersion": "!>=1.0.0",
      "automerge": false
    },
    {
      "matchUpdateTypes": ["patch"],
      "matchPackageNames": ["!typescript"],
      "automerge": true,
      "automergeType": "branch"
    },
    {
      "groupName": "AWS SDK monorepo",
      "matchPackagePrefixes": ["@aws-sdk/"]
    },
    {
      "groupName": "OpenTelemetry dependencies",
      "matchPackagePrefixes": ["@opentelemetry/"]
    },
    {
      "matchDepTypes": ["devDependencies"],
      "automerge": true,
      "automergeSchedule": ["at any time"]
    }
  ],
  "vulnerabilityAlerts": {
    "labels": ["security", "cve"],
    "schedule": ["at any time"]
  }
}
```

### 2. GitHub Dependabot Configuration (`.github/dependabot.yml`)
```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "04:00"
    open-pull-requests-limit: 10
    groups:
      lint-and-test:
        patterns: ["eslint*", "jest*", "prettier*"]
    ignore:
      - dependency-name: "webpack"
        update-types: ["version-update:semver-major"]
```

### 3. CVE Severity Triage & CI Gates
Enforce remediation response service-level agreements based on CVSS scoring:
| Severity | CVSS v3 Score | Target Remediation SLA | CI Pipeline Action |
| :--- | :--- | :--- | :--- |
| **Critical** | 9.0 - 10.0 | < 24 hours | Break CI build; block deployment |
| **High** | 7.0 - 8.9 | < 7 days | Break CI build; alert on-call |
| **Medium** | 4.0 - 6.9 | < 30 days | Non-blocking warning; log tracking issue |
| **Low** | 0.1 - 3.9 | < 90 days | Batch during quarterly maintenance |

Automate vulnerability audits in CI:
```yaml
# CI Audit Step
- name: Audit Node.js dependencies
  run: npx audit-ci --high --moderate=false

- name: Audit Python dependencies with pip-audit
  run: |
    pip install pip-audit
    pip-audit --desc on --fail-on-severity high
```

## Anti-Patterns to Avoid
- **Unfrozen Installs in CI**: Running `npm install` or `pip install` without `--frozen-lockfile` or `--require-hashes`, causing silent non-deterministic environment variations.
- **Ignoring CVE Warnings**: Adding blanket suppressions (`--audit-level=critical` or ignoring advisories) instead of applying targeted overrides or updates.
- **Uncontrolled Major Upgrades**: Allowing automated bots to merge major semantic version bumps without explicit human code review and breaking change validation.
- **Hardcoding Registry Secrets**: Checking auth tokens directly into `.npmrc` or `.yarnrc` rather than sourcing them from repository secrets or environment variables.
- **Uncoordinated Monorepo Versions**: Individual subprojects pinning diverging versions of React, TypeScript, or database drivers within the same repository.

## Verification Checklist
- [ ] Lockfiles are committed to version control and verified via immutable CI commands (`npm ci`, `cargo build --locked`).
- [ ] Automated dependency updates (Renovate/Dependabot) are active with grouped PRs and rate limiting.
- [ ] Automerge is restricted to patch updates with 100% passing test suites and branch protection rules.
- [ ] Security scanners (`audit-ci`, `pip-audit`, or Snyk/Trivy) fail pipelines on High/Critical CVEs.
- [ ] SPDX license checks verify that all packages adhere to permissive license guidelines.
- [ ] Private registry credentials are authenticated exclusively via environment variables.
