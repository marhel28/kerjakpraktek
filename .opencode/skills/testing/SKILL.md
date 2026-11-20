---
name: testing
description: Automated test execution, unit/integration test generation, Playwright browser test runner.
---

# Operational Skill: Testing

## Test Discovery
1. Identify test frameworks present:
   - Backend: `pytest`, `pytest-asyncio`, `httpx` test client.
   - Frontend: `vitest`, `playwright`, `jest`.
2. Inspect `conftest.py`, test configuration, fixtures, and existing test directories.

## Operational Standards
- **Write Tests for New Logic**: When adding features or fixing bugs, add tests reproducing the bug and verifying the fix.
- **Async Test Support**: In FastAPI/SQLAlchemy, use async fixtures with rollback/transaction isolation.
- **E2E Browser Testing with Playwright**:
  - Launch headless browser sessions.
  - Verify UI elements, navigation, input forms, and WebSocket event reactions.
  - Take visual artifacts/screenshots when testing visual rendering regressions.
- **Run Before Approval**: Never declare a task complete without executing existing test suites to ensure zero regressions.
