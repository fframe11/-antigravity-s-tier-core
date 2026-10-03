---
name: environment-config
description: Use when managing environment configurations, secret rotation, .env file strategies, or implementing 12-factor app configuration patterns. Covers dev/staging/prod isolation, config validation, and secret management integration.
---

# Environment Configuration & Secrets Management

Standardized workflows and patterns for configuring modern applications across development, ephemeral preview environments, staging, and production in compliance with 12-Factor App principles.

## When to Use This Skill

- Setting up or refactoring environment configuration schemas and validation pipelines.
- Managing `.env` hierarchies and local development overrides across teams.
- Implementing fail-fast startup configuration validation using typed schemas (Zod, Pydantic).
- Integrating container environments with Kubernetes ConfigMaps, Secrets, or cloud secret stores.
- Executing zero-downtime secret and credential rotations.
- Auditing and remediating configuration drift across environments.

## Core Principles & Guidelines

1. **Strict Separation of Config and Code (12-Factor III)**: Never hardcode credentials, endpoints, or toggles. Everything that varies between deployments belongs in environment variables.
2. **Config as Code vs. Config as Data**:
   - *Config as Code*: Schemas, defaults, and structural validation rules checked into version control.
   - *Config as Data*: Specific secrets, database URLs, and environment values injected at runtime.
3. **Hierarchy & Precedence Order**:
   - `Runtime Process Env` (Kubernetes / Cloud Provider / CLI flags) [Highest]
   - `.env.local` (Local developer machine overrides; gitignored)
   - `.env.{environment}.local` (e.g., `.env.development.local`; gitignored)
   - `.env.{environment}` (e.g., `.env.staging`, `.env.production`; tracked schemas or defaults)
   - `.env` (Base defaults for local development only) [Lowest]
4. **Fail Fast at Startup**: Crash immediately if required variables are missing or malformed before listening on network ports or accepting traffic.
5. **Environment Parity (dev ≈ staging ≈ prod)**: Keep backing services identical in architecture and protocol; vary only capacity, replicas, and specific resource coordinates.

## Implementation Patterns

### 1. Fail-Fast Startup Validation

Validate all environment variables on process initialization before application bootstrap.

#### TypeScript (Zod)
```typescript
// src/config/env.ts
import { z } from 'zod';

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'staging', 'production']).default('development'),
  PORT: z.coerce.number().int().positive().default(3000),
  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url(),
  API_KEY: z.string().min(32),
  ENABLE_ANALYTICS: z.coerce.boolean().default(false),
  MAX_CONNECTIONS: z.coerce.number().int().positive().default(10),
});

const parsed = envSchema.safeParse(process.env);

if (!parsed.success) {
  console.error('❌ Invalid environment configuration:');
  console.error(JSON.stringify(parsed.error.format(), null, 2));
  process.exit(1);
}

export const env = parsed.data;
export type Env = z.infer<typeof envSchema>;
```

#### Python (Pydantic Settings v2)
```python
# app/config.py
from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=('.env', '.env.local'), extra='ignore')
    
    ENVIRONMENT: str = "development"
    DATABASE_URL: PostgresDsn
    REDIS_URL: RedisDsn
    API_SECRET_KEY: str
    RATE_LIMIT_PER_MINUTE: int = 60

    @field_validator("API_SECRET_KEY")
    def validate_key_length(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("API_SECRET_KEY must be at least 32 characters")
        return v

config = Settings()
```

### 2. Zero-Downtime Secret Rotation

Rotate production credentials without service interruption using overlapping validity windows.

```text
Phase 1: Generate secondary credential in external secret store (Vault / AWS Secrets Manager)
Phase 2: Update application to accept [Primary, Secondary] keys for authentication
Phase 3: Deploy updated config/tokens pointing client workloads to the secondary key
Phase 4: Verify zero requests remain on primary credential via metrics/logs
Phase 5: Revoke old primary credential; promote secondary to new primary
```

```typescript
// Validating tokens against both active and retiring secrets during rotation
export function verifyToken(token: string, activeSecret: string, retiringSecret?: string): TokenPayload {
  try {
    return jwt.verify(token, activeSecret) as TokenPayload;
  } catch (err) {
    if (retiringSecret) {
      return jwt.verify(token, retiringSecret) as TokenPayload; // Fallback during rotation window
    }
    raise err;
  }
}
```

### 3. Kubernetes ConfigMap and Secret Injection

Use External Secrets Operator (ESO) to sync secrets from cloud vaults directly to Pod filesystems or environment variables.

```yaml
# external-secret.yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-secrets-sync
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: ClusterSecretStore
  target:
    name: app-runtime-secrets
  data:
    - secretKey: DATABASE_URL
      remoteRef:
        key: production/db
        property: connection_string
---
# pod-spec-snippet.yaml
spec:
  containers:
    - name: api
      image: api-service:v1.4.2
      envFrom:
        - configMapRef:
            name: app-config-defaults
        - secretRef:
            name: app-runtime-secrets
```

### 4. Dynamic Ephemeral & Preview Environments

Inject feature-branch dynamic configs via container orchestrator annotations or CI templates:

```yaml
# CI environment injection snippet
PREVIEW_SUBDOMAIN: "pr-${{ github.event.pull_request.number }}.preview.domain.internal"
DATABASE_NAME: "preview_${{ github.event.pull_request.number }}"
BASE_URL: "https://${{ env.PREVIEW_SUBDOMAIN }}"
```

### 5. Config Drift Detection

Calculate and log an SHA-256 hash of all non-sensitive config keys at boot time and monitor in APM:

```typescript
import { createHash } from 'crypto';

export function logConfigChecksum(validatedConfig: Record<string, unknown>): void {
  const sanitized = Object.keys(validatedConfig)
    .sort()
    .filter(k => !/secret|key|password|token/i.test(k))
    .reduce((acc, k) => ({ ...acc, [k]: validatedConfig[k] }), {});

  const hash = createHash('sha256').update(JSON.stringify(sanitized)).digest('hex');
  console.log(`[Config] Initialized config revision hash: ${hash.slice(0, 8)}`);
}
```

## Anti-Patterns to Avoid

- **Secret Commits**: Committing any `.env` file containing unencrypted staging or production values to Git.
- **In-Code Fallbacks for Production**: Writing `process.env.DB_PASS || 'default_password'`. In production, a missing variable must cause a hard failure.
- **Baking Config into Docker Images**: Running `ENV DATABASE_URL=...` in a Dockerfile during `docker build`. Images must remain immutable across environments.
- **Scattered `process.env` Calls**: Accessing `process.env` directly inside deep controller or utility functions instead of importing the validated config module.
- **Unversioned Live Edits**: Manually updating ConfigMaps or container environments directly with `kubectl edit` instead of driving changes via GitOps or CI/CD pipelines.

## Verification Checklist

- [ ] `.env*` pattern is present in `.gitignore` (only `.env.example` committed).
- [ ] Schema validation executes before database connections, background workers, or HTTP listeners start.
- [ ] Non-sensitive config checksum is emitted in logs on service boot to trace deployment parity.
- [ ] Secrets use External Secrets Operator, HashiCorp Vault, or cloud KMS rather than plain base64 strings in Git.
- [ ] Rotation procedure tested: can credentials be rotated while application handles active traffic?
- [ ] Staging environment runs identical DB engine, caching layer, and storage backend types as production.
- [ ] Ephemeral preview environments generate isolated backing namespaces or database schemas.
