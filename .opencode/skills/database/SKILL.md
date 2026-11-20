---
name: database
description: PostgreSQL & Dragonfly/Redis schema inspection, migration management, index tuning, and transaction safety.
---

# Operational Skill: Database

## Pre-Change Inspection Checklist
1. **Inspect Existing Relations**: Query `information_schema` or run `\dt` via psql to understand primary keys, foreign keys, and existing column types.
2. **Review Migrations**: Check Alembic migration versions (`alembic current`, `alembic history`) before altering models.
3. **Analyze Impact**: Evaluate table volume and locks before altering large production tables.

## Safety & Best Practices
- **Explicit Transactions**: Ensure operations that span multiple tables (e.g. order creation + inventory decrement) run inside an atomic transaction block.
- **Index Alignment**: Add indexes on foreign keys, filtering columns (e.g., `status`, `user_id`), and sorting columns (`created_at`).
- **N+1 Prevention**: Use `selectinload` or `joinedload` in SQLAlchemy to eager-load relationships when querying lists.
- **Rollback Strategy**: Every forward migration must have a tested, non-destructive downgrade path.
- **Caching Layer (Redis/Dragonfly)**:
  - Cache only serializable JSON/orjson data.
  - Set explicit TTL on keys.
  - Invalidate related keys immediately upon database mutations.
