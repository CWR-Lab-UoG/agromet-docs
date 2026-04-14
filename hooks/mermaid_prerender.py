from __future__ import annotations

"""MkDocs hook: pre-render Mermaid fenced blocks to PNG data-URI <img> tags.

Design rationale
----------------
PNG  — Mermaid v10+/v11 wraps node labels in <foreignObject> HTML.  WeasyPrint
  silently drops <foreignObject>, so all node text disappears in the PDF.
  mmdc rasterises through headless Chromium, which renders <foreignObject>
  correctly.  The resulting PNG contains the complete diagram.

data URI  — mkdocs-to-pdf combines every page into one HTML document before
  calling WeasyPrint.  Page-relative asset paths resolve against the site root
  in that combined document and miss the files.  Embedding as
  data:image/png;base64,… makes each diagram self-contained.

Resolution: PNG_WIDTH=820, PNG_SCALE=2 → 1640 px physical output.
  • Browser: 820 logical px at 2x = 1640px physical, displayed at 820px → 2:1 downscale → sharp.
  • PDF: ~320 DPI at 5 inches → good print quality.
  • Base64 size: ~30–100 KB per diagram.
    Keeping data URIs small prevents WeasyPrint from running out of memory
    when processing the combined multi-page PDF document.

PNG_WIDTH = 820  — Matches the CSS container max-width exactly.  When mmdc
  renders at 820 px with useMaxWidth: true, the SVG fills 820 px and every
  node is the same size as the browser shows for inline SVG at 820 px.
  This is the correct match: same viewport, same layout, same proportions.

Indentation preservation  — When a fenced block is indented (e.g., inside a
  pymdownx.details `???` block), the replacement <img> is written at the same
  indentation level so the enclosing admonition keeps its structure.

Cache
-----
PNGs are keyed by sha1(diagram_code + CONFIG_HASH).  Changing _RENDER_CFG
produces a new CONFIG_HASH → new filenames → stale PNGs ignored automatically.

    rm -rf docs/assets/mermaid/    ← clear disk cache

Usage
-----
    mkdocs serve
    mkdocs build
"""

import base64
import hashlib
import json
import os
import shutil
import subprocess
import textwrap
from pathlib import Path
from typing import List, Optional

MERMAID_VERSION = "11.12.0"
FENCE_START = "```mermaid"
FENCE_END   = "```"

PNG_WIDTH = 820    # logical px — matches CSS .mermaid-svg-wrap max-width exactly
PNG_SCALE = 2      # device pixel ratio → 820×2 = 1640 px physical, 2:1 downscale at 820px

_RENDER_CFG: dict = {
    "flowchart": {"useMaxWidth": True},    # fill the viewport — same as browser SVG rendering
    "gitGraph":  {"mainBranchName": "main"},
    "securityLevel": "loose",
    "theme":     "default",
}

CONFIG_HASH: str = hashlib.sha1(
    json.dumps(_RENDER_CFG, sort_keys=True).encode()
).hexdigest()[:8]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cache_hash(code: str) -> str:
    return hashlib.sha1((code + "\x00" + CONFIG_HASH).encode()).hexdigest()


def _find_mmdc(project_root: Path) -> List[str]:
    bin_dir = project_root / "node_modules" / ".bin"
    if os.name == "nt":
        local = bin_dir / "mmdc.cmd"
        if local.exists():
            return [str(local)]
    local = bin_dir / "mmdc"
    if local.exists():
        return [str(local)]
    found = shutil.which("mmdc")
    if found:
        return [found]
    return ["npx", "-y", f"@mermaid-js/mermaid-cli@{MERMAID_VERSION}"]


def _find_puppeteer_config(project_root: Path) -> Optional[Path]:
    """Return the Puppeteer config path if present, otherwise None.

    puppeteer.config.json lives at the project root alongside package.json.
    It supplies --no-sandbox flags required on GitHub Actions and other Linux
    sandbox-restricted environments.  Its absence is not an error — mmdc falls
    back to its default Puppeteer settings, which works on local dev machines.

    The file MUST be valid JSON.  mmdc passes it to JSON.parse() directly, so
    a .cjs / .js module with comments will raise a SyntaxError at render time.
    """
    p = project_root / "puppeteer.config.json"
    return p if p.exists() else None


