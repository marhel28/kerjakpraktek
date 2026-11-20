---
name: refactoring
description: Incremental structural improvements with zero behavioral regressions.
---

# Operational Skill: Refactoring

## Rules
**DO NOT REWRITE WORKING CODE WITHOUT EVIDENCE.**

## Pre-Refactor Inspection
1. **Usage Audit**: Search for all call sites (`grep -r` for function/class name across codebase).
2. **Dependency Graph**: Identify downstream files that import or inherit from the target.
3. **Test Coverage**: Confirm unit and integration tests cover the target behavior.

## Refactor Patterns
- **Extract Function**: Only when duplication ≥ 3 call sites.
- **Move Module**: Preserve import paths; use public re-exports if changing file location.
- **Rename Symbol**: Update across all callers atomically via IDE or tooling; never manually.
- **Simplify Conditional**: Use early returns (`guard clauses`) to reduce nesting; avoid boolean flag parameters.

## Post-Refactor Verification
- Run all related unit + integration tests.
- Run type-check and lint.
- Compare git diff for scope creep (no unrelated formatting changes).