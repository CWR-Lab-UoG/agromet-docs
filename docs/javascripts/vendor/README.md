# Vendored (Local) Runtime Assets

This docs site is configured for **zero external runtime dependencies**.

## MathJax (LaTeX rendering)

The MathJax v3.x `es5/` distribution is vendored locally:

```
docs/javascripts/vendor/mathjax/es5/
```

MkDocs serves MathJax locally and equations render with no CDN calls.

**Loading order matters.** In `mkdocs.yml`, `mathjax.js` (the config) must
be listed *before* the MathJax library:

```yaml
extra_javascript:
  - javascripts/mathjax.js                          # sets window.MathJax FIRST
  - javascripts/vendor/mathjax/es5/tex-mml-chtml.js
  - javascripts/mermaid-zoom.js
```

## Mermaid (diagrams)

Mermaid diagrams are **pre-rendered at build time** by the hook
`hooks/mermaid_prerender.py` using the Mermaid CLI (`mmdc`).  No
client-side Mermaid JavaScript is loaded or needed.

Pre-rendered SVGs are written to `docs/assets/mermaid/` and referenced as
`<img>` tags in the page HTML.

## Notes

- External CDN scripts (polyfill.io, etc.) have been intentionally removed.
- All runtime assets are self-hosted.
