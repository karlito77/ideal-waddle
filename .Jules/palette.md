## 2026-11-03 - Smooth Scrolling with Sticky Headers
**Learning:** When using anchor links on a page with a tall sticky header, smooth scrolling is crucial for orientation, but the `scroll-margin-top` on target sections must be larger than the actual computed height of the sticky header to prevent content obscuration. Always verify the actual height (including padding) using bounding client rects.
**Action:** Pair `scroll-behavior: smooth` (with reduced motion overrides) and sufficient `scroll-margin-top` on all anchor targets.
