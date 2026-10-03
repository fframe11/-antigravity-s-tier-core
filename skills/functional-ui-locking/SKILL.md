---
name: functional-ui-locking
description: Enforces functional UI integrity and data flow locking. Eliminates phantom/orphan UI elements (buttons, inputs, filters) lacking state or handlers, mandates interactive TDD tests, and enforces URL/state synchronization.
---

# Functional UI Enforcement & Data Flow Locking

## 🎯 Objective
- Eliminate "Phantom UI" elements (buttons, inputs, filters, dropdowns) that look visually complete but lack functional backend logic, state wiring, or event handlers.
- Guarantee that every visual element introduced performs a measurable, connected task.
- Enforce component-level interaction testing before declaring frontend work complete.

---

## 🚫 Anti-Phantom UI Rules (Non-Negotiable)

### 1. No Orphan Elements
You are strictly FORBIDDEN from rendering any `<button>`, `<input>`, `<form>`, `<select>`, `<Tab>`, `<DialogTrigger>`, or interactive UI component without explicitly defining its data flow. Every interactive element MUST have:
1. **Explicit State Binding**: Tied to a React state (`useState`, `useReducer`), form schema (React Hook Form + Zod), or URL search parameter (`useSearchParams` / `nuqs`).
2. **Active Event Handler**: Must have an active handler (`onClick`, `onChange`, `onSubmit`, `onSelect`) that triggers a state mutation, modal opening, or API request.

### 2. Explicit Mock or Toast Notification (Zero Empty Handlers)
If a backend endpoint or sub-feature for a button or field does not exist yet, you MUST NOT leave the handler empty (`onClick={() => {}}`) or unassigned. You must either:
- Connect it to a client-side feedback handler that displays a toast notification (e.g., `toast.info("Feature connecting to backend...")`).
- Throw a distinct console warning or dialog indicating the feature is currently in integration.

```tsx
// ❌ FORBIDDEN: Phantom Button
<Button size="sm">Export Report</Button>

// ❌ FORBIDDEN: Empty Handler
<Button size="sm" onClick={() => {}}>Export Report</Button>

// ✅ ALLOWED (Pending Backend): Explicit Client Feedback
<Button
  size="sm"
  onClick={() => {
    toast.info("Exporting CSV report...", { description: "Preparing data stream from server" });
    // Or trigger actual mock download generator
  }}
>
  <Download className="mr-2 h-4 w-4" /> Export Report
</Button>

// ✅ BEST: Fully Wired Handler
<Button size="sm" onClick={handleExportReport} disabled={isExporting}>
  {isExporting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Download className="mr-2 h-4 w-4" />}
  Export Report
</Button>
```

### 3. BI Filter Invariant (URL Parameter Synchronization)
Every analytical filter element (date picker, time range dropdown, status select, search bar) introduced for Technical/Business users must be fully wired to either central state or URL query parameters (`nuqs` or `useSearchParams`). Changing any filter must automatically trigger a data refetch loop.

```tsx
// ✅ BI Filter Invariant: Syncing to URL Search Params
import { useSearchParams, useRouter, usePathname } from 'next/navigation';

export function TimeRangeFilter() {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const { replace } = useRouter();

  const currentTimeRange = searchParams.get('timeRange') || '30d';

  const handleSelect = (val: string) => {
    const params = new URLSearchParams(searchParams);
    params.set('timeRange', val);
    params.set('page', '1'); // Reset pagination on filter change
    replace(`${pathname}?${params.toString()}`);
  };

  return (
    <Select value={currentTimeRange} onValueChange={handleSelect}>
      <SelectTrigger className="w-[140px]">
        <SelectValue placeholder="Time range" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="24h">Last 24 Hours</SelectItem>
        <SelectItem value="7d">Last 7 Days</SelectItem>
        <SelectItem value="30d">Last 30 Days</SelectItem>
        <SelectItem value="90d">Last Quarter</SelectItem>
      </SelectContent>
    </Select>
  );
}
```

---

## 🔬 Mechanical Sign-Off Requirement (Integration Matrix)

Before declaring any frontend view complete (`claim_done`), you must write a **Functional UI Integration Matrix** in your report detailing the exact wiring of every interactive element on the screen:

| Component / Label | Element Type | State / URL Binding | Handler / Mutation | Connected API Endpoint |
|---|---|---|---|---|
| "Export Report" | `<Button>` | `isExporting` (boolean) | `handleExport()` | `POST /api/reports/export` |
| "Date Range" | `<Select>` | URL `?timeRange=30d` | `handleTimeRangeChange()` | `GET /api/metrics?range=30d` |
| "Search Query" | `<Input>` | `searchQuery` (debounced) | `setSearchQuery()` | `GET /api/transactions?q=...` |
| "Delete Account" | `<AlertDialog>` | `isConfirmOpen` (boolean) | `confirmDelete()` | `DELETE /api/users/:id` |

---

## 🧪 Component Interaction TDD Test Pattern

Every interactive component MUST have an accompanying interaction test (Vitest + React Testing Library) to verify behavior deterministically:

```tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TransactionsToolbar } from './transactions-toolbar';

describe('TransactionsToolbar - Functional UI Guard', () => {
  it('triggers onFilterChange when status dropdown is changed', async () => {
    const mockFilterChange = vi.fn();
    render(<TransactionsToolbar onFilterChange={mockFilterChange} />);

    // Locate interactive element
    const statusSelect = screen.getByRole('combobox', { name: /status/i });
    await userEvent.click(statusSelect);

    const pendingOption = screen.getByRole('option', { name: /pending/i });
    await userEvent.click(pendingOption);

    // Assert that the element is NOT an orphan
    expect(mockFilterChange).toHaveBeenCalledTimes(1);
    expect(mockFilterChange).toHaveBeenCalledWith('PENDING');
  });

  it('triggers search callback when typing in search input', async () => {
    const mockSearch = vi.fn();
    render(<TransactionsToolbar onSearch={mockSearch} />);

    const searchInput = screen.getByPlaceholderText(/search transactions/i);
    await userEvent.type(searchInput, 'TX-9841');

    await waitFor(() => {
      expect(mockSearch).toHaveBeenCalledWith('TX-9841');
    });
  });
});
```
