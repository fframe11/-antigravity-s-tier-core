---
name: runtime-contract-mismatch
description: Use when auditing TypeScript/JavaScript, NestJS, and Prisma code for hidden runtime failures, cross-boundary contract mismatches, serialization casing drift, missing awaits in async loops, and null dereference crashes. Derived from review-skill find-mismatch patterns.
metadata:
  tags: "contract-mismatch, runtime-errors, casing-drift, async-await, null-safety, prisma-types, typescript-gotchas"
  category: "correctness-and-quality"
---
# Runtime Contract & Logic Mismatch Audit

## Purpose
Catch silent runtime breakages, cross-boundary serialization bugs, and TypeScript blindspots that pass compiler checks (`tsc`) but crash or corrupt data in production.

---

## 1. Top Runtime Bug Patterns (Audit Checklist)

### A. Cross-Boundary Casing & Field Name Drift
- **Frontend vs Backend vs Database**:
  - DTO accepts `camelCase` (`userId`), but raw SQL query or DB column expects `snake_case` (`user_id`).
  - Prisma models mapped with `@map("user_id")` — ensure queries use model field name (`userId`), while raw `$queryRaw` uses database column (`user_id`).
- **Discriminator & Enum Mismatches**:
  - Verify string literals match Prisma enums (`OrderStatus.COMPLETED` vs `"completed"` vs `"COMPLETED"`).

### B. The `forEach` Async / Missing Await Trap
- **The Bug**:
  ```typescript
  // ❌ CRITICAL BUG: forEach does NOT await async callbacks!
  // Database queries run unhandled in the background; function returns before completion!
  items.forEach(async (item) => {
    await prisma.item.update({ where: { id: item.id }, data: { processed: true } });
  });

  // ✅ Production Fix: Use for...of or Promise.all()
  for (const item of items) {
    await prisma.item.update({ where: { id: item.id }, data: { processed: true } });
  }
  // OR concurrent with Promise.all:
  await Promise.all(items.map(item => prisma.item.update({ where: { id: item.id }, data: { processed: true } })));
  ```

### C. Truncated Optional Chaining (`?.`)
- **The Bug**:
  ```typescript
  // ❌ Crashes with TypeError if user exists but profile is null:
  const bio = user?.profile.bio;

  // ✅ Production Fix: Chain at every nullable boundary:
  const bio = user?.profile?.bio ?? 'No bio provided';
  ```

### D. Prisma `undefined` vs `null` Semantics
- In Prisma:
  - `data: { field: undefined }` means **DO NOTHING** (leaves existing value untouched).
  - `data: { field: null }` means **SET VALUE TO NULL** in the database.
  - If a DTO property is optional and caller sends undefined, passing it directly might not clear a field that the user intended to reset.
  - Always verify whether field update requires explicit `null` or condition check.

### E. DTO Query Parameter Coercion (NestJS ValidationPipe)
- Query parameters (`@Query('limit') limit: number`) arrive as **strings** (`"10"`, not `10`) over HTTP.
- Without `@Type(() => Number)` from `class-transformer` or `transform: true` in `ValidationPipe`:
  - `limit + 1` becomes `"101"` instead of `11`!
  - `WHERE count > limit` fails or performs lexicographical comparison.
- **Rule**: Every numeric or boolean DTO field in `@Query()` or `@Param()` MUST have `@Type(() => Number)` / `@Type(() => Boolean)`.

### F. Return Type vs Real Object Shape
- TypeScript interface says `interface UserResponse { id: string; fullName: string; }`
- Service returns raw Prisma user `{ id: '...', first_name: '...', last_name: '...' }` without mapping `fullName`.
- TypeScript might not catch this if returned via `any` or untyped mapper. Verify every returned object property against its DTO contract.

---

## 2. Review Protocol for PRs & New Code

Before approving any endpoint or service method:
1. Trace input from `@Body()` / `@Query()` through DTO decorators to Service.
2. Verify all `async` functions are properly `await`ed (no dangling promises).
3. Check all DB column names against Prisma schema definitions.
4. Verify all array index or object property accesses (`array[0]`, `map.get()`) handle empty / `undefined`.
5. Ensure error handling does not catch-and-ignore (`catch (e) {}` with no logging or rethrow).
