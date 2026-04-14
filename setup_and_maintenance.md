# Setup and Maintenance Guide

This document describes how to **set up, build, run, and maintain** the EC/FG processing
documentation system.

It is intended for **maintainers and developers**, not end-users of the data products.

---

## 1. Prerequisites

### Operating system
- Windows (primary development environment)
- Linux/macOS (supported for documentation build; processing scripts may be OS-specific)

### Required software

| Component | Version | Purpose |
|-----------|---------|---------| 
| Python | ≥ 3.10 | MkDocs and plugins |
| Node.js | ≥ 18 | Mermaid CLI (build-time only) |
| Git | any | Version control |

### Python packages
```bash
pip install -r requirements.txt
```

Key dependencies:

| Package | Purpose |
|---------|---------|
| `mkdocs` | Static site generator |
| `mkdocs-material` | Theme |
| `pymdown-extensions` | Markdown extensions (math, superfences, etc.) |
| `mkdocs-glightbox` | Image lightbox plugin |
| `mkdocs-to-pdf` | PDF generation via WeasyPrint |
| `latex2mathml` | LaTeX → MathML conversion for PDF math rendering |

### Node packages (build-time only)
```bash
npm install
```

Provides `@mermaid-js/mermaid-cli` (pinned to 11.12.0), which bundles headless Chromium.
No Node dependencies are needed at runtime.

---

## 2. Repository Setup

```bash
git clone <repo-url>
cd <repo>
pip install -r requirements.txt
npm install
```

Verify:
```bash
mkdocs --version
node_modules/.bin/mmdc --version
```

---

## 3. Local Development

### Serve documentation locally
```bash
mkdocs serve
```
Live reload enabled. Mermaid diagrams are pre-rendered on first startup (slower);
subsequent serves reuse the PNG cache.

### Build static site + PDF
```bash
mkdocs build
```
Output written to `site/`. The PDF is generated automatically by the `to-pdf` plugin.
**No special environment variables or flags are needed.**

---

## 4. Flux-Gradient System: Key Constants and Parameters

This section summarises the MATLAB implementation parameters for the FG pipeline,
extracted from the `Guelph_agromet_constants` file and the `*_init_all.m` site
initialization functions.

### Physical Constants

| Constant | Value | Notes |
|----------|-------|-------|
| von Kármán constant κ | 0.40 | Standard |
| Gravitational acceleration g | 9.81 m s⁻² | Guelph, ~43.5 °N |
| Universal gas constant R | 8.31451 J mol⁻¹ K⁻¹ | |
| Specific gas constant dry air R_d | 287.05 J kg⁻¹ K⁻¹ | |
| Molar mass dry air | 28.96 g mol⁻¹ | |
| Molar mass CO₂ | 44.01 g mol⁻¹ | |
| Molar mass N₂O | 44.01 g mol⁻¹ | |

### Canopy Parameters (defaults; overridable per site)

| Parameter | Default formula | Notes |
|-----------|----------------|-------|
| Displacement height d | 0.67 × h_c | Standard agricultural value |
| Roughness length z₀ | 0.13 × h_c | Site-calibrated for Guelph crops |

### Stability Functions

The pipeline implements Businger-Dyer with coefficient **15** (not 16):

- **Stable** (ζ > 0): φ_h = 1 + 4.7ζ; ψ_h = −4.7ζ
- **Neutral** (|ζ| ≤ 0.01): φ_h = 1; ψ_h = 0
- **Unstable** (ζ < 0): φ_h = (1 − 15ζ)^−0.5; ψ_h = 2 ln((1 + x²)/2), x = (1 − 15ζ)^0.25
- **Very stable** (ζ > 2): K = NaN — reject
- **Very unstable** (ζ < −5): K = NaN — reject

### TGA Operational Parameters

| Parameter | Value |
|-----------|-------|
| Level duration | 60 s per intake |
| Omit period (start of level) | 10–15 s (configurable in `*_init_all.m`) |
| Minimum valid level duration | ≥ 12 s |
| Operating pressure | 50–80 mb |
| Sample flow | 500–2000 ml min⁻¹ |
| Tube delay (TGA100A) | 2–6 s (sine-curve fit to nighttime CO₂) |
| Outlier rejection threshold | > 100 outliers per half-hour |
| ΔP between intakes | < 0.075 kPa |
| Zero / negative concentrations | Converted to NaN |

