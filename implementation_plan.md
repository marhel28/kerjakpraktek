# Implementation Plan: WebSocket Migration for Real-Time Chat

[Overview]
Migrasi sistem chat real-time dari polling HTTP (3 detik) ke WebSocket native (FastAPI + Pinia) untuk latency sub-sekon, efisiensi server, dan pengalaman Tokopedia/Amazon style.

Saat ini sistem menggunakan smart polling: 3 detik saat popup terbuka, 2 menit saat tertutup, dengan rotasi 4x poll ringan + 1x sync full tiap 15 detik. WebSocket akan menghilangkan polling overhead, memberikan instant delivery pesan baru, read receipt, dan unread badge update.

[Types]
Definisi tipe data untuk WebSocket messages, connection state, dan event handling.

```typescript
// Connection States
type WSConnectionState = 'disconnected' | 'connecting' | 'open' | 'closing' | 'closed' | 'error';

// WebSocket Event Types (Server → Client)
type WSEventType = 
  | 'new_message'          // Pesan baru dari admin/user
  | 'message_read'         // Read receipt dari lawan bicara
  | 'unread_update'        // Update badge unread count
  | 'ping'                 // Heartbeat dari server
  | 'connection_ack'       // Konfirmasi koneksi berhasil
  | 'error';               // Error dari server

interface WSMessage<T = any> {
  type: WSEventType;
  payload: T;
  timestamp: string; // ISO 8601
}

// Payloads
interface NewMessagePayload extends ChatMessage { /* extends existing ChatMessage type */ }
interface MessageReadPayload { message_ids: string[]; reader_role: 'user' | 'admin'; }
interface UnreadUpdatePayload { unread_count: number; }
interface PingPayload { timestamp: string; }
interface ConnectionAckPayload { connection_id: string; user_role: 'user' | 'admin'; }
interface ErrorPayload { code: string; message: string; }

// Client → Server
type WSClientEventType = 'pong' | 'mark_read' | 'subscribe' | 'unsubscribe';
interface WSClientMessage<T = any> {
  type: WSClientEventType;
  payload: T;
}
interface MarkReadPayload { message_ids: string[]; }
interface SubscribePayload { conversation_ids?: string[]; } // Admin multi-conversation
```

[Files]
Daftar file baru dan modifikasi untuk implementasi WebSocket end-to-end.

**Backend (FastAPI) - New Files:**
- `backend/user/pesan/websocket.py` - WebSocket endpoint handler (`/ws/messages` dan `/ws/messages/admin`)
- `backend/user/pesan/connection_manager.py` - Connection registry, broadcast, heartbeat logic
- `backend/user/pesan/ws_auth.py` - WebSocket authentication dependency (reuse JWT)

**Backend - Modified Files:**
- `backend/user/pesan/__init__.py` - Export WebSocket modules
- `backend/user/pesan/route.py` - Add WebSocket routes ke router (opsional, atau router terpisah)
- `backend/user/pesan/service.py` - Tambah method `broadcast_new_message()`, `broadcast_read_receipt()`

**Frontend (Pinia) - Modified Files:**
- `frontend/app/stores/UsePesanStore.ts` - Replace polling logic dengan WebSocket client:
  - Add `ws` ref (WebSocket instance)
  - Add `connectionState` ref (`WSConnectionState`)
  - Add `reconnectAttempts`, `reconnectDelay` refs
  - Replace `_doPoll()`, `_doPollUnread()`, `_scheduleNextPoll()` dengan `connect()`, `disconnect()`, `reconnect()`
  - Add event handlers: `onmessage` (new_message, message_read, unread_update), `onopen`, `onclose`, `onerror`
  - Add `sendMessage()` via WS (fallback ke HTTP jika WS closed)
  - Add `markAllRead()` via WS
  - Keep `loadInitialHistory()`, `loadMoreHistory()` via HTTP (scroll history)
  - Exponential backoff reconnect: 1s, 2s, 4s, 8s, 16s, 30s (max)
  - Fallback ke polling jika reconnect gagal > 3x

- `frontend/app/components/FloatingChat.vue` - Pastikan `onPopupOpen()` trigger `connect()`, `onPopupClose()` tidak disconnect (keep alive untuk notifikasi), tapi pause message processing

**Configuration:**
- `backend/config.py` - Add `WS_HEARTBEAT_INTERVAL=30`, `WS_MAX_RECONNECT_DELAY=30000`, `WS_MAX_RECONNECT_ATTEMPTS=10`

