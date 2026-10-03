---
name: stitch
description: Google Lab's Stitch AI Design CLI integration. Enforces design-first workflow, UI generation, and auditing.
---

# Stitch CLI Integration

## Trigger
Use this skill whenever the user explicitly calls `/stitch`, mentions generating designs from Stitch, auditing UI with Stitch, or when starting a NEW frontend web development task.

## Mandatory Design-First Invariant (Strict Rule)
The user has strictly mandated: **You MUST design via Stitch before starting to build the web page.**
When tasked with building a new UI, component, or web page:
1. **DO NOT** immediately write React/Next.js/Tailwind code.
2. You **MUST** use the `stitch` CLI to generate the screen, design system, or UI prototype first.
3. Only proceed to code implementation after the Stitch design step is complete and approved or reviewed.

## Capabilities & Commands
The `@google/stitch` CLI provides the following capabilities that you can invoke via `run_command`:
- **Generate**: Create screens and design systems directly from the terminal.
- **Sync**: Send a snapshot of the local dev server (e.g., localhost) back to Stitch for parity checking.
- **Audit**: Run a UI audit on the running application.
- **Repo Linking**: Connect the current repository to define priorities, context, and perform codebase prototyping.
- **Agentic Loop**: `stitch loop` (Experimental) runs continuously to monitor the codebase, logs, analytics, and user feedback, proposing automated insights and fixes.

## Workflow Execution
1. Ask the user if they have run `stitch login` if authentication errors occur.
2. Execute `stitch` CLI commands using the standard shell.
3. Combine this with the `five-source-frontend` and `human-dashboard-design` invariants for the final coded output, but the *initial design* phase must belong to Stitch.
