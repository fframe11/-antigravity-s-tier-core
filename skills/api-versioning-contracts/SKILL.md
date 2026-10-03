---
name: api-versioning-contracts
description: Use when designing API versioning strategies, managing breaking changes, ensuring backward compatibility, or communicating API changes to client teams. Covers URL versioning, header versioning, deprecation timelines, and contract testing.
---
# API Versioning & Contract Management

## When to Use
- Adding a new API version
- Making breaking changes to existing endpoints
- Communicating API changes to frontend/mobile teams
- Setting up contract tests between services

## Versioning Strategy

### URL Path Versioning (Recommended for REST APIs)
```
/api/v1/users
/api/v2/users
```

### NestJS Implementation
```typescript
// app.module.ts
app.enableVersioning({
  type: VersioningType.URI,
  defaultVersion: '1',
});

// users.controller.ts
@Controller({ version: '2', path: 'users' })
export class UsersV2Controller { ... }
```

## Breaking vs Non-Breaking Changes

### Non-Breaking (Safe to deploy)
- Adding new optional fields to response
- Adding new endpoints
- Adding new optional query parameters
- Relaxing validation (accepting wider input)

### Breaking (Requires new version)
- Removing or renaming response fields
- Changing field types (string → number)
- Adding required request fields
- Changing endpoint URL structure
- Modifying error codes clients depend on

## Deprecation Workflow

```
1. New version released (v2) — old version (v1) still works
2. Add deprecation header to v1 responses:
   Deprecation: true
   Sunset: Sat, 01 Mar 2025 00:00:00 GMT
   Link: </api/v2/users>; rel="successor-version"
3. Notify client teams (email + Slack + changelog)
4. Monitor v1 traffic — wait until < 1% of total
5. Return 410 Gone on v1 after sunset date
```

## Contract Testing Checklist
- [ ] Response schema matches OpenAPI spec (use `jest-openapi` or `dredd`)
- [ ] All documented fields are present in actual responses
- [ ] Error responses follow the standard error contract
- [ ] New fields are additive-only (no removals without version bump)
- [ ] Pagination format is consistent (`{ data: [], meta: { total, page, limit } }`)

## Client Communication Template
```markdown
## API Change Notice — v2 Users Endpoint

**What changed:** `GET /api/v2/users` now returns `fullName` instead of separate `firstName`/`lastName`
**Why:** Simplify client rendering and support international name formats
**Migration:** Replace `firstName + ' ' + lastName` with `fullName`
**v1 sunset date:** 2025-03-01
**Questions:** Post in #api-changes Slack channel
```