[Functions]
Daftar fungsi baru dan modifikasi untuk WebSocket implementation.

**Backend - New Functions:**
- `ConnectionManager.connect(websocket, user_id, user_role)` - Register connection, send ack
- `ConnectionManager.disconnect(user_id, user_role)` - Cleanup connection
- `ConnectionManager.broadcast_new_message(message, exclude_sender=True)` - Broadcast ke semua koneksi user/admin
- `ConnectionManager.broadcast_read_receipt(message_ids, reader_role, conversation_id)` - Read receipt
- `ConnectionManager.broadcast_unread_update(user_id, unread_count)` - Badge update
- `ConnectionManager.send_personal(message, user_id)` - Direct send
- `ConnectionManager.heartbeat_loop()` - Ping/pong setiap 30 detik
- `ws_auth.get_current_user_ws(token)` - Auth dependency untuk WebSocket
- `ws_auth.get_admin_ws(token)` - Admin auth untuk WebSocket

**Backend - Modified Functions:**
- `MessageService.send_message()` - Tambah `await connection_manager.broadcast_new_message(msg)`
- `MessageService.mark_messages_read()` - Tambah `await connection_manager.broadcast_read_receipt(...)`
- `MessageService.get_unread_count()` - Tambah broadcast jika perlu

**Frontend - New Functions (UsePesanStore):**
- `connect()` - Initialize WebSocket, setup event listeners
- `disconnect()` - Close WebSocket cleanly
- `reconnect()` - Exponential backoff reconnect logic
- `handleWSMessage(event)` - Route event ke handler (`onNewMessage`, `onMessageRead`, `onUnreadUpdate`)
- `sendWSMessage(type, payload)` - Helper kirim ke server
- `queueMessage(message)` - Queue saat offline, flush saat reconnect

**Frontend - Modified Functions (UsePesanStore):**
- `onPopupOpen()` → `connect()` (jika belum connected)
- `onPopupClose()` → Tidak disconnect, hanya set `isPopupOpen = false`
- `sendMessage()` → Try WS first, fallback ke HTTP POST
- `markAllRead()` → Via WS `mark_read` event
- Hapus: `_doPoll()`, `_doPollUnread()`, `_scheduleNextPoll()`, `evaluatePollingState()`, `pollTimer`, `pollCycleCount`, `isPollingPaused`
- `stopPolling()` → `disconnect()` (pada logout/reset)
- `startPassivePolling()` → NOOP (WebSocket handle passive updates)

[Classes]
Modifikasi class/service untuk mendukung WebSocket.

**Backend - New Classes:**
```python
# backend/user/pesan/connection_manager.py
class ConnectionManager:
    def __init__(self):
        self.user_connections: dict[UUID, WebSocket] = {}      # user_id -> WebSocket
        self.admin_connections: dict[UUID, WebSocket] = {}     # admin_id -> WebSocket
        self.connection_metadata: dict[WebSocket, dict] = {}   # ws -> {user_id, role, connected_at}
    
    async def connect(self, websocket: WebSocket, user_id: UUID, role: SenderRole):
    async def disconnect(self, websocket: WebSocket):
    async def broadcast_new_message(self, message: MessageOut, exclude_sender: bool = True):
    async def broadcast_read_receipt(self, message_ids: list[UUID], reader_role: SenderRole, conversation_id: UUID):
    async def broadcast_unread_update(self, user_id: UUID, unread_count: int):
    async def send_personal(self, message: dict, user_id: UUID):
    async def heartbeat_loop(self):
```

**Frontend - Modified Store Structure (UsePesanStore):**
```typescript
// Add to state
const ws = ref<WebSocket | null>(null)
const connectionState = ref<WSConnectionState>('disconnected')
const reconnectAttempts = ref(0)
const maxReconnectAttempts = 10
const messageQueue = ref<ChatMessage[]>([])

// Add to actions
function connect(): Promise<void>
function disconnect(): void
function reconnect(): void
function handleWSMessage(event: MessageEvent): void
function sendWSMessage(type: WSClientEventType, payload: any): void
function flushMessageQueue(): void
```

[Dependencies]
Perubahan dependensi minimal, memanfaatkan ekosistem existing.

**Backend:**
- `fastapi` sudah include `websockets` (dependency bawaan)
- Tidak perlu dependency baru jika single-instance
- **Opsional**: `redis` + `redis-py` untuk multi-instance broadcast (Pub/Sub) — **defer ke Phase 2**

**Frontend:**
- Native `WebSocket` API (browser built-in) — **zero dependency**
- TypeScript types sudah didefinisikan di store

