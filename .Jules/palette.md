## 2024-10-16 - Smooth Scrolling to Anchors
**Learning:** When implementing smooth scrolling (`scroll-behavior: smooth`) on pages with anchor links and a sticky header, the combination with `scroll-margin-top` on target sections provides an optimal experience by preventing the sticky header from obscuring the content.
**Action:** Always combine `html { scroll-behavior: smooth }` with `scroll-margin-top` on the targeted elements if a sticky header is present. Ensure accessibility by overriding it with `@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }`.
