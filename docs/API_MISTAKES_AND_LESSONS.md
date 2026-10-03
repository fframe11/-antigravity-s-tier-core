# API Fatal Mistakes, Real Postmortems & Defensive Engineering Standards

> **The Architectural & DevSecOps Knowledge Base for Antigravity.**  
> Built from real production audits, Godkiller epistemic incident reports, and OWASP API Top 10 postmortems.  
> Every engineer and agent must adhere strictly to these defensive patterns to eliminate runtime failures.

---

## 📋 Table of Contents
1. [Authentication & Identity Verification (The sprint-1-auth-api-fix Postmortem)](#1-authentication--identity-verification)
2. [Runtime Contract Mismatch & Casing Drift](#2-runtime-contract-mismatch--casing-drift)
3. [Third-Party Integrations & Circuit Breakers](#3-third-party-integrations--circuit-breakers)
4. [Concurrency, TOCTOU & Atomic Inventory Control](#4-concurrency-toctou--atomic-inventory-control)
5. [Node.js Main Thread Starvation & Anti-OOM Workers](#5-nodejs-main-thread-starvation--anti-oom-workers)
6. [Authorization Flaws: BOLA, BFLA & Over-Posting](#6-authorization-flaws-bola-bfla--over-posting)
7. [Async/Await Traps & Floating Promises](#7-asyncawait-traps--floating-promises)
8. [Defensive Data Validation Layers (Defense-in-Depth)](#8-defensive-data-validation-layers)

---

## 1. Authentication & Identity Verification

### 🚨 Real Postmortem: `backend_itim_tech` (`sprint-1-auth-api-fix`)
- **The Fatal Flaw:** The API controller relied on raw client-supplied body parameters (`email`, `uid`, `password`) or trusted unverified request headers (`x-user-id`) to identify the caller.
- **The Exploit Window:** Any attacker could forge an HTTP POST with `{ "uid": "target_admin_uid" }` or set `x-user-id: 1` to impersonate arbitrary users or bypass authorization entirely.
- **The Anti-Pattern (Strictly Banned):**
  ```typescript
  // ❌ FATAL ANTI-PATTERN: Trusting client-supplied identity
  @Post('/profile')
  async updateProfile(@Body() body: { userId: string, bio: string }) {
    return this.userService.update(body.userId, body.bio); // BOLA / Impersonation risk
  }

  // ❌ FATAL ANTI-PATTERN: Unverified header trust
  @Get('/me')
  async getMe(@Headers('x-user-id') userId: string) {
    return this.userService.findById(userId); // Trivially spoofed by client
  }
  ```

### 🛡️ Mandatory Defensive Standards:
1. **Centralized Identity Resolution (`resolveUserId`):**
   - Extract user identity **strictly** from verified cryptographic signatures (e.g., Bearer JWT in the `Authorization` header).
   - Use official backend SDKs (Firebase Admin, Supabase Auth, Keycloak) to verify external tokens.
   ```typescript
   // ✅ SECURE DEFENSIVE PATTERN
   @UseGuards(JwtAuthGuard)
   @Get('/me')
   async getMe(@Req() req: AuthenticatedRequest) {
     const userId = req.user.id; // Cryptographically decoded & verified by AuthGuard
     return this.userService.findById(userId);
   }
   ```
2. **Zero Phantom DTO Fields:** Eliminate unused or legacy fields in request DTOs.
3. **Fail-Fast Environment Configuration:** Verify that `JWT_SECRET`, `FIREBASE_PROJECT_ID`, and database secrets are loaded at process startup; if missing, throw an exception immediately to prevent running in an insecure default state.

---

## 2. Runtime Contract Mismatch & Casing Drift

### 🚨 The Problem:
Frontend components assume a camelCase property (e.g. `userProfile.phoneNumber`), but the API serialized raw database rows in snake_case (e.g. `phone_number`), or returned `null` instead of an empty array. The frontend white-screens with `TypeError: Cannot read properties of undefined`.

### 🛡️ Mandatory Defensive Standards:
1. **Single Source of Truth Contracts:**
   - Both backend DTOs and frontend API clients must derive from shared Zod schemas (e.g. `packages/contracts/` or `types/api.ts`).
   ```typescript
   import { z } from 'zod';

   export const UserResponseSchema = z.object({
     id: z.string().uuid(),
     email: z.string().email(),
     displayName: z.string(),
     roles: z.array(z.string()).default([]),
   });

   export type UserResponse = z.infer<typeof UserResponseSchema>;
   ```
2. **Zero Direct Client-to-Database Leaks:**
   - Frontend React components (`app/`, `components/`) must **NEVER** import `@prisma/client`, `@/lib/db`, `typeorm`, or `pg`.
   - Run `audit-architecture-boundaries.ps1` before every commit to guarantee strict separation.

---

## 3. Third-Party Integrations & Circuit Breakers

### 🚨 The Problem:
An external payment gateway, broker platform (e.g. IUX), SMS provider, or courier API suffers an outage. The internal API handler waits synchronously until socket timeout (30-60s), exhausting the connection pool and crashing the entire server.

### 🛡️ Mandatory Defensive Standards:
1. **Circuit Breaker Invariant:**
   - Wrap all third-party external HTTP calls in a Circuit Breaker (e.g. `opossum`).
   - If >= 5 consecutive failures occur or latency exceeds 5 seconds, trip the circuit to `OPEN`.
   - Fail subsequent requests immediately without wasting sockets.
2. **Defensive Client-Facing Degradation:**
   - **Never** expose raw error traces (`ECONNREFUSED`, `503 Service Unavailable`, stack traces) in user viewports.
   - Render a polite, branded maintenance banner explaining that the partner platform is temporarily undergoing maintenance.
3. **Transaction Safety & Button Locking:**
   - When the circuit is `OPEN`, safely disable execution buttons (Submit, Checkout, Place Order) with clear explanatory tooltips to prevent double charges.
4. **Dead Letter Queue (DLQ):**
   - Non-blocking events (webhooks, notifications, background sync) must be queued in Redis (BullMQ) or PostgreSQL with exponential backoff for replay upon partner recovery.

---

## 4. Concurrency, TOCTOU & Atomic Inventory Control

### 🚨 The Problem:
Two requests hit the `/checkout` endpoint simultaneously for the last item in stock. Both read `stock === 1`, both approve the order, and stock becomes `-1` (Overselling / Double-Spending).

### 🛡️ Mandatory Defensive Standards:
1. **Atomic Database Mutation:**
   ```sql
   -- ✅ ATOMIC UPDATE: Protects against race conditions
   UPDATE products 
   SET stock = stock - :quantity 
   WHERE id = :productId AND stock >= :quantity;
   ```
   Check the affected rows count; if 0, throw an `InsufficientStockException`.
2. **Pessimistic Locking in Transactions:**
   ```typescript
   await prisma.$transaction(async (tx) => {
     const product = await tx.$queryRaw`
       SELECT * FROM products WHERE id = ${productId} FOR UPDATE
     `;
     // execute booking or stock reduction safely
   });
   ```

---

## 5. Node.js Main Thread Starvation & Anti-OOM Workers

### 🚨 The Problem:
Generating a PDF report, resizing large user avatars, or computing heavy statistics inside the Express/NestJS route handler blocks the single-threaded Node.js event loop. All incoming HTTP requests stall, health checks fail, and Kubernetes restarts the pod.

### 🛡️ Mandatory Defensive Standards:
1. **Dedicated Worker Queues:** Heavy processing (image resizing, video transcoding, bulk CSV exports, AI embeddings) MUST be offloaded to worker processes using BullMQ / Redis.
2. **Bounded Concurrency:** Worker pools must limit simultaneous tasks (e.g. max 5 concurrent transcode jobs) to prevent out-of-memory (OOM) kernel kills.

---

## 6. Authorization Flaws: BOLA, BFLA & Over-Posting

### 🚨 The Problem:
- **BOLA (Broken Object Level Authorization):** `/api/orders/1234` only checks if the caller is logged in, not whether order `1234` belongs to the caller.
- **Over-Posting (Mass Assignment):** A client sends `{ "name": "Jane", "isAdmin": true }` to `/api/users/profile`, and the ORM blindly updates all fields.

### 🛡️ Mandatory Defensive Standards:
1. **Mandatory Ownership Checks:**
   ```typescript
   const order = await this.orderRepo.findOne({ where: { id: orderId } });
   if (!order) throw new NotFoundException();
   if (order.userId !== currentUser.id && !currentUser.roles.includes('ADMIN')) {
     throw new ForbiddenException('Access to requested resource is denied');
   }
   ```
2. **Strict DTO Whitelist Stripping:**
   ```typescript
   // In NestJS main.ts
   app.useGlobalPipes(new ValidationPipe({
     whitelist: true,              // Strips unexpected fields
     forbidNonWhitelisted: true,  // Rejects payload if unknown fields are present
     transform: true,
   }));
   ```

---

## 7. Async/Await Traps & Floating Promises

### 🚨 The Problem:
Using `.forEach()` with an async callback:
```typescript
// ❌ FATAL BUG: Array.prototype.forEach ignores async returns
items.forEach(async (item) => {
  await saveToDatabase(item); // Loop finishes BEFORE saves complete!
});
```

### 🛡️ Mandatory Defensive Standards:
```typescript
// ✅ CORRECT: Sequential
for (const item of items) {
  await saveToDatabase(item);
}

// ✅ CORRECT: Concurrent with Promise.all
await Promise.all(items.map(item => saveToDatabase(item)));
```

---

## 8. Defensive Data Validation Layers (Defense-in-Depth)

Every enterprise feature must be defended by 4 distinct validation layers:
1. **Client Layer:** Immediate UI form validation (React Hook Form + Zod) for instant user feedback.
2. **Transport Layer:** API Gateway / Controller DTO validation with whitelist stripping.
3. **Domain Layer:** Business logic invariants inside use-cases / services (e.g., verifying account balances and user state).
4. **Persistence Layer:** Database constraints (Foreign keys, CHECK constraints, NOT NULL, UNIQUE indexes).
