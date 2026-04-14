# Project Overview

## Purpose

This repository hosts the **CWR Lab EC/FG Processing & Documentation System**, a
reproducible, implementation-focused documentation and processing framework for
**Eddy Covariance (EC)** and **Flux-Gradient (FG)** data workflows developed by the
Wagner-Riddle research group at the University of Guelph.

The primary goal is to:

- Document *how the system actually runs in production*
- Support long-term maintenance and onboarding
- Minimize duplication and conceptual drift

This is **not** a theory textbook. It is a practical reference for users and maintainers
working with real data and automation.

---

## Scope

### Included

- End-to-end EC and FG processing workflows
- Automation orchestration (Task Scheduler → BAT → Python → MATLAB)
- MATLAB-driven FG processing (db_* scripts)
- Interfaces to external tools (EddyPro, REddyProc)
- Data products, QA/QC, archiving, and publication
- MkDocs-based documentation system

### Explicitly Excluded

- Detailed micrometeorological theory (see references)
- Instrument manufacturer manuals (linked, not duplicated)
- Generic tutorials unrelated to this system

---

## System Architecture

The system is structured around **daily automated processing** driven by Windows Task
Scheduler. Each task invokes scripts that operate on time-segmented data products.

High-level layers:

1. **Raw data acquisition** — EC: 10 Hz raw system files; FG: TGA / ancillary system files
2. **Half-hour segmentation** (MATLAB `db_split_hhour`)
3. **Primary processing** — EC: EddyPro → REddyProc; FG: MATLAB db_* pipeline
4. **Diagnostics and QA/QC**
5. **Standardised outputs** (vectors, NetCDF)
6. **Archiving and publication**

---

## Flux-Gradient Processing System

The FG system measures **N₂O and CO₂** fluxes using the flux-gradient (aerodynamic
gradient) method, implemented entirely in MATLAB. Key implementation details:

### Physical Constants and Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| von Kármán constant κ | 0.40 | Standard |
| Gravity g | 9.81 m s⁻² | Appropriate for Guelph (~43.5 °N) |
| Displacement height | d = 0.67 × h_c | Standard agricultural value |
| Roughness length | z₀ = 0.13 × h_c | Site-calibrated for Guelph crops |
| Valid stability range | −5 ≤ ζ ≤ 2 | Outside → K = NaN |

### Stability Functions

The pipeline uses Businger-Dyer stability functions with **coefficient 15**:

- Stable: φ_h = 1 + 4.7ζ, ψ_h = −4.7ζ
- Unstable: φ_h = (1 − 15ζ)^−0.5, ψ_h = 2 ln((1 + x²)/2), x = (1 − 15ζ)^0.25
- Neutral (|ζ| ≤ 0.01): φ_h = ψ_h = 0

### Friction Velocity and Coordinate Rotation

Friction velocity is derived from 3-D sonic anemometer covariances:
u* = (u'w'² + v'w'²)^(1/4). Double coordinate rotation is applied in
`db_process_hhour_sonic` before computing turbulent statistics.

### TGA Measurement Cycle

- **Level duration:** 60 seconds per intake
- **Omit period:** 10–15 seconds at level start (configurable per plot)
- **Tube delay:** 2–6 seconds, estimated by sine-curve fitting to CO₂ nighttime signal
- **Supported gases:** N₂O and CO₂
- **Output units:** ng N₂O-N m⁻² s⁻¹; µg CO₂ m⁻² s⁻¹

### Output Products

The MATLAB pipeline produces, for each site and date:

- Half-hour MATLAB `.mat` structure files
- ASCII vector time series files
- Flux calculation tables (N₂O and CO₂)
- TGA diagnostic plots

### Key References

- Brown, S.E., Wagner-Riddle, C., & Conrad, B. (2024). Low-power flux gradient
  measurements for quantifying the impact of agricultural management on nitrous oxide
  emissions. *Agricultural and Forest Meteorology*, 353, 110027.
- Businger, J.A., et al. (1971). Flux-profile relationships in the atmospheric surface
  layer. *Journal of Atmospheric Sciences*, 28, 181–189.
- Wagner-Riddle, C., et al. (2017). Globally important nitrous oxide emissions from
  croplands induced by freeze–thaw cycles. *Nature Geoscience*, 10(4), 279–283.

---

## Documentation Philosophy

