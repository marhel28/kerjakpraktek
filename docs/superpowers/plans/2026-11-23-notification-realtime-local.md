# Notifikasi Realtime Lokal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mengganti Supabase Realtime + tabel `notifications` di Supabase dengan WebSocket FastAPI sendiri dan tabel `notification` di PostgreSQL lokal, tanpa mengubah perilaku konsumen notifikasi.

**Architecture:** Modul baru `backend/user/notifications/` berisi model SQLModel, service penulis (session sendiri, post-commit, best-effort), REST untuk user, WS `/ws/notifications/{uuid}`, dan jembatan Redis pub/sub agar notifikasi dari Celery tetap sampai. Frontend mempertahankan API `useNotificationStore()` persis; hanya isi store, proxy Nuxt, dan composable socket yang diganti. Auth bridge Supabase di backend tidak disentuh.

**Tech Stack:** Python 3.13 / FastAPI / SQLModel / asyncpg / Redis pub/sub (Dragonfly) / Celery; Nuxt 4 / Vue 3 / Pinia / TypeScript.

**Spec:** `docs/architecture/system-overview.md` + keputusan desain yang disetujui dalam percakapan (2026-11-23).

## Global Constraints

- `id` notifikasi tetap `number` (`BIGSERIAL`) — kontrak `admin/project/src/stores/notificationStore.js` dan `/recap/notifications/{id}`.
- Field JSON tetap: `id, user_id, title, content, type, metadata, read_at, created_at`.
- `useNotificationStore()` harus tetap mengekspor 17 member yang ada sekarang.
- Chat tidak berubah perilaku; hanya 2 baris import di `ws_route.py`.
- Auth bridge Supabase (`backend/auth/supabase_auth.py`, `UserMap`, `SUPABASE_*` config backend) tidak dihapus.
- Tabel lokal mulai kosong; tidak ada backfill data Supabase.
- Notifikasi bersifat best-effort: gagal insert tidak boleh menggagalkan checkout/webhook.
- Tidak ada secret yang dicatat, dicetak, atau di-commit.

## Review Focus

- User tanpa `UserMap`: harus tetap menerima notifikasi (sekarang dibuang diam-diam). → test service `notify_user()` dengan uuid biasa.
- Race fetch + push INSERT: tidak boleh ada notifikasi dobel. → test dedupe by id di store.
- Celery → API lintas proses: notifikasi promo harus tetap live. → publish ke Redis saat smoke test.
- Multi-worker: tiap worker kirim hanya ke socket lokalnya. → uji dengan 2 worker.
- Logout/pergantian user: socket harus terputus dan state kosong. → Playwright logout.

---

### Task 1: Model + service notifikasi lokal

**Files:**
- Create: `backend/user/notifications/__init__.py`, `model.py`, `schema.py`, `service.py`
- Modify: `backend/db/main.py` (pastikan model ter-import untuk `create_all`)

**Interfaces:**
- Produces: `Notification` (tabel `notification`), `NotificationOut`, `notify_user(user_id: UUID, title: str, content: str = "", notif_type: str = "general", action_url: str | None = None, metadata: dict | None = None) -> dict`, `notify_users(user_ids: list[UUID], ...) -> list[dict]`

- [ ] Buat model dengan kolom `id BIGSERIAL`, `user_id uuid FK user.uuid CASCADE`, `title`, `content`, `type`, kolom DB `metadata` (atribut Python `meta`), `read_at`, `created_at`, index `(user_id, created_at DESC)` dan partial unread.
- [ ] Buat schema `NotificationOut` dengan `meta` → alias `metadata`, `user_id` sebagai `str`.
- [ ] Buat service dengan session sendiri, commit, lalu publish Redis.
- [ ] Verifikasi: import modul + `SQLModel.metadata.create_all` membuat tabel.

### Task 2: REST + WebSocket + Redis pub/sub

**Files:**
- Create: `backend/auth/ws_auth.py`, `backend/user/notifications/router.py`, `ws_manager.py`, `ws_route.py`, `pubsub.py`
- Modify: `backend/user/pesan/ws_route.py` (import), `backend/__init__.py` (router + lifespan)

- [ ] Pindahkan `authenticate_ws_token` ke `backend/auth/ws_auth.py`; chat import dari sana.
- [ ] Endpoint REST: GET /notifications, PATCH /notifications/{id}/read, POST /notifications/read-all, DELETE /notifications/{id}.
- [ ] WS `/ws/notifications/{user_id}?token=` dengan event `connection_established`, `notification.created|updated|deleted`, `pong`.
- [ ] `pubsub.py`: channel `notif:{uuid}`, subscriber di lifespan, tolerate Redis mati.
- [ ] Verifikasi: WS menerima event dari publish manual.

### Task 3: Alihkan penulis & pembaca notifikasi backend

**Files:**
- Modify: `backend/data/transaksi/service.py`, `backend/data/public/promobanner/service.py`, `backend/data/jasa/service.py`, `backend/admin/adminTransaksi/service.py`, `backend/tasks/promo_tasks.py`, `backend/db/supabse.py`, `requirements.txt`
- Delete: `backend/data/transaksi/service_backup.py`, `backend/scratch/test_notifications.py`

- [ ] Ganti 5 helper pengirim supaya memakai `notify_user`/`notify_users` dengan `user.uuid`.
- [ ] Ganti admin read/mark endpoints ke tabel lokal.
- [ ] Ganti Celery bulk notification ke lokal + publish.
- [ ] Pangkas `db/supabse.py` menjadi helper auth httpx saja; hapus dependency `supabase` dari requirements.
- [ ] Verifikasi: `rg SupabaseNotificationService backend` = 0 hit.

### Task 4: Frontend

**Files:**
- Create: `frontend/app/composables/useNotificationSocket.ts`, `frontend/app/utils/session.ts`, `frontend/server/api/notifications.ts`
- Modify: `frontend/app/stores/notificationStore.ts`, `frontend/app/composables/useChatSocket.ts`, plugin realtime, `useAuth.ts`, `login.vue`, server api login/google, komponen logout, `nuxt.config.ts`, `package.json`
- Delete: `frontend/plugins/supabase.client.ts`, `frontend/app/types/database.types.ts`

- [ ] Ekstrak `getBackendUserId` ke `utils/session.ts`, pakai bersama chat & notifikasi.
- [ ] Proxy `/api/notifications` mengikuti pola `pesan.ts`.
- [ ] Store: ganti 4 call PostgREST dengan `$fetch`, ganti channel dengan composable socket, dedupe INSERT.
- [ ] Hapus semua pemakaian `@nuxtjs/supabase` / `@supabase/supabase-js` di frontend.
- [ ] Verifikasi: `rg -i supabase frontend --glob '!node_modules/**' --glob '!.nuxt/**' --glob '!.output/**' --glob '!.vercel/**'` = 0 hit; `npx nuxi typecheck`.

### Task 5: Verifikasi & git

- [ ] `git diff` kedua repo.
- [ ] Commit conventional, stage eksplisit.
- [ ] Push ke `marhel28/kerjakpraktek` (main) dan `marhel28/marketplace` (main).
