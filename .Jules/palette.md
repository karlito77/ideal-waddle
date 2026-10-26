## 2026-10-26 - Sticky Header Offset
**Learning:** When using sticky headers with anchor links, ensure `scroll-margin-top` on target elements is larger than the header's computed height to prevent obscuring content. Pair `scroll-behavior: smooth` with `prefers-reduced-motion` media queries for accessibility.
**Action:** Use Playwright to check bounding client rect height to set appropriate scroll margins.
