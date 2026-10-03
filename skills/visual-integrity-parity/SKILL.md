---
name: visual-integrity-parity
description: Visual integrity, anti-flicker layout stabilization, and Mermaid architectural parity. Enforces fixed container geometry (min-h-*, aspect-ratio) to prevent layout thrashing/CLS during data hydration, and mandates 100% synchronization between technical Mermaid diagrams and implementation code.
---

# 🗺️ VISUAL INTEGRITY, MERMAID PARITY & ANTI-FLICKER INVARIANTS

## 🎯 Objective
- Eliminate layout thrashing, label flickering, and Cumulative Layout Shift (CLS) during asynchronous data fetching and video/image streaming.
- Guarantee 100% synchronization between system architecture diagrams (Mermaid) and the actual underlying code.

## 🔲 1. Interface Stabilization & Anti-Flicker Rules
1. **Layout Constraints & Fixed Bounding Boxes:**
   - Dynamic visualization nodes, charts, video streams, and live metric cards MUST occupy container footprints with fixed geometric boundaries (`min-h-[300px]`, explicit aspect ratios, or fixed flex basis).
   - Asynchronous data arrivals or streaming updates are strictly FORBIDDEN from dynamically pushing or shifting surrounding layout tokens (Zero Cumulative Layout Shift / Anti-Flickering).
2. **Deterministic Layout States & Skeleton Parity:**
   - Every component undergoing dynamic data hydration must render a uniform Skeleton loader matching the exact pixel dimensions of the final loaded state.
   - Layout shifts and rendering reflows are strictly treated as P1 critical frontend bugs.

## 📊 2. Diagram-to-Code Parity (Strict Mermaid Gate)
1. **Architectural Synchronization:**
   - Whenever modifying backend modules, service boundaries, data pipelines, database models, or state transitions, you are STRICTLY REQUIRED to update the local architecture diagrams (`.md` or Mermaid blocks) within the exact same atomic commit.
2. **Code Truth Principle:**
   - Mermaid sequence diagrams, entity relationship diagrams (ERD), and state machines must strictly reflect verified execution logic in code.
   - Symmetrical design schemas must be validated via code review gates before declaring a feature complete.

## 🛠️ 3. Automated Diagram Repairs & Mechanical Parity Verification
1. **Automated Mermaid Validation Toolchain:**
   - Enforce syntax validation via `@mermaid-js/mermaid-cli` or Mermaid GitHub App across all documentation and PRs (`npx -p @mermaid-js/mermaid-cli mmdc -i docs/architecture.mmd -o /dev/null`).
   - Run `audit-mermaid-parity.ps1` locally to automatically extract entities from Prisma/TypeORM/Zod schemas and cross-reference against Mermaid ERDs.
2. **Automated Repair & Sync Protocol:**
   - When schema drift is detected (e.g., added fields, updated relations, modified route parameters), the parity engine automatically proposes or applies the synchronized Mermaid AST patch in the same commit.
   - PR builds MUST fail-closed if diagrams have syntax errors or drift from underlying database entities.

