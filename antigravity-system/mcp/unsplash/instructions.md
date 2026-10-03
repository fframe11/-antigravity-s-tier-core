# Unsplash MCP Server Instructions

## Overview
The Unsplash MCP server provides access to authentic, high-resolution royalty-free photography for web interfaces, hero sections, feature grids, user avatars, and brand assets.

## Tools
- `search_photos`: Search curated and official Unsplash photos by keyword with ready-to-paste `<Image />` JSX snippets.
- `get_photo`: Retrieve specific photo details and direct high-resolution URLs.

## Usage Guidelines
1. Always replace placeholder image URLs (`/placeholder.svg`, `via.placeholder.com`) with authentic Unsplash CDN URLs.
2. Group images in containers with fixed aspect ratio (`aspect-video`, `aspect-square`) and `overflow-hidden rounded-xl` to prevent layout shifts (CLS).
3. Use the generated `jsx_snippet` for Next.js or standard React applications.
