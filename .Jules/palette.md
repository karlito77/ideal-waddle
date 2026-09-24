## 2024-05-15 - role="listitem" on button semantics

**Learning:** When using `role="listitem"` on a `<button>` element, it overrides the semantic meaning of the button for screen readers. The screen reader will announce it as a list item instead of a button, hiding its interactive capability.

**Action:** When a button is logically part of a list (like in a step tracker), ensure the list semantics are handled by the container (e.g. using `<nav>`), and let the `<button>` retain its default semantics without an overriding `role`.
