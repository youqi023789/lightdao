# LightDAO Web Accessibility & Performance Audit (self-audit, 2026-09-26)

Scope: `/` (marketing landing), `/app.html` (mining dApp), `/explorer.html`, `/governance.html`.

## Accessibility (WCAG 2.1 AA-oriented)
- [x] `lang` attribute set and updated on language switch (landing + app).
- [x] Semantic landmarks: `header/nav/main-equivalent sections/footer`; heading hierarchy h1→h2→h3.
- [x] Skip-link to primary content (landing → #vision, app → #sec-main).
- [x] Visible focus indicator (`:focus-visible` ring) on all interactive elements.
- [x] `aria-label` on icon/ambiguous controls (language select).
- [x] Color contrast: body text #eef1f6 on #05060a (~17:1); muted #9aa3b2 on dark (~7:1) — pass AA.
- [x] `prefers-reduced-motion`: animations/parallax/canvas disabled (landing canvas gated, app media query).
- [x] Native accessible widgets used for disclosure (details/summary) and selects.
- [x] Touch targets >= 44px effective for primary CTAs.
- [ ] Known gap: full screen-reader flow test with NVDA/VoiceOver not run (no assistive tech in CI). Manual pass recommended.

## Performance
- [x] Single-file pages, no render-blocking external CSS; system font stack (no webfont download).
- [x] Heavy libs (cosmjs) loaded via dynamic `import()` only when needed (wallet/stats), not on first paint.
- [x] `preconnect` to CDN used by dynamic imports.
- [x] Service worker: network-first for HTML/JS shell (fresh deploys), cache-first for static media; offline fallback.
- [x] Canvas particle field capped (<=60 nodes) and skipped under reduced-motion.
- [x] Images: single OG card; no unoptimized raster in body.
- [ ] Known gap: no build-step minification (acceptable for current scale); consider at traffic growth.

## SEO / Share
- [x] title/description per page; canonical; hreflang x-default + 14 locales; per-locale landing pages with localized og:title/description/locale.
- [x] og:image brand card (1200x630-equivalent), og:locale:alternate list.
- [x] robots.txt + sitemap.xml; RSS feed at /rss.xml.
- [x] theme-color for mobile browser chrome.

## Security headers / files
- [x] /.well-known/security.txt + SECURITY.md (responsible disclosure, 90-day, bounty tiers).
- [ ] Known gap: CSP/HSTS not set at nginx (recommend adding when TLS cert auto-renew confirmed).

Verdict: ship-ready for current stage; two manual/infra gaps logged above.
