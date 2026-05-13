from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4
from datetime import datetime
from typing import Any, Optional
from sqlalchemy import func

class SystemSetting(SQLModel, table=True):
    __tablename__ = "system_setting"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )
    
    key: str = Field(sa_column=Column(pg.VARCHAR(100), unique=True, index=True, nullable=False))
    value: Any = Field(sa_column=Column(pg.JSONB, nullable=False))
    
    description: Optional[str] = Field(default=None, sa_column=Column(pg.TEXT))
    
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    )
