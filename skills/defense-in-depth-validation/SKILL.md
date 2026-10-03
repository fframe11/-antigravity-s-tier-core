---
name: defense-in-depth-validation
description: Use when designing or reviewing data validation and business rule enforcement across multiple architectural layers to ensure invalid states are structurally impossible. Derived from carlopezzuto-agents defense-in-depth patterns.
metadata:
  tags: "validation, defense-in-depth, data-integrity, input-validation, business-invariants, db-constraints"
  category: "architecture-and-security"
---
# Defense-in-Depth Validation Architecture

## Core Principle
**Never rely on a single checkpoint for correctness or security.**
A single validation check can be bypassed by refactoring, direct internal service calls, alternate code paths, or mocked unit tests.
Validate at **EVERY** layer data passes through to make bugs and corruption structurally impossible.

---

## The 4-Layer Defense Architecture

```
[ HTTP / Controller ]      --> Layer 1: Boundary Validation (DTO, class-validator, type coercion)
         ↓
[ Domain Service ]         --> Layer 2: Business Logic Invariants & State Guards
         ↓
[ Infrastructure / Context] --> Layer 3: Environment & Resource Guards (Rate-limits, auth context, tenant bounds)
         ↓
[ Database / Storage ]     --> Layer 4: Storage Constraints (CHECK constraints, @unique, FK, Transactions)
```

### Layer 1: Boundary & Entry Point Validation (Controllers / DTOs)
- **Objective**: Reject malformed, malicious, or unexpected payload shapes at the edge before allocating business logic resources.
- **Rules**:
  - Global `ValidationPipe({ whitelist: true, forbidNonWhitelisted: true, transform: true })`.
  - Validate every field with strict decorators (`@IsString()`, `@IsUUID()`, `@IsInt()`, `@Min()`, `@Max()`).
  - Sanitize string inputs (trim whitespace, strip HTML/scripts if text).

### Layer 2: Domain & Business Logic Invariants (Services)
- **Objective**: Ensure inputs make contextual sense for the requested domain operation.
- **Rules**:
  - Even if DTO passed `amount: 100`, the Service must verify: `if (account.balance < amount) throw new InsufficientFundsException()`.
  - Verify state transitions: `if (!ALLOWED_TRANSITIONS[order.status].includes(newStatus)) throw new InvalidStateTransitionException()`.
  - Verify entity ownership (BOLA prevention): `if (resource.userId !== currentUser.id) throw new ForbiddenException()`.

### Layer 3: Environment & Runtime Context Guards
- **Objective**: Prevent dangerous operations from running in the wrong context or exceeding safe operational bounds.
- **Rules**:
  - Guard destructive operations (e.g. database wipe, sandbox bypass) with strict `NODE_ENV !== 'production'` assertions.
  - Enforce concurrency rate-limiting and quota controls per user/IP.
  - Fail-fast if mandatory runtime secrets or environment configurations are missing at startup.

### Layer 4: Database Storage Constraints (The Final Fortress)
- **Objective**: Guarantee data integrity even if bugs slip through all upper layers.
- **Rules**:
  - Never rely only on code to enforce uniqueness: add `@unique` or composite unique indexes in the database schema.
  - Use database `CHECK` constraints (e.g., `CHECK (balance >= 0)`, `CHECK (price > 0)`).
  - Use foreign keys with appropriate `ON DELETE RESTRICT` or `ON DELETE CASCADE` rules.
  - Enforce transactional atomicity (`prisma.$transaction`) so partial writes cannot leave corrupted orphaned state.

---

## Validation Audit Checklist for New Features

- [ ] Can an invalid value reach the database if the controller check is bypassed? (If yes, add Layer 2 check and Layer 4 DB constraint).
- [ ] Is ownership validated at the service layer using authenticated identity, not client-supplied query params?
- [ ] Are business invariants (like balances or stock counts) protected by database-level constraints?
- [ ] Do tests verify rejection at each layer independently?
