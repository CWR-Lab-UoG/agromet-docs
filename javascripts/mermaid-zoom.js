/**
 * Mermaid SVG zoom overlay (no GLightbox dependency)
 *
 * Click a Mermaid diagram to open it in a full-screen overlay.
 * - Mouse wheel: zoom in/out
 * - Click-and-drag: pan
 * - Double click: reset
 * - Esc or click outside: close
 */
(function () {
  window.__MERMAID_ZOOM_LOADED__ = true;

  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

  let overlay, stage, img;
  let scale = 1;
  let panX = 0, panY = 0;
  let dragging = false;
  let lastX = 0, lastY = 0;

  function ensureOverlay() {
    if (overlay) return;

    overlay = document.createElement('div');
    overlay.id = 'mermaid-zoom-overlay';
    overlay.innerHTML = `
      <div class="mzo-backdrop" tabindex="-1"></div>
      <div class="mzo-stage" role="dialog" aria-modal="true">
        <button class="mzo-close" aria-label="Close">×</button>
        <img class="mzo-img" alt="Diagram">
        <div class="mzo-hint">Wheel to zoom • Drag to pan • Double‑click to reset • Esc to close</div>
      </div>
    `;
    document.body.appendChild(overlay);

    stage = overlay.querySelector('.mzo-stage');
    img = overlay.querySelector('.mzo-img');

    const closeBtn = overlay.querySelector('.mzo-close');
    const backdrop = overlay.querySelector('.mzo-backdrop');

    closeBtn.addEventListener('click', close);
    backdrop.addEventListener('click', close);

    // wheel zoom
    stage.addEventListener('wheel', (e) => {
      e.preventDefault();
      const dir = Math.sign(e.deltaY);
      scale *= (dir > 0 ? 0.9 : 1.1);
      scale = clamp(scale, 0.2, 20);
      applyTransform();
    }, { passive: false });

    // drag to pan
    stage.addEventListener('mousedown', (e) => {
      // don't start dragging when clicking close button or hint
      if (e.target.closest('.mzo-close') || e.target.closest('.mzo-hint')) return;
      dragging = true;
      lastX = e.clientX;
      lastY = e.clientY;
      stage.classList.add('mzo-dragging');
    });
    window.addEventListener('mousemove', (e) => {
      if (!dragging) return;
      panX += (e.clientX - lastX);
      panY += (e.clientY - lastY);
      lastX = e.clientX;
      lastY = e.clientY;
      applyTransform();
    });
    window.addEventListener('mouseup', () => {
      dragging = false;
      stage.classList.remove('mzo-dragging');
    });

    // double click reset
    stage.addEventListener('dblclick', () => {
      scale = 1;
      panX = 0;
      panY = 0;
      applyTransform();
    });

    // esc close
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && overlay.classList.contains('is-open')) close();
    });
  }

  function applyTransform() {
    img.style.transform = `translate(-50%, -50%) translate(${panX}px, ${panY}px) scale(${scale})`;
  }

  function open(src) {
    ensureOverlay();
    img.src = src;

    // Reset zoom & pan so the diagram opens centered every time
    scale = 1;
    panX = 0;
    panY = 0;

    // Force centering on open (avoid corner placement)
    img.style.left = '50%';
    img.style.top = '50%';
    img.style.transform = 'translate(-50%, -50%) translate(0px, 0px) scale(1)';

    img.onload = () => applyTransform();
    overlay.classList.add('is-open');
    document.documentElement.classList.add('mzo-noscroll');
  }

  function close() {
    if (!overlay) return;
    overlay.classList.remove('is-open');
    document.documentElement.classList.remove('mzo-noscroll');
  }
  function onClickDiagram(e) {
    // Diagrams are <img class="mermaid-svg" src="data:image/svg+xml;base64,...">
    // Click anywhere on the image to open it in the zoom overlay.
    const imgEl = e.target.closest('img.mermaid-svg');
    if (!imgEl) return;

    e.preventDefault();
    e.stopPropagation();
    open(imgEl.getAttribute('src'));   // src is a self-contained data URI
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('click', onClickDiagram, true);
  });
})();