---
name: supply-chain-security
description: Use when scanning container images for vulnerabilities, generating Software Bill of Materials (SBOMs), or cryptographically signing artifacts to secure the software supply chain. Mapped to local repositories trivy, syft, and cosign.
metadata:
  tags: "security, supply-chain, sbom, trivy, syft, cosign, container, vulnerability"
  category: "security"
---
# Supply Chain Security — Container & Dependency Hardening

## 1. Container Image Scanning (Trivy)
### When to Scan
- Every `docker build` in CI/CD before pushing to registry
- Weekly scheduled scans of all deployed images
- On any dependency update (Renovate/Dependabot PR)

### How to Run
```bash
# Scan local image
trivy image --severity HIGH,CRITICAL my-app:latest

# Scan and fail CI if HIGH/CRITICAL found
trivy image --exit-code 1 --severity HIGH,CRITICAL my-app:latest

# Scan filesystem (node_modules, requirements.txt)
trivy fs --severity HIGH,CRITICAL .

# Scan IaC (Dockerfile, docker-compose, Kubernetes manifests)
trivy config .
```

### Remediation Priority
| Severity | SLA | Action |
|---|---|---|
| CRITICAL | Fix within 24 hours | Patch immediately, rebuild & redeploy |
| HIGH | Fix within 7 days | Schedule in current sprint |
| MEDIUM | Fix within 30 days | Add to backlog |
| LOW | Best effort | Fix during dependency update cycles |

## 2. Software Bill of Materials (SBOM) with Syft
### Generate SBOM
```bash
# Generate SBOM from container image
syft my-app:latest -o spdx-json > sbom.spdx.json

# Generate SBOM from source directory
syft dir:. -o cyclonedx-json > sbom.cyclonedx.json

# Generate SBOM from lock file
syft file:package-lock.json -o spdx-json > sbom.spdx.json
```

### SBOM Best Practices
- Generate SBOM at build time and attach as OCI artifact alongside the image
- Store SBOMs in a versioned, searchable registry (e.g., Dependency-Track)
- Automate license compliance checks against SBOM (reject GPL in proprietary projects)
- Review SBOM before every release for unexpected transitive dependencies

## 3. Artifact Signing (Cosign)
### Sign Container Images
```bash
# Generate key pair (one-time)
cosign generate-key-pair

# Sign an image
cosign sign --key cosign.key my-registry/my-app:v1.2.3

# Verify signature before deployment
cosign verify --key cosign.pub my-registry/my-app:v1.2.3
```

### Keyless Signing (OIDC / Sigstore)
```bash
# Sign using OIDC identity (GitHub Actions, Google Cloud Build)
cosign sign --identity-token=$(gcloud auth print-identity-token) my-registry/my-app:latest

# Verify keyless signature
cosign verify --certificate-identity=user@example.com --certificate-oidc-issuer=https://accounts.google.com my-registry/my-app:latest
```

## 4. Dependency Hygiene
### Node.js / npm
```bash
# Audit for known vulnerabilities
npm audit --production

# Fix automatically where safe
npm audit fix

# Check for outdated packages
npm outdated

# Verify package integrity
npm ci  # Always use in CI (respects lock file exactly)
```

### Python / pip
```bash
# Audit with pip-audit
pip-audit -r requirements.txt

# Pin versions with hashes
pip install --require-hashes -r requirements.txt
```

### Pre-commit Checks
- Run `npm audit` or `pip-audit` in pre-commit hooks
- Block PRs with CRITICAL/HIGH vulnerabilities
- Require lock file (`package-lock.json` / `poetry.lock`) in every commit

## 5. CI/CD Integration Pattern
```yaml
# GitHub Actions example
supply-chain-check:
  steps:
    - name: Build image
      run: docker build -t my-app:${{ github.sha }} .
    
    - name: Scan with Trivy
      run: trivy image --exit-code 1 --severity HIGH,CRITICAL my-app:${{ github.sha }}
    
    - name: Generate SBOM
      run: syft my-app:${{ github.sha }} -o spdx-json > sbom.json
    
    - name: Sign image
      run: cosign sign --key ${{ secrets.COSIGN_KEY }} my-app:${{ github.sha }}
    
    - name: Upload SBOM
      uses: actions/upload-artifact@v4
      with:
        name: sbom
        path: sbom.json
```

## 6. Incident Response for Supply Chain Attacks
1. **Detection**: Monitor CVE feeds for dependencies in your SBOM
2. **Assessment**: Cross-reference CVE with SBOM to identify affected services
3. **Containment**: Pin affected dependency to last-known-good version
4. **Remediation**: Update dependency, rebuild, re-scan, redeploy
5. **Verification**: Verify fix with `trivy image` and confirm SBOM is clean
