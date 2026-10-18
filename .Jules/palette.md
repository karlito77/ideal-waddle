## 2025-02-18 - Smooth Scrolling
**Learning:** When implementing smooth scrolling to anchor links on pages with a sticky header, pair `scroll-behavior: smooth` with `scroll-margin-top` on target sections to ensure the content isn't obscured. Always include a `prefers-reduced-motion: reduce` media query override to ensure accessibility for users who prefer less motion.
**Action:** Consistently apply `scroll-behavior: auto` inside a `@media (prefers-reduced-motion: reduce)` block alongside `scroll-behavior: smooth` on `html` tags, ensuring `scroll-margin-top` is set on anchor targets.
