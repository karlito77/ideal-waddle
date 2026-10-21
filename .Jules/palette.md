## 2025-02-18 - Smooth scrolling with sticky headers
**Learning:** When adding `scroll-behavior: smooth` to a page with a sticky header, anchor links will cause the target section's top to be obscured by the header unless `scroll-margin-top` is set.
**Action:** Pair smooth scrolling with `scroll-margin-top` on target sections, and ensure `prefers-reduced-motion: reduce` is added for a11y.
