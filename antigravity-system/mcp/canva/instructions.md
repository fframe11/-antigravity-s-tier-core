# Canva MCP Server Instructions

Official Canva Model Context Protocol remote integration (`https://mcp.canva.com/mcp`).
Authentication: OAuth 2.0 with PKCE via `mcp-remote` (tokens saved in `~/.mcp-auth/mcp-remote-v1/`).

## Available Capability Groups (48 Live Tools):

1. **Designs & Generation**:
   - `create-design`: Create fresh design canvases (presentation, doc, social post, etc.).
   - `generate-design`: AI-driven design generation from natural language prompts.
   - `search-designs`: Search user/team designs by keyword.
   - `get-design`, `get-design-pages`, `get-design-content`: Inspect structure, pages, and components.
   - `copy-design`: Duplicate designs.
   - `create-design-from-brand-template`: Spawn designs from corporate brand templates.

2. **Editing & Transactions**:
   - `start-editing-transaction`: Open an atomic editing session.
   - `perform-editing-operations`: Apply element updates, text changes, styling, and transformations.
   - `commit-editing-transaction`: Finalize and commit edits.
   - `cancel-editing-transaction`: Discard in-flight edits.
   - `resize-design`: Reframe and resize design dimensions.

3. **Asset & Image Intelligence**:
   - `generate-image`: Text-to-image AI synthesis directly into Canva.
   - `remove-background`: AI background removal on design assets.
   - `separate-image-layers`: Extract foreground/subject into distinct manipulable layers.
   - `upload-asset-from-url`, `create-upload-url`, `get-assets`: Media catalog management.

4. **Exports & Collaboration**:
   - `export-design`: Export to PDF, PNG, JPG, PPTX, MP4.
   - `get-export-formats`: Query permitted formats for a given design.
   - `comment-on-design`, `list-comments`, `reply-to-comment`: Collaborative review loops.
   - `create-folder`, `search-folders`, `move-item-to-folder`: Workspace structure.
