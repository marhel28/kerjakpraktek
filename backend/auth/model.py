from datetime import datetime
from typing import Optional
from enum import Enum
import pytz
from uuid import UUID, uuid4 
from sqlalchemy import ForeignKey, Index
from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg

jakarta_tz = pytz.timezone("Asia/Jakarta")

def get_jakarta_now():
    return datetime.now(jakarta_tz)

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserType(str, Enum):
    BIASA = "biasa"
    CORPORATE = "corporate"

class User(SQLModel, table=True):
    __tablename__ = "user"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
            unique=True,
            nullable=False
        )
    )
    username: str = Field(index=True, unique=True, nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    password: Optional[str] = Field(
        default=None,
        sa_column=Column(pg.TEXT, nullable=True)
    )
    alamat: Optional[str] = None
    provinsi: Optional[str] = None
    kabupaten: Optional[str] = None
    kecamatan: Optional[str] = None
    nomertlp: Optional[str] = Field(
        default=None,
        sa_column=Column(pg.VARCHAR(15), nullable=True)
    )
    role: UserRole = Field(default=UserRole.USER)
    user_type: UserType = Field(default=UserType.BIASA)

    is_verified: bool = Field(
        default=False,
        sa_column=Column(pg.BOOLEAN, server_default="false", nullable=False)
    )
    google_id: Optional[str] = Field(
        default=None,
        sa_column=Column(pg.VARCHAR(128), unique=True, nullable=True, index=True)
    )
    waktu_create: datetime = Field(
        default_factory=get_jakarta_now,
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False)
    )
    waktu_update: datetime = Field(
        default_factory=get_jakarta_now,
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            onupdate=get_jakarta_now
        )
    )


class UserAddress(SQLModel, table=True):
    __tablename__ = "user_address"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )
    user_id: UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("user.uuid", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )
    location_id: str = Field(
        sa_column=Column(pg.VARCHAR(20), index=True)
    )
    province: Optional[str] = Field(
        default=None, sa_column=Column(pg.VARCHAR(100))
    )
    city: Optional[str] = Field(
        default=None, sa_column=Column(pg.VARCHAR(100))
    )
    district: Optional[str] = Field(
        default=None, sa_column=Column(pg.VARCHAR(100))
    )
    subdistrict: Optional[str] = Field(
        default=None, sa_column=Column(pg.VARCHAR(100))
    )
    label: Optional[str] = Field(
        default=None, sa_column=Column(pg.VARCHAR(200))
    )
    zip_code: str = Field(sa_column=Column(pg.VARCHAR(10)))
    full_address: str = Field(sa_column=Column(pg.TEXT))
    is_default: bool = Field(
        default=False,
        sa_column=Column(pg.BOOLEAN, server_default="false")
    )
    created_at: datetime = Field(
        default_factory=get_jakarta_now,
        sa_column=Column(pg.TIMESTAMP(timezone=True))
    )

    __table_args__ = (
        Index("idx_user_address_user_default", "user_id", "is_default"),
    )
    



class UserMap(SQLModel, table=True):
    __tablename__ = "user_maps"

    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
    )
    local_user_id: str = Field(index=True, unique=True)   # ← str, bukan bigint
    supabase_user_id: str = Field(index=True, unique=True)
    supabase_password: str