from sqlmodel import SQLModel, Field, Column, Relationship, func
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING



class Banner(SQLModel, table=True):
    __tablename__ = "banner"

    uuid: UUID = Field(default_factory=uuid4, primary_key=True)

    title: Optional[str] = None
    link: str = Field(sa_column=Column(pg.TEXT))  # route frontend

    asset_uuid: UUID = Field(
        sa_column=Column(pg.UUID(as_uuid=True), ForeignKey("asset.uuid"))
    )

    position: int = Field(default=0)  
    is_active: bool = Field(default=True)

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now())
    )

    asset: Optional["Asset"] = Relationship()