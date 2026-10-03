---
name: analytics-tracking
description: Use when implementing product analytics, event tracking, user behavior analysis, or configuring analytics platforms. Covers PostHog, Mixpanel, Google Analytics 4, Segment, and custom event pipelines.
---

# Analytics & Product Event Tracking Guide

This skill governs telemetry instrumentation, event taxonomy, identity resolution, privacy compliance, server/client hybrid pipelines, and data warehouse integration across PostHog, Mixpanel, GA4, and Segment.

## When to Use This Skill
- Designing and enforcing a structured tracking plan and event taxonomy across engineering and product teams.
- Instrumenting client-side and server-side tracking pipelines in web, mobile, and backend microservices.
- Configuring identity resolution (`identify`, `alias`, `group`, `reset`) for B2B multi-tenant or B2C platforms.
- Implementing GDPR/CCPA privacy consent banners, opt-in/opt-out gates, and first-party ingestion proxies.
- Tracking conversion funnels, retention cohorts, feature flag exposures, and A/B test experiment variants.
- Exporting, partitioning, and modeling raw event streams in cloud data warehouses (BigQuery, Snowflake, ClickHouse).

---

## Core Principles & Guidelines

### 1. Event Taxonomy Design (Object-Action Naming)
- **Standard Syntax**: `[object]_[action]` in `lower_snake_case` using past-tense verbs (e.g., `account_created`, `workspace_member_invited`, `checkout_completed`, `document_exported`).
- **Property Casing**: Strictly `lower_snake_case` for all event and user properties (e.g., `order_id`, `plan_type`, `billing_cycle`).
- **Standard Contextual Properties**: Include global dimensions on every event: `app_version`, `environment` (`production`, `staging`), `platform` (`web`, `ios`, `android`), `user_role`, and `organization_id`.
- **Avoid Semantic Duplication**: Do not create separate events for variants of the same action (e.g., use `cta_clicked` with `{ button_name: "hero_signup" }`, not `hero_signup_button_clicked`).

### 2. Core API Primitives
- `identify(userId, traits)`: Links an anonymous visitor session to an authenticated user upon login or registration. Never pass auth tokens, passwords, or raw PII.
- `track(event, properties)`: Emits discrete user or system actions with explicit schema attributes.
- `page(name, properties)` / `screen`: Tracks navigation events and route transitions in SPAs or mobile apps.
- `group(groupId, traits)`: Associates a user with a collective entity (organization, company, workspace) for B2B account analytics.
- `reset()`: Mandated on user logout to flush distinct IDs, local storage cookies, and session state.

### 3. Server-Side vs. Client-Side Telemetry
- **Client-Side**: Essential for UI engagement (clicks, pageviews, viewport scroll, form abandonment, initial referrer, UTMs). Susceptible to 20–40% data loss from ad-blockers and browser privacy protections (Safari ITP).
- **Server-Side**: Source of truth for financial, billing, authorization, and lifecycle state changes (`order_completed`, `subscription_cancelled`). 100% reliable, zero ad-blocker loss.
- **Rule**: Never calculate revenue, activation milestones, or mission-critical metrics exclusively from client-side events.

### 4. Attribution & UTM Parameter Handling
- Capture UTM parameters (`utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`) and `referrer` on first visit.
- Store UTMs in first-party cookies or `sessionStorage`. Persist throughout the session and attach them to downstream `account_created` or `order_completed` conversion events.

### 5. Funnel Analysis & Behavioral Cohorts
- **Conversion Funnels**: Track ordered steps (e.g., `signup_started` -> `email_verified` -> `workspace_created`). Apply strict sequential ordering to identify precise user friction points.
- **Behavioral Cohorts**: Define user segments by action recency and frequency (e.g., active users performing `document_exported` >= 3 times in 14 days) instead of static demographic traits alone.
- **A/B Testing Exposures**: Log `$feature_flag_called` only when the experiment variant is actively rendered on-screen, preventing metric dilution.

### 6. Privacy, Consent & Governance
- **Consent Gates**: Default to denied consent (`posthog.opt_out_capturing()` or GA4 `analytics_storage: 'denied'`) until user grants explicit GDPR/CCPA cookie consent.
- **PII Redaction**: Automate sanitization of emails, IP addresses, credit card numbers, and auth tokens before dispatching payloads.
- **Anti-Bloat Governance**: Block continuous stream telemetry (keystrokes, mouse moves, continuous scroll coordinates). Maintain an active tracking plan and deprecate unused events annually.

---

## Implementation Patterns with Concrete Examples

