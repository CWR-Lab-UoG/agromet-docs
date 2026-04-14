from __future__ import annotations

"""MkDocs hook: pre-render LaTeX math to MathML for PDF output.

Problem
-------
pymdownx.arithmatex (generic: true) wraps every LaTeX expression in
<span class="arithmatex">\\(...\\)</span> (inline) or
<div  class="arithmatex">\\[...\\]</div> (display).
MathJax processes these in the browser — but WeasyPrint (used by mkdocs-to-pdf)
renders the HTML without executing JavaScript, so raw LaTeX appears in the PDF.

Solution
--------
This hook adds a companion MathML element alongside every arithmatex block:

    <span class="arithmatex">\\(E = mc^2\\)</span>       ← browser: MathJax renders this
    <span class="math-mathml">                             ← PDF: WeasyPrint renders this
      <math ...>...</math>
    </span>

CSS (in mermaid-svg.css) hides .math-mathml in the browser and hides .arithmatex
in print, so each medium sees the correct rendering.

If latex2mathml fails for an equation (unsupported command), the original
arithmatex element is left unchanged and a warning is printed.  The PDF will
show raw LaTeX for that equation, but it will not break.

Dependency
----------
    pip install latex2mathml
(listed in requirements.txt)
"""

import re
from typing import Optional

try:
    from latex2mathml import converter as _l2m
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    print(
        "[math_prerender] WARNING: latex2mathml is not installed.\n"
        "  Run:  pip install latex2mathml\n"
        "  Math equations will show as raw LaTeX in the PDF until it is installed."
    )

# ── Regex patterns ───────────────────────────────────────────────────────────
# pymdownx.arithmatex with generic:true produces exactly these patterns.

# Inline:  \(...\)  inside  <span class="arithmatex">
_INLINE_RE = re.compile(
    r'<span\s+class="arithmatex">\\\((.+?)\\\)</span>',
    re.DOTALL,
)

# Display: \[...\]  inside  <div class="arithmatex">
_DISPLAY_RE = re.compile(
    r'<div\s+class="arithmatex">\s*\\\[(.+?)\\\]\s*</div>',
    re.DOTALL,
)


# ── Unicode Mathematical Italic substitution ─────────────────────────────────
#
# latex2mathml produces <mi>K</mi>, <mi>z</mi>, <mi>κ</mi>, etc. using plain
# ASCII / standard Unicode characters.  In proper math typesetting (LaTeX,
# MathJax, MathML spec) single-letter identifiers are displayed in *math
# italic* — a specifically designed style, not a geometric slant of upright
# glyphs.  The Unicode Standard encodes the full math italic alphabet in the
# Mathematical Alphanumeric Symbols block (U+1D400–U+1D7FF) and the Latin
# Modern Math OpenType font ships with every one of these glyphs.
#
# Replacing the plain character inside <mi> with the corresponding math-italic
# code point lets the PDF renderer (WeasyPrint) pick the correct designed glyph
# directly, without any CSS font-style trick.  Multi-letter <mi> elements (like
# "ln", "sin") are intentionally left unchanged — they represent function names
# and should remain upright per the MathML spec.
#
# Mappings
# --------
#   Latin uppercase  A–Z  →  U+1D434–U+1D44D
#   Latin lowercase  a–z  →  U+1D44E–U+1D467  (h → U+210E ℎ, no gap otherwise)
#   Greek uppercase       →  U+1D6E2–U+1D6FA  (order follows the math block,
#                                              which inserts ϴ between Ρ and Σ)
#   Greek lowercase       →  U+1D6FC–U+1D714

