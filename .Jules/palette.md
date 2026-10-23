## 2026-10-23 - Sticky Header Scroll Offset Adjustment
**Learning:** Hardcoded scroll-margin-top (72px) failed to account for variable sticky header heights on mobile breakpoints (164px), causing anchor links to obscure content behind the header.
**Action:** Replaced static 72px with 180px and paired with smooth scrolling to provide better anchor link navigation context while always verifying header dimensions dynamically across breakpoints.
