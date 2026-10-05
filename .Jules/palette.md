## 2024-05-18 - Keyboard Focus Indicators for Stepper Links
**Learning:** Elements used for navigation or section jumping (like `.step` links) often lack sufficient focus indicators out-of-the-box. Without them, keyboard users cannot easily tell which step they are currently focusing on while tabbing through the document.
**Action:** Always verify keyboard focus visibility for custom navigation components and add `outline: 2px solid var(--accent)` using `:focus-visible` where it is missing, rather than relying solely on native browser defaults or hover states.
