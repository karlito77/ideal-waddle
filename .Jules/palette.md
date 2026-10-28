## 2026-10-28 - Sticky Header Anchor Overlap
**Learning:** When using fixed or sticky headers, target sections must use `scroll-margin-top` matching the maximum computed height of the header across breakpoints to prevent overlapping content. Smooth scrolling should always be paired with a `prefers-reduced-motion` override for accessibility.
**Action:** Verify header height on mobile breakpoints and ensure `html` element handles smooth scrolling with an accessibility override.
