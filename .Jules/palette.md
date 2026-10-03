
## 2024-05-24 - Smooth scrolling and keyboard focus state on pipeline navigation
**Learning:** The pipeline navigation relies on hash-links to scroll between sections but lacked `scroll-behavior: smooth`, making navigation sudden and jarring, and the links themselves lacked explicit `focus-visible` styles, making keyboard navigation hard to track. The branding SVG was also missing `aria-hidden="true"`.
**Action:** Always verify `scroll-behavior: smooth` is applied when using anchor links for navigation (behind a `prefers-reduced-motion` media query). Ensure structural/decorative SVGs have `aria-hidden="true"` and custom focus states are added to interactive components that override or obscure default browser outlines.
