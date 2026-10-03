---
name: motion-framer
description: Production-grade animation and micro-interactions library for React and Next.js using Motion / Framer Motion. Enforces fluid spring physics, whileHover/whileTap micro-interactions, staggered layout reveals, AnimatePresence transitions, and scroll-driven effects with GPU acceleration.
metadata:
  tags: "framer-motion, motion, animation, micro-interactions, react, nextjs, frontend"
  category: "frontend"
---

# Motion & Framer Motion (Production-Grade UI Dynamics)

## Overview
Motion (formerly Framer Motion) is the industry standard for production animations in React and Next.js. Use this skill to eliminate stiff, robotic, static UI components by infusing organic micro-interactions, fluid spring physics, and orchestrated layout reveals.

**Core Targets:**
- Micro-interactions on buttons, cards, list items (`whileHover`, `whileTap`)
- Staggered list and grid entrances (`staggerChildren`, `delayChildren`)
- Smooth scroll-driven reveals (`whileInView`, `viewport={{ once: true }}`)
- Modals, drawers, and tabs with `AnimatePresence`
- Shared element and layout transitions (`layout`, `layoutId`)
- Accessibility: Automatic `prefers-reduced-motion` compliance

---

## 1. Setup & Package Imports

### Package Installation
```bash
npm install motion
# Or legacy framer-motion:
npm install framer-motion
```

### Import Conventions
```tsx
// Motion v12+ (Recommended):
import { motion, AnimatePresence, useScroll, useTransform, useReducedMotion } from "motion/react"

// Framer Motion (v10 / v11):
import { motion, AnimatePresence, useScroll, useTransform, useReducedMotion } from "framer-motion"
```

---

## 2. Production Spring Physics Defaults

Avoid linear or generic `ease-in-out` transitions. Use tuned physical springs:

```tsx
// Snappy Micro-interaction Spring (Buttons, Badges)
export const snappySpring = {
  type: "spring",
  stiffness: 400,
  damping: 25,
  mass: 0.8,
}

// Gentle Entrance Spring (Cards, Drawers, Modals)
export const gentleSpring = {
  type: "spring",
  stiffness: 260,
  damping: 20,
  mass: 1,
}

// Bouncy Playful Spring (Toggles, Icons)
export const playfulSpring = {
  type: "spring",
  stiffness: 500,
  damping: 15,
}
```

---

## 3. Micro-Interactions Pattern (Buttons & Interactive Cards)

Every interactive button, card, and clickable list item MUST feature responsive affordances:

```tsx
<motion.button
  whileHover={{ scale: 1.02, y: -1 }}
  whileTap={{ scale: 0.98 }}
  transition={snappySpring}
  className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow-sm hover:shadow"
>
  Start Test
</motion.button>
```

```tsx
<motion.div
  whileHover={{ y: -3, transition: { duration: 0.2 } }}
  whileTap={{ scale: 0.99 }}
  className="overflow-hidden rounded-xl border border-border/40 bg-card p-5 shadow-sm transition-shadow hover:shadow-md"
>
  <h3 className="font-semibold text-card-foreground">CEFR B2 Assessment</h3>
  <p className="text-sm text-muted-foreground">Grammar and reading comprehension module</p>
</motion.div>
```

---

## 4. Structural Reveals & Staggered Lists

Never allow dense cards or list items to pop into the viewport simultaneously. Orchestrate entrance:

```tsx
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.1,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: {
    opacity: 1,
    y: 0,
    transition: gentleSpring,
  },
}

export function TestCatalog({ items }: { items: TestItem[] }) {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-50px" }}
      className="grid grid-cols-1 gap-4 md:grid-cols-3"
    >
      {items.map((item) => (
        <motion.div key={item.id} variants={itemVariants} className="rounded-xl border p-4">
          <h4>{item.title}</h4>
        </motion.div>
      ))}
    </motion.div>
  )
}
```

---

## 5. Exit Animations with AnimatePresence

Wrap conditional DOM elements inside `<AnimatePresence mode="wait">` to guarantee graceful unmounting:

```tsx
<AnimatePresence mode="wait">
  {isOpen && (
    <motion.div
      key="modal-backdrop"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
    >
      <motion.div
        key="modal-content"
        initial={{ opacity: 0, scale: 0.95, y: 12 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 12 }}
        transition={gentleSpring}
        className="mx-auto mt-20 max-w-lg rounded-xl border bg-card p-6 shadow-xl"
      >
        <h2>Confirm Submission</h2>
        <button onClick={() => setIsOpen(false)}>Close</button>
      </motion.div>
    </motion.div>
  )}
</AnimatePresence>
```

---

## 6. Performance & Accessibility Guardrails

1. **GPU Acceleration Only:** Animate `transform` (scale, translate, rotate) and `opacity`. Never animate `width`, `height`, `top`, `left`, or `margin` directly.
2. **Respect Reduced Motion:**
   ```tsx
   const shouldReduceMotion = useReducedMotion()
   const animation = shouldReduceMotion ? { opacity: 1 } : { opacity: 1, y: 0 }
   ```
3. **Scroll Viewport Once:** When using `whileInView`, always pass `viewport={{ once: true }}` to avoid flickering on re-scroll.