### Output Units

| Gas | Unit |
|-----|------|
| N₂O flux | ng N₂O-N m⁻² s⁻¹ |
| CO₂ flux | µg CO₂ m⁻² s⁻¹ |

---

## 5. Mermaid Diagram Pipeline

### How it works

`hooks/mermaid_prerender.py` runs during every build and serve:

1. Scans Markdown source for ` ```mermaid ` fenced blocks
2. Renders each diagram to **PNG** via `mmdc` (Chromium backend):
   - Viewport: 820 logical px × 2× device pixel ratio → **1640 px physical width**
   - Background: white
3. Caches PNGs in `docs/assets/mermaid/` keyed by `sha1(diagram_source + config_hash)`
4. Embeds each PNG as a `data:image/png;base64,…` URI in `<img class="mermaid-svg">`

### Why PNG (not SVG)

Mermaid v10+/v11 renders flowchart and sequence node labels as HTML inside SVG
`<foreignObject>` elements. WeasyPrint silently drops `<foreignObject>` content —
all node text disappears from the PDF. PNG bypasses this: mmdc rasterises through
headless Chromium, which renders `<foreignObject>` correctly.

### Why data URI (not an external file reference)

`mkdocs-to-pdf` combines every page into a single HTML document before calling
WeasyPrint. Page-relative paths like `../../assets/mermaid/x.png` resolve against
the site root in that combined document and miss the files. A `data:image/png;base64,…`
URI is self-contained — no external lookup needed.

### Cache invalidation

The cache key encodes `sha1(diagram_source + CONFIG_HASH)`. Changing `_RENDER_CFG`
in the hook rotates `CONFIG_HASH`, producing new filenames and bypassing stale PNGs.
To force a full re-render:
```bash
rm -rf docs/assets/mermaid/
```

### Diagram CSS

- **Browser:** `img.mermaid-svg` uses `max-width: 100%; width: auto; max-height: 70vh`
  — tall TB flowcharts are viewport-capped while preserving aspect ratio; click opens
  the zoom overlay.
- **PDF:** `max-height: 190mm` prevents any diagram from exceeding A4 content height;
  `page-break-inside` is intentionally **not** set (setting it on elements taller than
  a page causes WeasyPrint to abort rendering everything after).

---

## 6. Math Equations — Browser and PDF

### The problem

`pymdownx.arithmatex` (generic mode) wraps every equation in
`<span class="arithmatex">\(...\)</span>` or `<div class="arithmatex">\[...\]</div>`.
MathJax processes these in the browser via JavaScript. WeasyPrint (PDF) has no JavaScript,
so raw LaTeX appears in the PDF.

### The solution: three-layer pipeline

`hooks/math_prerender.py` runs after each page's Markdown → HTML conversion:

1. Finds every `arithmatex` inline span and display div
2. **Decodes HTML entities** in the extracted LaTeX — `pymdownx.arithmatex`
   HTML-escapes special characters (`<` → `&lt;`, `>` → `&gt;`, `&` → `&amp;`)
   before the hook sees them; `html.unescape()` restores them to plain LaTeX
   before the next step
3. Converts the LaTeX to MathML using `latex2mathml` (pure Python)
4. Applies Unicode math-italic substitution (`_italicize_mi()`) to single-letter
   `<mi>` elements — see below
5. Inserts a companion `.math-mathml` element immediately after each equation

CSS controls which version each medium sees:

```css
/* Browser: hide MathML, MathJax renders arithmatex */
.math-mathml { display: none; }