**Environment Variables (backend/.env):**
```
WS_HEARTBEAT_INTERVAL=30
WS_MAX_RECONNECT_DELAY=30000
WS_MAX_RECONNECT_ATTEMPTS=10
WS_CONNECTION_TIMEOUT=10000
```

[Testing]
Strategi testing untuk memastikan WebSocket berfungsi dengan benar.

**Unit Tests (Backend):**
- `test_connection_manager.py` - Connect, disconnect, broadcast, heartbeat
- `test_ws_auth.py` - Valid/invalid token, expired token, missing token
- `test_ws_endpoints.py` - Connect user/admin, send/receive messages, broadcast

**Integration Tests (Frontend):**
- Cypress/Playwright: Buka chat, kirim pesan, verifikasi instant delivery (<500ms)
- Test reconnect: Kill WS server → verifikasi auto-reconnect → message queue flush
- Test fallback: Block WS port → verifikasi fallback ke polling HTTP
- Test read receipt: Admin baca → user lihat centang biru instant
- Test unread badge: Admin kirim pesan → user badge update tanpa polling

**Load Test:**
- 100 koneksi WebSocket simultan → verifikasi memory/CPU stable
- Broadcast 1000 pesan → verifikasi latency < 100ms p95

[Implementation Order]
Urutan implementasi logis untuk meminimalkan konflik dan risiko.

1. **Backend: Connection Manager & Auth** (2-3 jam)
   - Buat `connection_manager.py` dengan connect, disconnect, broadcast, heartbeat
   - Buat `ws_auth.py` dengan dependency `get_current_user_ws`, `get_admin_ws`
   - Unit test connection manager

2. **Backend: WebSocket Endpoints** (1-2 jam)
   - Buat `websocket.py` dengan endpoint `/ws/messages` (user) dan `/ws/messages/admin` (admin)
   - Handle events: `new_message`, `message_read`, `unread_update`, `ping`/`pong`
   - Integrasi dengan `ConnectionManager` dan `MessageService`
   - Tambah route ke `backend/user/pesan/route.py` atau router terpisah

3. **Backend: Service Integration** (1 jam)
   - Modifikasi `MessageService.send_message()` → broadcast via ConnectionManager
   - Modifikasi `MessageService.mark_messages_read()` → broadcast read receipt
   - Update `message_service.py` import ConnectionManager

4. **Frontend: WebSocket Client di UsePesanStore** (2-3 jam)
   - Tambah state: `ws`, `connectionState`, `reconnectAttempts`, `messageQueue`
   - Implement `connect()`, `disconnect()`, `reconnect()` dengan exponential backoff
   - Implement `handleWSMessage()` routing ke `onNewMessage`, `onMessageRead`, `onUnreadUpdate`
   - Replace polling logic (`_doPoll`, `_scheduleNextPoll`, dll) dengan WS event handlers
   - Update `sendMessage()`, `markAllRead()` → gunakan WS dengan fallback HTTP
   - Update `onPopupOpen()` → `connect()`, `onPopupClose()` → keep alive

5. **Frontend: FloatingChat Integration** (30 menit)
   - Pastikan `onPopupOpen()` memanggil `usePesanStore().connect()`
   - `onPopupClose()` tidak disconnect, hanya pause processing
   - Verify FloatingChat tetap menerima pesan saat tertutup (badge update)

6. **Testing & Verification** (1-2 jam)
   - Manual test: Buka 2 browser (user + admin), kirim pesan → instant delivery
   - Test reconnect: Stop backend → verifikasi auto-reconnect → pesan queue flush
   - Test read receipt: Admin baca → user centang biru instant
   - Test unread badge: Admin kirim → user badge update tanpa polling
   - Test fallback: Block WS → verifikasi fallback ke polling (opsional)

7. **Documentation & Cleanup** (30 menit)
   - Hapus kode polling yang tidak terpakai di store
   - Update README/CHANGELOG
   - Verify no console error/warning

**Total Estimasi: ~8-12 jam**

---

### Catatan Penting:
- **Backward Compatibility**: HTTP endpoints (`/poll`, `/history`, `/read`, `/unread`) **dibiarkan** untuk fallback dan admin inbox yang tidak pakai WS
- **Notification System**: `notificationStore.ts` sudah pakai Supabase Realtime — **tidak disentuh**
- **Admin Inbox**: Bisa pakai WS (`/ws/messages/admin`) untuk real-time inbox refresh, atau tetap polling 5 detik — **pilihan implementasi**