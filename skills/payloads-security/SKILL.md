---
name: payloads-security
description: Use when auditing APIs for security flaws, verifying code against security checklists, or searching for exploit payloads to test system defense (e.g. SQL Injection, XSS, Path Traversal). Mapped to local repositories API-Security-Checklist, CheatSheetSeries, and PayloadsAllTheThings.
---
# API Security Audit & Exploit Payload Reference

This skill provides actionable security checklists and references to real attack payloads for hardening backend APIs. Use it during Adversarial Review (code-review-and-quality Section 0) or when designing new API endpoints.

## Quick API Security Checklist (from API-Security-Checklist repo)

### Authentication
- Never use Basic Auth in production. Use JWT / OAuth2 with proper token rotation.
- Enforce `Max Retry` + account lockout on login endpoints.
- Encrypt all sensitive data at rest and in transit.

### Authorization
- Validate `redirect_uri` server-side (OAuth). Only allow safelisted URLs.
- Use `state` parameter with random hash to prevent CSRF on OAuth flows.
- **BOLA Prevention**: Never expose raw user IDs in URLs. Use `/me/orders` not `/user/654321/orders`. Use UUID instead of auto-increment IDs.

### Input Validation
- Validate `content-type` on request headers. Reject unexpected types with `406`.
- Never put credentials, API keys, or tokens in the URL. Use `Authorization` header.
- Validate all user input against XSS, SQL Injection, and Remote Code Execution.

### Output Security
- Send `X-Content-Type-Options: nosniff`, `X-Frame-Options: deny`, `Content-Security-Policy: default-src 'none'`.
- Remove fingerprinting headers: `X-Powered-By`, `Server`, `X-AspNet-Version`.
- Never return sensitive data (passwords, tokens, PII) in API responses.
- Return generic error messages to clients. Log detailed errors server-side only.

### Rate Limiting
- Implement sliding window rate limiting per API key and IP.
- Use exponential backoff for repeated failed auth attempts.
- Monitor and alert on unusual API usage patterns.

## Attack Payload Reference (from PayloadsAllTheThings repo)

When performing Adversarial Review, reference these payload categories at `~/security_repos\PayloadsAllTheThings\` to test defenses:

### Most Relevant for NestJS + PostgreSQL APIs
| Attack Category | Folder | What to Check |
|---|---|---|
| **SQL Injection** | `SQL Injection/` | Parameterized queries everywhere. No string concatenation in Prisma `$queryRaw`. |
| **NoSQL Injection** | `NoSQL Injection/` | If using MongoDB alongside PostgreSQL. |
| **Insecure Direct Object References** | `Insecure Direct Object References/` | BOLA: Can user A access user B's data by swapping IDs? |
| **Mass Assignment** | `Mass Assignment/` | Are request bodies filtered with DTOs/whitelist? Can users set `role: admin`? |
| **JSON Web Token** | `JSON Web Token/` | `alg: none` bypass, JWT secret brute force, token expiry checks. |
| **Race Condition** | `Race Condition/` | Double-spend, double-booking via concurrent requests. |
| **Server Side Request Forgery** | `Server Side Request Forgery/` | Can user-supplied URLs trigger internal network requests? |
| **Command Injection** | `Command Injection/` | Any `exec()`, `spawn()`, or shell calls with user input? |
| **Directory Traversal** | `Directory Traversal/` | File upload/download paths sanitized? `../../../etc/passwd` blocked? |
| **Upload Insecure Files** | `Upload Insecure Files/` | File type validation, size limits, storage outside webroot. |
| **Business Logic Errors** | `Business Logic Errors/` | Negative quantities, zero-price orders, state machine shortcuts. |
| **OAuth Misconfiguration** | `OAuth Misconfiguration/` | Open redirect, token leakage via referrer, scope escalation. |
| **Prototype Pollution** | `Prototype Pollution/` | `__proto__`, `constructor.prototype` in JSON payloads (Node.js specific). |
| **Open Redirect** | `Open Redirect/` | Unvalidated redirect URLs after login/logout. |

### Secondary (Check If Applicable)
| Attack Category | Folder | When Relevant |
|---|---|---|
| XSS Injection | `XSS Injection/` | If rendering HTML or using template engines |
| CORS Misconfiguration | `CORS Misconfiguration/` | If serving cross-origin requests |
| GraphQL Injection | `GraphQL Injection/` | If using GraphQL |
| CSRF | `Cross-Site Request Forgery/` | If using cookie-based auth |
| XXE Injection | `XXE Injection/` | If parsing XML |
| Insecure Deserialization | `Insecure Deserialization/` | If deserializing user-supplied objects |

### How to Use During Adversarial Review
1. Identify which attack categories apply to the code being reviewed.
2. Open the relevant folder in PayloadsAllTheThings to see real exploit examples.
3. For each applicable category, verify the code has explicit defenses (validation, sanitization, parameterized queries, ownership checks).
4. If any defense is missing, flag it as a vulnerability before claiming the task done.

## Full Repo Paths
- API Security Checklist: `~/security_repos\API-Security-Checklist`
- OWASP CheatSheetSeries: `~/security_repos\CheatSheetSeries`
- PayloadsAllTheThings: `~/security_repos\PayloadsAllTheThings`
