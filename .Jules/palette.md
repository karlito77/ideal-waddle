## 2026-11-11 - Sticky Header Scroll Offset
**Learning:** When using sticky headers with anchor links, the 'scroll-margin-top' value needs to account for the header's maximum height, which often occurs on mobile viewports where header contents wrap and stack, exceeding its desktop height.
**Action:** Use Playwright to check the bounding client height of the header at small viewports (e.g., 320px width) before setting 'scroll-margin-top'.
