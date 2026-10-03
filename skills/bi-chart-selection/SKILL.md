---
name: bi-chart-selection
description: Automated BI chart selection engine and data flow invariants derived from Microsoft Fabric and Financial Times Visual Vocabulary. Enforces Product-Context-First analysis, Cleveland-McGill perceptual accuracy hierarchy, cardinality gates, and 3-tier production data flows.
---

# 📊 AUTOMATED BI CHART SELECTION & DATA FLOW INVARIANTS

## 🎯 Core Directive: Product Context & Analytical Question First
You are strictly FORBIDDEN from guessing charts based on generic aesthetic impulse ("what looks cool"). Every chart selection MUST be grounded in:
1. **Product Archetype & Audience Context** (Executive vs Operational vs Analytical vs Comparative).
2. **The Core Analytical Question** ("What exact question does this visual answer?").
3. **Cleveland & McGill's Perceptual Accuracy Hierarchy**.
4. **Cardinality & Density Constraints**.

Official Reference: `references/chart-selection.md` (Microsoft Fabric / FT Visual Vocabulary / Abela Taxonomy).

---

## 🧭 Step 1: Infer Product Archetype & Audience Tolerance

Before picking any visual, identify who is reading the screen and what action they must take:
- **Executive Archetype**: Single high-level KPI cards + 1 primary hero trend/bar chart. Maximum glanceability (< 5s decode). **Avoid**: Scatter plots, box plots, dense matrices, gauges.
- **Operational Archetype**: Real-time status indicators (RAG badges), compact cards with sparklines, clean tabular queues. Focus on immediate operational bottlenecks.
- **Analytical Archetype**: Deep interactive drill-down. Scatter plots, histograms, box plots, small multiples grids, multi-dimensional filters.
- **Comparative Archetype**: Grouped/clustered horizontal bars, small multiples, slope charts, deviation indicators.

---

## 🧠 Step 2: Match Core Analytical Question to Chart Encoding

Identify the analytical intent of the query and map to the optimal visual type:

| Analytical Question / Intent | Primary Chart Selection | Cardinality / Constraints | Strict Prohibitions |
|---|---|---|---|
| **Trend over Time (Continuous)** | **Line Chart** (`LineChart`) | Continuous time axis, ≥ 7 data points, max 5 lines | Never use vertical bar charts with angled/tilted labels; avoid smoothed lines that hide volatility |
| **Trend over Time (Discrete Periods)**| **Column Chart** (`BarChart` vertical) | ≤ 6 discrete periods (e.g. Q1-Q4) | Do not exceed 6 columns for trends |
| **Categorical Comparison** | **Horizontal Bar Chart** | ≥ 7 items or long textual labels (prevents label tilt) | Never use pie charts for comparison |
| **Part-to-Whole / Composition** | **Donut Chart** (≤ 4 categories) or **Treemap** (> 4 categories) | Donut strictly ≤ 4 slices with exact %; Treemap for hierarchical | Never use 3D pie charts or pie charts with > 5 slices |
| **Process, Stage & Funnel** | **Funnel Chart** or **Sankey Diagram** | Funnel for monotone drop-off; Sankey for complex multi-path routes | Never use simple bars for conversion pipelines |
| **Statistical Distribution** | **Histogram** or **Box Plot** | Shape of variance and spread matters | Never use simple line charts for frequency distribution |
| **Correlation & Relationship** | **Scatter Plot** | Testing clusters / correlation across 2 numerical dimensions | Never merge unrelated units ($ vs #) into dual-axis lines |
| **Deviation from Baseline** | **Diverging Bar** or **Waterfall** | Variance (+/-) from a reference target or additive walk | Bars must not use arbitrary non-zero baselines |
| **Single Glance KPI** | **Compact Card + Sparkline** | Single metric with historical directional context | Never give a bare single-value card the entire hero canvas |

---

## 📏 Step 3: Cleveland & McGill Perceptual Accuracy Hierarchy

When selecting chart encoding, prioritize higher perceptual accuracy based on experimental psychology:
1. **Rank 1 (Highest Accuracy - ★★★★★)**: Position on common scale (Horizontal bars, dot plots, scatter plots). *Use when exact precision matters.*
2. **Rank 2 (★★★★)**: Length (Bar charts starting at 0).
3. **Rank 3 (★★★)**: Direction / Slope (Line charts).
4. **Rank 4 (Imprecise - ★★)**: Angle (Donut / Pie — human eyes struggle to compare angles).
5. **Rank 5 (Pattern only - ★★)**: Area (Bubble charts, Treemaps).
6. **Rank 6 (Worst - ★)**: Volume (3D charts — strictly banned across all production deliverables).

---

## 🚫 Step 4: Cardinality & Visual Limit Gates

- **Horizontal Bar**: Max 15–20 bars. If > 20, bucket tail into "Other" or use pagination.
- **Line Chart**: Max 5 series. Beyond 5 lines, charts become unreadable spaghetti. Switch to Small Multiples.
- **Donut / Pie**: Max 4–5 slices. Slices beyond 5 are unreadable.
- **Scatter Plot**: 3–5 color groups max.
- **Dual Axis**: Strictly FORBIDDEN when units differ (e.g., Revenue $ vs Conversion Count #). Create separate coordinated charts instead.

---

## 🔄 Step 5: Production Data Flow & 3-Tier ETL Pipeline

When building data pipelines connecting PostgreSQL/Prisma down to frontend Recharts/Visx:

1. **Backend Aggregation First**:
   - Strictly FORBIDDEN from streaming raw transaction logs or un-aggregated row collections to frontend charts.
   - The backend API must pre-aggregate data via SQL (`SUM()`, `AVG()`, `COUNT()` grouped by date clusters or category keys).
2. **Strict 3-Tier Data Architecture**:
   - *Ingestion Layer*: Fetch data asynchronously with React Query / SWR and validate payloads with Zod schemas.
   - *Transformation Layer*: Format dates (ISO -> locale), format currency/percentages, compute deltas, and impute defaults for missing buckets.
   - *Visualization Layer*: Hydrate clean arrays into reactive chart containers with fixed bounding heights (`h-[300px]`, `min-h-[250px]`) to eliminate layout thrashing (CLS).
3. **Chart Defensive Loading & Fallback Gate**:
   - Every chart MUST declare an explicit `<Skeleton className="h-[300px] w-full" />` matching the rendered visual geometry.
   - Every chart MUST supply an `<EmptyState message="No transaction data in selected range" />`.
   - Every chart MUST be enclosed in an Error Boundary handling 500s and network timeouts gracefully.
