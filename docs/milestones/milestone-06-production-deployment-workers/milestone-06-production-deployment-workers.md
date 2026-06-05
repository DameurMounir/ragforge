# Milestone 6 — Production Deployment & Workers

Milestone 6 moves RAGForge from a working RAG Core toward production infrastructure.

## Scope

- PostgreSQL persistence boundary
- SQLAlchemy async ORM
- Alembic migrations
- PgVector-ready database service
- Docker deployment improvements
- background workers
- scheduler and operational tooling

## Branches

| Branch | Title | Goal |
|---|---|---|
| 20 | PostgreSQL + SQLAlchemy + Alembic Production Layer | Add relational persistence infrastructure with transaction discipline. |
| 21 | PgVector Direction | Prepare vector persistence/search evolution. |
| 22+ | Deployment Stack | Harden deployment, environment, and runtime operations. |
| 24–25 | Workers | Add Celery/Flower/scheduler workflows. |
