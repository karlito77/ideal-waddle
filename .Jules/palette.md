## 2023-11-02 - Ensure sticky header doesn't overlap anchor links
**Learning:** When implementing smooth scrolling and anchor links on pages with a sticky header, ensure the `scroll-margin-top` is large enough to account for the computed height of the sticky header (plus optional padding). Playwright's `getBoundingClientRect().height` is useful to verify this.
**Action:** Pair `html { scroll-behavior: smooth }` with `scroll-margin-top` on target sections, and always include a `@media (prefers-reduced-motion: reduce)` media query override.
