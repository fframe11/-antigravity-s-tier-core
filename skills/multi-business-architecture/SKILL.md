---
name: multi-business-architecture
description: Multi-Business Platform Architecture & Inventory Safety. Governs E-commerce, Booking, SaaS, and Public Content systems. Enforces atomic inventory control (SELECT FOR UPDATE / Redis locks), idempotent checkout, strict runtime schema validation (Zod), and server-first SSR/SSG for SEO.
---

# Multi-Business Platform Architecture & Inventory Safety

## 🎯 Objective
- Expand agent engineering boundaries beyond internal BI dashboards into **E-commerce, Booking Systems, Content/Marketing, and SaaS platforms**.
- Eliminate catastrophic business bugs: overselling inventory, double-booking time slots, unvalidated form injections, and zero-SEO client rendering.

---

## 🛒 1. E-Commerce & Booking Rules (Overbooking & Concurrency)

### A. Atomic Inventory Control (`SELECT FOR UPDATE`)
Application-layer checks (e.g., `if (item.stock > 0) item.stock--`) are **strictly FORBIDDEN** because concurrent requests will cause negative stock or overselling.

```typescript
// ✅ Prisma Transaction with Pessimistic Row Lock (Raw SQL or PostgreSQL)
export async function reserveStock(tx: Prisma.TransactionClient, productId: string, quantity: number) {
  // 1. Lock the row immediately with SELECT FOR UPDATE
  const [product] = await tx.$queryRaw<Array<{ id: string; stock: number }>>`
    SELECT id, stock FROM "Product"
    WHERE id = ${productId}
    FOR UPDATE
  `;

  if (!product || product.stock < quantity) {
    throw new BadRequestException({
      code: 'OUT_OF_STOCK',
      message: `Insufficient stock for product ${productId}. Requested: ${quantity}, Available: ${product?.stock ?? 0}`,
    });
  }

  // 2. Decrement atomically within the same locked transaction
  return tx.product.update({
    where: { id: productId },
    data: { stock: { decrement: quantity } },
  });
}
```

### B. Booking Slot Locking (PostgreSQL Advisory Locks / Exclusion Constraints)
For appointment booking, hotel rooms, or seat reservations, prevent double-booking across overlapping time intervals:

```sql
-- PostgreSQL Exclusion Constraint ensuring NO overlapping bookings for the same resource
ALTER TABLE "Booking" ADD CONSTRAINT "no_double_booking"
EXCLUDE USING gist (
  resource_id WITH =,
  tstzrange("startTime", "endTime") WITH &&
);
```

### C. Idempotent Checkout Submission
Checkout, payment execution, and order placement endpoints MUST enforce the `Idempotency-Key` header:

```typescript
@Post('checkout')
async processCheckout(
  @Headers('idempotency-key') idempotencyKey: string,
  @Body() orderDto: CheckoutDto,
  @CurrentUser() user: User,
) {
  if (!idempotencyKey) {
    throw new BadRequestException('Idempotency-Key header is required for checkout');
  }

  // Exact-once lock via Redis (TTL: 5 minutes)
  const lockKey = `idempotency:${user.id}:${idempotencyKey}`;
  const acquired = await this.redis.set(lockKey, 'PROCESSING', 'EX', 300, 'NX');
  if (!acquired) {
    // Return cached response or reject concurrent duplicate click
    const cachedResponse = await this.redis.get(`${lockKey}:response`);
    if (cachedResponse) return JSON.parse(cachedResponse);
    throw new ConflictException('Order request is already processing. Please wait.');
  }

  try {
    const orderResult = await this.orderService.executeCheckout(orderDto, user);
    await this.redis.set(`${lockKey}:response`, JSON.stringify(orderResult), 'EX', 300);
    return orderResult;
  } catch (err) {
    await this.redis.del(lockKey); // Release lock on catastrophic failure
    throw err;
  }
}
```

### D. Cryptographic Payment Webhook Verification & Event Deduplication
AI systems frequently parse webhooks as raw JSON without verifying signatures, exposing the system to forged webhook attacks (allowing attackers to spoof paid orders). Follow these non-negotiable rules:

1. **Verify Raw Body Signature**: Always compute or verify the signature against the unparsed raw `Buffer` of the request payload:
```typescript
// NestJS Webhook Controller (Stripe / Omise / GB Prime Pay)
@Post('webhook/payment')
async handlePaymentWebhook(
  @Req() req: RawBodyRequest<Request>,
  @Headers('stripe-signature') signature: string,
) {
  if (!signature) {
    throw new BadRequestException('Missing payment signature header');
  }

  let event: Stripe.Event;
  try {
    // MUST verify against raw body buffer, NOT parsed JSON
    event = this.stripe.webhooks.constructEvent(
      req.rawBody,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET,
    );
  } catch (err) {
    throw new UnauthorizedException(`Webhook signature verification failed: ${err.message}`);
  }

  // 2. Event Deduplication: Ensure exact-once fulfillment
  const eventKey = `webhook:event:${event.id}`;
  const isNew = await this.redis.set(eventKey, 'PROCESSED', 'EX', 86400, 'NX');
  if (!isNew) {
    return { received: true, note: 'Duplicate event ignored' };
  }

  // 3. Process business logic within transaction
  await this.orderService.fulfillOrder(event.data.object);

  return { received: true };
}
```


