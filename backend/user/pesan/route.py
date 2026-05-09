"""
ROUTE: /messages — Sistem Pesan Customer ↔ Admin (Gabungan)
============================================================
Rules:
- Satu file router, dua kelompok endpoint dibedakan oleh prefix & dependency auth
- User endpoint   : prefix /messages/*           → auth: get_current_user
- Admin endpoint  : prefix /messages/admin/*     → auth: get_admin
- Role ditentukan dari JWT, bukan path param — tidak ada manual role-check di handler
- Shared helper _ensure_conversation dipakai oleh kedua sisi

── USER ENDPOINTS (/messages) ──────────────────────────────────────
  POST  /messages/send              Kirim pesan ke admin (multipart)
  GET   /messages/poll              Polling pesan baru (after_sent_at cursor)
  GET   /messages/history           Load pesan lama (before_sent_at, scroll atas)
  PATCH /messages/read              Mark pesan sebagai dibaca
  GET   /messages/unread            Jumlah pesan belum dibaca (badge)

── ADMIN ENDPOINTS (/messages/admin) ───────────────────────────────
  GET   /messages/admin/inbox                     Daftar semua conversation
  POST  /messages/admin/{conversation_id}/send    Balas pesan user
  GET   /messages/admin/{conversation_id}/poll    Polling pesan baru
  GET   /messages/admin/{conversation_id}/history Load history
  PATCH /messages/admin/{conversation_id}/read    Mark dibaca
  GET   /messages/admin/{conversation_id}/unread  Unread count

── POLLING PATTERN ─────────────────────────────────────────────────
  User:
    1. GET /messages/history          → load awal
    2. GET /messages/poll?after_sent_at=<ts>  → tiap 3 detik
    3. PATCH /messages/read           → saat buka/scroll ke bawah

  Admin:
    1. GET /messages/admin/inbox      → tiap 5 detik (refresh badge)
    2. GET /messages/admin/{id}/history → saat buka chat
    3. GET /messages/admin/{id}/poll?after_sent_at=<ts> → tiap 3 detik
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.main import get_session as get_db
from .model import SenderRole
from .schema import (
    ConversationOut, MarkReadRequest, MessageOut, PollResponse, UnreadCountOut,
)
from .service import message_service
from backend.auth.depedence import get_current_user, get_admin  # sesuaikan

router = APIRouter(prefix="/messages", tags=["Messages"])


# ══════════════════════════════════════════════════════════════════
# SHARED HELPER
# ══════════════════════════════════════════════════════════════════

async def _ensure_conversation(db: AsyncSession, user_id: UUID, username: str):
    """
    Pastikan conversation untuk user ini sudah ada.
    Kalau belum, buat baru. Dipanggil sebelum semua operasi sisi user.
    """
    return await message_service.get_or_create_conversation(db, user_id, username)


# ══════════════════════════════════════════════════════════════════
# USER ENDPOINTS
# ══════════════════════════════════════════════════════════════════

# ── POST /messages/send ────────────────────────────────────────────
@router.post(
    "/send",
    response_model=MessageOut,
    status_code=status.HTTP_201_CREATED,
    summary="[User] Kirim pesan ke admin",
    description="Multipart form: `body` (teks, optional) + `images` (UploadFile, maks 2).",
)
async def user_send_message(
    body: Optional[str] = Form(default=None, max_length=4000),
    images: list[UploadFile] = File(default=[]),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    conv = await _ensure_conversation(db, current_user.uuid, current_user.username)
    return await message_service.send_message(
        db=db,
        conversation_id=conv.uuid,
        sender_id=current_user.uuid,
        sender_role=SenderRole.USER,
        body=body,
        images=images,
    )


# ── GET /messages/poll ─────────────────────────────────────────────
@router.get(
    "/poll",
    response_model=PollResponse,
    summary="[User] Polling pesan baru",
    description=(
        "Kirim `after_sent_at` (ISO 8601) = sent_at pesan terakhir yang sudah diterima FE. "
        "Panggil setiap 3–5 detik saat chat terbuka."
    ),
)
async def user_poll_messages(
    after_sent_at: Optional[datetime] = Query(
        default=None,
        description="Timestamp ISO 8601 pesan terakhir yang sudah diterima FE.",
    ),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    conv = await _ensure_conversation(db, current_user.uuid, current_user.username)
    return await message_service.poll_messages(
        db=db,
        conversation_id=conv.uuid,
        after_sent_at=after_sent_at,
    )


# ── GET /messages/history ──────────────────────────────────────────
@router.get(
    "/history",
    response_model=list[MessageOut],
    summary="[User] Load history pesan",
    description="Ambil pesan lama sebelum `before_sent_at`. Untuk load-more saat scroll ke atas.",
)
async def user_get_history(
    before_sent_at: Optional[datetime] = Query(
        default=None,
        description="Ambil pesan sebelum timestamp ini.",
    ),
    limit: int = Query(default=30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    conv = await _ensure_conversation(db, current_user.uuid, current_user.username)
    return await message_service.get_message_history(
        db=db,
        conversation_id=conv.uuid,
        before_sent_at=before_sent_at,
        limit=limit,
    )


# ── PATCH /messages/read ───────────────────────────────────────────
@router.patch(
    "/read",
    summary="[User] Tandai pesan sebagai dibaca",
    description="Kirim list `message_ids`. Reset unread_by_user counter di conversation.",
)
async def user_mark_read(
    payload: MarkReadRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    conv = await _ensure_conversation(db, current_user.uuid, current_user.username)
    count = await message_service.mark_messages_read(
        db=db,
        conversation_id=conv.uuid,
        reader_role=SenderRole.USER,
        message_ids=payload.message_ids,
    )
    return {"updated": count}


# ── GET /messages/unread ───────────────────────────────────────────
@router.get(
    "/unread",
    response_model=UnreadCountOut,
    summary="[User] Jumlah pesan belum dibaca (badge)",
    description="Polling ringan khusus badge notif. Baca dari kolom denormalized — O(1).",
)
async def user_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    conv = await _ensure_conversation(db, current_user.uuid, current_user.username)
    count = await message_service.get_unread_count(
        db=db,
        conversation_id=conv.uuid,
        reader_role=SenderRole.USER,
    )
    return UnreadCountOut(unread_count=count)


# ══════════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS
# ══════════════════════════════════════════════════════════════════

# ── GET /messages/admin/inbox ──────────────────────────────────────
@router.get(
    "/admin/inbox",
    response_model=list[ConversationOut],
    summary="[Admin] Daftar semua percakapan (inbox)",
    description=(
        "Diurutkan dari conversation paling baru aktif. "
        "Poll setiap 5 detik untuk refresh badge unread di inbox."
    ),
)
async def admin_inbox(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_admin),
):
    return await message_service.get_conversation_list(db=db, skip=skip, limit=limit)


# ── POST /messages/admin/{conversation_id}/send ────────────────────
@router.post(
    "/admin/{conversation_id}/send",
    response_model=MessageOut,
    status_code=status.HTTP_201_CREATED,
    summary="[Admin] Balas pesan user",
    description="Multipart form: `body` (teks, optional) + `images` (UploadFile, maks 2).",
)
async def admin_send_message(
    conversation_id: UUID,
    body: Optional[str] = Form(default=None, max_length=4000),
    images: list[UploadFile] = File(default=[]),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_admin),
):
    return await message_service.send_message(
        db=db,
        conversation_id=conversation_id,
        sender_id=current_admin.uuid,
        sender_role=SenderRole.ADMIN,
        body=body,
        images=images,
    )


# ── GET /messages/admin/{conversation_id}/poll ─────────────────────
@router.get(
    "/admin/{conversation_id}/poll",
    response_model=PollResponse,
    summary="[Admin] Polling pesan baru dalam satu conversation",
    description=(
        "Poll setiap 3 detik saat chat admin terbuka. "
        "Kirim `after_sent_at` = timestamp pesan terakhir yang sudah diterima."
    ),
)
async def admin_poll_messages(
    conversation_id: UUID,
    after_sent_at: Optional[datetime] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_admin),
):
    return await message_service.poll_messages(
        db=db,
        conversation_id=conversation_id,
        after_sent_at=after_sent_at,
    )


# ── GET /messages/admin/{conversation_id}/history ─────────────────
@router.get(
    "/admin/{conversation_id}/history",
    response_model=list[MessageOut],
    summary="[Admin] Load history pesan (scroll ke atas)",
    description="Ambil pesan lama sebelum `before_sent_at`. Untuk fitur load-more.",
)
async def admin_get_history(
    conversation_id: UUID,
    before_sent_at: Optional[datetime] = Query(default=None),
    limit: int = Query(default=30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_admin),
):
    return await message_service.get_message_history(
        db=db,
        conversation_id=conversation_id,
        before_sent_at=before_sent_at,
        limit=limit,
    )


# ── PATCH /messages/admin/{conversation_id}/read ───────────────────
@router.patch(
    "/admin/{conversation_id}/read",
    summary="[Admin] Mark pesan sebagai dibaca",
    description="Kirim list `message_ids`. Reset unread_by_admin counter di conversation.",
)
async def admin_mark_read(
    conversation_id: UUID,
    payload: MarkReadRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_admin),
):
    count = await message_service.mark_messages_read(
        db=db,
        conversation_id=conversation_id,
        reader_role=SenderRole.ADMIN,
        message_ids=payload.message_ids,
    )
    return {"updated": count}


# ── GET /messages/admin/{conversation_id}/unread ───────────────────
@router.get(
    "/admin/{conversation_id}/unread",
    response_model=UnreadCountOut,
    summary="[Admin] Unread count satu conversation (badge)",
    description="Baca dari kolom denormalized di conversation — O(1), tidak COUNT query.",
)
async def admin_unread_count(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_admin),
):
    count = await message_service.get_unread_count(
        db=db,
        conversation_id=conversation_id,
        reader_role=SenderRole.ADMIN,
    )
    return UnreadCountOut(unread_count=count)