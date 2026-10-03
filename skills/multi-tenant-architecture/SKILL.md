---
name: multi-tenant-architecture
description: Use when designing multi-tenant systems, implementing tenant isolation, or managing shared infrastructure for multiple customers. Covers database-per-tenant, schema-per-tenant, row-level security, and hybrid approaches.
---

# Multi-Tenant Architecture & Data Isolation

Production patterns for engineering secure, compliant, and cost-effective multi-tenant SaaS architectures across compute, storage, caching, and background processing.

## When to Use This Skill

- Architecting multi-tenant SaaS applications from early-stage MVPs to enterprise scale.
- Selecting and implementing tenant isolation models (Pool, Silo, or Bridge).
- Implementing database partitioning strategies (PostgreSQL RLS, schema-per-tenant, database-per-tenant).
- Securing tenant context propagation across distributed microservices.
- Enforcing noisy neighbor mitigation, tenant rate limiting, and consumption billing.
- Automating tenant onboarding, lifecycle management, and regulatory data residency.

## Core Principles & Guidelines

1. **Isolation Models**:
   - *Pool Model*: All tenants share compute and storage. Highest cost efficiency, relies on logical software barriers (e.g., Row-Level Security).
   - *Silo Model*: Dedicated compute (containers/namespaces) and dedicated database per tenant. Maximum isolation, blast-radius containment, and compliance.
   - *Bridge / Hybrid Model*: Shared compute tier, but dedicated schemas or databases for enterprise tiers.
2. **Database Partitioning Strategies**:
   - *Shared DB + Row-Level Security (RLS)*: Tables contain `tenant_id`. Database engine enforces policies automatically via session variables.
   - *Schema-per-Tenant*: PostgreSQL schemas (`tenant_acme.users`). Clean namespace boundary, easy per-tenant point-in-time restore.
   - *Database-per-Tenant*: Separate physical or logical databases. Required for strict HIPAA/SOC2 enterprise SLAs.
3. **Deterministic Context Resolution**: Extract tenant identity once at the API Gateway or edge middleware (from verified JWT claims, custom subdomains, or mutual TLS certs), then bind immutably to request context.
4. **Defense in Depth**: Never rely solely on application-layer `WHERE tenant_id = ?` clauses. Enforce isolation at the database session or connection level.
5. **Fair-Share Resource Allocation**: Prevent noisy neighbors from exhausting DB connection pools, CPU, or cache memory using per-tenant rate limits and query timeouts.

## Implementation Patterns

### 1. PostgreSQL Row-Level Security (RLS) with Session Variables

Enforce database-level data isolation that prevents accidental data leakage even if application query logic omits tenant filters:

```sql
-- Enable RLS on the table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents FORCE ROW LEVEL SECURITY;

-- Create isolation policy based on transaction session variable
CREATE POLICY tenant_isolation_policy ON documents
  FOR ALL
  USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)
  WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);
```

### 2. Tenant Context Propagation via Middleware

Capture tenant context early and propagate it safely through asynchronous execution trees:

```typescript
// src/middleware/tenant-context.ts
import { AsyncLocalStorage } from 'async_hooks';
import { Request, Response, NextFunction } from 'express';
import { Pool } from 'pg';

export interface TenantContext {
  tenantId: string;
  plan: 'starter' | 'enterprise';
}

export const tenantStorage = new AsyncLocalStorage<TenantContext>();

export function tenantMiddleware(req: Request, res: Response, next: NextFunction): void {
  // Extract tenant from verified JWT claim or subdomain
  const tenantId = (req.user?.tenantId as string) || (req.headers['x-tenant-id'] as string);
  if (!tenantId) {
    res.status(401).json({ error: 'Tenant context could not be resolved' });
    return;
  }

  tenantStorage.run({ tenantId, plan: req.user?.plan || 'starter' }, () => {
    next();
  });
}

// Scoped DB transaction runner applying RLS session setting
export async function withTenantDb<T>(pool: Pool, callback: (client: any) => Promise<T>): Promise<T> {
  const context = tenantStorage.getStore();
  if (!context) throw new Error('No tenant context found in execution chain');

  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    // Set transaction-local session variable for RLS
    await client.query('SET LOCAL app.current_tenant_id = $1', [context.tenantId]);
    const result = await callback(client);
    await client.query('COMMIT');
    return result;
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}
```

