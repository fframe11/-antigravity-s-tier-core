---
name: error-handling-standards
description: Use when designing error handling, structuring API error responses, implementing global exception filters, or standardizing error codes across a backend service. Covers NestJS exception filters, Prisma error mapping, and client-facing error contracts.
---
# Error Handling Standards

## When to Use
- Designing API error response format
- Implementing NestJS exception filters
- Mapping Prisma/database errors to HTTP responses
- Reviewing error handling completeness

## Standard Error Response Contract

Every API error response MUST follow this shape:

```typescript
{
  "statusCode": 400,
  "code": "VALIDATION_FAILED",
  "message": "Human-readable error description",
  "details": [
    { "field": "email", "issue": "must be a valid email" }
  ],
  "requestId": "req_abc123"
}
```

### Rules
1. **Always return `code`** — Machine-readable error code (e.g., `USER_NOT_FOUND`, `INSUFFICIENT_BALANCE`). Clients switch on this, not `statusCode`.
2. **Never leak internals** — No stack traces, SQL queries, or Prisma error messages in responses.
3. **Always include `requestId`** — Correlate with server logs for debugging.
4. **Use standard HTTP status codes** — 400 validation, 401 unauthenticated, 403 forbidden, 404 not found, 409 conflict, 422 unprocessable, 429 rate limited, 500 internal.

## NestJS Global Exception Filter

```typescript
@Catch()
export class GlobalExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse();
    const request = ctx.getRequest();

    const { statusCode, code, message, details } = this.mapException(exception);

    response.status(statusCode).json({
      statusCode,
      code,
      message,
      details,
      requestId: request.headers['x-request-id'] || generateId(),
    });

    // Log full error server-side (never send to client)
    this.logger.error({ code, message, stack: exception?.stack, requestId });
  }
}
```

## Prisma Error Mapping

| Prisma Code | HTTP Status | App Code | When |
|---|---|---|---|
| `P2002` | 409 | `DUPLICATE_ENTRY` | Unique constraint violation |
| `P2025` | 404 | `RECORD_NOT_FOUND` | Record not found |
| `P2003` | 400 | `FOREIGN_KEY_VIOLATION` | FK constraint failed |
| `P2024` | 503 | `DB_CONNECTION_TIMEOUT` | Connection pool exhausted |

## Anti-Patterns
- ❌ Empty `catch {}` blocks — Always log or re-throw
- ❌ `catch (e) { return res.status(500).json({ error: e.message }) }` — Leaks internals
- ❌ String-based error checking: `if (e.message.includes('unique'))` — Use error codes
- ❌ Swallowing errors in async operations (fire-and-forget without logging)

## Verification
- [ ] Every endpoint returns the standard error shape on failure
- [ ] No Prisma/TypeORM raw errors reach the client
- [ ] `requestId` is present in every error response
- [ ] Server logs contain full stack traces; client responses do not
