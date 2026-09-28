## 2025-10-24 - Smooth scrolling and prefers-reduced-motion
**Learning:** Using `scroll-behavior: smooth` is an elegant way to improve UX for in-page navigation (like a pipeline stepper anchoring to sections), but it can trigger motion sickness for users who prefer reduced motion. We must remember to disable it for accessibility.
**Action:** Always pair `html { scroll-behavior: smooth }` with a corresponding `@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto } }` fallback block when implementing smooth scroll.
