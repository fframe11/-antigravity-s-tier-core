---
name: owasp-cheatsheets
description: Provides access to the OWASP Cheat Sheet Series for secure coding, backend security guidelines, cryptography, authentication, session management, input validation, and general security reviews. Use this skill when designing, reviewing, or writing backend services, APIs, and components.
metadata:
  tags: "security, owasp, cheatsheet, backend, authentication, session, input-validation, cryptography"
  category: "security"
---
# OWASP Cheat Sheet Series — Production Security Reference

> Reference: https://cheatsheetseries.owasp.org

## 1. Authentication Security
- **Password Storage**: Use bcrypt (cost ≥ 12) or argon2id. Never MD5/SHA-256 alone.
- **Credential Stuffing Prevention**: Implement rate limiting, CAPTCHA after N failures, account lockout with exponential backoff.
- **Multi-Factor Authentication**: Enforce TOTP/WebAuthn for admin and sensitive operations.
- **Password Policy**: Minimum 8 chars, check against breached password lists (Have I Been Pwned API), no composition rules.

## 2. Session Management
- **Session ID**: Generate with CSPRNG, minimum 128-bit entropy. Never expose in URL.
- **Cookie Attributes**: Always set `Secure`, `HttpOnly`, `SameSite=Lax` (or `Strict`), `Path=/`, reasonable `Max-Age`.
- **Session Fixation Prevention**: Regenerate session ID after login, privilege escalation, and password change.
- **Idle Timeout**: 15-30 minutes for sensitive apps, absolute timeout 8-24 hours.
- **Server-Side Invalidation**: Store sessions server-side (Redis/DB). On logout, destroy session immediately.

## 3. Authorization (Access Control)
- **Deny by Default**: If no explicit permission grants access, deny.
- **BOLA Prevention**: Always validate that the authenticated user owns the requested resource. Never trust client-supplied IDs without ownership check.
- **BFLA Prevention**: Check function-level permissions (role/scope) on every endpoint, not just at the router level.
- **Principle of Least Privilege**: Grant minimum permissions needed. Admin endpoints must have separate authorization middleware.

## 4. Input Validation
- **Whitelist Validation**: Define allowed characters, patterns, and ranges. Reject anything not explicitly allowed.
- **Server-Side Always**: Never rely on client-side validation alone.
- **Type Coercion**: Validate and cast types explicitly (string → number, string → date). Reject unexpected types.
- **File Upload**: Validate MIME type, extension, and file size. Scan for malware. Store outside webroot.
- **NestJS Pattern**: Use `ValidationPipe({ whitelist: true, forbidNonWhitelisted: true, transform: true })` globally.

## 5. SQL Injection Prevention
- **Parameterized Queries Only**: Use Prisma, TypeORM query builder, or `$queryRawUnsafe` with explicit parameters. Never string concatenation.
- **Stored Procedures**: Prefer parameterized stored procedures for complex queries.
- **Least Privilege DB User**: Application DB user should have only SELECT/INSERT/UPDATE/DELETE on specific tables. Never GRANT ALL.

## 6. XSS Prevention
- **Output Encoding**: HTML-encode all dynamic content in templates. Use framework auto-escaping.
- **Content-Security-Policy**: Set strict CSP headers. Avoid `unsafe-inline` and `unsafe-eval`.
- **DOMPurify**: Sanitize any user-supplied HTML before rendering.

## 7. CSRF Prevention
- **Synchronizer Token Pattern**: Generate unique CSRF token per session, validate on every state-changing request.
- **SameSite Cookies**: Set `SameSite=Lax` or `Strict` on session cookies.
- **Origin/Referer Validation**: As defense-in-depth, validate `Origin` header on POST/PUT/DELETE.

## 8. Cryptography
- **Encryption at Rest**: AES-256-GCM for data encryption. Never ECB mode.
- **Encryption in Transit**: TLS 1.2+ only. Disable TLS 1.0/1.1.
- **Key Management**: Store encryption keys in secret managers (GCP Secret Manager, AWS KMS, HashiCorp Vault). Rotate annually.
- **Hashing**: SHA-256 for integrity checks. bcrypt/argon2 for passwords. HMAC-SHA256 for message authentication.

## 9. Error Handling & Logging
- **Generic Error Responses**: Return `{ error: "Internal Server Error", statusCode: 500 }` in production. Never expose stack traces, SQL errors, or file paths.
- **Log Security Events**: Log authentication failures, authorization denials, input validation failures, and rate limit triggers.
- **Never Log Secrets**: Never log passwords, tokens, API keys, credit card numbers, or PII.
- **Structured Format**: JSON logs with `severity`, `timestamp`, `traceId`, `userId`, `action`.

## 10. API Security
- **Rate Limiting**: Apply per-IP and per-user rate limits. Stricter on auth endpoints (5 req/min for login).
- **Request Size Limits**: Set `body-parser` limit (e.g., 1MB). Reject oversized payloads.
- **HTTP Headers**: Use `helmet` middleware. Remove `X-Powered-By`. Set `X-Content-Type-Options: nosniff`.
- **CORS**: Whitelist specific origins. Never `Access-Control-Allow-Origin: *` with credentials.
- **JWT Best Practices**: Short-lived access tokens (15 min), longer refresh tokens (7 days) with rotation. Validate `iss`, `aud`, `exp` claims. Use RS256 or ES256, avoid HS256 with weak secrets.

## Workflow: When to Use This Skill
1. **Before writing any auth endpoint**: Read Sections 1-3
2. **Before writing any data input endpoint**: Read Sections 4-5
3. **Before deploying to production**: Read Sections 8-10
4. **During code review / adversarial review**: Audit against all 10 sections
