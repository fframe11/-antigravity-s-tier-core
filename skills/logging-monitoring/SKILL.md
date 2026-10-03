---
name: logging-monitoring
description: Use when implementing structured logging, configuring monitoring dashboards, setting up alerts, or instrumenting application metrics. Covers NestJS logger setup, structured JSON logs, Cloud Run logging, and alert thresholds.
---
# Logging & Monitoring Standards

## When to Use
- Setting up logging for a new service
- Adding monitoring to production endpoints
- Configuring alerts for error spikes or latency
- Reviewing log output for security compliance

## Structured Logging Setup (NestJS)

### Use Pino (Recommended for Production)
```typescript
// main.ts
import { Logger } from 'nestjs-pino';

app.useLogger(app.get(Logger));

// app.module.ts
PinoModule.forRoot({
  pinoHttp: {
    level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
    transport: process.env.NODE_ENV !== 'production'
      ? { target: 'pino-pretty' }
      : undefined,
    redact: ['req.headers.authorization', 'req.headers.cookie', 'body.password'],
  },
});
```

### Log Format (JSON in Production)
```json
{
  "level": "error",
  "time": "2025-01-15T10:30:00Z",
  "requestId": "req_abc123",
  "userId": "usr_xyz",
  "service": "order-service",
  "method": "POST",
  "path": "/api/v1/orders",
  "statusCode": 500,
  "duration": 234,
  "error": {
    "code": "DB_CONNECTION_TIMEOUT",
    "message": "Connection pool exhausted"
  }
}
```

## Mandatory Logging Rules

### Always Log
1. **Request start/end** — Method, path, status code, duration (auto via Pino HTTP)
2. **Authentication events** — Login success/failure, token refresh, logout
3. **Business events** — Order created, payment processed, user registered
4. **Errors with context** — Error code, affected resource ID, request ID

### Never Log
5. **Passwords or credentials** — Use `redact` option in Pino
6. **Full credit card numbers** — Log last 4 digits only
7. **JWT tokens** — Redact `Authorization` header
8. **PII in excess** — Log user ID, not full profile data
9. **Raw SQL queries in production** — Disable Prisma query logging

## Cloud Run Logging Integration

Cloud Run automatically sends stdout/stderr to Cloud Logging. Structure your logs as JSON to enable filtering:

```typescript
// Cloud Logging severity mapping
// console.log → INFO
// console.warn → WARNING
// console.error → ERROR

// For structured logs recognized by Cloud Logging:
console.log(JSON.stringify({
  severity: 'ERROR',
  message: 'Payment failed',
  'logging.googleapis.com/trace': traceId,
  orderId: 'ord_123',
}));
```

## Alert Thresholds

| Metric | Warning | Critical | Action |
|---|---|---|---|
| Error rate (5xx) | > 1% of requests | > 5% of requests | Page on-call |
| P95 latency | > 500ms | > 2000ms | Investigate slow queries |
| DB connection pool | > 70% utilized | > 90% utilized | Scale pool or instances |
| Memory usage | > 70% of limit | > 90% of limit | Check for memory leaks |
| CPU usage | > 70% sustained | > 90% sustained | Scale Cloud Run instances |

## Verification
- [ ] Logs are structured JSON in production (not console.log strings)
- [ ] Sensitive data is redacted (check with `grep -i password` on sample logs)
- [ ] Every error log includes `requestId` for correlation
- [ ] Alert thresholds are configured for error rate and latency
- [ ] Cloud Run logs appear correctly in Cloud Logging console