@media print {
    /* PDF: hide raw arithmatex, WeasyPrint renders MathML */
    .arithmatex        { display: none !important; }
    .math-mathml       { display: inline !important; }
    .math-mathml-block { display: block  !important; text-align: center; }
}
```

If `latex2mathml` fails for a specific equation, the original `arithmatex` element
is left unchanged and a build warning is printed. The browser still renders correctly;
only that equation will show raw LaTeX in the PDF.

### WeasyPrint MathML layout (extra.css)

WeasyPrint (tested through v68) parses MathML elements but does **not** implement
the MathML layout algorithm. The most visible symptom: `<mfrac>` fractions render
as flat inline text — numerator and denominator are concatenated with no fraction
bar or vertical stacking.

`docs/stylesheets/extra.css` supplies explicit CSS `display` rules for every MathML
element produced by `latex2mathml` inside the `@media print` block:

| MathML element | CSS treatment | Result |
|---|---|---|
| `<math>` | `display: inline-block` | Isolated formatting context |
| `<mrow>`, `<mstyle>` | `display: inline` | Transparent grouping |
| `<mfrac>` | `display: inline-table` + `border-bottom` on numerator row | Visual fraction with bar |
| Nested `<mfrac>` | `font-size: 0.85em` | Prevents nested fractions from overpowering outer |
| `<msub>`, `<msup>` | `display: inline` + `vertical-align: sub/super` on script child | Correct sub/superscripts |
| Leaf elements (`<mi>`, `<mn>`, `<mo>` …) | `display: inline` | Explicit, prevents block fallback |

### Latin Modern Math font (docs/fonts/)

`docs/fonts/latinmodern-math.otf` is the OpenType successor to Computer Modern Math
— the same font family LaTeX uses. It is declared in `extra.css` as a `@font-face`
and applied to `math` elements in the `@media print` block:

```css
@font-face {
    font-family: 'Latin Modern Math';
    src: url('../fonts/latinmodern-math.otf') format('opentype');
    font-weight: normal;
    font-style: normal;
}

@media print {
    math {
        font-family: 'Latin Modern Math', 'STIX Two Math', 'Cambria Math', serif;
    }
}
```

The font is licensed under the GUST Font License (GFL), which permits embedding in
PDFs and redistribution. MkDocs copies it to `site/fonts/` automatically as a static
asset — no `mkdocs.yml` changes are needed.

### Unicode math-italic substitution (math_prerender.py)

In proper math typesetting (LaTeX, MathJax), single-letter identifiers are shown in
a *designed* italic alphabet — distinct Unicode code points, not a geometric slant
of upright glyphs. `math_prerender.py` implements this via `_italicize_mi()`, which
runs after `latex2mathml` conversion and before the MathML is injected into the page.

Substitution rules follow LaTeX convention exactly:

| Category | Treatment | Example |
|---|---|---|
| Latin uppercase A–Z | → U+1D434–U+1D44D (math italic capitals) | `K` → `𝐾` |
| Latin lowercase a–z | → U+1D44E–U+1D467 (`h` → U+210E ℎ) | `z` → `𝑧` |
| Greek lowercase α–ω | → U+1D6FC–U+1D714 | `κ` → `𝜅`, `ψ` → `𝜓` |
| Greek uppercase (Δ, Σ …) | Kept upright | `Δ` stays `Δ` |
| Multi-letter `<mi>` (ln, sin …) | Kept upright | function names unchanged |

`latex2mathml` encodes non-ASCII characters as HTML entities (e.g. `&#x003BA;` for
κ). `_italicize_mi()` decodes these before lookup so Greek letters are substituted
correctly alongside ASCII letters.

### MathJax load order

The `mathjax.js` configuration file **must be listed before** the MathJax library
in `mkdocs.yml`:

```yaml
extra_javascript:
  - javascripts/mathjax.js                          # MUST be first — sets window.MathJax
  - javascripts/vendor/mathjax/es5/tex-mml-chtml.js
  - javascripts/mermaid-zoom.js
```

MathJax reads `window.MathJax` at startup. Loading the config after the library
means the config is silently ignored and equations do not render.

---

## 7. JavaScript, CSS, and Font Files Reference

| File | Purpose |
|------|---------|
| `docs/javascripts/mathjax.js` | MathJax v3 configuration (`window.MathJax`) — load **first** |
| `docs/javascripts/vendor/mathjax/es5/tex-mml-chtml.js` | MathJax v3 library (self-hosted) |
| `docs/javascripts/mermaid-zoom.js` | Click-to-zoom overlay for pre-rendered diagram images |
| `docs/stylesheets/mermaid-svg.css` | Diagram sizing + video/iframe print suppression |
| `docs/stylesheets/extra.css` | Math print/browser switching, WeasyPrint MathML layout rules, Latin Modern Math font declaration, zoom overlay styles |
| `docs/stylesheets/mermaid-loading.css` | Fallback message if mmdc fails |
| `docs/fonts/latinmodern-math.otf` | Latin Modern Math OpenType font — embedded in PDF for LaTeX-quality math typography; licensed under GUST Font License (GFL) |

