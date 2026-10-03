---
name: openapi-contract-testing
description: Use when validating API contracts, ensuring backward compatibility, or implementing consumer-driven contract testing. Covers OpenAPI spec validation, Pact, Dredd, and schema-first development.
---

# OpenAPI & Contract Testing Guide

This skill provides comprehensive methodologies for schema-first API engineering, consumer-driven contract testing with Pact, backward compatibility enforcement, automated CI validation, and mock server orchestration.

## When to Use This Skill
- Designing RESTful APIs using schema-first specifications before writing backend code.
- Enforcing backward compatibility and preventing breaking changes across microservice boundaries.
- Implementing consumer-driven contract testing (CDC) using Pact between frontend/backend or microservices.
- Running mock servers (Prism) for parallel frontend development against OpenAPI 3.x specifications.
- Automating spec linting (Spectral), contract verification (Dredd), and changelog generation in CI/CD.
- Defining formal API versioning, deprecation headers, and sunsetting policies.

## Core Principles & Design Strategies

### Schema-First vs Code-First API Design
- **Schema-First (Recommended)**: Define the OpenAPI 3.x YAML/JSON specification before writing code. Serves as the single source of truth for documentation, client SDK generation, mock servers, and contract test assertions. Prevents implementation leakage into API design.
- **Code-First**: Write controller annotations that generate specs dynamically. Often leads to subtle breaking changes during refactorings, leaky abstractions, and coupling to language serialization defaults. Use only for legacy migrations.

### Backward Compatibility & Change Rules
| Operation | Type | Impact | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Add optional field to response** | Non-breaking | Additive | Ensure client decoders ignore unknown properties. |
| **Add optional request parameter** | Non-breaking | Additive | Provider supplies defaults if omitted. |
| **Remove / rename response field** | Breaking | Breaking | Mark field `deprecated: true`; maintain for deprecation window. |
| **Add required request parameter** | Breaking | Breaking | Require new API major version or make parameter optional. |
| **Change field data type / format** | Breaking | Breaking | Create new field name or bump major API version. |
| **Change enum values / response codes** | Breaking | Breaking | Additive enums break strict client deserializers. |

### API Versioning Strategies
1. **URI Path Versioning (Recommended for public APIs)**: `https://api.example.com/v1/users` - Explicit, easily routed at API gateways, works cleanly with OpenAPI tooling.
2. **Request Header Versioning**: `X-API-Version: 2026-09-01` or `API-Version: 2` - Cleaner URLs, supports calendar/date-based release cycles.
3. **Content Negotiation (Accept Header)**: `Accept: application/vnd.company.v2+json` - Strict RESTful resource versioning; requires custom gateway caching.

### Deprecation & Sunset Policies (RFC 8594)
When sunsetting endpoints or fields, advertise timelines directly in HTTP response headers:
```http
HTTP/1.1 200 OK
Content-Type: application/json
Deprecation: @1774051200
Sunset: Wed, 21 Sep 2027 00:00:00 GMT
Link: <https://api.example.com/docs/deprecations/v1>; rel="deprecation"
```
Enforce a minimum **6-month grace period** for minor endpoint deprecations and **12 months** for major API version shutdowns.

## Implementation Patterns & Concrete Examples

### 1. Robust OpenAPI 3.1 Spec Pattern
```yaml
openapi: 3.1.0
info:
  title: User Management Service
  version: 1.2.0
paths:
  /users/{id}:
    get:
      summary: Retrieve user by ID
      operationId: getUserById
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema: { $ref: '#/components/schemas/UserResponse' }
        '404':
          description: User not found
          content:
            application/json:
              schema: { $ref: '#/components/schemas/ErrorResponse' }
components:
  schemas:
    UserResponse:
      type: object
      required: [id, email, status]
      properties:
        id: { type: string, format: uuid }
        email: { type: string, format: email }
        status: { type: string, enum: [active, suspended, archived] }
      additionalProperties: false
    ErrorResponse:
      type: object
      required: [code, message]
      properties:
        code: { type: string, example: USER_NOT_FOUND }
        message: { type: string, example: The requested user does not exist }
```

### 2. Consumer-Driven Contract Testing (Pact)
Define consumer expectations, generate the pact contract file, and verify against the provider:
```python
# Consumer Test (pytest with pact-python)
from pact import Consumer, Provider

pact = Consumer("WebFrontend").has_pact_with(Provider("UserService"), port=1234)

def test_get_user_contract():
    expected = {"id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "email": "alex@example.com", "status": "active"}
    (pact.given("user exists")
     .upon_receiving("a request for user details")
     .with_request("GET", "/users/a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
     .will_respond_with(200, body=expected))
    with pact:
        from my_client import get_user
        res = get_user("http://localhost:1234", "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
        assert res["email"] == "alex@example.com"
```
```bash
# Provider Verification via CLI
pact-provider-verifier --provider-base-url=http://localhost:8080 --pact-urls=./pacts/webfrontend-userservice.json
```

### 3. Automated Spec Validation & Breaking Change Detection in CI
Prevent breaking contract changes on pull requests using `spectral`, `oasdiff`, and `dredd`:
```yaml
# .github/workflows/contract-testing.yml
name: API Contract Validation
on: [pull_request]
jobs:
  validate-contracts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - name: Lint Spec with Spectral
        run: npx @stoplight/spectral-cli lint openapi.yaml --ruleset .spectral.yaml
      - name: Detect Breaking Changes vs Main Branch
        run: |
          git show origin/main:openapi.yaml > openapi_base.yaml
          docker run --rm -v $(pwd):/specs tufin/oasdiff -base /specs/openapi_base.yaml -revision /specs/openapi.yaml -breaking --fail-on ERR
      - name: Run Dredd Contract Testing against Local Backend
        run: |
          npm run start:server &
          npx dredd openapi.yaml http://localhost:8080 --hookfiles=./dredd-hooks.js
```

### 4. Mock Servers & Spec Changelog Generation
Run instant dynamic mock servers from OpenAPI specs for frontend development without running backends:
```bash
# Spin up Prism HTTP mock server with schema validation
npx @stoplight/prism-cli mock -p 4010 openapi.yaml

# Generate Markdown changelog between versions
docker run --rm -v $(pwd):/specs tufin/oasdiff -base /specs/openapi_v1.yaml -revision /specs/openapi_v2.yaml -format markdown > CHANGELOG.md
```

## Anti-Patterns to Avoid
- **Uncontrolled In-Band Breaking Changes**: Changing response field names or removing properties without releasing a new version or deprecation window.
- **Permissive Open Schemas**: Leaving `additionalProperties` untyped or unconstrained, allowing accidental schema bloat and unpredictable serialization.
- **Contract Drift**: Writing OpenAPI specs manually that are never validated in CI against running service responses.
- **Testing Against Live Staging Endpoints**: Running consumer tests against flaky multi-tenant staging environments instead of deterministic Pact mock contracts.
- **Ghost Deprecations**: Deprecating endpoints in documentation without returning `Sunset` and `Deprecation` HTTP response headers.

## Verification Checklist
- [ ] OpenAPI 3.x specification is validated with Spectral linter on every commit.
- [ ] Pull requests run breaking change detection (`oasdiff -breaking`) against base branch.
- [ ] Reusable models are consolidated under `components/schemas` with explicit `required` lists.
- [ ] Consumer-driven pacts are verified by provider builds before deployment (`can-i-deploy`).
- [ ] Prism mock server is available for integration and frontend test suites.
- [ ] Deprecated routes include RFC 8594 `Sunset` headers and documentation migration links.