### Pattern 1: Type-Safe Event Tracking Plan (TypeScript)
```typescript
// tracking-plan.ts: Enforces compile-time validation for all emitted events
export type AnalyticsEvent =
  | {
      event: 'account_created';
      properties: { auth_provider: 'google' | 'github' | 'email'; plan_tier: string };
    }
  | {
      event: 'checkout_completed';
      properties: { order_id: string; total_amount: number; currency: string; items_count: number };
    }
  | {
      event: 'experiment_viewed';
      properties: { experiment_id: string; variant_id: string };
    };

export class AnalyticsTracker {
  static track<E extends AnalyticsEvent>(event: E['event'], properties: E['properties']): void {
    if (typeof window === 'undefined') return;
    // Example using PostHog client
    if (window.posthog && !window.posthog.has_opted_out_capturing()) {
      window.posthog.capture(event, { ...properties, app_version: process.env.NEXT_PUBLIC_APP_VERSION });
    }
  }
}
```

### Pattern 2: Server-Side Authoritative Event Pipeline (Node.js)
```typescript
// server-analytics.ts: High-reliability backend event emitter
import { PostHog } from 'posthog-node';

const client = new PostHog(process.env.POSTHOG_API_KEY!, {
  host: process.env.POSTHOG_HOST || 'https://us.i.posthog.com',
  flushAt: 1, // Flush immediately in serverless/backend runtimes
  flushInterval: 0,
});

export async function trackBillingConversion(userId: string, orgId: string, invoice: any) {
  client.capture({
    distinctId: userId,
    event: 'subscription_upgraded',
    properties: {
      organization_id: orgId,
      plan_id: invoice.lines.data[0].plan.id,
      mrr_amount: invoice.amount_paid / 100,
      currency: invoice.currency.toUpperCase(),
      billing_interval: invoice.lines.data[0].plan.interval,
    },
    groups: { organization: orgId },
  });
  await client.shutdown();
}
```

### Pattern 3: First-Party Reverse Proxy & Ad-Blocker Resilience (Next.js)
```javascript
// next.config.js: Rewrites analytics requests to avoid ad-blocker packet dropping
module.exports = {
  async rewrites() {
    return [
      {
        source: '/ingest/static/:path*',
        destination: 'https://us-assets.i.posthog.com/static/:path*',
      },
      {
        source: '/ingest/:path*',
        destination: 'https://us.i.posthog.com/:path*',
      },
    ];
  },
};
```

### Pattern 4: A/B Testing Exposure & Conversion Funnel Setup
```typescript
// Feature Flag & Experiment Evaluation
import posthog from 'posthog-js';

export function recordExperimentExposure(experimentKey: string) {
  const variant = posthog.getFeatureFlag(experimentKey);
  
  // Emit exposure event once when user sees the variant
  posthog.capture('$feature_flag_called', {
    $feature_flag: experimentKey,
    $feature_flag_response: variant,
  });

  return variant;
}

// Funnel step 1: Registration form opened
posthog.capture('signup_funnel_started', { entry_point: 'navbar_cta' });

// Funnel step 2: Account verified and registered
posthog.capture('account_created', { auth_provider: 'google', plan_tier: 'starter' });
```

### Pattern 5: Local Debug Mode & Telemetry Verification
```typescript
// Enable verbose debug logging during development
if (process.env.NODE_ENV === 'development') {
  posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
    api_host: '/ingest',
    loaded: (ph) => ph.debug(true), // Outputs detailed payload captures to dev console
  });
}
```

---

## Anti-Patterns to Avoid
- **Unstructured Free-Form Naming**: Using inconsistent names (`User Signed Up`, `click_btn_submit`, `PAGEVIEW`) destroys funnel queries and pollutes dashboards.
- **Client-Side-Only Revenue Tracking**: Relying on the browser to record payment completions; network drops and ad-blockers create discrepancy with Stripe/financial logs.
- **Identity Session Bleed**: Omitting `reset()` on user sign-out, which incorrectly stitches the previous user's profile to the next user on shared workstations.
- **Transmitting Raw PII in Event Payloads**: Sending plaintext email addresses, passwords, or personal telephone numbers in `properties` violates GDPR/CCPA.
- **Discarding UTMs on Route Changes**: Capturing UTM parameters on `/landing` but not persisting them when user navigates to `/register`, breaking attribution models.
- **High-Frequency Stream Flooding**: Capturing scroll ticks, hover events, or keystroke inputs, incurring massive SaaS billing charges and exhausting ingestion rate limits.

---

## Verification Checklist
- [ ] Tracking plan defines all events using `object_action` syntax with strongly typed schemas.
- [ ] `identify(userId, traits)` is called on sign-in and `reset()` is called on sign-out.
- [ ] Multi-tenant accounts implement `group(groupId, traits)` linking individual users to organizations.
- [ ] Financial and critical conversion milestones are emitted server-side.
- [ ] First-party proxy rewrites are configured to prevent client-side telemetry drops.
- [ ] Explicit GDPR consent mechanism prevents event dispatch prior to user consent.
- [ ] UTM parameters and referrer strings are persisted across page transitions and linked to sign-up events.
- [ ] No PII (passwords, credit card numbers, raw tokens) is present in event properties or payloads.
- [ ] Debug mode is enabled and verified in development environments prior to production release.
- [ ] Warehouse sync destination (BigQuery / Snowflake) receives partitioned, non-duplicative events.
