---
name: race-condition-audit
description: Use when auditing or writing code prone to concurrency bugs, TOCTOU timing windows, double-spending, inventory overselling, race conditions in database transactions, or asynchronous state mutation. Derived from Claude-Red and open-agent-skills concurrency patterns.
metadata:
  tags: "race-condition, concurrency, TOCTOU, database-locks, row-locking, advisory-locks, idempotency, double-spend"
  category: "security-and-correctness"
---
# Race Condition & Concurrency Defense Audit

## Purpose
Eliminate Time-of-Check to Time-of-Use (TOCTOU), double-spending, inventory exhaustion races, and state corruption across concurrent asynchronous operations and distributed workers.

## 1. The Core TOCTOU Flaw in Web APIs

```
❌ Vulnerable Pattern (Read-Calculate-Write separated):
1. Client A: SELECT balance FROM accounts WHERE id = 123;   --> (Reads 100)
2. Client B: SELECT balance FROM accounts WHERE id = 123;   --> (Reads 100)
3. Client A: UPDATE accounts SET balance = 100 - 100;       --> (Sets to 0)
4. Client B: UPDATE accounts SET balance = 100 - 100;       --> (Sets to 0 - Double spend succeeded!)

✅ Production Defense 1 (Single Atomic SQL Statement):
UPDATE accounts
SET balance = balance - 100
WHERE id = 123 AND balance >= 100
RETURNING balance;
-- If affected rows == 0, abort with 400 Insufficient Funds.

✅ Production Defense 2 (Pessimistic Row Lock inside Transaction):
await prisma.$transaction(async (tx) => {
  const [account] = await tx.$queryRaw<Account[]>`
    SELECT * FROM "accounts" WHERE id = ${id} FOR UPDATE
  `;
  if (account.balance < amount) throw new InsufficientFundsError();
  await tx.account.update({ where: { id }, data: { balance: account.balance - amount } });
});
```

---

## 2. High-Risk Concurrency Vectors & Defenses

### A. Financial & Balance Mutations (Double-Spend)
- **Check**: Is balance verified in memory before saving (`if (user.balance >= cost) save()`)?
- **Remedy**: Always decrement atomically at the database level using `UPDATE ... SET balance = balance - :amount WHERE id = :id AND balance >= :amount` or `SELECT ... FOR UPDATE`.

### B. Single-Use Redemptions (Coupons, Invite Codes, OTP Tokens)
- **Check**: Can 10 concurrent requests redeem the same promo code before `is_used` flips to `true`?
- **Remedy**: Use conditional atomic updates:
  ```sql
  UPDATE promo_codes SET is_used = true, used_by = :userId, used_at = NOW()
  WHERE code = :code AND is_used = false
  RETURNING id;
  ```
  If zero rows updated, reject immediately as already claimed.

### C. Unique Registration & Upsert Races
- **Check**: Does the code check existence with `findUnique` before creating (`if (!exists) create()`)?
- **Remedy**: Rely on Database Unique Constraints (`@unique` in Prisma) and handle duplicate key errors (`P2002` in Prisma) gracefully. Never rely on application-level existence checks.

### D. Inventory & Slot Double-Booking
- **Check**: Are booking slots or stock counts reserved by checking current occupancy count?
- **Remedy**: Use PostgreSQL exclusion constraints or pessimistic locks (`SELECT ... FOR UPDATE`) on the parent inventory record.

### E. Idempotency Key Pattern (Network Retry Defense)
- **Check**: What happens when payment or order endpoints receive duplicate requests within 100ms?
- **Remedy**: Require an `Idempotency-Key` header. Store the key in Redis or PostgreSQL with a short TTL (e.g. 5 minutes) and a status (`IN_PROGRESS`, `COMPLETED`, `FAILED`).
  ```typescript
  // Atomic claim
  const acquired = await redis.set(`idemp:${key}`, 'IN_PROGRESS', 'PX', 10000, 'NX');
  if (!acquired) {
    // Wait or return cached response
    return await pollForCachedResponse(key);
  }
  ```

---

## 3. Concurrency Checklist for Every API Route

