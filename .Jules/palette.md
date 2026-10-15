
## 2026-10-15 - [Anchor Link Smooth Scrolling]
**Learning:** When implementing smooth scrolling for anchor links to sections that have sticky headers, you must pair `scroll-behavior: smooth` with `scroll-margin-top` on the target sections. Furthermore, it is critical for accessibility to respect user preferences by resetting it with `html { scroll-behavior: auto; }` within a `@media (prefers-reduced-motion: reduce)` query.
**Action:** Always include a `prefers-reduced-motion: reduce` override when adding smooth scrolling to avoid motion sickness and maintain accessibility.
