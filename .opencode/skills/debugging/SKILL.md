---
name: debugging
description: Systematic root cause analysis, hypothesis testing, log inspection, and minimal-diff defect resolution.
---

# Operational Skill: Debugging

## Operational Workflow
```text
Reproduce
   ↓
Collect Evidence (Logs, Stack Trace, Network, State)
   ↓
Trace Execution Flow
   ↓
Form Hypothesis
   ↓
Test Hypothesis (Asserts, Minimal Repro)
   ↓
Apply Minimal Safe Fix
   ↓
Regression Test & Verify
```

## Mandatory Rules
- **No Shotgun Debugging**: Never make random code changes hoping an error disappears.
- **Inspect Exact Logs**: Read backend container logs via `docker logs` or stdout, inspect frontend console logs and network response bodies.
- **Isolate the Failure**: Determine if the failure is at:
  1. Network / CORS / reverse proxy layer.
  2. Authentication / JWT / Token verification layer.
  3. Validation / Schema parsing layer.
  4. Database / SQL / Transaction layer.
  5. Frontend reactive state / template binding layer.
- **Preserve Unrelated Behavior**: Do not refactor adjacent working code while fixing a specific bug.
