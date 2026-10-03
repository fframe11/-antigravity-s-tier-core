---
name: docker-production
description: Use when writing Dockerfiles, optimizing container images, configuring multi-stage builds, or deploying containers to Cloud Run, Kubernetes, or any container runtime. Covers image security, layer caching, and runtime configuration.
---
# Docker Production Best Practices

## When to Use
- Writing or reviewing Dockerfiles for production deployment
- Optimizing image size and build time
- Configuring containers for Cloud Run or Kubernetes
- Debugging container startup issues

## Multi-Stage Build Pattern (NestJS)

```dockerfile
# Stage 1: Build
FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build
RUN pnpm prune --prod

# Stage 2: Production
FROM node:22-alpine AS runner
RUN apk add --no-cache dumb-init
WORKDIR /app
USER node
COPY --from=builder --chown=node:node /app/dist ./dist
COPY --from=builder --chown=node:node /app/node_modules ./node_modules
COPY --from=builder --chown=node:node /app/package.json ./
EXPOSE 8080
CMD ["dumb-init", "node", "dist/main.js"]
```

## Mandatory Rules

### Security
1. **Never run as root** — Always add `USER node` or a non-root user.
2. **No secrets in image** — Use runtime env vars or secret managers. Never `COPY .env`.
3. **Use `dumb-init`** — Ensures proper signal handling (SIGTERM for Cloud Run graceful shutdown).
4. **Pin base image versions** — Use `node:22.x-alpine`, not `node:latest`.

### Performance
5. **Order COPY for cache** — Copy `package.json` + lockfile first, then `RUN install`, then `COPY . .`
6. **Use `.dockerignore`** — Exclude `node_modules`, `.git`, `dist`, test files, `.env`.
7. **Frozen lockfile only** — `pnpm install --frozen-lockfile` or `npm ci`. Never `npm install`.
8. **Prune dev dependencies** — `pnpm prune --prod` after build to shrink `node_modules`.

### Cloud Run Specific
9. **Listen on `process.env.PORT`** — Cloud Run assigns PORT dynamically (default 8080).
10. **Single process per container** — No supervisor, no pm2. One `node dist/main.js`.
11. **Health check endpoint** — Expose `GET /health` returning `200 OK` for startup probes.
12. **Startup timeout** — Cloud Run default is 240s. If app needs Prisma migration, run it in CI, not at startup.

### Prisma in Docker
13. **Generate in build stage** — `RUN npx prisma generate` before `pnpm build`.
14. **Copy Prisma client** — Ensure `node_modules/.prisma` is in the final image.
15. **Cloud SQL connection** — Use Unix socket `/cloudsql/INSTANCE_NAME` not TCP in production.

## Full-Stack Local Parity (Standard `docker-compose.yml`)

To prevent CORS issues, port conflicts, and environmental drift between frontend and backend on local machines, every fullstack project MUST provide a unified `docker-compose.yml` running on a shared bridge network.

```yaml
version: '3.8'

services:
  # 1. PostgreSQL Database
  postgres:
    image: postgres:16-alpine
    container_name: app_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-app_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-app_password}
      POSTGRES_DB: ${POSTGRES_DB:-app_database}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-app_user} -d ${POSTGRES_DB:-app_database}"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - app_network

  # 2. Redis Cache & Idempotency Store
  redis:
    image: redis:7-alpine
    container_name: app_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - app_network

  # 3. Backend (NestJS / Node.js API)
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: app_backend
    restart: unless-stopped
    environment:
      NODE_ENV: development
      PORT: 8080
      DATABASE_URL: postgresql://${POSTGRES_USER:-app_user}:${POSTGRES_PASSWORD:-app_password}@postgres:5432/${POSTGRES_DB:-app_database}?schema=public
      REDIS_URL: redis://redis:6379
      JWT_SECRET: ${JWT_SECRET:-super-secure-local-dev-jwt-secret-min-32-chars}
      CORS_ORIGIN: http://localhost:3000
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - app_network

  # 4. Frontend (Next.js / React Web UI)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: app_frontend
    restart: unless-stopped
    environment:
      NODE_ENV: development
      PORT: 3000
      NEXT_PUBLIC_API_URL: http://localhost:8080
      INTERNAL_API_URL: http://backend:8080
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - app_network

networks:
  app_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

### Mandatory Compose Rules:
1. **Always Use Service Healthchecks**: Backend must wait for Postgres and Redis via `condition: service_healthy` to eliminate startup race condition crashes.
2. **Dual URL Strategy for Frontend**: Use `INTERNAL_API_URL` (`http://backend:8080`) for server-side rendering (SSR) inside Docker network, and `NEXT_PUBLIC_API_URL` (`http://localhost:8080`) for client browser calls.
3. **Volume Isolation**: Database data must persist across restarts via named volumes (`postgres_data`, `redis_data`).

## Verification Checklist
- [ ] Image size < 300MB (Alpine + pruned deps)
- [ ] `docker run --rm -p 8080:8080 <image>` starts and responds to `curl localhost:8080/health`
- [ ] No secrets visible in `docker history <image>`
- [ ] Container runs as non-root (`docker exec <container> whoami` → `node`)
- [ ] `docker compose up -d` boots all 4 services without exit codes or dependency race conditions

