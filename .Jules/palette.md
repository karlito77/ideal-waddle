## 2026-10-27 - [Sticky Headers & Anchor Links]
**Learning:** When using sticky headers, anchor links will cause the browser to scroll content underneath the header, obscuring the section title.
**Action:** Always set `scroll-margin-top` on target sections to a value larger than the sticky header's height (e.g., 140px for a 117px header), and pair it with `scroll-behavior: smooth` (wrapped in `prefers-reduced-motion: reduce` media query) for better UX.
