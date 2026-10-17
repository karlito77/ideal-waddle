## 2024-05-14 - Smooth scrolling with motion accessibility
**Learning:** When adding `scroll-behavior: smooth` to a page with a sticky header and anchor links, it's critical to respect user OS preferences for reduced motion by wrapping an override (`scroll-behavior: auto`) inside a `@media (prefers-reduced-motion: reduce)` block to prevent inducing nausea or dizziness for sensitive users.
**Action:** Always pair `scroll-behavior: smooth` with a `prefers-reduced-motion` override.
