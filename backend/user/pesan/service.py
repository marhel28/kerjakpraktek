"""
backend/user/pesan/service.py
==============================
Rules:
- Dieksport sebagai INSTANCE `message_service` agar bisa diimport dengan:
    from .service import message_service
    message_service.send_message(...)
- Semua method async, menerima db: AsyncSession sebagai arg pertama
- Tidak ada state internal — class hanya sebagai namespace/organizer
- Upload gambar ke R2 via backend.db.cdn (upload_file, delete_file)
- Unread counter disimpan denormalized di kolom conversation (O(1) baca)
- Cursor polling berbasis sent_at (timestamp) bukan UUID — manfaatkan index
"""

import uuid as _uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

import pytz
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.cdn import delete_file, upload_file
from backend.user.pesan.model import (
    Conversation,
    Message,
    MessageImage,
    MessageStatus,
    SenderRole,
)
from backend.user.pesan.ws_manager import chat_ws_manager
from backend.user.pesan.schema import (
    ConversationOut,
    MessageImageOut,
    MessageOut,
    PollResponse,
)

jakarta_tz = pytz.timezone("Asia/Jakarta")

# Ekstensi gambar yang diizinkan
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_IMAGE_BYTES    = 5 * 1024 * 1024   # 5 MB


class MessageService:
    """
    Service layer sistem pesan customer ↔ admin.
    Dipakai sebagai singleton: `message_service = MessageService()`.
    """

    # ── Private: validasi + upload satu gambar ke R2 ──────────────
    async def _upload_image(self, file: UploadFile, folder: str = "chat") -> tuple[str, str]:
        """
        Validasi ekstensi & ukuran, lalu upload ke R2.
        Return: (public_url, r2_key)
        """
        ext = (file.filename or "").rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Ekstensi '{ext}' tidak diizinkan. Gunakan: {ALLOWED_EXTENSIONS}",
            )

        content = await file.read()
        if len(content) > MAX_IMAGE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Ukuran gambar maksimal 5 MB.",
            )

        filename  = f"{_uuid.uuid4()}.{ext}"
        url       = await upload_file(
            content,
            folder=folder,
            filename=filename,
            content_type=file.content_type or "image/jpeg",
        )
        key = f"{folder}/{filename}"
        return url, key

    # ── 1. Get or Create Conversation ─────────────────────────────
    async def get_or_create_conversation(
        self,
        db: AsyncSession,
        user_id: UUID,
        user_username: str,
    ) -> Conversation:
        """
        Cari conversation milik user. Kalau belum ada, buat baru.
        1 user = 1 conversation (UNIQUE constraint pada user_id).
        """
        result = await db.execute(
            select(Conversation).where(Conversation.user_id == user_id)
        )
        conv = result.scalar_one_or_none()

        if conv is None:
            conv = Conversation(
                user_id=user_id,
                user_username=user_username,
            )
            db.add(conv)
            await db.commit()
            await db.refresh(conv)

        return conv

    # ── 2. Send Message ────────────────────────────────────────────
    async def send_message(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        sender_id: UUID,
        sender_role: SenderRole,
        body: Optional[str],
        images: list[UploadFile],
    ) -> MessageOut:
        """
        Kirim pesan baru.
        - Upload semua gambar ke R2 dulu; rollback (delete R2) kalau gagal
        - Update snapshot last_message_at, preview, unread counter di Conversation
        - Maks 2 gambar per pesan
        """
        if not body and not images:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Pesan harus berisi teks atau minimal satu gambar.",
            )
        if len(images) > 2:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Maksimal 2 gambar per pesan.",
            )

        # Upload gambar dulu sebelum insert DB
        uploaded: list[tuple[str, str]] = []
        try:
            for img in images:
                url, key = await self._upload_image(img)
                uploaded.append((url, key))
        except HTTPException:
            # Rollback: hapus yang sudah terupload
            for _, key in uploaded:
                await delete_file(key)
            raise

        now = datetime.now(jakarta_tz)

        # Simpan Message
        msg = Message(
            conversation_id=conversation_id,
            sender_role=sender_role,
            sender_id=sender_id,
            body=body,
            status=MessageStatus.SENT,
            sent_at=now,
        )
        db.add(msg)
        await db.flush()   # dapatkan msg.uuid sebelum insert MessageImage

        # Simpan MessageImage
        img_rows: list[MessageImage] = []
        for url, key in uploaded:
            row = MessageImage(message_id=msg.uuid, image_url=url, image_key=key)
            db.add(row)
            img_rows.append(row)

        # Update snapshot di Conversation (denormalized)
        preview      = (body or "")[:100] if body else "[Gambar]"
        unread_col   = (
            Conversation.unread_by_admin
            if sender_role == SenderRole.USER
            else Conversation.unread_by_user
        )
        await db.execute(
            update(Conversation)
            .where(Conversation.uuid == conversation_id)
            .values(
                last_message_at=now,
                last_message_preview=preview,
                **{unread_col.key: unread_col + 1},
            )
        )

        await db.commit()
        await db.refresh(msg)

        # 🔔 EMIT WEBSOCKET EVENT AFTER COMMIT
        # Build message payload for realtime push
        message_payload = {
            "uuid": str(msg.uuid),
            "conversation_id": str(msg.conversation_id),
            "sender_role": msg.sender_role.value,
            "sender_id": str(msg.sender_id),
            "body": msg.body,
            "status": msg.status.value,
            "sent_at": msg.sent_at.isoformat(),
            "images": [
                {
                    "uuid": str(r.uuid),
                    "image_url": r.image_url,
                    "uploaded_at": r.uploaded_at.isoformat(),
                }
                for r in img_rows
            ],
        }

        if sender_role == SenderRole.USER:
            # Notify all connected admins
            await chat_ws_manager.broadcast_to_admins({
                "type": "new_message",
                "data": message_payload,
            })
        else:
            # Notify the specific user in this conversation
            conv_result = await db.execute(
                select(Conversation).where(Conversation.uuid == conversation_id)
            )
            conv = conv_result.scalar_one_or_none()
            if conv:
                await chat_ws_manager.send_to_user(conv.user_id, {
                    "type": "new_message",
                    "data": message_payload,
                })

        return MessageOut(
            uuid=msg.uuid,
            conversation_id=msg.conversation_id,
            sender_role=msg.sender_role,
            sender_id=msg.sender_id,
            body=msg.body,
            status=msg.status,
            sent_at=msg.sent_at,
            images=[
                MessageImageOut(uuid=r.uuid, image_url=r.image_url, uploaded_at=r.uploaded_at)
                for r in img_rows
            ],
        )

    # ── 3. Poll Messages (cursor by sent_at) ───────────────────────
    async def poll_messages(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        after_sent_at: Optional[datetime] = None,
        limit: int = 30,
    ) -> PollResponse:
        """
        Ambil pesan baru setelah `after_sent_at`.
        Kalau after_sent_at=None → ambil 30 pesan terbaru (load awal).
        Batch-load semua gambar dalam satu query (tidak N+1).
        """
        q = select(Message).where(Message.conversation_id == conversation_id)
        if after_sent_at:
            q = q.where(Message.sent_at > after_sent_at)
        q = q.order_by(Message.sent_at.asc()).limit(limit + 1)

        rows = (await db.execute(q)).scalars().all()
        has_more = len(rows) > limit
        rows     = rows[:limit]

        if not rows:
            return PollResponse(messages=[], last_id=None, has_more=False)

        img_map = await self._load_images(db, [r.uuid for r in rows])
        return PollResponse(
            messages=[self._to_out(m, img_map) for m in rows],
            last_id=rows[-1].uuid,
            has_more=has_more,
        )

    # ── 4. Get Message History (load-more / initial) ───────────────
    async def get_message_history(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        before_sent_at: Optional[datetime] = None,
        limit: int = 30,
    ) -> list[MessageOut]:
        """
        Ambil pesan lama sebelum `before_sent_at` untuk fitur scroll-up / load-more.
        Dikembalikan dalam urutan chronological (asc).
        """
        q = select(Message).where(Message.conversation_id == conversation_id)
        if before_sent_at:
            q = q.where(Message.sent_at < before_sent_at)
        q = q.order_by(Message.sent_at.desc()).limit(limit)

        rows = (await db.execute(q)).scalars().all()
        rows = list(reversed(rows))   # kembalikan urutan asc

        if not rows:
            return []

        img_map = await self._load_images(db, [r.uuid for r in rows])
        return [self._to_out(m, img_map) for m in rows]

    # ── 5. Mark Messages as Read ───────────────────────────────────
    async def mark_messages_read(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        reader_role: SenderRole,
        message_ids: list[UUID],
    ) -> int:
        """
        Update status pesan dari lawan bicara menjadi 'read'.
        Sekaligus reset unread counter di Conversation.
        Return: jumlah baris yang diupdate.
        """
        target_sender = (
            SenderRole.USER if reader_role == SenderRole.ADMIN else SenderRole.ADMIN
        )

        result = await db.execute(
            update(Message)
            .where(
                and_(
                    Message.uuid.in_(message_ids),
                    Message.conversation_id == conversation_id,
                    Message.sender_role == target_sender,
                    Message.status == MessageStatus.SENT,
                )
            )
            .values(status=MessageStatus.READ)
            .returning(Message.uuid)
        )
        count = len(result.fetchall())

        if count > 0:
            unread_col = (
                Conversation.unread_by_admin
                if reader_role == SenderRole.ADMIN
                else Conversation.unread_by_user
            )
            await db.execute(
                update(Conversation)
                .where(Conversation.uuid == conversation_id)
                .values({unread_col.key: 0})
            )
            await db.commit()

            # 🔔 EMIT READ EVENT KE WEBSOCKET
            read_payload = {
                "type": "message_read",
                "data": {
                    "conversation_id": str(conversation_id),
                    "message_ids": [str(mid) for mid in message_ids],
                    "reader_role": reader_role.value,
                },
            }
            if reader_role == SenderRole.USER:
                await chat_ws_manager.broadcast_to_admins(read_payload)
            else:
                conv_result = await db.execute(
                    select(Conversation).where(Conversation.uuid == conversation_id)
                )
                conv = conv_result.scalar_one_or_none()
                if conv:
                    await chat_ws_manager.send_to_user(conv.user_id, read_payload)

        return count

    # ── 6. Get Conversation List (admin inbox) ─────────────────────
    async def get_conversation_list(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
    ) -> list[ConversationOut]:
        """
        Semua conversation diurutkan dari yang terbaru aktif.
        Data snapshot sudah ada di kolom conversation — tidak JOIN ke message.
        """
        result = await db.execute(
            select(Conversation)
            .order_by(Conversation.last_message_at.desc().nullslast())
            .offset(skip)
            .limit(limit)
        )
        return [ConversationOut.model_validate(c) for c in result.scalars().all()]

    # ── 7. Get Unread Count ────────────────────────────────────────
    async def get_unread_count(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        reader_role: SenderRole,
    ) -> int:
        """
        Baca unread count langsung dari kolom denormalized — O(1).
        Tidak pakai COUNT(*) query.
        """
        result = await db.execute(
            select(Conversation).where(Conversation.uuid == conversation_id)
        )
        conv = result.scalar_one_or_none()
        if not conv:
            return 0
        return (
            conv.unread_by_admin
            if reader_role == SenderRole.ADMIN
            else conv.unread_by_user
        )

    # ── Private: batch load gambar ─────────────────────────────────
    async def _load_images(
        self,
        db: AsyncSession,
        message_ids: list[UUID],
    ) -> dict[UUID, list[MessageImage]]:
        """
        Load semua MessageImage untuk sekumpulan message_id dalam 1 query.
        Return: dict { message_id → [MessageImage, ...] }
        Menghindari N+1 query.
        """
        if not message_ids:
            return {}
        result = await db.execute(
            select(MessageImage).where(MessageImage.message_id.in_(message_ids))
        )
        img_map: dict[UUID, list[MessageImage]] = {}
        for img in result.scalars().all():
            img_map.setdefault(img.message_id, []).append(img)
        return img_map

    # ── Private: konversi row → MessageOut ─────────────────────────
    def _to_out(
        self,
        m: Message,
        img_map: dict[UUID, list[MessageImage]],
    ) -> MessageOut:
        return MessageOut(
            uuid=m.uuid,
            conversation_id=m.conversation_id,
            sender_role=m.sender_role,
            sender_id=m.sender_id,
            body=m.body,
            status=m.status,
            sent_at=m.sent_at,
            images=[
                MessageImageOut(
                    uuid=i.uuid,
                    image_url=i.image_url,
                    uploaded_at=i.uploaded_at,
                )
                for i in img_map.get(m.uuid, [])
            ],
        )


# ── Singleton — diimport oleh route.py ────────────────────────────
# from .service import message_service
message_service = MessageService()