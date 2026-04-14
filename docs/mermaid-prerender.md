# Mermaid Build-Time Rendering

This documentation site pre-renders all Mermaid diagrams to **PNG** at **build time** using `mmdc` (Mermaid CLI) and embeds them as **data URIs** directly in the page HTML.

## How it works

1. The hook `hooks/mermaid_prerender.py` scans every Markdown file for ` ```mermaid ` fenced blocks
2. Each diagram is rendered to a PNG via `mmdc` (Chromium backend):
   - Resolution: 800 logical px × 2× DPR → **1600 px physical width**
   - Background: white
3. The PNG is base64-encoded and embedded as `<img src="data:image/png;base64,…">`
4. PNGs are cached in `docs/assets/mermaid/` keyed by a hash of the diagram source + render config

## Why PNG (not SVG)

Mermaid v10+ renders flowchart and sequence node labels as HTML inside SVG `<foreignObject>` elements.
WeasyPrint (used by `mkdocs-to-pdf`) silently drops `<foreignObject>` content — all node text disappears.

PNG sidesteps this entirely: `mmdc` uses headless Chromium to rasterise each diagram, and Chromium renders `<foreignObject>` perfectly.

## Why data URI (not `<img src="path">`)

`mkdocs-to-pdf` combines every page into a single HTML document before calling WeasyPrint.
In that combined document, page-relative paths (like `../../assets/mermaid/x.png`) resolve against the **site root**, not the originating page — the files go missing and only the `alt` text appears.

Embedding as a data URI makes each diagram self-contained with no external file lookup required.

## Build requirements

Install Node dependencies once:
```bash
npm install
```

Then build normally — no special flags:
```bash
mkdocs serve       # browser preview with live reload
mkdocs build       # static build; PDF contains diagrams with all text
```

Headless Chromium must be available (it ships with the `@mermaid-js/mermaid-cli` package via Puppeteer).

## Cache management

Cached PNGs are stored in `docs/assets/mermaid/`.
They are keyed by `sha1(diagram_source + render_config_hash)` so any change to the diagram or config automatically produces a new file.

To clear all cached diagrams and force a full re-render:
```bash
rm -rf docs/assets/mermaid/
```