### 3. Tenant-Aware Cache Key Namespacing

Prevent cross-tenant cache contamination by enforcing strict tenant prefixing on every cache key:

```typescript
// src/cache/tenant-cache.ts
import { Redis } from 'ioredis';
import { tenantStorage } from '../middleware/tenant-context';

export class TenantCache {
  constructor(private redis: Redis) {}

  private getScopedKey(key: string): string {
    const context = tenantStorage.getStore();
    if (!context) throw new Error('Tenant context missing for cache access');
    return `tenant:${context.tenantId}:${key}`;
  }

  async get<T>(key: string): Promise<T | null> {
    const data = await this.redis.get(this.getScopedKey(key));
    return data ? JSON.parse(data) : null;
  }

  async set(key: string, value: unknown, ttlSeconds = 300): Promise<void> {
    await this.redis.set(this.getScopedKey(key), JSON.stringify(value), 'EX', ttlSeconds);
  }

  async purgeTenant(tenantId: string): Promise<void> {
    const keys = await this.redis.keys(`tenant:${tenantId}:*`);
    if (keys.length > 0) await this.redis.del(...keys);
  }
}
```

### 4. Noisy Neighbor Protection (Tenant Token Bucket)

```typescript
// Rate limiting middleware per tenant using Redis
export async function tenantRateLimiter(redis: Redis, tenantId: string, limit: number, windowSec: number): Promise<boolean> {
  const key = `ratelimit:${tenantId}`;
  const current = await redis.incr(key);
  if (current === 1) {
    await redis.expire(key, windowSec);
  }
  return current <= limit;
}
```

### 5. Tenant Onboarding & Data Residency Routing

```text
Onboarding Workflow:
1. Validate Organization Name & Billing Subscription
2. Assign Data Residency Region (e.g., 'eu-central-1' vs 'us-east-1')
3. Provision Schema/Database via Migration Runner (Flyway/Liquibase/Prisma)
4. Seed Default Roles, Permissions, and Outbox Events
5. Emit TenantCreated webhook for billing metric ingestion
```

## Anti-Patterns to Avoid

- **Application-Only Tenant Filtering**: Relying solely on developers remembering `SELECT * FROM items WHERE tenant_id = ?` without RLS or schema boundaries.
- **Global Shared Cache Keys**: Storing cached objects under `user:101` instead of `tenant:org_123:user:101`, causing data leakage across organizations.
- **Uncapped Concurrency**: Allowing an enterprise tenant running bulk ETL to consume all available database connections, starving other tenants.
- **Synchronous Tenant Provisioning**: Creating databases or executing heavy schema migrations synchronously in the HTTP request loop.
- **Unshredded Offboarding**: Performing standard `DELETE` queries on tenant offboarding instead of cryptographically shredding tenant encryption keys and auditing compliance deletion.

## Verification Checklist

- [ ] Row-Level Security (`ENABLE ROW LEVEL SECURITY` and `FORCE ROW LEVEL SECURITY`) is enabled on every tenant table.
- [ ] Integration test suite attempts cross-tenant reads and verifies database rejects queries with 0 rows or errors.
- [ ] Tenant context is propagated through `AsyncLocalStorage` (Node.js) or thread-local contexts (Java/Python) to background workers.
- [ ] Redis cache keys and messaging queues (e.g., RabbitMQ, SQS) are prefixed with tenant identifiers.
- [ ] Per-tenant rate limits and database query timeouts (e.g., `statement_timeout = 5000`) are active.
- [ ] Tenant billing metrics (API calls, storage GB, active seats) are emitted asynchronously to telemetry.
- [ ] Data residency routing directs regional tenants to appropriate regional database replicas or clusters.
