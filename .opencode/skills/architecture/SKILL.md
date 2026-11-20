---
name: architecture
description: Maintain high cohesion, low coupling, single-responsibility boundaries, and backward compatibility across full-stack systems.
---

# Operational Skill: Architecture

## Core Principles
1. **Preserve Existing Architecture**: Respect established project conventions (FastAPI routers, SQLModel/SQLAlchemy async sessions, Nuxt 4 composables).
2. **Coupling & Boundaries**:
   - Keep business logic in `service.py` layers, never in API router handlers.
   - Keep SQL queries isolated in repositories or explicit service functions.
   - Frontend components must consume Pinia stores or composables, avoiding raw unstructured HTTP calls inside UI elements.
3. **No Premature Abstraction**: Avoid introducing heavy design patterns (factories, adapters, abstract classes) unless there are multiple implementations.
4. **Backward Compatibility**:
   - Preserve existing API request/response schema contracts.
   - Database migrations must support rolling zero-downtime releases where possible.