---

## 🔍 2. Strict Schema Gatekeeping (Forms & User Entry Points)

Loose manual `if (!data.name)` checks are **strictly FORBIDDEN**. Every user entry point (React Hook Form, query parameters, webhook payloads, REST endpoints) must be validated with **Zod**:

### A. Shared Fullstack Schema Definition
```typescript
// shared/schemas/registration.schema.ts
import { z } from 'zod';

export const RegistrationSchema = z.object({
  email: z.string().email('Invalid business email').trim().toLowerCase(),
  fullName: z.string().min(2, 'Name must be at least 2 characters').max(100).trim(),
  phone: z.string().regex(/^\+?[1-9]\d{7,14}$/, 'Invalid international E.164 phone number'),
  companySize: z.enum(['1-10', '11-50', '51-200', '201+']),
  taxId: z.string().regex(/^[0-9]{13}$/, 'Tax ID must be 13 digits').optional(),
});

export type RegistrationDto = z.infer<typeof RegistrationSchema>;
```

### B. Client-Side Form Guard (React Hook Form)
```tsx
const form = useForm<RegistrationDto>({
  resolver: zodResolver(RegistrationSchema),
  mode: 'onBlur',
});
```

### C. Backend Endpoint Guard (NestJS Zod Pipe)
```typescript
@Post('register')
@UsePipes(new ZodValidationPipe(RegistrationSchema))
async register(@Body() body: RegistrationDto) {
  return this.authService.registerBusiness(body);
}
```

---

## 🌐 3. Server-First for Public Content & SEO (Next.js SSR/SSG)

Public marketing pages, catalog listings, and landing pages must **NEVER** be client-rendered behind blank loading spinners. They must be rendered on the server for instant First Contentful Paint (FCP) and full Googlebot indexing:

### A. Server Component with Dynamic Metadata (Product Catalog Page)
```tsx
// src/app/(public)/products/[slug]/page.tsx
import type { Metadata } from 'next';
import { notFound } from 'next/navigation';

export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const product = await getProductBySlug(params.slug);
  if (!product) return {};

  return {
    title: `${product.title} | Premium Store`,
    description: product.description,
    openGraph: {
      title: product.title,
      description: product.description,
      images: [{ url: product.thumbnailUrl, width: 1200, height: 630 }],
    },
    alternates: {
      canonical: `https://example.com/products/${params.slug}`,
    },
  };
}

