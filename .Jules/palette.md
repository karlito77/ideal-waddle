## 2026-11-12 - Smooth Scrolling with Sticky Headers
**Learning:** When using scroll-behavior: smooth on pages with a sticky header, ensure the scroll-margin-top on anchor targets accounts for the computed maximum height of the sticky header on smaller viewports where elements wrap.
**Action:** Always measure sticky header heights on mobile viewports and set a responsive scroll-margin-top to prevent obscured sections. Always include a prefers-reduced-motion media query for accessibility.