- [ ] **No External Network I/O in DB Transactions**: External HTTP calls, email sending, or payment requests must NEVER occur inside `prisma.$transaction`.
- [ ] **Locking Strategy Explicit**: Does this operation use Atomic Update, `SELECT FOR UPDATE`, or Optimistic Locking (Version column `WHERE version = expected`)?
- [ ] **Explicit State Machine Transitions**: State changes must check current state in the WHERE clause:
  `UPDATE orders SET status = 'CANCELLED' WHERE id = :id AND status = 'PENDING'`
- [ ] **Distributed Concurrency Guard**: For background workers processing identical events in parallel (e.g., Cloud Run horizontal scaling), use Redis Redlock or PostgreSQL Advisory Locks (`pg_try_advisory_xact_lock(hash(resourceId))`).

---

## 4. Mandatory Runtime Concurrency Fuzz/Stress Test Template (Runtime Proof)

Static analysis cannot prove race freedom under load. For any financial, inventory, token, or state mutation endpoint, execute this test pattern to provide **empirical proof**:

```typescript
// test/concurrency-fuzz.spec.ts (Jest / Supertest)
describe('Concurrency & Double-Spend Fuzz Proof', () => {
  it('should guarantee exact-once execution across 50 simultaneous parallel requests', async () => {
    // 1. Arrange: Setup fresh account with 100 credits (can only afford 1 purchase of 100)
    const user = await createTestUserWithBalance(100);
    const CONCURRENCY_BURST = 50;

    // 2. Act: Fire 50 simultaneous HTTP requests in the same millisecond
    const burstPromises = Array.from({ length: CONCURRENCY_BURST }).map((_, index) =>
      request(app.getHttpServer())
        .post('/api/orders/checkout')
        .set('Authorization', `Bearer ${user.token}`)
        .send({
          itemId: 'item-100-credits',
          requestId: `burst-${index}-${Date.now()}`,
        })
    );

    // Run all requests simultaneously
    const responses = await Promise.all(burstPromises);

    // 3. Assert Invariants
    const successes = responses.filter(r => r.status === 200 || r.status === 201);
    const conflicts = responses.filter(r => r.status === 400 || r.status === 409);

    // INVARIANT 1: Exactly ONE request can succeed
    expect(successes.length).toBe(1);

    // INVARIANT 2: All 49 competing requests must be rejected
    expect(conflicts.length).toBe(CONCURRENCY_BURST - 1);

    // INVARIANT 3: Database state must be consistent (balance == 0, never negative)
    const updatedAccount = await prisma.account.findUnique({ where: { userId: user.id } });
    expect(updatedAccount.balance).toBe(0);

    // INVARIANT 4: Only 1 order record created
    const ordersCount = await prisma.order.count({ where: { userId: user.id } });
    expect(ordersCount).toBe(1);
  });
});
```

---

## 5. Database Isolation Level & Infrastructure Locking Architecture

Relying on application code alone is insufficient. Enforce concurrency safety at the database engine level:

### A. PostgreSQL Transaction Isolation Levels
- **`READ COMMITTED` (Default)**:
  - Prone to non-repeatable reads and race conditions between read and write.
  - **Rule**: If using Read Committed, you MUST use `SELECT ... FOR UPDATE` or atomic `UPDATE ... WHERE balance >= amount RETURNING balance`.
- **`REPEATABLE READ`**:
  - Prevents non-repeatable reads. Concurrent updates to the same row throw serialization conflict error `40001` (Cannot serialize access).
  - **Rule**: Application must catch `P2034` (Prisma transaction conflict) and retry with exponential backoff.
- **`SERIALIZABLE` (Highest Safety)**:
  - Guarantees execution matches serial order. Mandatory for multi-table financial ledger adjustments where atomic SQL is impossible.
  ```typescript
  await prisma.$transaction(
    async (tx) => {
      // Ledger balance calculations across multiple accounts
    },
    {
      isolationLevel: Prisma.TransactionIsolationLevel.Serializable,
      maxWait: 5000,
      timeout: 10000,
    }
  );
  ```

### B. PostgreSQL Advisory Locks (Distributed Node.js Workers)
When running horizontal replicas on Cloud Run, use connection-bound advisory locks to serialize mutations for a specific entity ID without locking the entire table:
```typescript
// Lock by hashing the UUID/string ID to a 64-bit bigint
await tx.$executeRaw`SELECT pg_advisory_xact_lock(hashtext(${entityId}))`;
// Lock automatically releases when the transaction commits or aborts!
```

