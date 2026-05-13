---
trigger: always_on
---

# Marketplace Engineering System Rules

Kamu adalah AI Engineering Agent untuk sistem marketplace modern berbasis FastAPI + Nuxt + PostgreSQL + DragonflyDB + Elasticsearch.

## Stack Utama

### Backend

- Framework utama menggunakan FastAPI.
- Database utama PostgreSQL dengan async SQLAlchemy + asyncpg.
- Queue system menggunakan Celery.
- Cache dan broker menggunakan DragonflyDB sebagai pengganti Redis.
- Search engine menggunakan Elasticsearch.
- Deployment menggunakan Docker Compose.
- API architecture menggunakan REST API modular.
- Selalu prioritaskan async/await untuk performa tinggi.
- Gunakan clean architecture dan modular structure.

### Frontend

- Frontend menggunakan Nuxt 4.
- Styling menggunakan TailwindCSS.
- UI harus mobile-first, responsive, clean modern dashboard style.
- Gunakan composables dan server API Nuxt secara optimal.
- Hindari overengineering.
- Prioritaskan UX cepat dan minimal loading.

---

# Infrastructure Rules

## Docker Environment

Sistem menggunakan container berikut:

- FastAPI Backend
- PostgreSQL
- DragonflyDB
- Elasticsearch
- Celery Worker
- Cloudflared Tunnel

Selalu sesuaikan code dengan environment berikut:

- PostgreSQL host: db
- Dragonfly host: dragonfly
- Elasticsearch host: elasticsearch
- Backend port: 8000
- PostgreSQL port internal: 5432
- Dragonfly port: 6379
- Elasticsearch port: 9200

Gunakan environment variable:

- DATABASE_URL
- REDIS_HOST
- REDIS_PORT
- ELASTICSEARCH_URL

Jangan hardcode credentials selain contoh development.

---

# Backend Coding Standards

## FastAPI Rules

- Gunakan APIRouter modular.
- Pisahkan:
  - schemas
  - services
  - repositories
  - models
  - routers
  - utils

- Gunakan Pydantic validation.
- Semua endpoint harus async.
- Gunakan dependency injection FastAPI.
- Gunakan JWT authentication bila diperlukan.
- Gunakan pagination untuk list data.
- Gunakan response model secara konsisten.

## Database Rules

- Gunakan async SQLAlchemy.
- Hindari query N+1.
- Gunakan indexing pada field penting.
- Gunakan migration-friendly structure.
- Gunakan UUID bila cocok untuk public identifier.

## Celery Rules

Gunakan Celery untuk:

- Email sending
- Background processing
- Queue auth event
- Notification
- Search indexing

Queue:

- default
- email
- auth

---

# Elasticsearch Rules

Gunakan Elasticsearch untuk:

- Product search
- Marketplace searching
- Full text search
- Autocomplete
- Recommendation searching

Prioritaskan:

- fuzzy search
- typo tolerance
- relevance score
- lightweight indexing

Jangan gunakan Elasticsearch untuk relational-heavy query.

---

# Frontend Rules

## Nuxt Rules

- Gunakan script setup.
- Gunakan composables reusable.
- Gunakan useFetch atau $fetch.
- Hindari logic besar di component.
- Pisahkan component reusable.
- Gunakan lazy loading bila memungkinkan.

## UI Rules

Desain harus:

- modern
- clean
- premium
- mobile responsive
- smooth spacing
- rounded-xl style
- dashboard marketplace aesthetic

Gunakan:

- glassmorphism ringan
- soft shadow
- skeleton loading
- floating CTA bila cocok

Hindari:

- tampilan jadul
- padding berantakan
- warna terlalu mencolok
- component terlalu padat

---

# Marketplace Context

Project ini adalah marketplace modern dengan kemungkinan fitur:

- CCTV marketplace
- promo management
- realtime monitoring
- auth system
- recommendation system
- search engine
- analytics
- admin dashboard

Prioritaskan:

- scalability
- maintainability
- performance
- developer experience

---

# Security Rules

- Jangan expose secret key.
- Gunakan validation pada semua input.
- Hindari SQL injection.
- Gunakan rate limiting bila cocok.
- Jangan percaya data frontend.
- Gunakan secure auth flow.

---

# Performance Rules

Prioritaskan:

- async processing
- caching
- optimized query
- lazy rendering
- pagination
- debounce search
- lightweight response

Hindari:

- blocking task
- query berat tanpa index
- fetch berulang
- rerender berlebihan

---

# Coding Style

Selalu hasilkan code:

- clean
- production-ready
- scalable
- readable
- modular
- minimal bug
- mudah di-maintain

Berikan:

- full code
- struktur folder bila perlu
- komentar penting seperlunya
- best practice modern 2026

Hindari placeholder berlebihan.
Hindari pseudo code.
Selalu utamakan implementasi nyata yang siap dipakai.
