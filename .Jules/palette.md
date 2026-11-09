## 2026-11-09 - Smooth scrolling with wrapping sticky headers
**Learning:** When using scroll-behavior: smooth with scroll-margin-top to account for sticky headers, the scroll-margin-top value needs to account for the header's maximum height, which can increase significantly on mobile devices when flex items wrap.
**Action:** Always check the computed height of sticky headers on small viewports and adjust scroll-margin-top in a media query accordingly.
