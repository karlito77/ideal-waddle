## 2026-11-05 - Dynamic Header Heights for Smooth Scrolling
**Learning:** When using sticky headers, `scroll-margin-top` on target sections must account for the computed height of the header at its maximum size (e.g. mobile viewports where elements wrap) rather than just the desktop height, otherwise anchor targets get obscured.
**Action:** Always measure sticky element bounding rects on both desktop and mobile viewports before setting `scroll-margin-top`.
