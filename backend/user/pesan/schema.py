"""
SCHEMA: Request & Response untuk sistem pesan
===============================================
Rules:
- SendMessageRequest  : payload dari user/admin saat kirim pesan (form-data, ada file)
- MessageImageOut     : representasi gambar dalam response
- MessageOut          : satu pesan lengkap dengan daftar gambar
- ConversationOut     : summary conversation (untuk list inbox admin)
- PollResponse        : response polling — berisi pesan baru + timestamp cursor
- MarkReadRequest     : body untuk endpoint mark-as-read

Catatan:
- Gambar dikirim sebagai multipart/form-data (UploadFile FastAPI)
- Polling menggunakan cursor `after` (UUID pesan terakhir yang sudah diterima)
  agar tidak re-fetch pesan lama
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


# ── Request: Kirim Pesan ───────────────────────────────────────────
class SendMessageRequest(BaseModel):
    """
    Dipakai bersama UploadFile di route (Form + File).
    body wajib diisi jika tidak ada gambar.
    images dikirim terpisah sebagai UploadFile list (maks 2).
    """
    body: Optional[str] = Field(default=None, max_length=4000)

    @model_validator(mode="after")
    def body_or_image_required(self):
        # Validasi ini hanya memastikan body ada kalau tidak ada gambar.
        # Validasi gambar dilakukan di service karena UploadFile tidak masuk Pydantic.
        return self


# ── Response: Gambar ───────────────────────────────────────────────
class MessageImageOut(BaseModel):
    uuid: UUID
    image_url: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}


# ── Response: Satu Pesan ───────────────────────────────────────────
class MessageOut(BaseModel):
    uuid: UUID
    conversation_id: UUID
    sender_role: str          # "user" | "admin"
    sender_id: UUID
    body: Optional[str]
    status: str               # "sent" | "read"
    sent_at: datetime
    images: list[MessageImageOut] = []

    model_config = {"from_attributes": True}


# ── Response: Summary Conversation (untuk admin inbox) ────────────
class ConversationOut(BaseModel):
    uuid: UUID
    user_id: UUID
    user_username: str
    unread_by_admin: int
    unread_by_user: int
    last_message_at: Optional[datetime]
    last_message_preview: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Response: Polling ──────────────────────────────────────────────
class PollResponse(BaseModel):
    """
    Dikembalikan setiap kali FE polling /messages/poll.
    - messages   : daftar pesan baru setelah cursor `after_message_id`
    - last_id    : UUID pesan terakhir di batch ini (jadi cursor berikutnya)
    - has_more   : apakah masih ada pesan lebih lama (untuk load-more, bukan polling)
    """
    messages: list[MessageOut]
    last_id: Optional[UUID]       # None kalau tidak ada pesan baru
    has_more: bool = False        # untuk pagination load-more


# ── Request: Mark as Read ──────────────────────────────────────────
class MarkReadRequest(BaseModel):
    """
    Kirim list UUID pesan yang ingin di-mark read.
    Endpoint: PATCH /messages/read
    """
    message_ids: list[UUID] = Field(..., min_length=1, max_length=100)


# ── Response: Jumlah Unread (untuk badge notif polling) ───────────
class UnreadCountOut(BaseModel):
    unread_count: int