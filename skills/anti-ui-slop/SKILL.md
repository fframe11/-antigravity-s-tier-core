---
name: anti-ui-slop
description: Anti-UI-Slop & Zero-Phantom-UI skill. Strictly forbids orphan interactive elements, mandates simultaneous state-handler co-declaration, and enforces Playwright E2E interaction assertions to verify real network and DOM reactivity.
---

# Anti-UI-Slop & Phantom UI Buster

## 🎯 Purpose
AI models frequently generate "UI Slop": beautiful buttons, datepickers, and search inputs that are completely dead (unwired to state or backend). This skill establishes mechanical rules and Playwright E2E test gates to make dead UI structurally impossible.

---

## 🚫 Non-Negotiable Engineering Rules

1. **Simultaneous Co-Declaration**:
   Whenever writing `<Button>`, `<Input>`, `<Select>`, or `<Dropdown>`, the state hook and event handler MUST be declared in the same file or hook immediately before rendering:
   ```tsx
   // ❌ FORBIDDEN: UI Slop
   <Button>Filter</Button>

   // ✅ MANDATORY: Co-declared state and handler
   const [statusFilter, setStatusFilter] = useState<Status>('ALL');
   const handleFilterChange = (status: Status) => {
     setStatusFilter(status);
     queryClient.invalidateQueries({ queryKey: ['orders', status] });
   };
   <Select value={statusFilter} onValueChange={handleFilterChange}>...</Select>
   ```

2. **Network/Toast Binding Invariant**:
   Every clickable element MUST trigger either:
   - A real API mutation / query refetch
   - A client state transition (modal open, tab change, URL param update)
   - Or an explicit user notification (`toast.info("Connecting...")`) during development. **Empty handlers (`() => {}`) are treated as build-breaking bugs.**

3. **Anti-Parenthetical Translation & Locale Gate (No Localization Slop)**:
   You are strictly FORBIDDEN from rendering dual-language content wrapped in parentheses within a single text element or button payload (e.g. `แดชบอร์ดวิเคราะห์ผลการเรียน (Performance Telemetry)` or `Performance Telemetry (แดชบอร์ด)`).
   - **Strict Single-Language Output**: Viewport microcopy must remain strictly in one locale at a time based on the active domain or language switcher state.
   - **Architectural Localization**: Split strings into clean i18n dictionaries (`locales/th.json`, `locales/en.json`) and bind dynamically with standard hooks (`const { t } = useTranslation();` or `next-intl`).
   - **Deterministic Scanner**: Run `audit-ai-slop.ps1` to reject dual-language parenthetical regex patterns: `[\u0E00-\u0E7F]{2,}\s*\([A-Za-z0-9\s_\-\.\/]{2,}\)|[A-Za-z0-9\s_\-\.\/]{2,}\s*\([\u0E00-\u0E7F\s]{2,}\)`.

---

## 🎭 Playwright E2E Phantom UI Test Suite

Before closing any frontend feature, run this Playwright test suite to mechanically prove that all interactive elements trigger real state or network events:

```typescript
// e2e/anti-phantom-ui.spec.ts
import { test, expect } from '@playwright/test';

test.describe('BI Dashboard - Anti-Phantom UI Gate', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard/analytics');
    // Ensure dashboard skeleton is resolved
    await expect(page.locator('h1')).toContainText('Analytics Overview');
  });

  test('Date range filter triggers network request and updates metric cards', async ({ page }) => {
    // 1. Intercept analytical API call
    const metricsResponsePromise = page.waitForResponse(
      (resp) => resp.url().includes('/api/metrics') && resp.status() === 200
    );

    // 2. Click the date filter dropdown
    const filterTrigger = page.getByRole('combobox', { name: /time range/i });
    await expect(filterTrigger).toBeVisible();
    await filterTrigger.click();

    // 3. Select 'Last 7 Days'
    const option = page.getByRole('option', { name: /last 7 days/i });
    await option.click();

    // 4. Assert URL parameter updated (Invariant Check)
    await expect(page).toHaveURL(/timeRange=7d/);

    // 5. Assert network call was actually fired (Zero-Phantom Check)
    const response = await metricsResponsePromise;
    expect(response.ok()).toBeTruthy();

    // 6. Assert DOM re-rendered with new data
    const kpiBadge = page.locator('[data-testid="kpi-revenue-delta"]');
    await expect(kpiBadge).toBeVisible();
  });

  test('Export button triggers active download stream or user toast', async ({ page }) => {
    const exportButton = page.getByRole('button', { name: /export/i });
    await expect(exportButton).toBeEnabled();

    // Listen for either a file download event or a visible toast
    const downloadPromise = page.waitForEvent('download', { timeout: 3000 }).catch(() => null);
    await exportButton.click();

    const download = await downloadPromise;
    if (!download) {
      // If not instant download, verify active toast feedback (No Silent Clicks!)
      const toastMessage = page.locator('[data-sonner-toast]');
      await expect(toastMessage).toBeVisible();
    }
  });
});
```

---

## 🔄 Production BI Data Flow Pattern (Reference Blueprint)

The canonical pattern for connecting frontend UI to backend API without waterfalls or dead UI:

```tsx
// 1. Frontend: src/app/(main)/dashboard/analytics/_components/analytics-toolbar.tsx
'use client';

import { useQueryClient } from '@tanstack/react-query';
import { useSearchParams, useRouter, usePathname } from 'next/navigation';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Download, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';

export function AnalyticsToolbar({ isRefetching }: { isRefetching: boolean }) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();

  const currentRange = searchParams.get('range') || '30d';

  const handleRangeChange = (value: string) => {
    const params = new URLSearchParams(searchParams);
    params.set('range', value);
    router.replace(`${pathname}?${params.toString()}`);
  };

  const handleManualRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['analytics-metrics', currentRange] });
    toast.success('Refreshing analytics telemetry...');
  };

  return (
    <div className="flex items-center gap-3">
      <Select value={currentRange} onValueChange={handleRangeChange}>
        <SelectTrigger className="w-36 h-9 text-xs">
          <SelectValue placeholder="Select range" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="24h">Last 24 Hours</SelectItem>
          <SelectItem value="7d">Last 7 Days</SelectItem>
          <SelectItem value="30d">Last 30 Days</SelectItem>
        </SelectContent>
      </Select>

      <Button
        variant="outline"
        size="sm"
        onClick={handleManualRefresh}
        disabled={isRefetching}
        className="h-9"
      >
        <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${isRefetching ? 'animate-spin' : ''}`} />
        Sync
      </Button>
    </div>
  );
}
```
