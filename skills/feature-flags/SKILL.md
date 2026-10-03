---
name: feature-flags
description: Use when implementing feature flags, progressive rollouts, A/B testing, or kill switches in production systems. Covers LaunchDarkly, PostHog, Flagsmith, Unleash, and custom implementations.
---

# Feature Flags & Progressive Delivery Guide

## When to Use This Skill
- Decoupling software deployments from feature releases to enable trunk-based development.
- Implementing canary releases, percentage rollouts, and user cohort targeting (beta testers, enterprise tiers).
- Setting up system kill switches, circuit breakers, and operational controls for high-risk dependencies.
- Managing experiment variants for A/B/n testing and measuring statistical conversions.
- Integrating feature flag providers (LaunchDarkly, PostHog, Unleash, Flagsmith) or custom evaluation engines.

## Core Principles
1. **Short-Lived by Default**: Release flags are technical debt with an expiration date. Treat un-removed flags as active defects; schedule cleanup tickets upon feature release.
2. **Zero-Latency In-Memory Evaluation**: Server-side flag evaluation must happen in memory via local streaming or polling caches. Never make synchronous network calls to flag vendors inside request hot paths.
3. **Deterministic Bucketing**: Percentage rollouts must evaluate consistently for the same user identifier (e.g., `hash(userId + flagKey) % 100`) without sticky sessions or database lookups.
4. **Safe Fallbacks (Fail-Closed vs Fail-Open)**: Every flag evaluation must declare an explicit default. Operational safety switches should fail open or fall back to static, proven degradation paths.
5. **Decouple Code from State**: Application logic must not depend on flag service availability. If SDK initialization fails or times out, the application must boot and operate with baked-in defaults.

## Implementation Patterns

### 1. Flag Taxonomy and Naming Conventions
Structure flag keys systematically by category, service, and intent:
`[type].[service].[domain].[feature-description]`

| Flag Type | Lifetime | Dynamic / Static | Typical Use Case |
| :--- | :--- | :--- | :--- |
| `release.*` | 1 - 4 weeks | Dynamic rollout | Continuous delivery, new checkout UI |
| `experiment.*` | 2 - 8 weeks | Dynamic cohort | A/B testing conversion algorithms |
| `ops.*` | Permanent | Dynamic toggle | Circuit breaker, third-party vendor bypass |
| `permission.*` | Permanent | Dynamic rule | Tiered entitlement (e.g., Enterprise SSO) |

*Example keys*: `release.billing.stripe-v3-migration`, `ops.search.disable-vector-reranking`.

### 2. Server-Side Evaluation with Local Cache & Fallbacks
Pre-fetch or stream flag definitions into an in-memory store to eliminate network latency.

```typescript
// featureFlags.ts
import { UnleashClient } from 'unleash-client';

const unleash = new UnleashClient({
  url: process.env.UNLEASH_API_URL!,
  appName: 'payment-service',
  customHeaders: { Authorization: process.env.UNLEASH_API_TOKEN! },
});

export function isFeatureEnabled(flagKey: string, context: { userId?: string; orgId?: string }, defaultValue = false): boolean {
  try {
    return unleash.isEnabled(flagKey, {
      userId: context.userId,
      properties: { orgId: context.orgId },
    }, defaultValue);
  } catch (err) {
    logger.warn({ err, flagKey }, 'Flag evaluation error, falling back to default');
    return defaultValue;
  }
}
```

### 3. Consistent Hashing for Percentage Rollouts
Ensure consistent assignment without state storage using deterministic hashing.

```python
import mmh3  # MurmurHash3

def is_user_in_rollout(flag_name: str, entity_id: str, rollout_percentage: int) -> bool:
    """Deterministically buckets entity into 0-99 percentage groups."""
    if rollout_percentage <= 0:
        return False
    if rollout_percentage >= 100:
        return True
    hash_value = abs(mmh3.hash(f"{flag_name}:{entity_id}")) % 100
    return hash_value < rollout_percentage
```

### 4. Emergency Kill Switch (Operational Flag)
Bypass degraded third-party services instantly without code redeployment.

```python
def process_recommendations(user_id: str):
    # ops flag defaults to True (enabled). If AI service degrades, flip to False.
    use_ai_recommendations = flag_client.evaluate("ops.recommendations.enable-ai-engine", default=True)
    
    if use_ai_recommendations:
        try:
            return call_vector_search(user_id, timeout_ms=300)
        except VectorServiceUnavailable:
            metrics.increment("recommendation.fallback.invoked")
            
    # Static rule-based fallback path
    return get_trending_items_fallback()
```

### 5. Client-Side Flag Bootstrapping
Prevent client-side layout shifts (flicker) by evaluating flags server-side during SSR and bootstrapping initial state.

```typescript
// Next.js / React Server Component
export default async function DashboardPage({ session }) {
  // Evaluate flags on server
  const flags = await getEvaluatedFlagsForUser(session.userId);

  return (
    <FeatureFlagProvider initialFlags={flags}>
      <DashboardView />
    </FeatureFlagProvider>
  );
}
```

### 6. Automated Testing with Flags
Test both branch paths (flag enabled vs flag disabled) explicitly in unit and integration suites.

```typescript
describe('Checkout Flow', () => {
  it('processes legacy checkout when new flow is disabled', async () => {
    flagMock.setFlag('release.billing.stripe-v3', false);
    const res = await processCheckout(payload);
    expect(res.gateway).toBe('legacy_v1');
  });

  it('routes to Stripe v3 when flag is enabled', async () => {
    flagMock.setFlag('release.billing.stripe-v3', true);
    const res = await processCheckout(payload);
    expect(res.gateway).toBe('stripe_v3');
  });
});
```

## Anti-Patterns to Avoid
- **Synchronous Network Calls on Request Path**: Querying flag SaaS APIs via HTTP during incoming web requests, adding latency and single points of failure.
- **Nested Flag Conditionals (Flag Spaghetti)**: Nesting multiple interdependent flags (`if flagA && (!flagB || flagC)`), creating exponential testing permutations and unmaintainable code.
- **Orphaned / Zombie Flags**: Leaving release flags in code months after 100% rollout, cluttering source files with dead execution paths.
- **Client-Side Secret Leakage**: Sending internal targeting rules, employee emails, or unreleased feature configurations in client-facing evaluation payloads.
- **Reusing Flags Across Unrelated Domains**: Using a single flag for both UI presentation and backend data schema migration.
- **Non-Idempotent Evaluations**: Changing a user's variant mid-session during transactional workflows (e.g., changing checkout forms during multi-step submission).

## Verification Checklist
- [ ] Every new flag has a documented owner, designated category, and target deprecation date.
- [ ] Flags default to a safe, non-breaking fallback state if the evaluation engine is unreachable.
- [ ] Percentage rollouts use consistent hashing against a fixed identifier (e.g., `userId` or `orgId`).
- [ ] Client-side delivery minimizes layout shifting using server-side pre-computation or hydration bootstrap.
- [ ] Both enabled and disabled codepaths are covered by automated unit and integration tests.
- [ ] Monitoring dashboards track flag evaluation rates, variant distributions, and system errors.
- [ ] Scheduled recurring audit alerts identify flags older than 30-60 days for removal.
