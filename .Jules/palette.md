## 2025-02-18 - [SVG Chart Accessibility]
**Learning:** Raw SVG charts embedded in HTML lack accessibility. Screen readers ignore them, and keyboard-only users cannot access tooltips triggered by mouse movement over SVG rects/circles.
**Action:** When manually writing SVG charts, attach `tabindex="0"`, `role="graphics-symbol"`, and an `aria-label` directly to the "hit area" shapes (`.hit`). Wire `focus`/`blur` events to display the same tooltip logic used for `mouseenter`, and provide CSS `:focus-visible` styling (e.g., thicker stroke) to show keyboard users which element is active.
