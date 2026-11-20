---
name: performance
description: Measurement-driven optimization, query profiling, caching strategy, and frontend bundle tuning.
---

# Operational Skill: Performance

## The Optimization Rule
**Never optimize based on intuition alone. Always Measure → Identify Bottleneck → Optimize → Benchmark → Compare.**

## Backend Profiling
1. **Database Query Latency**: Use `EXPLAIN ANALYZE` on queries exceeding latency thresholds. Identify sequential table scans where index scans should occur.
2. **Connection Pooling**: Configure appropriate pool size (`max_connections`) and connection reuse in SQLAlchemy `create_async_engine`.
3. **Serialization Overhead**: Use ultra-fast serialization (e.g. `orjson`, `ORJSONResponse` in FastAPI) for heavy payloads.
4. **Asynchronous I/O**: Ensure all network and database operations use non-blocking `async`/`await` calls without blocking the event loop.

## Frontend Profiling
1. **Bundle Size**: Inspect chunk sizes in build logs (`vite.config.ts` / `nuxt.config.ts`).
2. **Re-rendering & Reactivity**: Avoid deep object watches; use fine-grained computed properties.
3. **Asset Delivery**: Ensure images are served in modern formats (WebP/AVIF) with appropriate CDN caching headers.
