---
name: investigate
description: Systematically inspect repositories, trace execution flow, identify boundaries and dependencies before any code modification.
---

# Operational Skill: Investigation

## Core Rule
**Never modify code before investigating the target area and verifying all direct & indirect dependencies.**

## Investigation Workflow
1. **Inspect Repository Layout**: Identify entrypoints, directories, framework structure (e.g. backend FastAPI, frontend Nuxt/Vue, background jobs Celery).
2. **Identify Existing Patterns**: Check how error handling, database transactions, state management, and authentication are implemented in adjacent files.
3. **Locate Target Files**: Use Glob and Grep tools with exact symbols. Never assume file paths.
4. **Trace Execution Flow**:
   - Trace HTTP route / WebSocket endpoint -> Controller / Router -> Service -> Data Repository / ORM -> Database.
   - Trace Frontend Event -> Pinia / Composable -> API Fetcher -> Backend Endpoint.
5. **Analyze Dependencies & Side Effects**:
   - Check Celery tasks triggered by database hooks.
   - Check cache invalidation in Redis/Dragonfly.
   - Check WebSocket broadcasts or notifications.
6. **Formulate Findings**: Propose concrete, minimal, safe solution plan before writing any code.