No client-side Mermaid JavaScript is loaded — all diagrams are pre-rendered at build time.

---

## 8. Navigation and Content Management

`mkdocs.yml` defines the canonical navigation tree. Only files listed in `nav` appear
in the site navigation. Files not listed still exist but are not linked.

!!! warning "Keep nav in sync with existing files"
    If a nav entry references a file that does not exist, `mkdocs-to-pdf` fails to
    generate a complete PDF — sections after the missing entry are dropped entirely.
    Only add nav entries for files that actually exist.

---

## 9. Adding or Updating Content

### New documentation page
1. Create the Markdown file under `docs/`
2. Add it to the appropriate section in `mkdocs.yml` under `nav:`
3. Run `mkdocs serve` to verify

### Mermaid diagrams
- Always include a diagram type header (`flowchart TD`, `graph LR`, `sequenceDiagram`, …)
- Multi-line node labels with `<br/>` are supported
- Avoid experimental Mermaid features for maximum compatibility
- Very tall TB flowcharts (10+ linear nodes) will be capped at 70 vh in the browser
  and 190 mm in the PDF — this is by design

### Math equations (LaTeX)
- Inline: `$...$` or `\(...\)`
- Display: `$$...$$` or `\[...\]`
- Both render via MathJax in the browser and via MathML in the PDF

---

## 10. Deployment

### GitHub Pages via GitHub Actions (recommended)

The repository ships a ready-to-use workflow at `.github/workflows/deploy.yml`.
Every push to `main` triggers it automatically:

```
push to main  →  checkout  →  pip install  →  npm ci  →  mkdocs gh-deploy
```

`mkdocs gh-deploy` builds the site into `site/` and pushes it to the `gh-pages`
branch in one step. You never touch the `gh-pages` branch manually.

#### One-time repository setup

1. Go to **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: **`gh-pages`** / `/ (root)`

Then update `mkdocs.yml` with your actual URL so internal links resolve correctly:

```yaml
site_url: https://<your-username>.github.io/<repo-name>/
```

After the first successful Actions run the site is live at that URL, and every
subsequent push to `main` updates it automatically.

#### What the workflow installs on the CI runner

| Step | Why |
|------|-----|
| `sudo apt-get install -y libpangocairo-1.0-0` | WeasyPrint requires the Pango + Cairo text engine for PDF rendering; it is not pre-installed on `ubuntu-latest` |
| `pip install -r requirements.txt` | MkDocs, theme, plugins, `latex2mathml` |
| `npm ci` | Mermaid CLI + its bundled Chromium (pinned via `package-lock.json`, ~150 MB) |

`pip` and `node_modules` are both cached between runs keyed on their respective
lockfiles, so routine doc edits that don't change dependencies complete in under
a minute after the first run.

#### Mermaid diagrams and the PNG cache

`hooks/mermaid_prerender.py` checks `docs/assets/mermaid/` for a cached PNG before
calling mmdc. Committing the cache directory means unchanged diagrams are never
re-rendered — mmdc and Chromium are not invoked at all on a cache hit. Only diagrams
whose source has actually changed are re-rendered.

Without the cache, every CI build re-renders every diagram, adding 30–60 s per
diagram on a cold runner. The `.gitignore` is written to keep the cache files.

#### Puppeteer sandbox — puppeteer.config.json

GitHub Actions runners do not permit the Chromium process sandbox. Without the
`--no-sandbox` flag, mmdc silently fails for every diagram with:

```
SyntaxError: Unexpected token '/', "/**  ← what you see if the file is .cjs
```

or exits without producing a PNG (if no config is given at all).

`puppeteer.config.json` at the project root supplies these flags:

```json
{
  "args": ["--no-sandbox", "--disable-setuid-sandbox"]
}
```

`mermaid_prerender.py` detects the file automatically and passes it to mmdc via
`--puppeteerConfigFile`. If the file is absent, the hook falls back to mmdc's
default Puppeteer settings (fine on local macOS/Windows dev machines).