def _build_italic_map() -> dict[str, str]:
    m: dict[str, str] = {}

    # Latin uppercase A–Z
    for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        m[c] = chr(0x1D434 + i)

    # Latin lowercase a–z  (h is the lone exception)
    for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"):
        m[c] = chr(0x210E if c == "h" else 0x1D44E + i)

    # Greek LOWERCASE only → U+1D6FC–U+1D714
    # (contiguous in both the standard Unicode Greek block and the math-italic block)
    #
    # Greek UPPERCASE is intentionally omitted.  In standard LaTeX math,
    # uppercase Greek letters (Δ, Λ, Σ, Ω …) are rendered upright — they
    # are used as named operators and constants, not italic variables.
    # Applying the italic substitution to them would diverge from LaTeX
    # convention (e.g. Δz for a difference should stay Δ, not 𝛥).
    for i, c in enumerate("αβγδεζηθικλμνξοπρςστυφχψω"):
        m[c] = chr(0x1D6FC + i)

    return m


_ITALIC_MAP: dict[str, str] = _build_italic_map()

# Matches a single-character <mi> element (the char may be multi-byte Unicode)
_MI_SINGLE_RE = re.compile(r"<mi>(.)</mi>")


def _italicize_mi(mml: str) -> str:
    """Replace single-char <mi> content with the Unicode math-italic glyph.

    latex2mathml encodes non-ASCII characters as HTML entities (e.g. κ →
    &#x003BA;).  This function normalises those to plain Unicode first so the
    character lookup works for Greek letters and other symbols, then applies
    the italic substitution.  Multi-character <mi> elements (function names
    like 'ln', 'sin') are left untouched — they should render upright per the
    MathML specification.
    """
    import html as _html

    def _sub(match: re.Match) -> str:
        # Decode any HTML entities (&#x003BA; → κ, &alpha; → α, etc.)
        raw = _html.unescape(match.group(1))
        if len(raw) != 1:
            return match.group(0)   # multi-char after decoding → function name, skip
        italic = _ITALIC_MAP.get(raw)
        return f"<mi>{italic}</mi>" if italic else match.group(0)

    # The entity pattern may span more than one character in the source string
    # (e.g. "&#x003BA;" is 9 chars), so we need a broader match than `.`
    mi_re = re.compile(r"<mi>([^<]+)</mi>")
    return mi_re.sub(_sub, mml)


# ── LaTeX → MathML conversion ────────────────────────────────────────────────

def _convert(latex: str, display: bool) -> Optional[str]:
    """Return MathML string for *latex*, or None on failure."""
    if not _AVAILABLE:
        return None
    try:
        # pymdownx.arithmatex HTML-escapes special characters in the LaTeX
        # source before our hook sees it (e.g. < → &lt;, > → &gt;, & → &amp;).
        # latex2mathml does not understand HTML entities, so it decomposes
        # &lt; into the individual characters &, l, t, ; rather than treating
        # it as the < operator.  Decode entities back to plain LaTeX first.
        import html as _html
        latex_clean = _html.unescape(latex.strip())
        mml = _l2m.convert(latex_clean, display="block" if display else "inline")
        return _italicize_mi(mml)
    except Exception as exc:
        snippet = latex.strip().replace("\n", " ")[:70]
        print(f"[math_prerender] LaTeX→MathML failed for {snippet!r}: {exc}")
        return None


def _replace_inline(m: re.Match) -> str:
    latex = m.group(1)
    mml = _convert(latex, display=False)
    if mml is None:
        return m.group(0)          # leave unchanged — MathJax still works in browser
    return (
        m.group(0)                 # original arithmatex (browser)
        + f'<span class="math-mathml math-mathml-inline">{mml}</span>'
    )


def _replace_display(m: re.Match) -> str:
    latex = m.group(1)
    mml = _convert(latex, display=True)
    if mml is None:
        return m.group(0)
    return (
        m.group(0)
        + f'<div class="math-mathml math-mathml-block">{mml}</div>'
    )


# ── MkDocs hook ──────────────────────────────────────────────────────────────

def on_page_content(html: str, page, config, files) -> str:
    """Called after Markdown → HTML conversion, before theme template is applied."""
    if not _AVAILABLE:
        return html
    html = _INLINE_RE.sub(_replace_inline, html)
    html = _DISPLAY_RE.sub(_replace_display, html)
    return html
