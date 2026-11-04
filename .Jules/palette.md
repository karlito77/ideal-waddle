## 2026-11-04 - Sticky Header Anchor Navigation
**Learning:** Implementing anchor navigation with sticky headers requires matching 'scroll-margin-top' to the header's height (which often changes responsively). Without it, target sections get obscured.
**Action:** Always measure sticky header heights with Playwright/tools across viewports, adjust 'scroll-margin-top' via media queries, and explicitly include 'prefers-reduced-motion: reduce' to reset 'scroll-behavior: auto' when introducing smooth scrolling.
