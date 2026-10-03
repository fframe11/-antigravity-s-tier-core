---
name: iconography-and-emoji-ban
description: Strictly forbids raw Unicode emojis in frontend code, enforces semantic tree-shaken SVG icon imports (Lucide React, Phosphor, Heroicons), and maps common business intents to standard design tokens.
---

# 🛡️ Strict Iconography & Emoji Ban Protocol

## 🎯 Objective
- Completely eradicate raw Unicode Emojis (📊, 🛒, 🛡️, 🔑, etc.) from all navigation bars, buttons, tables, badges, and marketing views.
- Enforce semantic, performant SVG icon mappings using standard design libraries (Lucide React, Phosphor, Heroicons).
- Prevent bundle bloat through strict tree-shaken imports.

---

## ❌ Absolute Emoji Prohibition (Non-Negotiable)
1. **Zero Emojis in Source Code**:
   - Strictly FORBIDDEN from rendering dynamic or static Unicode emojis in client-facing components (`.tsx`, `.jsx`, `.vue`, `.html`).
   - Emojis look amateur, render inconsistently across operating systems (Windows vs iOS vs Linux), and break corporate Figma design systems.
2. **Automated Conversion Rule**:
   - If an illustrative or categorical element is required, you MUST map it directly to a professional SVG icon component.
   - If an existing draft contains emojis, replace them immediately using the Semantic Mapping Table below.

---

## 🎨 Semantic Icon Mapping Table (Lucide React Standard)

| Emoji | Intent / Meaning | Lucide Component | Tree-Shaken Import |
|---|---|---|---|
| 📊 | Analytics / Reports / Charts | `BarChart3`, `LineChart` | `import { BarChart3 } from 'lucide-react'` |
| 📈 | Growth / Trends Up | `TrendingUp` | `import { TrendingUp } from 'lucide-react'` |
| 📉 | Downward Trend | `TrendingDown` | `import { TrendingDown } from 'lucide-react'` |
| 🛒 | Cart / Checkout | `ShoppingCart` | `import { ShoppingCart } from 'lucide-react'` |
| 🛍️ | Products / Shopping Bag | `ShoppingBag` | `import { ShoppingBag } from 'lucide-react'` |
| 📦 | Inventory / Shipping / Order | `Package` | `import { Package } from 'lucide-react'` |
| 💳 | Payment / Billing | `CreditCard` | `import { CreditCard } from 'lucide-react'` |
| 🏷️ | Pricing / Coupons / Tags | `Tag`, `BadgePercent` | `import { Tag } from 'lucide-react'` |
| 🛡️ | Security / Protection | `Shield`, `ShieldCheck` | `import { ShieldCheck } from 'lucide-react'` |
| 🔒 | Privacy / Encrypted | `Lock` | `import { Lock } from 'lucide-react'` |
| 🔑 | Auth / Credentials / API Keys | `KeyRound` | `import { KeyRound } from 'lucide-react'` |
| ⚙️ | Settings / Config / System | `Settings`, `Sliders` | `import { Settings } from 'lucide-react'` |
| ⚡ | Fast / Webhooks / Triggers | `Zap` | `import { Zap } from 'lucide-react'` |
| 🔍 | Search / Discovery | `Search` | `import { Search } from 'lucide-react'` |
| 🔔 | Notifications / Alerts | `Bell` | `import { Bell } from 'lucide-react'` |
| ⚠️ | Warning / Caution | `AlertTriangle`, `AlertCircle`| `import { AlertTriangle } from 'lucide-react'` |
| ❌ | Error / Cancel / Failed | `XCircle`, `X` | `import { XCircle } from 'lucide-react'` |
| ✅ | Success / Approved / Done | `CheckCircle2`, `Check` | `import { CheckCircle2 } from 'lucide-react'` |
| 📅 | Date / Booking / Schedule | `Calendar` | `import { Calendar } from 'lucide-react'` |
| ⏰ | Time / Reminders / Hours | `Clock` | `import { Clock } from 'lucide-react'` |
| 👤 | User Profile / Single Account | `User` | `import { User } from 'lucide-react'` |
| 👥 | Team / Organization / Members | `Users` | `import { Users } from 'lucide-react'` |
| 📁 | Documents / File Explorer | `Folder`, `FileText` | `import { Folder } from 'lucide-react'` |
| 🔄 | Sync / Refresh / Repeat | `RefreshCw`, `RotateCw` | `import { RefreshCw } from 'lucide-react'` |
| 🗑️ | Delete / Remove | `Trash2` | `import { Trash2 } from 'lucide-react'` |
| 🚀 | Deploy / Launch / Release | `Rocket` | `import { Rocket } from 'lucide-react'` |

---

## ⚙️ Performance & Implementation Rules

1. **Strict Tree-Shaking**:
   - ALWAYS import named icons directly:
     ```tsx
     // ✅ MANDATORY: Tree-shakable import (< 1KB per icon)
     import { BarChart3, TrendingUp, ShieldCheck } from 'lucide-react';

     // ❌ FORBIDDEN: Bulk imports
     import * as Icons from 'lucide-react';
     ```
2. **Consistent Visual Weight & Size**:
   - Default icon dimensions: `h-4 w-4` (16px) for table rows and buttons; `h-5 w-5` (20px) for navigation items; `h-6 w-6` (24px) for metric headers.
   - Maintain a standardized `strokeWidth` globally (e.g. `strokeWidth={1.75}` or `strokeWidth={2}`).
3. **Color Inheritance**:
   - Icons must inherit color via `currentColor` or subtle Tailwind tokens:
     ```tsx
     <BarChart3 className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
     ```
4. **Accessible Iconography**:
   - Decorative icons must declare `aria-hidden="true"`.
   - Standalone icon buttons (e.g., search icon without text) MUST supply `aria-label="Search"` to meet WCAG AA standards.