!!! warning "Must be valid JSON — not a .cjs or .js module"
    mmdc calls `JSON.parse()` on the file directly.  A `.cjs` module with
    `/** ... */` or `//` comments is not valid JSON and will cause every diagram
    to fail with a `SyntaxError`. Keep the file as plain JSON with no comments.

### Cloudflare Pages
Compatible with the static output in `site/`. No external CDN dependencies at
runtime. Build command: `mkdocs build`. Output directory: `site`.

---

## 11. Maintenance Guidelines

- Keep workflows documented *only once*
- Update docs alongside code changes
- Avoid copying content between pages
- Prefer deleting obsolete documentation over leaving it stale
- Never add nav entries for files that do not yet exist

---

## 12. Troubleshooting

### Mermaid diagrams not generated
- Run `node_modules/.bin/mmdc --version` — if this fails, run `npm install`
- Check build output for `[mermaid_prerender]` error messages
- Ensure Puppeteer/Chromium downloaded correctly during `npm install`

### Mermaid diagrams fail with `SyntaxError: Unexpected token '/'` on CI
mmdc is trying to `JSON.parse()` the Puppeteer config file and failing because it
contains JS comments (e.g. the file is a `.cjs` module, not pure JSON).

- Verify `puppeteer.config.json` exists at the project root (not `.cjs` or `.js`)
- Verify it contains only valid JSON — no `//` or `/* */` comments, no `module.exports`
- The correct content is exactly:
  ```json
  { "args": ["--no-sandbox", "--disable-setuid-sandbox"] }
  ```

### Math equations not rendering in browser
- Open browser devtools → check for 404 errors on MathJax files
- Confirm `docs/javascripts/vendor/mathjax/es5/` directory is present
- Confirm `mathjax.js` is listed **before** `tex-mml-chtml.js` in `mkdocs.yml`

### Math equations show raw LaTeX in PDF
- Confirms `latex2mathml` is not installed — run `pip install latex2mathml`
- Check build log for `[math_prerender] WARNING` or `LaTeX→MathML failed` messages

### `<`, `>`, `&` symbols appear as `&lt;` / `&gt;` / `&amp;` in PDF equations
`pymdownx.arithmatex` HTML-escapes these characters in the LaTeX string before the
hook sees it. `latex2mathml` does not understand HTML entities, so it decomposes
`&lt;` into the individual glyphs `&`, `l`, `t`, `;` rather than a `<` operator.

- Confirm `_convert()` in `hooks/math_prerender.py` calls `html.unescape()` on the
  LaTeX string before passing it to `latex2mathml` (should be present in current version)
- If the issue reappears, check that no upstream step is double-escaping the LaTeX

### Math fractions appear as flat text in PDF (no fraction bar)
- This is a WeasyPrint limitation; it should be resolved by the CSS rules in
  `extra.css` (`@media print` MathML layout section)
- If it reappears after a CSS change, verify the `mfrac` `inline-table` rules are
  still present in `extra.css`

### PDF math uses wrong font / looks sans-serif
- Verify `docs/fonts/latinmodern-math.otf` exists
- Check that the `@font-face` declaration and `math { font-family: 'Latin Modern Math' … }`
  rule are present inside `extra.css`
- WeasyPrint resolves the font path relative to the CSS file; the path in
  `@font-face` should be `../fonts/latinmodern-math.otf`

### PDF sections missing or truncated
- Check `mkdocs.yml` nav — every entry must reference a file that exists
- Run `mkdocs build --verbose` and look for warnings in the output

### PDF diagrams missing text / showing "Mermaid diagram" alt text
- Clear the PNG cache and rebuild: `rm -rf docs/assets/mermaid/ && mkdocs build`
- Diagrams are rasterised by Chromium via mmdc — this should not occur if `npm install`
  completed successfully

### First build is slow
Normal — all diagrams are rendered via mmdc/Chromium on a cold cache. Subsequent builds
reuse cached PNGs and are much faster.

---

## 13. Versioning Policy

- Documentation versions track **structural changes**, not minor edits
- Processing logic changes should reference commit hashes or script versions

---

## 14. Support and Ownership

This repository is maintained by the CWRLab processing team.
Changes affecting automation or data provenance should be reviewed before merging.
