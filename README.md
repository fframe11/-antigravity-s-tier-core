# Antigravity S-Tier: Enterprise AI Agent Ecosystem

> **The Definitive Configuration, 98+ Skills Registry, MCP Server Mesh, and Guardrail Engine for Google Antigravity.**  
> Transform standard Antigravity into an elite Principal DevSecOps & Enterprise Full-Stack AI Engineer.

---

## ⚡ Quick Start (1-Click Installation)

Clone this repository and run the automated installer for your operating system:

### Windows (PowerShell)
```powershell
git clone <YOUR_REPO_URL> antigravity-s-tier-core
cd antigravity-s-tier-core
.\install.ps1
```

### macOS / Linux (Bash)
```bash
git clone <YOUR_REPO_URL> antigravity-s-tier-core
cd antigravity-s-tier-core
chmod +x install.sh
./install.sh
```

The installer automatically:
1. Deploys **98+ S-Tier Skills** into `~/.gemini/config/skills/`
2. Configures **Enterprise Project Guardrails** in `~/.gemini/templates/`
3. Installs global cognitive rules (`GEMINI.md`, `AGENTS.md`) into `~/.gemini/`
4. Deploys custom MCP servers (`code-analysis`, `vulnerability-scanner`, `unsplash`, `google-image-search`)
5. Generates the active `mcp_config.json` tailored to your local user home directory

---

## 🏛️ Architecture & System Structure

```
antigravity-s-tier-core/
├── skills/                     # 98+ Production-Grade Agent Skills
│   ├── five-source-frontend/   # 5-Source UI sourcing invariant (21st.dev, aceternity, etc.)
│   ├── stitch/                 # Google Lab's @google/stitch design-first integration
│   ├── human-dashboard-design/ # Enterprise BI & Admin layouts (Next-Shadcn)
│   ├── anti-ui-slop/           # Zero-phantom UI & event handler verification
│   ├── security-and-hardening/ # Supply-chain, attack surface & auth hardening
│   ├── owasp-cheatsheets/      # OWASP Top 10 secure coding guidelines
│   ├── user-persona/           # Authentic senior engineering voice & decision engine
│   ├── i-have-adhd/            # Direct-action communication & Bot Template Ban
│   └── ... (90+ more)
├── rules/                      # Global Cognitive Invariants & Rules
│   ├── GEMINI.md               # S-Tier Master Rules (Godkiller orchestration, UI invariants)
│   └── AGENTS.md               # Execution guidelines and invariant constraints
├── docs/                       # Definitive Technical & Cognitive Manuals
│   ├── API_MISTAKES_AND_LESSONS.md # Fatal API mistakes, real postmortems & defense patterns
│   └── COGNITIVE_PERSONA_ARCHITECTURE.md # 3-layer cognitive thinking reference & preview
├── lessons/                    # Epistemic Postmortems Database
│   ├── lessons.db              # Godkiller memory SQLite database
│   └── lessons.json            # Human-readable export of validated architectural lessons
├── templates/                  # Automated Project Guardrails (Self-Scaffolding)
│   ├── init-guardrails.ps1     # 1-click project onboarding guardrail injector
│   └── project-guardrails/     # Injected into every new/existing workspace
│       ├── CLAUDE.md           # Project rules with 24 non-negotiable invariants
│       ├── audit-ai-slop.ps1   # Scanner for AI writing & UI slop
│       ├── audit-mermaid-parity.ps1 # 100% diagram-to-code parity verifier
│       ├── audit-architecture-boundaries.ps1 # Dependency layer boundary checker
│       ├── backup-project.ps1  # Atomic workspace backup script
│       └── watch-autocommit.ps1# Continuous git background commit watcher
├── mcp/                        # Model Context Protocol (MCP) Mesh
│   ├── mcp_config.template.json# Portable multi-platform MCP configuration
│   └── custom-servers/         # Embedded Python MCP servers
│       ├── code-analysis-mcp/  # AST code analyzer & dependency mapper
│       ├── mcp-scanner/        # Semgrep & OWASP vulnerability scanner
│       ├── unsplash-mcp/       # Context-aware authentic photo discovery
│       └── google-image-search-mcp/ # Technical diagram & product reference search
├── plugins/                    # Remotion video engineering & rules plugins
├── install.ps1                 # Windows PowerShell Installer
├── install.sh                  # macOS/Linux POSIX Installer
└── README.md                   # This documentation
```

---