### 1. One canonical overview

High-level workflows are defined once and referenced everywhere else. Product pages do
not repeat them.

### 2. Implementation-first

Documentation reflects actual scripts, real file paths, and real automation order.
If something is not implemented, it should not be documented as if it were.

### 3. Separation of concerns

- **Workflow pages**: orchestration and sequencing
- **Pipeline pages**: detailed processing steps
- **Setup docs**: how to build, run, and maintain the system

---

## Target Audience

**Primary**: Project maintainers, developers modifying scripts or workflows, power users
adding new sites or instruments.

**Secondary**: Collaborators needing to understand data provenance, reviewers and auditors.

---

## Repository Structure

- `docs/` — MkDocs source (authoritative documentation)
  - `fonts/` — Bundled OpenType fonts used by the PDF renderer:
    - `latinmodern-math.otf` — Latin Modern Math, the OpenType successor to Computer
      Modern Math (same font LaTeX uses); embedded in the PDF for correct math typography
- `hooks/` — Build-time hooks:
  - `mermaid_prerender.py` — renders Mermaid diagrams to PNG data URIs at build time
  - `math_prerender.py` — converts LaTeX equations to MathML companions for PDF output,
    including Unicode math-italic substitution for correct variable typography
- `.github/workflows/deploy.yml` — GitHub Actions workflow; builds and publishes to
  GitHub Pages on every push to `main`
- `puppeteer.config.json` — Puppeteer launch flags for mmdc; supplies `--no-sandbox`
  for GitHub Actions runners. Must be valid JSON (mmdc calls `JSON.parse()` on it)
- `scripts/` — Automation helpers (BAT / Python)
- `MATLAB/` — FG and preprocessing scripts
- `site/` — Generated documentation output (not authoritative; not committed)

---

## Documentation Build System

### Mermaid diagrams

All Mermaid diagrams are **pre-rendered at build time** to PNG by `hooks/mermaid_prerender.py`.
The hook uses `mmdc` (Mermaid CLI / headless Chromium) to rasterise each diagram at
**1640 px physical** (820 logical × 2× DPR). Each PNG is base64-encoded and embedded as a
`data:image/png;base64,…` URI so all diagrams render correctly in both browser and PDF
without any external file dependencies.

### Math equations — browser and PDF

A **three-layer strategy** ensures equations render correctly in both contexts and
match the typographic quality of a LaTeX document:

| Context | Mechanism |
|---------|-----------|
| **Browser** | MathJax (self-hosted, `docs/javascripts/vendor/mathjax/`) renders `arithmatex` spans via JavaScript |
| **PDF structure** | `hooks/math_prerender.py` converts each LaTeX expression to MathML using `latex2mathml` and inserts it as a companion `.math-mathml` element; `@media print` CSS hides the raw LaTeX and shows the MathML |
| **PDF typography** | Latin Modern Math (`docs/fonts/latinmodern-math.otf`) is declared as the math font in print CSS; `math_prerender.py` substitutes single-letter `<mi>` characters with their Unicode Mathematical Italic equivalents so glyphs match LaTeX output exactly |

**WeasyPrint MathML layout** — WeasyPrint (the PDF backend) parses MathML but does
not implement the MathML layout algorithm; without intervention `<mfrac>` fractions
render as flat inline text. Explicit CSS `display` rules for every MathML element
(using `inline-table` / `table-row` for fractions, `vertical-align` for scripts)
in `docs/stylesheets/extra.css` resolve this.

**Unicode math italic** — `math_prerender.py` maps each single-letter `<mi>` character
to its Unicode Mathematical Italic code point (e.g. `z` → `𝑧` U+1D467, `κ` → `𝜅`
U+1D705) so Latin Modern Math renders designed italic glyphs, not a synthetic slant.
Greek uppercase letters (Δ, Σ …) are intentionally kept upright, matching LaTeX
convention.

The `mathjax.js` configuration file **must be listed before** the MathJax library
in `mkdocs.yml` — MathJax reads its config at startup.

### No external CDN dependencies

All runtime JavaScript, CSS, and font assets are self-hosted.

---

## Long-Term Vision

- **Stable**: minimal churn in core workflows
- **Traceable**: clear provenance from raw data to products
- **Portable**: runnable locally, on GitHub Pages, or Cloudflare Pages
- **Maintainable**: explicit design decisions documented
