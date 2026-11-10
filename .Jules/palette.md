## 2024-11-10 - Smooth Scrolling with Sticky Headers
**Learning:** When adding smooth scrolling to a page with a sticky header, `scroll-margin-top` on target elements needs to account for the computed height of the header at its maximum size to prevent targets from being obscured. Always test the header height using `bounding_box()["height"]`.
**Action:** Verify sticky header height programmatically before setting `scroll-margin-top`.
