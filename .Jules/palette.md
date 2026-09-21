## 2025-05-15 - Chart Tooltips Need Explicit Keyboard Focus
**Learning:** Custom SVG tooltips that use mouseenter/mousemove events leave keyboard users (and screen readers) blind to the data points.
**Action:** When creating custom chart tooltips, always add `tabindex="0"` to the interactive `.hit` elements and bind `focus`, `blur` and `keydown` (for Escape) events to display and hide the tooltip programmatically based on the element's bounding rectangle instead of mouse coordinates. Provide a `:focus-visible` outline for visual clarity.
