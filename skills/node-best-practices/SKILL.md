---
name: node-best-practices
description: Use when writing Node.js / TypeScript / NestJS / Express backend services, configuring Monorepos, Dockerfiles, Cloud Run jobs/services, Prisma/ORM layers, or reviewing production Node.js architecture. Mapped to local repository nodebestpractices.
---
# Node.js / TypeScript / NestJS Production Engineering Guardrails

This skill provides strict production-grade coding guardrails for Node.js, TypeScript, NestJS, Express, and Prisma services, in addition to referencing local guides at `C:\Users\ffram\security_repos\nodebestpractices`.

Whenever writing or modifying Node.js / TypeScript backend code, you MUST enforce these **5 Production-Grade Coding Guardrails** before claiming completion:

## 1. Build, Bundler & Path Alias Resolution (`dist/` Verification)
- **Never rely solely on `tsc --noEmit` for monorepos or path aliases (`@app/*`, `@common/*`)**: Standard `tsc` compiles TypeScript to JavaScript in `dist/` **without** rewriting TypeScript `paths` aliases. When executed with `node dist/...`, Node.js will crash with `Cannot find module '@app/common'`.
- **Mandatory Bundler / Alias Rewriting**:
  - In **NestJS Monorepos (`nest-cli.json`)**: Always set `"webpack": true` in `compilerOptions` so `nest build <app>` bundles path aliases into runnable `dist/apps/<app>/main.js`, OR configure `tsconfig-paths/register` / `tsc-alias` in the build script.
  - **Entrypoint Parity**: Verify the exact output path produced by the build tool (e.g., `dist/apps/api/main.js` vs `dist/apps/api/apps/api/src/main.js`) and ensure `package.json` (`start:prod`) and `Dockerfile` (`CMD`) point to the exact existing file.

## 2. Docker Multi-Stage & Cloud Run Job / Worker Binary Preservation
- **Preserve Required CLI Binaries for Migration / Worker Jobs**:
  - If the same Docker runtime image is shared between an API service and a Cloud Run Job (e.g., `npx prisma migrate deploy`), **NEVER run `npm prune --omit=dev` without preserving the `prisma` CLI** in `dependencies` (or copying the required CLI binary and generated client engines into the final stage).
  - Always `COPY --from=builder /app/prisma ./prisma` into the final runner stage so migration jobs have access to `schema.prisma` and `migrations/`.
- **Non-Root Container Execution**:
  - Run the final container stage as a non-root user (`USER node`) and set `NODE_ENV=production`.

## 3. Cloud Run & Container Runtime Lifecycle Guardrails
- **Dynamic Port Binding (`process.env.PORT`)**:
  - Every HTTP server (`app.listen()`) MUST read `const port = Number(process.env.PORT || 8080)` (or project default) and bind to `0.0.0.0` (`await app.listen(port, '0.0.0.0')`). Never hardcode `app.listen(3000)`.
- **Single Graceful Shutdown Hook (`SIGTERM` / `SIGINT`)**:
  - Call `app.enableShutdownHooks()` **exactly once** (typically in `main.ts`). Do NOT duplicate `app.enableShutdownHooks()` inside sub-modules (`PrismaService`, `RedisService`) to prevent duplicate signal listener warnings and race conditions during container drain.
- **Structured JSON Logging (`severity` field)**:
  - Production logs must output single-line JSON containing `"severity"` (`INFO`, `WARNING`, `ERROR`, `CRITICAL`), `"message"`, `"timestamp"`, and `"traceId"`/`"correlationId"` so Google Cloud Logging / Datadog parses severity levels automatically.

## 4. Database Transaction, Outbox & Concurrency Safety
- **Zero External Network I/O Inside DB Transactions**:
  - Never call external HTTP APIs, payment gateways, or Pub/Sub publish directly inside an open `prisma.$transaction(...)` block. Hold DB locks for the shortest possible duration.
- **Transactional Outbox Pattern**:
  - Write domain state changes and `OutboxEvent` records inside the **same** database transaction (`prisma.$transaction`). Relay/publish outbox events asynchronously outside the transaction using `FOR UPDATE SKIP LOCKED` (or atomic claim updates) to prevent duplicate publishing across horizontal replicas.
- **Idempotency on Webhook / Push Consumers**:
  - Every Pub/Sub push handler, webhook endpoint, and background worker MUST enforce idempotency (via unique `eventId` / `idempotencyKey` constraint or atomic state machine transition check `WHERE status = expected_status`) before executing side effects.

