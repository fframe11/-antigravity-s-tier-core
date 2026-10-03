---
name: human-dashboard-design
description: Human-designed, enterprise-grade admin and BI dashboard patterns based on next-shadcn-admin-dashboard, Tailwind CSS v4, and Shadcn UI. Enforces high data density, unified grid containers, colocation architecture, anti-AI-slop typography, and browser screenshot verification loops.
---

# Human-Dashboard-Design (Enterprise Admin & BI Standards)

## Overview
AI agents naturally default to "AI slop" when designing dashboards: low data density, oversized rounded cards (`rounded-3xl`), heavy drop shadows (`shadow-2xl`), saturated neon badges, and disconnected floating widgets.

This skill grounds frontend dashboard development in **real human-designed engineering standards** extracted from production-grade reference implementations (`C:\Users\ffram\security_repos\next-shadcn-admin-dashboard` and `C:\Users\ffram\security_repos\shadcndashboard`).

---

## 1. Anti-AI-Slop Visual Rules

| AI-Slop Pattern (FORBIDDEN) | Human-Designed Standard (MANDATORY) |
|---|---|
| Floating isolated cards with `shadow-lg` or `shadow-2xl` | **Unified Container Grid**: Single container with `ring-1 ring-foreground/10` and internal hairline borders `border-foreground/10`. |
| Giant rounded corners (`rounded-3xl`) | Subtle corporate radius (`rounded-lg` or `rounded-xl`). |
| Giant numbers (`text-6xl`) with no context | Compact, tight metrics (`text-3xl leading-none tracking-tight`). |
| Saturated solid green/red badge pills (`bg-green-600 text-white`) | **Subtle tinted badges**: `bg-green-500/10 text-green-700 dark:bg-green-500/15 dark:text-green-300`. |
| Huge empty padding (`p-10`) wasting screen space | High data density (`p-4` to `p-5`, `gap-4`). |
| No timestamp or sync state | Contextual metadata: "Updated 5 min ago", date subheader (`format(new Date(), "EEEE, do MMMM yyyy")`). |
| Random centering of all text and cards | Left-aligned data hierarchy with right-aligned action triggers. |

---

## 2. Core Architectural Patterns

### A. The Unified KPI Container (Hairline Grid)
Instead of rendering 4 separate `<Card>` components that float disconnectedly, group them into a single border-boxed container with shared internal dividing lines:

```tsx
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function OverviewKpis() {
  return (
    <div className="overflow-hidden rounded-xl bg-card ring-1 ring-foreground/10">
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4">
        {/* KPI Cell 1 */}
        <Card className="gap-4 overflow-hidden rounded-none border-0 border-foreground/10 border-b ring-0 md:border-r xl:border-b-0">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-muted-foreground text-sm font-medium">Total Revenue</CardTitle>
          </CardHeader>
          <CardContent className="flex items-end justify-between p-4 pt-0">
            <div className="space-y-1">
              <div className="text-3xl leading-none tracking-tight font-semibold">$128,450</div>
              <p className="text-muted-foreground text-xs">+$9.8K vs last month</p>
            </div>
            <Badge className="bg-emerald-500/10 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300 border-0">
              +8.4%
            </Badge>
          </CardContent>
        </Card>

        {/* KPI Cell 2 */}
        <Card className="gap-4 overflow-hidden rounded-none border-0 border-foreground/10 border-b ring-0 xl:border-r xl:border-b-0">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-muted-foreground text-sm font-medium">Active Subscriptions</CardTitle>
          </CardHeader>
          <CardContent className="flex items-end justify-between p-4 pt-0">
            <div className="space-y-1">
              <div className="text-3xl leading-none tracking-tight font-semibold">2,340</div>
              <p className="text-muted-foreground text-xs">+180 new this week</p>
            </div>
            <Badge className="bg-emerald-500/10 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300 border-0">
              +4.1%
            </Badge>
          </CardContent>
        </Card>

        {/* KPI Cell 3 */}
        <Card className="gap-4 overflow-hidden rounded-none border-0 border-foreground/10 border-b ring-0 md:border-r md:border-b-0">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-muted-foreground text-sm font-medium">Monthly Churn</CardTitle>
          </CardHeader>
          <CardContent className="flex items-end justify-between p-4 pt-0">
            <div className="space-y-1">
              <div className="text-3xl leading-none tracking-tight font-semibold">1.2%</div>
              <p className="text-muted-foreground text-xs">-0.4% improvement</p>
            </div>
            <Badge className="bg-emerald-500/10 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300 border-0">
              -0.4%
            </Badge>
          </CardContent>
        </Card>

        {/* KPI Cell 4 */}
        <Card className="gap-4 overflow-hidden rounded-none border-0 ring-0">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-muted-foreground text-sm font-medium">Avg Order Value</CardTitle>
          </CardHeader>
          <CardContent className="flex items-end justify-between p-4 pt-0">
            <div className="space-y-1">
              <div className="text-3xl leading-none tracking-tight font-semibold">$54.80</div>
              <p className="text-muted-foreground text-xs">+$2.10 vs baseline</p>
            </div>
            <Badge className="bg-emerald-500/10 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300 border-0">
              +3.8%
            </Badge>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

---

### B. Standard 12-Column Dashboard Rhythm
Dashboard layouts follow an explicit 12-column responsive grid with consistent gaps:

```tsx
<div className="flex flex-col gap-4 p-6">
  {/* Header & Controls */}
  <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
    <div className="space-y-1">
      <h1 className="text-2xl font-bold tracking-tight">Executive Overview</h1>
      <p className="text-muted-foreground text-xs">Real-time system telemetry and commercial metrics</p>
    </div>
    <div className="flex items-center gap-2">
      <DateRangePicker />
      <Button variant="outline" size="sm">Export Report</Button>
    </div>
  </div>

  {/* Row 1: KPI Overview Grid (Full Width) */}
  <OverviewKpis />

  {/* Row 2: Primary Analytics (8 cols) + Secondary Breakdown (4 cols) */}
  <div className="grid grid-cols-1 gap-4 xl:grid-cols-12">
    <div className="xl:col-span-8">
      <RevenuePerformanceChart />
    </div>
    <div className="xl:col-span-4">
      <CategoryDistributionCard />
    </div>
  </div>

  {/* Row 3: Detail Data Tables (8 cols) + Realtime Feed (4 cols) */}
  <div className="grid grid-cols-1 gap-4 xl:grid-cols-12">
    <div className="xl:col-span-8">
      <RecentTransactionsTable />
    </div>
    <div className="xl:col-span-4">
      <ActivityAuditTimeline />
    </div>
  </div>
