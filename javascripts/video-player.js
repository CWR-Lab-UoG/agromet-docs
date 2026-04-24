/**
 * Multi-part video playlist player
 *
 * Finds every element with class `.video-playlist` and builds a self-contained
 * player inside it. The video list is read from the element's `data-videos`
 * attribute (a JSON array of relative paths).
 *
 * Usage in Markdown:
 *
 *   <div class="video-playlist video-embed"
 *        data-videos='[
 *          "videos/tutorials/part_000.mp4",
 *          "videos/tutorials/part_001.mp4"
 *        ]'>
 *   </div>
 *   <div class="video-placeholder">
 *     📹 Video title — available in the online documentation.
 *   </div>
 *
 * Features:
 *   - Native browser controls handle seek, pause, volume, and fullscreen
 *     within the current part.
 *   - Prev / Next buttons allow jumping between parts without waiting for
 *     each segment to finish.
 *   - A part counter ("Part N of M") shows position in the playlist.
 *   - Auto-advances to the next part when a segment ends.
 *   - Playback starts only on explicit user interaction, respecting browser
 *     autoplay policies.
 *   - Single-video lists render without the navigation bar.
 *   - The `.video-embed` class on the container ensures the player is hidden
 *     in the PDF (WeasyPrint cannot render video elements).
 */
(function () {
  'use strict';

  // ── Styles ────────────────────────────────────────────────────────────────
  // Injected once; uses Material theme CSS variables where available so the
  // player adapts to light/dark mode automatically.
  function injectStyles() {
    if (document.getElementById('vp-styles')) return;

    const style = document.createElement('style');
    style.id = 'vp-styles';
    style.textContent = `
      .vp-container {
        width: 100%;
      }

      .vp-video {
        display: block;
        width: 100%;
        max-height: 70vh;
        background: #000;
        border-radius: 4px 4px 0 0;
      }

      /* Navigation bar — only shown when there is more than one part */
      .vp-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
        padding: 0.45rem 0.75rem;
        background: var(--md-code-bg-color, #f5f5f5);
        border: 1px solid var(--md-default-fg-color--lightest, #e0e0e0);
        border-top: none;
        border-radius: 0 0 4px 4px;
        font-size: 0.78rem;
        font-family: var(--md-text-font, inherit);
        color: var(--md-typeset-color, #333);
      }

      .vp-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.25rem 0.7rem;
        border: 1px solid var(--md-default-fg-color--light, #aaa);
        border-radius: 3px;
        background: var(--md-default-bg-color, #fff);
        color: var(--md-typeset-color, #333);
        font-size: 0.78rem;
        cursor: pointer;
        transition: background 0.15s, border-color 0.15s;
        white-space: nowrap;
      }

      .vp-btn:hover:not(:disabled) {
        background: var(--md-accent-fg-color--transparent,
                        var(--md-primary-fg-color--transparent, #e3f2fd));
        border-color: var(--md-accent-fg-color, var(--md-primary-fg-color, #1976d2));
      }

      .vp-btn:disabled {
        opacity: 0.35;
        cursor: default;
      }

      .vp-counter {
        flex: 1;
        text-align: center;
        font-variant-numeric: tabular-nums;
        color: var(--md-default-fg-color--light, #555);
      }

      .vp-counter strong {
        color: var(--md-typeset-color, #333);
      }
    `;
    document.head.appendChild(style);
  }

  // ── Player factory ────────────────────────────────────────────────────────
  function buildPlayer(container) {
    let videos;
    try {
      videos = JSON.parse(container.dataset.videos || '[]');
    } catch (e) {
      console.warn('[video-player] Invalid data-videos JSON on', container, e);
      return;
    }
    if (!videos.length) return;

    const multiPart = videos.length > 1;
    let current = 0;

    // ── Video element ───────────────────────────────────────────────────────
    const video = document.createElement('video');
    video.className  = 'vp-video';
    video.controls   = true;
    video.preload    = 'metadata';
    video.src        = videos[0];

    // ── Navigation bar (only for multi-part playlists) ──────────────────────
    let prevBtn, nextBtn, counter;

    function updateNav() {
      if (!multiPart) return;
      const n = current + 1;
      const m = videos.length;
      counter.innerHTML = `Part <strong>${n}</strong> of ${m}`;
      prevBtn.disabled = current === 0;
      nextBtn.disabled = current === m - 1;
    }

    function goTo(index, autoplay) {
      if (index < 0 || index >= videos.length) return;
      current = index;
      video.src = videos[current];
      updateNav();
      if (autoplay) {
        // play() returns a Promise; silence the rejection if autoplay is
        // blocked (e.g., on a fresh page load before any user gesture).
        const p = video.play();
        if (p && typeof p.catch === 'function') p.catch(() => {});
      }
    }

    // Auto-advance on segment end
    video.addEventListener('ended', () => {
      if (current < videos.length - 1) goTo(current + 1, true);
    });

    // ── Assemble DOM ────────────────────────────────────────────────────────
    // Replace the container's content rather than the container itself so
    // any surrounding classes (e.g. .video-embed for PDF hiding) are preserved.
    container.innerHTML = '';
    container.appendChild(video);

    if (multiPart) {
      prevBtn  = document.createElement('button');
      nextBtn  = document.createElement('button');
      counter  = document.createElement('span');

      prevBtn.type      = 'button';
      nextBtn.type      = 'button';
      prevBtn.className = 'vp-btn vp-prev';
      nextBtn.className = 'vp-btn vp-next';
      counter.className = 'vp-counter';

      prevBtn.innerHTML = '&#9664; Prev';
      nextBtn.innerHTML = 'Next &#9654;';

      prevBtn.addEventListener('click', () => goTo(current - 1, !video.paused));
      nextBtn.addEventListener('click', () => goTo(current + 1, !video.paused));

      const nav = document.createElement('div');
      nav.className = 'vp-nav';
      nav.appendChild(prevBtn);
      nav.appendChild(counter);
      nav.appendChild(nextBtn);
      container.appendChild(nav);

      updateNav();
    }
  }

  // ── Initialise all playlists on the page ──────────────────────────────────
  function init() {
    injectStyles();
    document.querySelectorAll('.video-playlist').forEach(buildPlayer);
  }

  document.addEventListener('DOMContentLoaded', init);
})();
