
## 2025-02-12 - Sticky header obscuring anchor links
**Learning:** When using scroll-behavior: smooth with anchor links, scroll-margin-top must account for the actual computed height of the sticky header, which can vary by viewport width due to wrapping flex items.
**Action:** Use Playwright's getBoundingClientRect to verify the max possible header height at different breakpoints.