</div>
```

---

## 3. Directory Colocation Architecture

Always colocate route-specific dashboard components inside the route folder:

```
src/app/(main)/dashboard/[domain]/
├── page.tsx                    # Page layout & data orchestration
├── _components/
│   ├── overview-kpis.tsx       # KPI grid
│   ├── main-chart.tsx          # Primary Recharts/Visx chart
│   ├── data-table.tsx          # TanStack Table instance
│   ├── filter-toolbar.tsx      # Date picker, status filters, search
│   └── side-breakdown.tsx      # Donut/distribution card
├── _hooks/
│   └── use-domain-data.ts      # Data fetching & query caching
└── _types/
    └── index.ts                # DTO and UI view models
```

---

## 4. 19 Production Domain Archetypes (Reference Map)

When designing a dashboard for a specific domain, refer to the battle-tested archetypes in `C:\Users\ffram\security_repos\next-shadcn-admin-dashboard\src\app\(main)\dashboard\`:

1. **Finance** (`/dashboard/finance`): Net worth, cash flow velocity, income breakdown, wallet allocation, scheduled debits.
2. **Analytics** (`/dashboard/analytics`): Real-time visitors, session duration, device share, bounce rate, geographic distribution.
3. **Ecommerce** (`/dashboard/ecommerce`): Sales volume, AOV, returns, top SKU rankings, inventory velocity.
4. **CRM & Sales** (`/dashboard/crm`): Pipeline funnel, deal conversion, sales representative leaderboard, active opportunities.
5. **Infrastructure / SRE** (`/dashboard/infrastructure`): CPU/Memory load, p95/p99 response latency, error budget, container pod health.
6. **Logistics & Fleet** (`/dashboard/logistics`): Delivery route tracking, driver utilization, warehouse fulfillment SLAs, shipment exceptions.
7. **Task / Project Management** (`/dashboard/tasks`): Sprint progress, burndown velocity, blocker alerts, member workload.
8. **Healthcare / Patient Monitoring** (`/dashboard/patient-monitoring`): Vital signs, triage queue, bed occupancy, doctor on-call roster.
9. **Invoice & Billing** (`/dashboard/invoice`): Outstanding receivables, aging buckets (30/60/90 days), automated reminder queue.
10. **Roles & RBAC** (`/dashboard/roles`): Permission matrices, audit logs, active session revocation.

---

## 5. Visual Screenshot Verification Loop (Mandatory)

Never mark a frontend dashboard task complete based solely on code compilation. Execute the visual verification loop:

1. **Start Local Dev Server** (if not already running):
   Ensure the frontend builds and runs locally (e.g. `npm run dev` or test server).
2. **Capture Browser Screenshots**:
   Use `puppeteer` or `playwright` MCP tools to capture:
   - **Desktop**: 1440x900 viewport
   - **Mobile**: 375x812 viewport
3. **Inspect Visual Invariants**:
   - [ ] No layout shift or overflow horizontal scrollbars on mobile.
   - [ ] Data density is balanced (no huge empty white voids).
   - [ ] All badges use subtle tinting (`bg-*/10 text-*`), no harsh unreadable contrast.
   - [ ] All tables have pagination, sorting headers, and clean row borders.
   - [ ] Empty states and loading skeletons are visually aligned with loaded content.

---

## 6. Client-Side Caching & State Hydration (TanStack Query / SWR)

AI systems often write naïve `useEffect` fetches on every route change, causing layout flashing, repeated spin-wheels, and backend database thrashing. Follow this caching standard:

### A. Global Stale-While-Revalidate Configuration
Configure the global QueryClient with instant cache reuse:

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,    // 5 minutes: Data remains fresh, no network fetch on page flip
      gcTime: 10 * 60 * 1000,       // 10 minutes: Retain cached data in memory
      refetchOnWindowFocus: false,  // Prevent jarring layout shifts while multitasking
      retry: 1,                     // Fail fast on network errors
    },
  },
});
```

