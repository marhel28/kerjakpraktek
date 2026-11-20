---
name: implementation
description: Plan-first, minimal-change coding with type-checking, linting, and regression prevention.
---

# Operational Skill: Implementation

## Workflow
```text
Understand Requirement
   ↓
Investigate Existing Implementation
   ↓
Create Plan (sketch in memory or as todo)
   ↓
Implement Smallest Working Diff
   ↓
TypeCheck (mypy / tsc / pyright)
   ↓
Lint (ruff / eslint)
   ↓
Run Related Tests
   ↓
Inspect Git Diff
   ↓
Verify Behavior
```

## Mandatory Practices
- **Reuse First**: Before creating new utility functions, classes, or helpers, search existing codebase for equivalent patterns.
- **Minimal Surface Area**: Prefer inline or locally-scoped helpers over global shared modules until reuse is proven.
- **Explicit Type Hints**: Python: `typing` module; TypeScript: strict `tsconfig` with no `any`.
- **No Dead Code**: Remove commented-out code, unused imports, unreachable branches.
- **Transaction Safety**: Backend DB operations wrapped in `async with session.begin():` or explicit `commit()` / `rollback()`.
- **Concurrency Awareness**: Use `asyncio` primitives; avoid shared mutable state across requests.