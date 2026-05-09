from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from sqlalchemy import func

# ==========================================
# 🧱 DATABASE MODEL
# ==========================================
class MainBottomBanner(SQLModel, table=True):
    __tablename__ = "main_bottom_banner"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )
    title: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    image_url: str = Field(sa_column=Column(pg.TEXT, nullable=False))
    route_link: str = Field(sa_column=Column(pg.TEXT, nullable=False))
    is_active: bool = Field(default=True, sa_column=Column(pg.BOOLEAN, index=True))
    sort_order: int = Field(default=0, sa_column=Column(pg.INTEGER))
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now())
    )

# ==========================================
# 📄 SCHEMAS
# ==========================================
class BannerCreate(SQLModel):
    """Digunakan untuk membuat banner tanpa file (programmatic)."""
    title: str
    image_url: str
    route_link: str
    is_active: bool = True
    sort_order: int = 0

class BannerCreateForm(SQLModel):
    """Digunakan di form multipart admin (tanpa image_url)."""
    title: str
    route_link: str
    is_active: bool = True
    sort_order: int = 0

class BannerUpdate(SQLModel):
    title: Optional[str] = None
    image_url: Optional[str] = None
    route_link: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None