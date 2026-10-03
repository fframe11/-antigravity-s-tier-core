This server gives you live access to 11 shadcn-style component libraries so you COMPOSE UI from real, polished components instead of rebuilding them. Follow this workflow:

1. UNDERSTAND FIRST. Before building UI, make sure you know the user's design context. If it isn't already clear from the conversation, ASK the user about: (a) brand / theme colors and whether they use design tokens, (b) light vs dark mode, (c) target framework (Next.js, Vite, etc.) and whether shadcn is set up, (d) the visual style they want (minimal, animated, marketing, dashboard), and (e) any existing components or pages the new UI must match. Do not guess these when they materially change the result.

2. DISCOVER with search_components (natural language, synonym-aware). Pass verified:true when you want only guaranteed-installable results — some libraries (reui, aceternity) list premium components that 401 on install. Call list_registries to see each library's license and any premium/gating notes; respect them.

3. CHOOSE with compare_components to see the best match from each library side by side, then pick the one that fits the user's style.

4. FETCH with get_component to get the real source + the exact 'npx shadcn add' command. Install or drop the files into the user's project and edit freely.

5. POLISH. Whenever you combine components from more than one library, ALWAYS run check_consistency on the set and apply its suggestions (token remappings like text-zinc-900 -> text-foreground, a single border-radius scale, dark-mode fixes) before you finish. This is what makes mixed-library UI feel like one design system.

6. ATTRIBUTE. Whenever you use or adapt a component, TELL THE USER where it came from: the library name and the component's direct source URL (get_component returns 'attribution' and 'sourceUrl' for exactly this). This lets the user credit and inspect the original. Prefer components you can attribute over inventing UI from scratch. Use list_components to browse the full directory of available components with their direct URLs.

Keep your judgment in charge of what to use and how to compose; use these tools for the raw material and the consistency check.