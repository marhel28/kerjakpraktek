"""
MODEL: Message & MessageImage
==============================
Rules:
- Satu percakapan (conversation) terdiri dari banyak pesan (message)
- Setiap pesan bisa punya maksimal 2 gambar (MessageImage)
- Conversation diidentifikasi oleh user_id (1 user = 1 conversation dengan admin)
- Status pesan: sent, read
- Polling-based: tidak ada WebSocket, FE polling endpoint /messages/poll
- Gambar disimpan di R2 via cdn.py, URL disimpan di DB
- Semua timestamp pakai timezone Asia/Jakarta
"""

from datetime import datetime
from typing import Optional
from enum import Enum
from uuid import UUID, uuid4

import pytz
from sqlalchemy import ForeignKey
from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg

jakarta_tz = pytz.timezone("Asia/Jakarta")


def get_jakarta_now():
    return datetime.now(jakarta_tz)


# ── Enum status pesan ──────────────────────────────────────────────
class MessageStatus(str, Enum):
    SENT = "sent"      # Pesan terkirim, belum dibaca
    READ = "read"      # Pesan sudah dibaca


# ── Enum pengirim pesan ────────────────────────────────────────────
class SenderRole(str, Enum):
    USER = "user"      # Customer yang kirim
    ADMIN = "admin"    # Admin yang balas


# ── Tabel Conversation (1 per user) ───────────────────────────────
class Conversation(SQLModel, table=True):
    """
    Satu user memiliki tepat satu conversation dengan admin.
    conversation_id dipakai sebagai grouping semua message.
    last_message_at dipakai untuk sorting di sisi admin (inbox view).
    """
    __tablename__ = "conversation"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    )
    user_id: UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("user.uuid", ondelete="CASCADE"),
            nullable=False,
            unique=True,   # 1 user = 1 conversation
            index=True
        )
    )
    # Snapshot nama user untuk tampilan admin — tidak perlu JOIN saat polling
    user_username: str = Field(sa_column=Column(pg.VARCHAR(100), nullable=False))

    # Berapa pesan belum dibaca oleh admin (untuk badge notif)
    unread_by_admin: int = Field(default=0, sa_column=Column(pg.INTEGER, server_default="0"))

    # Berapa pesan belum dibaca oleh user
    unread_by_user: int = Field(default=0, sa_column=Column(pg.INTEGER, server_default="0"))

    # Timestamp pesan terakhir — untuk sort inbox admin
    last_message_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=True)
    )
    # Preview teks pesan terakhir (maks 100 char) — agar tidak perlu JOIN message
    last_message_preview: Optional[str] = Field(
        default=None,
        sa_column=Column(pg.VARCHAR(120), nullable=True)
    )

    created_at: datetime = Field(
        default_factory=get_jakarta_now,
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False)
    )


# ── Tabel Message ──────────────────────────────────────────────────
class Message(SQLModel, table=True):
    """
    Satu pesan dalam sebuah conversation.
    - sender_role menentukan apakah ini dari user atau admin
    - status: sent → read (diupdate saat pihak lawan polling/buka chat)
    - body bisa None kalau hanya kirim gambar
    """
    __tablename__ = "message"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    )
    conversation_id: UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("conversation.uuid", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )
    # Siapa yang kirim: user atau admin
    sender_role: SenderRole = Field(
        sa_column=Column(pg.VARCHAR(10), nullable=False)
    )
    # UUID pengirim: user_id atau admin_id (dari tabel user)
    sender_id: UUID = Field(
        sa_column=Column(pg.UUID(as_uuid=True), nullable=False, index=True)
    )

    # Isi teks pesan (nullable, bisa kirim gambar aja)
    body: Optional[str] = Field(
        default=None,
        sa_column=Column(pg.TEXT, nullable=True)
    )

    status: MessageStatus = Field(
        default=MessageStatus.SENT,
        sa_column=Column(pg.VARCHAR(10), server_default="sent", nullable=False)
    )

    sent_at: datetime = Field(
        default_factory=get_jakarta_now,
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False, index=True)
    )


# ── Tabel MessageImage (maks 2 per message) ────────────────────────
class MessageImage(SQLModel, table=True):
    """
    Gambar yang dilampirkan ke sebuah pesan.
    Maksimal 2 gambar per pesan — divalidasi di service layer.
    image_url = URL publik R2 (dari cdn.upload_file)
    image_key = key di R2 bucket (untuk delete jika pesan dihapus)
    """
    __tablename__ = "message_image"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    )
    message_id: UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("message.uuid", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )
    # URL publik gambar di R2
    image_url: str = Field(sa_column=Column(pg.TEXT, nullable=False))
    # Key R2 untuk keperluan delete
    image_key: str = Field(sa_column=Column(pg.VARCHAR(300), nullable=False))

    uploaded_at: datetime = Field(
        default_factory=get_jakarta_now,
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False)
    )