export default async function ProductDetailPage({ params }: { params: { slug: string } }) {
  const product = await getProductBySlug(params.slug);
  if (!product) notFound();

  // Structured Data (JSON-LD) for Google Rich Snippets
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.title,
    image: product.thumbnailUrl,
    description: product.description,
    offers: {
      '@type': 'Offer',
      price: product.price,
      priceCurrency: 'THB',
      availability: product.stock > 0 ? 'https://schema.org/InStock' : 'https://schema.org/OutOfStock',
    },
  };

  return (
    <main className="container mx-auto px-4 py-8">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <h1 className="text-3xl font-bold tracking-tight">{product.title}</h1>
      <p className="text-xl font-semibold mt-2">{product.price.toLocaleString()} THB</p>
      {/* Rest of server-rendered markup */}
    </main>
  );
}
```

### B. Server-First Security & Assessment Platforms (Proprietary Logic Protection)
For testing portals, assessment engines, scoring algorithms, or sensitive calculation systems:
- **Anti-Naive SPA Veto**: Strictly FORBIDDEN from spinning up as client-only React SPA when secrets or proprietary logic are involved. You MUST enforce **Next.js App Router (SSR/RSC)**.
- **Proprietary Logic Protection (RSC Boundary)**: Scoring rubrics, evaluation thresholds, and answer verification MUST execute exclusively inside Server Components or Server Actions (`'use server'`). Secret keys or evaluation logic must never be exposed or hydrated into client JavaScript state.
- **Deterministic Internationalization**: All criteria and UI elements must ingest localized strings via `next-intl` (`locales/th.json` and `locales/en.json`). Robotic parenthetical strings (`แดชบอร์ด... (Performance Telemetry)`) are strictly banned.
- **Strict Zod Form Guard**: All submissions, answers, and operational parameters must be validated through strict Zod schemas before touching the persistence layer.

---

## 🧪 4. Concurrency Fuzz Test for Inventory Overbooking

Every inventory or reservation service MUST pass a 50-thread concurrent Jest burst test proving that overbooking is mathematically impossible:

```typescript
// test/inventory-concurrency.spec.ts
describe('Inventory Concurrency Gate (Overbooking Protection)', () => {
  it('prevents overselling when 50 concurrent users attempt to buy the last 5 items', async () => {
    const initialStock = 5;
    const productId = 'prod_limited_edition_001';
    await resetProductStock(productId, initialStock);

    // Launch 50 simultaneous parallel purchase requests
    const concurrentAttempts = 50;
    const promises = Array.from({ length: concurrentAttempts }).map((_, i) =>
      checkoutService.reserveItem({
        productId,
        quantity: 1,
        userId: `user_${i}`,
        idempotencyKey: `key_${i}`,
      }).then(() => ({ success: true }))
        .catch(err => ({ success: false, error: err.message }))
    );

    const results = await Promise.all(promises);
    const successCount = results.filter(r => r.success).length;
    const failureCount = results.filter(r => !r.success).length;

    // INVARIANTS:
    expect(successCount).toBe(initialStock); // Exactly 5 orders succeeded
    expect(failureCount).toBe(concurrentAttempts - initialStock); // 45 were safely rejected

    const finalProduct = await getProduct(productId);
    expect(finalProduct.stock).toBe(0); // Stock reached exactly 0, NEVER negative
  });
});
```

---

## 🍱 5. Personal User Health Invariant (Severe Shellfish Allergy: Shrimp & Crab)
Whenever generating mock data, database seeds, test fixtures, recipe datasets, or UI menus for food, restaurant, grocery, or delivery platforms:
- **Strictly FORBIDDEN** from including shrimp (`กุ้ง`), crab (`ปู`), lobster, or shellfish ingredients.
- Use safe alternative proteins and ingredients (e.g. Chicken, Wagyu Beef, Salmon, Pork, Tofu, Eggs, Mushrooms, Vegetables) to prevent confusion and errors during local development and testing.

---

## 🔌 6. Vendor Downtime Invariant & Circuit Breaker Pattern (Third-Party Service Continuity)

When integrating external third-party APIs (e.g., Payment Gateways, Trading/Broker Platforms like IUX, Shipping/Courier APIs, SMS/Notification providers):

### A. Circuit Breaker Pattern Enforcement
Every remote call to an external vendor MUST be wrapped in a resilient Circuit Breaker (e.g., using `opossum` in Node.js or a bounded state machine):
- **Failure Threshold**: Trip circuit to `OPEN` if consecutive failures or 5xx responses exceed 5 occurrences or 50% over a 10s window.
- **Timeout Bound**: Enforce strict 5000ms timeout per external HTTP request; never permit hanging connections.
- **Half-Open Probing**: Probe with a single request after a 30s reset cooldown before resuming full traffic.

```typescript
// ✅ Resilient Third-Party Vendor Wrapper with Circuit Breaker
import CircuitBreaker from 'opossum';

const vendorBreakerOptions = {
  timeout: 5000, // 5s timeout
  errorThresholdPercentage: 50,
  resetTimeout: 30000, // 30s before attempting half-open
};

export const externalVendorBreaker = new CircuitBreaker(callExternalVendorApi, vendorBreakerOptions);

externalVendorBreaker.fallback((params, err) => {
  // Graceful fallback response
  return {
    isAvailable: false,
    status: 'VENDOR_MAINTENANCE',
    message: 'Partner service is currently undergoing scheduled maintenance. Please try again shortly.',
    retryAfterSeconds: 30,
  };
});
```

### B. Graceful Degradation & Anti-Raw-Error UI Invariant
When the circuit is `OPEN` or the vendor returns HTTP 502/503/504:
- **Zero Raw Traces**: Strictly FORBIDDEN from exposing raw error messages (`ECONNREFUSED`, `ETIMEDOUT`, `503 Service Unavailable`, stack traces) to user viewports.
- **Polite Maintenance Banner / Modal**: Display a clear, branded user-facing notification informing users that the specific feature is temporarily undergoing scheduled vendor maintenance, with an estimated return time.
- **Transaction Button Disabling**: Temporarily disable checkout, submit, or trade execution buttons with tooltip feedback ("Service temporarily paused for scheduled partner maintenance") to prevent duplicate charging or inconsistent state.
- **Asynchronous Dead Letter Queue (DLQ)**: For non-blocking external operations (webhooks, notifications, audit sync), queue payloads in a persistent Redis/PostgreSQL queue with exponential backoff for replay once vendor service recovers.


