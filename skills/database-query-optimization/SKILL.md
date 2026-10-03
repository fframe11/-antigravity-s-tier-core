---
name: database-query-optimization
description: Use when optimizing database queries, fixing N+1 problems, adding indexes, analyzing query plans, or tuning PostgreSQL performance. Covers Prisma query optimization, EXPLAIN ANALYZE, indexing strategy, and connection pooling.
---
# Database Query Optimization (PostgreSQL + Prisma)

## When to Use
- API endpoint is slow (> 200ms response time)
- Database CPU or memory is consistently high
- N+1 query pattern detected in logs
- Adding new queries that involve JOINs or large datasets

## N+1 Query Detection & Fix

### The Problem
```typescript
// ❌ N+1: 1 query for orders + N queries for users
const orders = await prisma.order.findMany();
for (const order of orders) {
  const user = await prisma.user.findUnique({ where: { id: order.userId } });
}
```

### The Fix
```typescript
// ✅ Single query with include
const orders = await prisma.order.findMany({
  include: { user: true },
});

// ✅ Or batch load with findMany + IN clause
const userIds = [...new Set(orders.map(o => o.userId))];
const users = await prisma.user.findMany({
  where: { id: { in: userIds } },
});
```

## EXPLAIN ANALYZE Workflow

```sql
-- Always analyze before deploying new queries
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT o.*, u.name
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.status = 'pending'
  AND o.created_at > NOW() - INTERVAL '30 days';
```

### Red Flags in Query Plans
| Red Flag | What It Means | Fix |
|---|---|---|
| `Seq Scan` on large table | Full table scan, no index used | Add index on filter columns |
| `Nested Loop` with high rows | O(n²) join | Check join conditions, add index |
| `Sort` with high cost | Sorting without index | Add index matching ORDER BY |
| `Hash Join` + high `Buffers` | Large dataset in memory | Filter earlier, add WHERE clauses |

## Indexing Strategy

### Must-Have Indexes
```sql
-- Columns used in WHERE clauses
CREATE INDEX idx_orders_status ON orders(status);

-- Columns used in JOIN conditions
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Composite index for common query patterns
CREATE INDEX idx_orders_status_created ON orders(status, created_at DESC);

-- Partial index for active records only
CREATE INDEX idx_orders_pending ON orders(created_at DESC) WHERE status = 'pending';
```

### Prisma Schema Indexes
```prisma
model Order {
  id        String   @id @default(uuid())
  status    String
  userId    String
  createdAt DateTime @default(now())
  user      User     @relation(fields: [userId], references: [id])

  @@index([status, createdAt(sort: Desc)])
  @@index([userId])
}
```

## Connection Pooling

### Prisma + PgBouncer (Production)
```
DATABASE_URL="postgresql://user:pass@pgbouncer:6432/mydb?pgbouncer=true&connection_limit=10"
```

### Rules
1. **Set `connection_limit`** — Match to Cloud Run instance count × concurrency
2. **Use PgBouncer in transaction mode** — Required for serverless (Cloud Run)
3. **Monitor pool exhaustion** — `P2024` Prisma error = pool is full

## Pagination

### Cursor-Based (Recommended for large datasets)
```typescript
const results = await prisma.order.findMany({
  take: 20,
  skip: 1, // skip the cursor itself
  cursor: { id: lastSeenId },
  orderBy: { createdAt: 'desc' },
});
```

### Offset-Based (Simple but slow on large tables)
```typescript
// ⚠️ Avoid offset > 10,000 rows — performance degrades linearly
const results = await prisma.order.findMany({
  take: 20,
  skip: page * 20,
});
```

## Verification Checklist
- [ ] No N+1 queries (check Prisma query log with `log: ['query']`)
- [ ] All WHERE/JOIN columns have indexes
- [ ] EXPLAIN ANALYZE shows Index Scan (not Seq Scan) for common queries
- [ ] Connection pool is configured for production concurrency
- [ ] Large list endpoints use cursor pagination
