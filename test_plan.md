1. **Explore codebase:**
   - Look for elements lacking keyboard accessibility or ARIA properties.
2. **Implement micro-UX improvement:**
   - Add focus-visible states to pipeline navigation links (`.step`) in `docs/demo.html` to improve keyboard navigation.
   - Make the charts' tooltips keyboard accessible by adding `tabindex="0"`, focus handlers to the SVG `.hit` areas, and `focus-visible` styling.
   - Add `aria-hidden="true"` to the decorative logo SVG.
3. **Verify changes:**
   - Ensure `docs/demo.html` renders without errors.
4. **Log learnings:**
   - Create and log findings in `.Jules/palette.md`.
5. **Pre-commit and submit:**
   - Complete pre-commit instructions, commit changes with a descriptive message, and submit.
