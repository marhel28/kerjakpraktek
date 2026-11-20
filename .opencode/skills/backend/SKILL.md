---
name: backend
description: Production-grade FastAPI, async SQLAlchemy/SQLModel, Redis caching, Celery task processing, and robust architecture.
---

# Operational Skill: Backend Development

## Architecture Rules
1. **Layered Structure**:
   - `route.py`: HTTP / WebSocket router, request validation, dependency injection.
   - `service.py`: Business logic, transaction orchestration, cache invalidation.
   - `model.py`: Database entities (SQLModel / SQLAlchemy declarative base).
   - `schema.py`: Pydantic input / output DTO contracts.
2. **Asynchronous Execution**:
   - Use `async def` for I/O bound endpoints.
   - Never use blocking synchronous sleep (`time.sleep`) or blocking HTTP calls (`requests.get`). Use `asyncio.sleep` and `httpx.AsyncClient`.
3. **Database Sessions**:
   - Inject `AsyncSession` via `Depends(get_session)`.
   - Never create dangling database connections. Always commit or rollback within a context manager.
4. **Error Handling**:
   - Raise explicit `HTTPException(status_code=..., detail=...)`.
   - Avoid generic 500 errors; provide actionable, secure error responses.
5. **Background Jobs**:
   - Offload heavy tasks (emails, batch cleanups, image resizing) to Celery workers via `.delay()`.
