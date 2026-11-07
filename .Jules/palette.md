## 2026-11-07 - [Sticky Headers & Anchor Scrolling]
**Learning:** Sticky header heights can increase significantly on mobile viewports due to wrapping. Setting a fixed `scroll-margin-top` without testing max header height across viewports leads to obscured anchor targets.
**Action:** Always verify max computed header height (e.g., using Playwright on mobile viewports) and ensure `scroll-margin-top` accommodates this worst-case scenario, while pairing it with smooth scrolling and reduced-motion fallbacks.
