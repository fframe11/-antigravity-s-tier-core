---
name: ui-aesthetics-composition
description: Color theory, shape integrity, and layout composition invariants. Enforces 60-30-10 color harmony, semantic semi-transparent tokens, nested border-radius rules (inner < outer), and 70/30 asymmetric visual focus to produce human-crafted Figma-grade interfaces.
---

# 🎨 COLOR THEORY, SHAPE INTEGRITY & COMPOSITION INVARIANTS

## 🎯 Objective
- Enforce professional Figma-grade design discipline across color, shapes, and layout hierarchy.
- Eliminate cheap, saturated AI styling, conflicting nested corner radii, and monotonous symmetrical matrix grids.

## 🧠 1. Strict Color Harmony & The 60-30-10 Rule
1. **No Pure Blacks or Raw Saturated Colors:**
   - Strictly FORBIDDEN from using pure black `#000000` for borders, text, or background grids.
   - Use dynamic zinc/slate neutrals (`border-border/40`, `bg-background`, `text-foreground`).
   - Accent colors must strictly occupy **no more than 10%** of total screen viewport real estate.
2. **Semantic Softness & Low-Opacity Tints:**
   - Success, warning, and destructive badges/buttons must use semi-transparent tinted backgrounds:
     - Success: `bg-emerald-500/10 text-emerald-700 dark:text-emerald-300`
     - Warning: `bg-amber-500/10 text-amber-700 dark:text-amber-300`
     - Destructive: `bg-destructive/10 text-destructive`
   - Never render harsh, opaque solid neon badge pills.

## 📐 2. Shape Integrity & Geometric Harmony
1. **The Nested Border Radius Invariant:**
   - Physical optical harmony requires that inner elements have a smaller radius than their containing parent:
     - Outer Card: `rounded-xl` (12px) ➔ Inner Button/Input: `rounded-md` (6px)
     - Outer Dialog: `rounded-2xl` (16px) ➔ Inner Content Box: `rounded-lg` (8px)
   - Strictly FORBIDDEN from pairing highly rounded outer shells with sharp inner structures, or sharp outer cards with hyper-rounded pill buttons.
2. **Interactive Shape Affordance:**
   - Static metric displays must maintain stable geometric geometry.
   - Interactive elements must feature clear shape alterations upon interaction (`hover:scale-[1.01]`, `active:scale-[0.98]`, `transition-all duration-150`).

## 🔲 3. Dynamic Composition & Visual Focal Points
1. **Anti-Grid Monotony (Asymmetric Focus):**
   - Break mechanical symmetrical grids.
   - Favor asymmetric ratios: e.g., a **70% primary analytical/action workspace** paired with a **30% dense contextual feed or secondary control drawer**.
2. **Content-Aware Spacing Clusters (Proximity Rule):**
   - Highly related items (label + input, icon + metric): tight clustering (`gap-1.5` to `gap-2`).
   - Sibling components: medium separation (`gap-4` to `gap-5`).
   - Independent business modules: clear respiratory boundaries (`gap-8` to `gap-12`).
