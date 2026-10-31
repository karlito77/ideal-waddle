## 2024-05-01 - Smooth Scrolling with Sticky Headers
**Learning:** When implementing smooth scrolling (`scroll-behavior: smooth`) for anchor links on a page with a sticky header, the `scroll-margin-top` on target sections must be equal to or greater than the exact computed height of the sticky header to prevent content from being obscured. Always test the offset with actual elements.
**Action:** Use Playwright's `getBoundingClientRect().height` to measure header height, pair `scroll-margin-top` with `scroll-behavior: smooth`, and always wrap in `prefers-reduced-motion: reduce` media query.
