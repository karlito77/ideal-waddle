## 2024-05-18 - [Add Smooth Scrolling for Anchor Links]
**Learning:** Adding smooth scrolling greatly enhances the user experience when navigating a page with anchor links, like a step-by-step pipeline section. However, it requires an accessibility check via `prefers-reduced-motion` media query for users sensitive to motion.
**Action:** When adding smooth scrolling to a project, always include `@media (prefers-reduced-motion: reduce)` rule overriding it to `auto`.
