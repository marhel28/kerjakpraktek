import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlmodel import Field, SQLModel


class Notification(SQLModel, table=True):
    __tablename__ = "notification"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    user_id: uuid.UUID = Field(
        sa_column=Column(
            PgUUID(as_uuid=True),
            ForeignKey("user.uuid", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    title: str = Field(max_length=255)
    content: str = Field(default="", sa_column=Column(Text, nullable=False, default=""))
    type: str = Field(default="general", max_length=32)
    # `metadata` dipakai SQLModel, jadi atribut Python memakai `meta`
    # sedangkan nama kolom database tetap "metadata" (kontrak lama).
    meta: dict = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSONB, nullable=False, server_default=text("'{}'::jsonb")),
    )
    read_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now()),
    )

    __table_args__ = (
        Index("idx_notification_user_created", "user_id", "created_at"),
        Index(
            "idx_notification_user_unread",
            "user_id",
            postgresql_where=text("read_at IS NULL"),
        ),
    )
