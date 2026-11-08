## 2026-11-08 - Dynamic Sticky Header Offset
**Learning:** Sticky headers that wrap text on smaller viewports can increase significantly in height (e.g. from 117px to 164px). Hardcoded `scroll-margin-top` values optimized for desktop will cause anchor targets to be obscured on mobile devices.
**Action:** Always compute the maximum possible height of sticky headers across all responsive breakpoints and set `scroll-margin-top` to accommodate the largest height, pairing it with smooth scrolling and `prefers-reduced-motion` support for accessibility.
