---
name: ui-uniqueness-audit
description: Quantitative UI Uniqueness & Human-Designed Audit Protocol. Enforces the 4 international human-vs-AI metrics (Spatial Rhythm 60-30-10, Intentional Information Density, Micro-Interactions & State, Structural Contrast over Hard Borders) and mandates self-auditing via <ui_audit> tags.
---

# 🎨 UI UNIQUENESS & HUMAN-DESIGNED AUDIT PROTOCOL

## 🎯 Objective
- Enforce strict professional UX principles to completely eliminate generic "AI-generated style" (monotonous grids, excessive borders, non-existent micro-interactions, flat un-styled cards).
- Use strict deterministic rules to prove the interface was crafted by a high-end Human UI/UX Designer.

## 📏 1. The 4 Quantitative Human-vs-AI Metrics
Every frontend component and screen must be evaluated against these 4 objective metrics:

| Metric | AI Slop / Machine Pattern (Strictly Forbidden) | Human Pro Standard (Mandatory) |
|---|---|---|
| **1. Spatial Rhythm & Padding** | Static padding across every block (e.g. `p-4` everywhere); flat and monotonous. | **Variable Visual Rhythm (60-30-10):** Tight within cards (`gap-2`, `p-3`), medium between components (`gap-4`, `p-5`), generous between major sections (`gap-6` to `gap-12`). |
| **2. Information & Data Density** | Over-density (cluttered charts without hierarchy) or Under-density (aimless blank whitespace). | **Intentional Density:** Layered for user journey; summary views are airy and clear, technical data tables are compact with high information density. |
| **3. Micro-Interactions & State** | Flat static boxes; zero hover transitions, missing focus rings, unresponsive buttons. | **Delicate Sensory Feedback:** Smooth hover transitions (`transition-colors duration-150`), subtle scale/fade, explicit `focus-visible:ring-2` focus rings. |
| **4. Structural Contrast & Borders** | Hard dark borders around every container, button, and card; looks like wireframe blocks. | **Shade Contrast & Ambient Depth:** Soft background shifts (`bg-muted/30`), translucent hairline borders (`border-muted/40`), subtle shadows (`shadow-sm`). |

## 📐 2. Visual Hierarchy & Spatial Invariants (The Human Blueprint)
1. **The 60-30-10 Spacing Rule:** You are FORBIDDEN from using a single static padding across the platform. Layouts must feature variable spatial grouping:
   - Elements inside a card/component: Strict tight spacing (`gap-2` or `p-3`).
   - Component-to-component margins: Medium dynamic spacing (`gap-4` or `p-5`).
   - Major section/dashboard layout boundaries: Generous respiratory space (`gap-6` to `gap-12`).
2. **Subtle Elevation over Hard Borders:** Eliminate dark, sharp borders around containers. To separate dashboard blocks or card components, prioritize subtle background shading (`bg-muted/30`) or extremely soft, blurred ambient shadow tokens (`shadow-sm`) with translucent border accents (`border-muted/40`).
3. **Typography Discipline:** Strictly maximum 3 font size tiers active in a single viewport (e.g. Page Title `text-2xl font-semibold`, Section Header `text-sm font-medium`, Body/Meta `text-xs text-muted-foreground`).

## 🧪 3. Automated Uniqueness Assessment Loop
Before submitting any frontend component, execute an internal self-audit loop within XML tags `<ui_audit>`:
- **Contrast Check:** Does every interactive row, button, or link feature an explicit micro-interaction state (`hover:bg-...`, `active:scale-[0.98]`, `focus-visible:ring-2`)?
- **Typography Check:** Is font scaling capped at ≤ 3 distinct scale tokens to prevent cognitive clutter?
- **Component Colocation Check:** Are functional elements clustered based on natural reading flow (F-pattern or Z-pattern) rather than aligned in a default mechanical matrix grid?
- **Border Check:** Are containers styled with soft background contrasts (`bg-card` / `bg-muted/30`) rather than stark solid dark borders?
- **Localization Slop Check:** Are all labels, headers, and microcopy free from dual-language parenthetical translations (e.g. "คำไทย (English Word)")? Are multi-language texts cleanly separated into i18n dictionaries (`locales/*.json`) with strict single-locale viewport rendering?

If the layout fails on any parameter, you MUST refactor the UI tree before presenting code.
