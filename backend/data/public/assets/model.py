from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from sqlalchemy import func, Index, text
from sqlalchemy import Index, text

class Asset(SQLModel, table=True):
    __tablename__ = "asset"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )

    url: str = Field(
        sa_column=Column(pg.TEXT, nullable=False, index=True)
    )

    type: str = Field(
        sa_column=Column(pg.VARCHAR(20), index=True)
    )

    alt_text: Optional[str] = Field(
        default=None,
        sa_column=Column(pg.TEXT)
    )

    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            server_default=func.now(),
            index=True
        )
    )



    __table_args__ = (
        Index(
            "idx_asset_alt_text_search",
            text("to_tsvector('simple', alt_text)"),
            postgresql_using="gin"
        ),
    )