### B. Instant Route Transitions via Hover Prefetching
Prefetch dashboard domain data when the user hovers over sidebar navigation links:

```tsx
import Link from 'next/link';
import { useQueryClient } from '@tanstack/react-query';

export function NavItem({ href, label, queryKey, queryFn }: NavItemProps) {
  const queryClient = useQueryClient();

  const handleMouseEnter = () => {
    // Prefetch before user clicks -> Instant Render on route navigation
    queryClient.prefetchQuery({ queryKey, queryFn, staleTime: 60 * 1000 });
  };

  return (
    <Link href={href} onMouseEnter={handleMouseEnter} className="flex items-center gap-2 p-2">
      {label}
    </Link>
  );
}
```

### C. Optimistic Mutations for Instant User Feedback
Update the UI immediately before waiting for the network roundtrip, with rollback on error:

```tsx
export function useUpdateTransactionStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      apiClient.patch(`/transactions/${id}`, { status }),
    onMutate: async ({ id, status }) => {
      await queryClient.cancelQueries({ queryKey: ['transactions'] });
      const previousData = queryClient.getQueryData(['transactions']);

      // Optimistically update cache
      queryClient.setQueryData(['transactions'], (old: any) => ({
        ...old,
        items: old.items.map((item: any) =>
          item.id === id ? { ...item, status } : item
        ),
      }));

      return { previousData };
    },
    onError: (_err, _vars, context) => {
      // Rollback to previous state on failure
      if (context?.previousData) {
        queryClient.setQueryData(['transactions'], context.previousData);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
    },
  });
}
```

---

## 7. BI Data Streaming & Cursor Pagination Architecture

Large BI dashboards must never fetch massive unpaginated datasets (>100 records) in a single synchronous JSON payload.

### A. Database Keyset / Cursor Pagination (Backend Contract)
Use indexed keyset pagination to maintain $O(1)$ query speed regardless of table depth:

```typescript
// NestJS Controller & Service
@Get('telemetry')
async getTelemetry(
  @Query('cursor') cursor?: string,
  @Query('limit') limit = 50,
) {
  const take = Math.min(Number(limit), 100);
  const items = await this.prisma.telemetryLog.findMany({
    take: take + 1, // Fetch +1 to check for next page
    cursor: cursor ? { id: cursor } : undefined,
    orderBy: { createdAt: 'desc' },
  });

  const hasNextPage = items.length > take;
  const pageItems = hasNextPage ? items.slice(0, take) : items;
  const nextCursor = hasNextPage ? pageItems[pageItems.length - 1].id : null;

  return { items: pageItems, nextCursor };
}
```

### B. Infinite Query Hook with Viewport Virtualization
Render 10,000+ items smoothly using TanStack Virtual + Infinite Query:

```tsx
import { useInfiniteQuery } from '@tanstack/react-query';
import { useVirtualizer } from '@tanstack/react-virtual';
import { useRef } from 'react';

export function VirtualizedBIEventStream() {
  const parentRef = useRef<HTMLDivElement>(null);

  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteQuery({
    queryKey: ['telemetry-stream'],
    queryFn: ({ pageParam }) => fetchTelemetry(pageParam),
    initialPageParam: null as string | null,
    getNextPageParam: (lastPage) => lastPage.nextCursor,
  });

  const allItems = data ? data.pages.flatMap((page) => page.items) : [];

  const rowVirtualizer = useVirtualizer({
    count: hasNextPage ? allItems.length + 1 : allItems.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 48,
    overscan: 5,
  });

  return (
    <div ref={parentRef} className="h-[500px] overflow-auto rounded-lg border border-foreground/10">
      <div style={{ height: `${rowVirtualizer.getTotalSize()}px`, position: 'relative' }}>
        {rowVirtualizer.getVirtualItems().map((virtualRow) => {
          const isLoaderRow = virtualRow.index > allItems.length - 1;
          const item = allItems[virtualRow.index];

          if (isLoaderRow) {
            fetchNextPage();
            return <div key="loader" style={{ transform: `translateY(${virtualRow.start}px)` }}>Loading more...</div>;
          }

          return (
            <div key={item.id} className="absolute left-0 top-0 w-full p-2 border-b border-foreground/5"
                 style={{ transform: `translateY(${virtualRow.start}px)` }}>
              <span className="font-mono text-xs">{item.timestamp}</span> - {item.event}
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

### C. Server-Sent Events (SSE) for Real-Time Telemetry
Stream live metrics directly without polling overhead:

```typescript
// Backend NestJS SSE Controller
@Sse('live-stream')
streamLiveMetrics(): Observable<MessageEvent> {
  return interval(1000).pipe(
    map(() => ({
      data: { cpu: process.cpuUsage(), timestamp: new Date().toISOString() }
    } as MessageEvent))
  );
}
```

