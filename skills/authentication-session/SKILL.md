---
name: authentication-session
description: Use when implementing authentication flows, JWT token management, session handling, OAuth2 integration, or role-based access control. Covers NestJS Guards, Passport strategies, token refresh, and RBAC/ABAC patterns.
---
# Authentication & Session Management (NestJS)

## When to Use
- Implementing login/register/logout flows
- Setting up JWT or session-based authentication
- Adding role-based access control (RBAC)
- Reviewing authentication security
- Integrating OAuth2 / social login

## JWT Authentication Setup

### Token Pair Strategy (Access + Refresh)
```typescript
// Access Token: short-lived, carries permissions
{
  sub: "user_uuid",
  role: "admin",
  permissions: ["orders:read", "orders:write"],
  iat: 1700000000,
  exp: 1700000900  // 15 minutes
}

// Refresh Token: long-lived, stored in DB
{
  sub: "user_uuid",
  jti: "unique_token_id",  // For revocation
  iat: 1700000000,
  exp: 1701209600  // 7 days
}
```

### Mandatory Security Rules
1. **Access token ≤ 15 min expiry** — Limits damage window if stolen
2. **Refresh token in httpOnly cookie** — Never in localStorage (XSS vulnerable)
3. **Rotate refresh tokens on use** — Issue new refresh token on each refresh call, invalidate old one
4. **Store refresh tokens in DB** — Enables forced logout and token revocation
5. **Use asymmetric keys (RS256)** — For multi-service architectures. HS256 only for single service
6. **Never put secrets in JWT payload** — JWTs are base64-encoded, not encrypted

### NestJS Guard Implementation
```typescript
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  handleRequest(err, user, info) {
    if (err || !user) {
      throw new UnauthorizedException({
        code: 'INVALID_TOKEN',
        message: 'Token is missing, expired, or invalid',
      });
    }
    return user;
  }
}
```

## Role-Based Access Control (RBAC)

```typescript
// roles.decorator.ts
export const Roles = (...roles: Role[]) => SetMetadata('roles', roles);

// roles.guard.ts
@Injectable()
export class RolesGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.get<Role[]>('roles', context.getHandler());
    if (!requiredRoles) return true;

    const { user } = context.switchToHttp().getRequest();
    return requiredRoles.includes(user.role);
  }
}

// Usage
@Roles(Role.ADMIN)
@UseGuards(JwtAuthGuard, RolesGuard)
@Delete(':id')
async deleteUser(@Param('id') id: string) { ... }
```

## BOLA Prevention (Broken Object Level Authorization)

```typescript
// ❌ WRONG — Any authenticated user can access any order
@Get('orders/:id')
async getOrder(@Param('id') id: string) {
  return this.orderService.findById(id);
}

// ✅ CORRECT — Verify ownership
@Get('orders/:id')
async getOrder(@Param('id') id: string, @CurrentUser() user: User) {
  const order = await this.orderService.findById(id);
  if (order.userId !== user.id) {
    throw new ForbiddenException({ code: 'ACCESS_DENIED' });
  }
  return order;
}

// ✅ BEST — Filter at query level
@Get('orders')
async getMyOrders(@CurrentUser() user: User) {
  return this.orderService.findByUserId(user.id);
}
```

## Frontend Route Middleware & Universal RBAC Guard (Zero-Flash Protection)

Security must exist at BOTH layers: Backend enforces data authorization; Frontend Route Middleware prevents unauthorized page rendering and UI layout flashes.

### 1. Next.js Edge Middleware (`middleware.ts`)
Run before any component or page layout renders. Inspect the secure `auth_token` cookie and evaluate route access:

```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { jwtVerify } from 'jose';

const PUBLIC_ROUTES = ['/login', '/register', '/forgot-password', '/api/public'];
const ROLE_ROUTE_MAP: Record<string, string[]> = {
  '/dashboard/finance': ['ADMIN', 'FINANCE'],
  '/dashboard/infrastructure': ['ADMIN', 'SRE', 'TECH_LEAD'],
  '/dashboard/roles': ['ADMIN'],
};

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public assets and public routes
  if (PUBLIC_ROUTES.some(route => pathname.startsWith(route)) || pathname.startsWith('/_next')) {
    return NextResponse.next();
  }

  const token = request.cookies.get('auth_token')?.value;

  // 1. Missing Token: Redirect to login with return callback
  if (!token) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('callbackUrl', encodeURIComponent(pathname));
    return NextResponse.redirect(loginUrl);
  }

  try {
    // 2. Decode token payload (using jose for Edge runtime compatibility)
    const secret = new TextEncoder().encode(process.env.JWT_SECRET);
    const { payload } = await jwtVerify(token, secret);
    const userRole = (payload.role as string) || 'USER';

    // 3. RBAC Route Check
    for (const [protectedPath, allowedRoles] of Object.entries(ROLE_ROUTE_MAP)) {
      if (pathname.startsWith(protectedPath) && !allowedRoles.includes(userRole)) {
        // Kick unauthorized role immediately to /unauthorized page
        return NextResponse.redirect(new URL('/unauthorized', request.url));
      }
    }

    return NextResponse.next();
  } catch (_err) {
    // Expired or invalid token: kick to login
    return NextResponse.redirect(new URL('/login', request.url));
  }
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
```

### 2. Silent Token Refresh Interceptor (Frontend API Client)
Intercept 401 responses, call `/auth/refresh` silently via httpOnly cookie, and replay the original request without user interruption:

```typescript
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
  withCredentials: true,
});

let isRefreshing = false;
let failedQueue: Array<{ resolve: (token?: unknown) => void; reject: (err: unknown) => void }> = [];

const processQueue = (error: unknown) => {
  failedQueue.forEach(prom => (error ? prom.reject(error) : prom.resolve()));
  failedQueue = [];
};

apiClient.interceptors.response.use(
  res => res,
  async error => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(() => apiClient(originalRequest));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        await apiClient.post('/auth/refresh');
        processQueue(null);
        return apiClient(originalRequest);
      } catch (refreshErr) {
        processQueue(refreshErr);
        window.location.href = '/login?expired=true';
        return Promise.reject(refreshErr);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);
```

## Session Security Checklist
- [ ] Passwords hashed with bcrypt (cost factor ≥ 10)
- [ ] Login endpoint has rate limiting (max 5 attempts / minute)
- [ ] Refresh tokens stored in DB with `jti` for revocation
- [ ] Access tokens expire in ≤ 15 minutes
- [ ] Logout invalidates refresh token in DB
- [ ] CORS configured to allow only trusted origins
- [ ] CSRF protection enabled for cookie-based auth
- [ ] Account lockout after 10 consecutive failed logins
- [ ] Frontend Route Middleware blocks unauthorized page renders before paint
- [ ] Silent refresh interceptor automatically renews expired session tokens

## Anti-Patterns
- ❌ Storing JWT in localStorage — Use httpOnly cookie
- ❌ Using `alg: none` — Always validate algorithm server-side
- ❌ Long-lived access tokens (> 1 hour) — Use refresh token rotation
- ❌ Checking role in frontend only without backend checks — Always enforce on backend
- ❌ Checking role in backend only without frontend route middleware — Causes UI flashing and unauthorized route leakage
- ❌ Trusting user ID from request body — Extract from JWT payload

