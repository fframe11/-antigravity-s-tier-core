---
name: five-source-frontend
description: The 5-Source Exclusive Frontend Sourcing Invariant. Mandates that all UI components, animations, and micro-interactions must be sourced strictly from 21st.dev, ui.aceternity.com, reactbits.dev, uiverse.io, and godly.design. Forbids ungrounded AI UI generation and enforces design harmonization.
---

# The 5-Source Exclusive Frontend Sourcing Invariant

## Overview & Core Mandate

When building or refining any frontend UI, landing page, dashboard, or interactive web component in Antigravity, **the agent is strictly forbidden from generating generic, uninspired UI components from scratch**.

Instead, every single visible element, layout block, text animation, and micro-interaction **MUST be explicitly sourced from the 5 authoritative design engines**:

| Source | Role & Domain | Primary Sourcing & Retrieval Tool |
| :--- | :--- | :--- |
| **1. 21st.dev** | Page Backbone, Bento Grid, Hero Section, Pricing, Navbar, Footer | `@21st-dev/cli` (`search`, `get`, `add`) or `twentyfirst` MCP |
| **2. ui.aceternity.com** | 3D Spatial Effects, Canvas, Background Beams, Lamps, Parallax | `ui-registry` MCP (`search_components`, `get_component`) or Shadcn Remote Registry |
| **3. reactbits.dev** | Interactive Typography, Text Pressure, Decrypted Text, Particle Shaders | `npx shadcn add @react-bits/<name>` or `DavidHDev/react-bits` raw repo |
| **4. uiverse.io** | Micro-interactions: Buttons, Custom Switches, Loaders, Atomic Cards | `uiverse-io/galaxy` GitHub archive or direct Tailwind extraction |
| **5. godly.design** | Visual Hierarchy, Spatial Rhythm, Spring Physics & Award-Winning Layouts | `hallmark` + DevTools DOM inspection of award-winning live web patterns |

---

## 1. 21st.dev: Page Architecture & Macro Layouts

Use **21st.dev** for the primary layout scaffold:
- **Hero Sections**: High-converting hero layouts, bento arrangements, and dynamic headers.
- **Bento Grids**: Modern asymmetric feature grids with nested content blocks.
- **Pricing & Comparison Tables**: Transparent multi-tier pricing cards with switchable billing cycles.
- **Navigation & Footers**: Responsive floating navbars and semantic multi-column footers.

### Execution Protocol:
1. Search via CLI:
   ```bash
   npx @21st-dev/cli search "bento grid" --json
   ```
2. Pull component source code:
   ```bash
   npx @21st-dev/cli get <component-id> --json
   ```
3. Install via author/slug if shadcn-compatible:
   ```bash
   npx @21st-dev/cli add <author>/<slug>
   ```

---

## 2. ui.aceternity.com: 3D Depth & Visual Hooks

Use **Aceternity UI** for high-impact visual centerpieces:
- **Background Effects**: `Background Beams`, `Background Gradient`, `Sparkles`, `Wavy Background`, `Vortex`.
- **Card Depth & Parallax**: `3D Card Effect`, `Card Hover Effect`, `Tracing Beam`, `Parallax Scroll`.
- **Hero Focal Elements**: `Lamp Effect`, `Macbook Scroll`, `Hero Parallax`.

### Execution Protocol:
1. Search via `ui-registry` MCP:
   - Tool: `search_components(query="lamp effect", registry="aceternity")`
2. Fetch complete code and dependencies:
   - Tool: `get_component(name="lamp-effect", registry="aceternity")`
3. Direct Shadcn CLI installation:
   ```bash
   npx shadcn add "https://ui.aceternity.com/registry/lamp.json"
   ```

---

## 3. reactbits.dev: Text Choreography & Background Shaders

Use **React Bits** for typography-driven personality and dynamic text:
- **Header Animations**: `Split Text`, `Decrypted Text`, `Text Pressure`, `Shiny Text`, `True Focus`, `Blur Text`.
- **Interactive Canvases**: `Particles`, `Ballpit`, `Waves`, `Hyperspeed`, `Dither`.

### Execution Protocol:
1. Install via React Bits registry:
   ```bash
   npx shadcn add @react-bits/<component-name>
   ```
2. Or fetch directly from open-source repository `DavidHDev/react-bits`:
   `https://raw.githubusercontent.com/DavidHDev/react-bits/main/src/content/Animations/<Component>/<Component>.tsx`

---

## 4. uiverse.io: Micro-Interactions & Atomic Controls

Use **Uiverse** for tactile micro-interactions that make interfaces feel responsive and playful:
- **Buttons**: Glow buttons, magnetic hover buttons, tactile 3D press buttons.
- **Feedback & Loaders**: Minimalist spinners, morphing progress bars, skeleton pulses.
- **Form Controls**: Dynamic theme toggle switches, animated checkboxes, floating inputs.

### Execution Protocol:
1. Query component category in `uiverse-io/galaxy` GitHub archive:
   `https://raw.githubusercontent.com/uiverse-io/galaxy/main/elements/<Category>/<Item-ID>.html` (or `.json`)
2. Extract Tailwind CSS utilities and wrap in an accessible React button/control with `whileTap={{ scale: 0.98 }}`.

---

## 5. godly.design: Curation & Motion Calibration

Use **Godly** as the aesthetic North Star:
- **Typography Scale**: Maximum 3 font scale tiers across the viewport (`text-3xl` -> `text-sm` -> `text-xs`).
- **Spring Physics**: Never use linear or bouncy clown animations. Mirror award-winning sites using spring configurations (`stiffness: 300, damping: 25`).
- **Spatial Rhythm (60-30-10 Spacing)**: Tight inside cards (`gap-2`), medium between related elements (`gap-4`), generous between major macro sections (`gap-12`).

---

## The Post-Sourcing Harmonization Pass

Whenever components from multiple sources are assembled into a single page, you **MUST run a mandatory Harmonization Pass**:

1. **Token Unification**:
   - Replace hardcoded colors (e.g. `bg-zinc-900`, `text-blue-500`) with semantic theme variables (`bg-card`, `text-foreground`, `ring-primary/20`).
2. **Nested Radius Invariant**:
   - Outer card container: `rounded-xl` (12px)
   - Inner buttons/inputs: `rounded-md` (6px)
   - *Never allow inner elements to have equal or larger radius than parent containers.*
3. **Consistency Check via `ui-registry` MCP**:
   - Call tool `check_consistency` on the assembled TSX file to catch token drift, missing dark mode classes, or contrasting border widths.
4. **Anti-CLS Geometry Locking**:
   - Wrap dynamic animations and loaded components in fixed bounding boxes (`min-h-[...]`, explicit aspect-ratios) to guarantee zero layout shifts.