def _ensure_config(out_dir: Path) -> Path:
    cfg = out_dir / "mermaid-render-config.json"
    cfg.write_text(json.dumps(_RENDER_CFG, indent=2), encoding="utf-8")
    return cfg


def _render_png(code: str, png_path: Path, out_dir: Path, project_root: Path) -> bool:
    src = out_dir / f"{png_path.stem}.mmd"
    cfg = _ensure_config(out_dir)
    src.write_text(code, encoding="utf-8")
    cmd = _find_mmdc(project_root)

    mmdc_args = cmd + [
        "-i", str(src),
        "-o", str(png_path),
        "--configFile",      str(cfg),
        "--backgroundColor", "white",
        "--width",           str(PNG_WIDTH),
        "--scale",           str(PNG_SCALE),
    ]

    # Pass Puppeteer config when present.  Required on GitHub Actions and other
    # Linux environments that restrict the Chromium sandbox; harmless elsewhere.
    puppeteer_cfg = _find_puppeteer_config(project_root)
    if puppeteer_cfg:
        mmdc_args += ["--puppeteerConfigFile", str(puppeteer_cfg)]

    try:
        subprocess.run(
            mmdc_args,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return png_path.exists() and png_path.stat().st_size > 0
    except Exception as e:
        print("[mermaid_prerender] mmdc failed:")
        print(getattr(e, "stderr", None) or str(e))
        return False
    finally:
        try:
            src.unlink()
        except FileNotFoundError:
            pass


def _choose_png(code: str, h: str, out_dir: Path, project_root: Path) -> Optional[Path]:
    png = out_dir / f"{h}.png"
    if png.exists():
        return png
    if _render_png(code, png, out_dir, project_root):
        return png
    return None


def _png_data_uri(png_path: Path) -> str:
    b64 = base64.b64encode(png_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


# ---------------------------------------------------------------------------
# MkDocs hook
# ---------------------------------------------------------------------------

def on_page_markdown(markdown: str, page, config, files) -> str:
    docs_dir    = Path(config["docs_dir"])
    project_root = docs_dir.parent
    out_dir     = docs_dir / "assets" / "mermaid"
    out_dir.mkdir(parents=True, exist_ok=True)

    lines = markdown.splitlines()
    out: List[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.strip() != FENCE_START:
            out.append(line)
            i += 1
            continue

        # Record indentation of the opening fence so the replacement HTML
        # stays at the same level (important for content inside ??? blocks).
        indent = len(line) - len(line.lstrip())
        pad    = " " * indent

        diagram: List[str] = []
        i += 1
        while i < len(lines) and lines[i].strip() != FENCE_END:
            diagram.append(lines[i])
            i += 1

        # Dedent the code so mmdc always receives clean, left-aligned source.
        code = textwrap.dedent("\n".join(diagram)).strip()

        if not code:
            out.append(f"{pad}<p><em>Empty Mermaid diagram block.</em></p>")
            i += 1
            continue

        h       = _cache_hash(code)
        png_path = _choose_png(code, h, out_dir, project_root)

        if png_path is None:
            msg = (
                "Mermaid diagram could not be rendered. "
                "Ensure Mermaid CLI is installed (npm install) and "
                "a headless Chromium runtime is available."
            )
            out.append(
                f'{pad}<div class="admonition warning mermaid-render-error">'
                f'<p class="admonition-title">Mermaid render failed</p>'
                f"<p>{msg}</p>"
                f"</div>"
            )
            i += 1
            continue

        uri = _png_data_uri(png_path)
        out.append(
            f'{pad}<div class="mermaid-svg-wrap">'
            f'<img src="{uri}" class="mermaid-svg" alt="Mermaid diagram" />'
            f'</div>'
        )
        i += 1

    return "\n".join(out)