## 5. Mandatory Runtime Artifact Verification Gate
Before finishing any Node.js / TypeScript implementation task, execute these 3 verification steps:
1. **Compile Build**: Run `npm run build` (not just `tsc --noEmit`).
2. **Verify `dist/` Artifact Path**: Confirm `Test-Path dist/.../main.js` matches the `Dockerfile` `CMD` and `package.json` `start:prod` script.
3. **Boot Smoke Test**: Start the compiled bundle (`node dist/.../main.js`) and verify it boots cleanly or reaches the expected connection step without `MODULE_NOT_FOUND` errors.

---

## 6. Node.js Best Practices Reference (from goldbergyoni/nodebestpractices)

### Architecture & Code Structure
- **[1.1] Structure by business components**: Organize into domain modules (`modules/orders/`, `modules/users/`) with isolated APIs and services. Never group all controllers/models in flat global folders.
- **[1.2] Layer components with 3-tiers**: Controllers handle HTTP mapping + DTO validation only. Pass pure DTOs into domain services. Never leak `req`/`res` into business logic.
- **[1.4] Environment-aware config**: Validate all env vars at startup with typed schema (Zod/Joi/class-validator). Crash immediately if required config is missing.
- **[3.13] No side effects at import time**: Wrap initialization and DB connections inside functions or NestJS `onModuleInit`. Never trigger I/O at file evaluation time.
- **[5.12] Stateless services**: Store sessions, rate-limit counters, and transient state in external stores (Redis/PostgreSQL). Containers can die at any time.

### Error Handling
- **[2.2] Extend built-in Error**: Always throw classes inheriting `Error` (or NestJS `HttpException`) with `name`, `statusCode`, `isOperational`.
- **[2.3] Operational vs catastrophic**: Mark predictable errors `isOperational = true` for clean client responses. Treat unknown exceptions as triggers for graceful restart.
- **[2.4] Centralized error handler**: All unhandled exceptions → global NestJS `ExceptionFilter`. Standardize error payloads, structured logs, and exit signals.
- **[2.7] Use mature logger**: Replace `console.log` with Pino. Output JSON with log levels and custom error properties.
- **[2.8] Catch unhandled rejections**: Register `process.on('unhandledRejection')` and `process.on('uncaughtException')` at bootstrap for graceful shutdown.
- **[2.12] Always await before returning**: Use `return await fn()` in async functions to preserve full stack traces.
- **[6.20] Hide error details from clients**: In production, return generic error codes. Log detailed stack traces internally only.

### Security
- **[6.2] Rate limit all public endpoints**: Use `@nestjs/throttler` or `rate-limiter-flexible` backed by Redis. Stricter limits on auth endpoints.
- **[6.3] Never hardcode secrets**: Inject via env vars from secret managers (GCP Secret Manager, AWS Secrets Manager, Vault).
- **[6.4] Parameterized queries only**: Use Prisma/TypeORM query builders. Never string concatenation in queries.
- **[6.6] Security headers**: Attach `helmet()` middleware at bootstrap. Remove `X-Powered-By`.
- **[6.8] Password hashing**: bcrypt (cost ≥ 12) or argon2. Constant-time comparisons.
- **[6.10] Validate JSON schemas**: Global `ValidationPipe({ whitelist: true, forbidNonWhitelisted: true, transform: true })` on every route.
- **[6.13] Run as non-root**: `USER node` in Dockerfile before `CMD`.
- **[6.16] Prevent ReDoS**: Use `validator.js` instead of custom regex on untrusted input. Audit with `safe-regex`.

### Testing
- **[4.1] Prioritize API (component) tests**: Integration tests with Supertest/Jest against compiled app module. Higher ROI than isolated unit tests.
- **[4.2] 3-part test names**: `it('when X, should Y')` — unit under test, scenario, expected outcome.
- **[4.3] AAA pattern**: Arrange (setup), Act (invoke), Assert (verify). Separate explicitly.
- **[4.5] Per-test data**: Each test creates its own DB entities and cleans up. Never share mutable state.
- **[4.10] Mock external HTTP**: Use `nock` or MSW to simulate third-party API successes, rate limits, and timeouts.

### Performance & Runtime
- **[5.14] Correlation IDs**: Generate UUID `traceId` at HTTP entry, propagate via `AsyncLocalStorage`, attach to every log.
- **[5.18] Log to stdout**: Write structured logs to `process.stdout`. Let Docker/K8s/Cloud Run collect and ship.
- **[7.1] Don't block event loop**: Offload CPU-heavy work to Worker Threads or BullMQ queues.
- **[8.1] Multi-stage Docker builds**: Build TypeScript in builder stage, copy only `dist/` + production deps to slim runtime image.
- **[8.6] Graceful shutdown**: `app.enableShutdownHooks()`, trap SIGTERM, stop new connections, drain active requests, close DB pools, exit 0.

