---
name: frontend
description: Production-grade Vue 3 & Nuxt 4 development, Tailwind CSS styling, Pinia state, and accessible responsive UX.
---

# Operational Skill: Frontend Development

## Tech Stack Standards
- **Framework**: Vue 3 `<script setup lang="ts">`, Nuxt 4 composition API.
- **Styling**: Tailwind CSS v4, adhering strictly to existing brand design tokens (`main.css`).
- **Typography**:
  - Headings, labels, badges, buttons: `Plus Jakarta Sans` (uppercase, tracking-wider).
  - Body, descriptions, inputs: `Open Sans`.
- **State Management**: Pinia stores with clear separation between local reactive state and persisted cookies/storage.

## Quality Standards
1. **Design System Adherence**: Always reuse existing UI components (`AmazonAuthCard`, `UIcon`, form elements) rather than creating ad-hoc div wrappers.
2. **Accessibility (WCAG AA)**:
   - Proper `aria-label`, `role="status"`, `aria-busy` on interactive elements.
   - Visible focus indicators (ring).
   - High text-to-background contrast ratio (>= 4.5:1).
3. **Reactivity Performance**:
   - Clean up event listeners in `onUnmounted` / `onBeforeUnmount`.
   - Prevent redundant watcher triggers or polling timers.
   - Handle loading, error, and empty states explicitly.
