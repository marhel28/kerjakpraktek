---
name: git-workflow
description: Safe, disciplined, and audit-friendly Git operations adhering to senior engineering workflows.
---

# Operational Skill: Git Workflow

## Safety Invariant
**NEVER execute destructive Git operations without explicit user confirmation.**
Forbidden without explicit command:
- `git reset --hard`
- `git clean -fd`
- `git push --force`
- `git branch -D`

## Standard Workflow
1. **Pre-Change Verification**:
   - Run `git status` to see unstaged changes.
   - Run `git diff` to understand current working tree state.
   - Verify current branch (`git branch --show-current`).
2. **Staging & Commit Rules**:
   - Stage only files relevant to the completed task (`git add <file1> <file2>`).
   - Never stage generated artifacts, secrets, `.env` files, or local cache directories.
   - Write clear, imperative, concise commit messages following Conventional Commits format (`feat:`, `fix:`, `refactor:`, `test:`, `chore:`).
3. **Post-Commit Check**:
   - Verify latest commit with `git log -n 1 --stat`.
