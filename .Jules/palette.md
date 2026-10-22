## 2024-10-23 - Smooth Scrolling and Sticky Headers
**Learning:** When using anchor link navigation on pages with a sticky header, the default jump obscures the top of the linked section because it aligns the top of the viewport with the top of the section, ignoring the sticky header.
**Action:** Pair `scroll-behavior: smooth` with `scroll-margin-top` on target sections. Verify the actual computed height of the sticky header (including padding) at various breakpoints to set the `scroll-margin-top` correctly, preventing content from being obscured.
