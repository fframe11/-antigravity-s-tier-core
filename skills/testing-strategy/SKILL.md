---
name: testing-strategy
description: Use when designing test architecture, choosing what to test, setting up E2E tests, or reviewing test quality and coverage strategy. Covers test pyramid, NestJS testing utilities, database test isolation, and what NOT to test.
---
# Testing Strategy for Production APIs

## When to Use
- Setting up test infrastructure for a new service
- Deciding what to unit test vs integration test vs E2E test
- Reviewing test quality (not just coverage numbers)
- Writing tests for database-dependent code

## Test Pyramid

```
        ╱╲
       ╱  ╲       E2E Tests (5-10%)
      ╱    ╲      Real HTTP requests, real DB
     ╱──────╲
    ╱        ╲    Integration Tests (20-30%)
   ╱          ╲   Service + DB, no HTTP
  ╱────────────╲
 ╱              ╲  Unit Tests (60-70%)
╱                ╲ Pure logic, no I/O
╱──────────────────╲
```

### What Goes Where

| Layer | What to Test | Example |
|---|---|---|
| **Unit** | Pure business logic, calculations, transformations, validators | Price calculation, discount rules, date formatting |
| **Integration** | Service + real database, repository queries, complex business flows | Order creation with inventory check, payment processing flow |
| **E2E** | Full HTTP request → response, auth flow, critical user journeys | `POST /api/v1/orders` returns 201 with correct body |

## NestJS Test Setup

### Unit Test (No dependencies)
```typescript
describe('PriceCalculator', () => {
  let calculator: PriceCalculator;

  beforeEach(() => {
    calculator = new PriceCalculator();
  });

  it('applies percentage discount correctly', () => {
    expect(calculator.applyDiscount(100, 10)).toBe(90);
  });

  it('never returns negative price', () => {
    expect(calculator.applyDiscount(100, 150)).toBe(0);
  });
});
```

### Integration Test (With real DB)
```typescript
describe('OrderService', () => {
  let service: OrderService;
  let prisma: PrismaService;

  beforeAll(async () => {
    const module = await Test.createTestingModule({
      imports: [PrismaModule],
      providers: [OrderService],
    }).compile();

    service = module.get(OrderService);
    prisma = module.get(PrismaService);
  });

  beforeEach(async () => {
    // Clean DB between tests — use transactions for speed
    await prisma.$transaction([
      prisma.order.deleteMany(),
      prisma.user.deleteMany(),
    ]);
  });

  it('creates order and deducts inventory', async () => {
    const user = await prisma.user.create({ data: { name: 'Test', email: 'test@test.com' } });
    const product = await prisma.product.create({ data: { name: 'Widget', stock: 10, price: 100 } });

    const order = await service.createOrder(user.id, product.id, 3);

    expect(order.quantity).toBe(3);
    const updatedProduct = await prisma.product.findUnique({ where: { id: product.id } });
    expect(updatedProduct.stock).toBe(7);  // 10 - 3
  });

  it('throws when insufficient stock', async () => {
    // ...setup with stock: 2
    await expect(service.createOrder(userId, productId, 5))
      .rejects.toThrow('INSUFFICIENT_STOCK');
  });
});
```

### E2E Test (Full HTTP)
```typescript
describe('Orders API (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const module = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = module.createNestApplication();
    app.useGlobalPipes(new ValidationPipe({ whitelist: true }));
    await app.init();
  });

  it('POST /api/v1/orders requires auth', () => {
    return request(app.getHttpServer())
      .post('/api/v1/orders')
      .send({ productId: 'xxx', quantity: 1 })
      .expect(401);
  });

  it('POST /api/v1/orders creates order for authed user', () => {
    return request(app.getHttpServer())
      .post('/api/v1/orders')
      .set('Authorization', `Bearer ${validToken}`)
      .send({ productId: productId, quantity: 2 })
      .expect(201)
      .expect(res => {
        expect(res.body.data.quantity).toBe(2);
        expect(res.body.data.status).toBe('pending');
      });
  });
});
```

## Database Test Isolation

### Option 1: Transaction Rollback (Fast)
```typescript
beforeEach(async () => {
  await prisma.$executeRaw`BEGIN`;
});
afterEach(async () => {
  await prisma.$executeRaw`ROLLBACK`;
});
```

### Option 2: Truncate Tables (Clean)
```typescript
beforeEach(async () => {
  const tables = await prisma.$queryRaw`
    SELECT tablename FROM pg_tables WHERE schemaname = 'public'`;
  for (const { tablename } of tables) {
    await prisma.$executeRawUnsafe(`TRUNCATE TABLE "${tablename}" CASCADE`);
  }
});
```

## What NOT to Test
- ❌ Framework internals (NestJS DI, Prisma queries without business logic)
- ❌ Simple CRUD with no business logic (test the controller, not `findMany`)
- ❌ Private methods directly — Test through public interface
- ❌ Mock everything — If you mock the DB in an "integration" test, it's not integration

## Test Quality Rules
1. **Test behavior, not implementation** — Assert outcomes, not method calls
2. **One assertion theme per test** — Multiple `expect` is fine if testing one behavior
3. **Test name describes the scenario** — `'throws INSUFFICIENT_STOCK when quantity > available'`
4. **No test interdependence** — Each test must pass when run alone
5. **Test edge cases** — Zero, negative, max int, empty string, null, duplicate

## Verification
- [ ] Critical business logic has unit tests
- [ ] Database operations have integration tests with real DB
- [ ] Auth-protected endpoints have E2E tests verifying 401/403
- [ ] Tests run in CI before merge
- [ ] Test DB is isolated (not shared with dev/staging)
