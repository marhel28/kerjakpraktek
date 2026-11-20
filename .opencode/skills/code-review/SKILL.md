---
name: code-review
description: Comprehensive review for correctness, security vulnerabilities, performance regressions, and architectural integrity.
---

# Operational Skill: Code Review

## Review Checklist
1. **Correctness**:
   - Does the logic handle all edge cases (empty lists, null/None, malformed strings, duplicate keys)?
   - Are async calls properly awaited?
2. **Security**:
   - Are inputs validated at the boundary?
   - Are queries parameterized to prevent SQL injection?
   - Is authentication & authorization verified on every protected endpoint?
   - Are secrets, passwords, and tokens prevented from leaking into logs or git diff?
3. **Performance**:
   - Are there N+1 query loops inside loops?
   - Are bulk inserts or updates used where applicable?
   - Are database indexes aligned with filter/join columns?
4. **Maintainability**:
   - Is naming self-describing?
   - Are diffs concise and minimal without gratuitous reformatting?
   - Are unused imports and variables cleaned up?
