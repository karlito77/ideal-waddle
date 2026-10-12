## 2026-10-12 - Smooth scrolling navigation
**Learning:** Adding `scroll-behavior: smooth` directly to the `html` element vastly improves the experience of navigating through on-page anchor links (like steppers or table of contents). It pairs beautifully with `scroll-margin-top` for sticky headers. However, motion should always respect user preferences for accessibility.
**Action:** Always include a `@media (prefers-reduced-motion: reduce)` override to set `scroll-behavior: auto` when introducing smooth scrolling animations.
