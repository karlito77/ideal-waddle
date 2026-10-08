## 2024-05-24 - Safe Smooth Scrolling Implementation
**Learning:** When adding `scroll-behavior: smooth` to enable pleasant anchor navigation on pages with sticky headers, it's critical to respect accessibility preferences. Ensure you wrap the feature with a fallback like `html { scroll-behavior: auto; }` within a `@media (prefers-reduced-motion: reduce)` block to prevent motion sickness for sensitive users.
**Action:** Always include the `prefers-reduced-motion` override when introducing smooth scrolling globally.
