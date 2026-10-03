---
name: database-migrations
description: Use when planning, writing, or reviewing database schema migrations for production systems. Covers Alembic, Flyway, Prisma Migrate, Django migrations, and raw SQL migrations with safety patterns.
---

# Database Migrations & Schema Evolution Guide

## When to Use This Skill
- Designing, reviewing, or applying schema changes to production databases (PostgreSQL, MySQL, CockroachDB).
- Implementing zero-downtime database upgrades on high-traffic, mission-critical systems.
- Resolving migration deadlocks, schema drifts, long-running lock contention, or slow query regressions.
- Orchestrating tooling workflows across Alembic (SQLAlchemy), Flyway, Prisma Migrate, and Django ORM.
- Managing multi-tenant or multi-database migration lifecycles and historical migration squashing.

## Core Principles
1. **Expand-Contract (Parallel Run)**: Never introduce breaking schema changes in a single deployment. Expand the schema (add new nullable column), backfill data asynchronously, switch application reads and writes to new column, then contract (drop old column).
2. **Short-Lived Locks**: DDL queries acquire `ACCESS EXCLUSIVE` locks on tables. Always set aggressive `lock_timeout` before DDL statements to avoid blocking concurrent read/write queries and queuing thread pools.
3. **Decouple Schema from Data**: Never execute heavy data backfills or bulk row transformations inside transactional schema DDL. Backfill asynchronously in batches or background workers.
4. **Reversibility vs Forward-Only**: Forward-only migrations (`fix-forward`) are safer in high-throughput distributed systems because rollbacks can truncate or corrupt new data written by updated services. Reversible scripts must be validated before production application.
5. **Advisory Locking**: Use distributed migration locks (`pg_advisory_lock` or tool-native locks) to prevent race conditions during concurrent container deployments.

## Implementation Patterns

### 1. Zero-Downtime Column Rename (Expand-Contract)
Direct `ALTER TABLE rename` breaks running service instances during rolling deployments. Use 3 phased releases:

```sql
-- Phase 1 (Deploy schema): Add new column without constraints
ALTER TABLE users ADD COLUMN full_name VARCHAR(255);

-- Create trigger to synchronize writes between old and new columns
CREATE OR REPLACE FUNCTION sync_user_name() RETURNS TRIGGER AS $$
BEGIN
    NEW.full_name = NEW.first_name || ' ' || NEW.last_name;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sync_user_name
BEFORE INSERT OR UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION sync_user_name();

-- Phase 2 (Deploy app): Backfill existing rows in batches, update application code to write/read full_name.
-- Phase 3 (Deploy cleanup): Drop trigger and obsolete columns
DROP TRIGGER trg_sync_user_name ON users;
ALTER TABLE users DROP COLUMN first_name, DROP COLUMN last_name;
```

### 2. Safe DDL Operations with Postgres Lock Guarding
Prevent pipeline lock queues from starving active queries by setting a strict `lock_timeout`.

```sql
-- migration_20260921_add_index_and_column.sql
SET lock_timeout = '2s';
SET statement_timeout = '10s';

-- 1. Adding a column with default value (PostgreSQL >= 11 optimizes without table rewrite)
ALTER TABLE orders ADD COLUMN status VARCHAR(32) NOT NULL DEFAULT 'pending';

-- 2. Non-blocking index creation (MUST run outside a single multi-statement transaction)
COMMIT;
CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders (customer_id);
```

### 3. Asynchronous Data Migration Chunking
Backfilling millions of records must not saturate write-ahead logs (WAL) or hold transaction snapshots.

```python
# data_migration_worker.py
def backfill_account_uuid(batch_size=1000):
    last_id = 0
    while True:
        with db.session.begin():
            rows = db.execute(
                """
                UPDATE accounts 
                SET uuid = gen_random_uuid() 
                WHERE id > :last_id AND uuid IS NULL 
                ORDER BY id ASC LIMIT :batch 
                RETURNING id
                """,
                {"last_id": last_id, "batch": batch_size}
            ).fetchall()
            
            if not rows:
                break
            last_id = rows[-1][0]
        time.sleep(0.05)  # Yield IO to active application traffic
```

### 4. Framework-Specific Patterns
- **Flyway**: `V{YYYYMMDDHHMMSS}__{description}.sql` for versioned migrations, `R__{description}.sql` for repeatable views/procedures.
- **Alembic**: Set `compare_type=True` and configure `transaction_per_migration = True`.
- **Prisma**: Run `prisma migrate diff` in CI to detect schema drift before running `prisma migrate deploy`.
- **Django**: Separate schema migrations (`RunSQL`) from data updates (`RunPython` with `atomic=False` for large iterations).

### 5. Multi-Tenant and Database Squashing
- **Squashing**: When historical migration files exceed ~100 or slow down fresh CI test databases, consolidate into a single baseline schema (`db/schema.sql` or squashed migration) while tracking applied versions in the metadata table.
- **Multi-Tenant Routing**: For schema-per-tenant, loop through active tenant schemas using connection pooling and schema advisory locks:

```python
for tenant_schema in get_active_tenants():
    with engine.connect() as conn:
        conn.execute(text(f"SET search_path TO {tenant_schema}"))
        alembic_runner.upgrade(conn, "head")
```

## Anti-Patterns to Avoid
- **Adding `NOT NULL` on Existing Columns Without Default**: Locks the table and causes immediate DDL failures if null values exist. Add nullable column first, backfill defaults, then attach `NOT NULL` constraint with validation.
- **Running DDL in Long-Running Transactions**: Holding an open transaction during lengthy operations holds locks on dependent tables, causing cascading connection pool exhaustion.
- **Non-Concurrent Index Creation in Production**: `CREATE INDEX` without `CONCURRENTLY` acquires a `SHARE` lock that blocks all incoming writes until index creation finishes.
- **Coupling App Code Deployments with Irreversible DDL**: Deploying code that immediately expects new columns before migrations finish, causing 500 errors on existing pods during canary rollouts.
- **Manual Schema Modifications**: Editing production database schemas manually without corresponding migration files, resulting in permanent drift across staging and production.

## Verification Checklist
- [ ] All DDL statements declare explicit `lock_timeout` (e.g., `<= 3s`).
- [ ] Index creations use `CREATE INDEX CONCURRENTLY` (or database equivalent) outside blocking transactions.
- [ ] Column additions and renames follow the expand-contract strategy across multi-step releases.
- [ ] Large table backfills are decoupled from schema deployment and chunked into batched transactions.
- [ ] Migration scripts run in CI against a sanitized production clone to detect timing and drift issues.
- [ ] Migration tools acquire an advisory lock (`pg_advisory_lock`) to prevent concurrent runner conflicts.
- [ ] Foreign keys on large tables are created `NOT VALID` and validated separately (`VALIDATE CONSTRAINT`).
- [ ] Rollback or forward-fix mitigation steps are documented for every release migration.