## 🎯 Core Operating Invariants

### 1. Mandatory Stitch Design-First Invariant (`@google/stitch`)
- **Strict Rule:** The agent is **strictly forbidden** from writing React, Next.js, HTML, or CSS code for any new web page without first designing it via Google Lab's `@google/stitch` CLI (`stitch generate` / `stitch prototype`).
- **Workflow:** Design in Stitch -> Review with human -> Code in IDE -> Parity check via `stitch sync` and `stitch audit`.

### 2. The 5-Source Exclusive Frontend Sourcing Invariant
- To prevent generic AI templates, all frontend components, animations, and micro-interactions MUST be sourced strictly from 5 vetted platforms:
  1. `21st.dev`
  2. `ui.aceternity.com`
  3. `reactbits.dev`
  4. `uiverse.io`
  5. `godly.design`
- Directly integrated via `ui-registry-mcp` for instant search and retrieval.

### 3. The 8 Enterprise-Grade Production UI Components
1. **Dynamic Navbar & Hero Block:** Shadcn Navigation Menu with subtle glowing action CTA (`ring-1 ring-primary/20 shadow-sm`).
2. **Skeleton & Progressive Loading:** Container-bounded `<Skeleton />` wrappers (`animate-pulse bg-muted/60`) with fixed aspect ratios (0% CLS).
3. **High-Density Micro-Interactions:** Physics-based spring feedback (`whileHover={{ scale: 1.02 }}`, `focus-visible:ring-2`).
4. **Advanced Interactive Tables:** TanStack Table data grids with column toggles and pagination.
5. **Asymmetric Metric Dashboards:** 70/30 focal layouts inside unified containers (`border-foreground/10`) with tinted trend badges.
6. **Global Notification & Toasts:** Sonner modern toast notifications replacing naive `alert()`.
7. **Multi-Locale Domain Toggle:** Clean i18n Select dropdowns reading from dedicated JSON dictionaries (`locales/th.json`, `locales/en.json`).
8. **Defensive Footer Structure:** Multi-column sitemap matrix with muted text tones (`text-muted-foreground/80`).

### 4. Universal Ban on Bot Template Headers (Rule 5.0)
The model is strictly prohibited from outputting robotic time tags and template headings:
- ❌ BANNED: `**สถานะความคืบหน้าปัจจุบัน**`, `**Step X of Y**`, `**สิ่งที่ทำต่อได้ทันที (ใช้เวลา 1 นาที)**`, `**Next Action**`
- ✅ REQUIRED: Direct, peer-to-peer senior engineer communication. Lead with actionable code, shell commands, or clear progress descriptions immediately.

---

## 🛠️ MCP Server Mesh

| MCP Server | Type | Description |
|---|---|---|
| `godkiller-mcp` | Python | Epistemic task orchestration, multi-phase verification, blast radius gating |
| `canva` | Remote SSE | Canva design creation, brand kit sync, and visual asset exports |
| `ui-registry` | NPX | Sourcing components from Aceternity UI, 21st.dev, and 10+ registries |
| `vulnerability-scanner` | Python (Semgrep) | Local OWASP Top 10, AST security audits, and secrets detection |
| `code-analysis` | Python | Codebase AST parsing, circular dependency checks, and architecture mapping |
| `playwright` / `puppeteer` | NPX | End-to-end browser automation, visual regression screenshots, and form testing |
| `unsplash` | Python | High-resolution editorial photography sourcing (Anti-CLS) |
| `google-image-search` | Python | Technical diagram and brand visual references |
| `sqlite-mock` / `redis-cache-mock` | Python | Fast in-memory database and caching simulation |
| `notion` | Remote SSE | Knowledge base search, documentation sync, and task management |
| `docker-manager` | NPX | Docker container inspection, log analysis, and lifecycle control |
| `tradingview` | NPX | Market data analysis, crypto/stock/forex screening, and technical indicators |

---

## 🚀 Pushing to Your GitHub Repository

To push this repository to your own GitHub account:

```bash
cd c:\Users\ffram\Documents\antigravity\antigravity-s-tier-core

# 1. Create a new repository on GitHub named "antigravity-s-tier-core"
# 2. Add your remote
git remote add origin https://github.com/fframe11/antigravity-s-tier-core.git

# 3. Rename branch to main (if not already)
git branch -M main

# 4. Push code
git push -u origin main
```

---

## 📜 License
MIT License. Free to use, customize, and distribute for personal and commercial agent workflows.
