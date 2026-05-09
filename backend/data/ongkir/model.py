from sqlmodel import SQLModel, Field, Column, Relationship, func
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.data.transaksi.model import Transaction


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )

    transaction_uuid: Optional[UUID] = Field(
            default=None,
            sa_column=Column(
                pg.UUID(as_uuid=True),
                ForeignKey("transaction.uuid", ondelete="CASCADE"),
                unique=True,
                nullable=True  # <--- SEKARANG BOLEH KOSONG
            )
        )
    promo_transaction_uuid: Optional[UUID] = Field(default=None, foreign_key="promo_transaction.uuid")
    courier_name: str = Field(sa_column=Column(pg.VARCHAR(50)))
    courier_service: Optional[str] = Field(default=None, sa_column=Column(pg.VARCHAR(50)))
    waybill_number: Optional[str] = Field(
        default=None,
        sa_column=Column(pg.VARCHAR(100), index=True, unique=True)
    )

    delivery_status: str = Field(
        default="PENDING",
        sa_column=Column(pg.VARCHAR(20), server_default="PENDING")
    )

    # ✅ Tambah field ini
    shipping_cost: int = Field(default=0, sa_column=Column(pg.INTEGER, nullable=False, server_default="0"))
    etd: Optional[str] = Field(default=None, sa_column=Column(pg.VARCHAR(50)))  # estimasi tiba

    recipient_name: str = Field(sa_column=Column(pg.VARCHAR(100)))
    recipient_phone: str = Field(sa_column=Column(pg.VARCHAR(20)))
    shipping_address: str = Field(sa_column=Column(pg.TEXT))

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    )

    transaction: Optional["Transaction"] = Relationship(back_populates="shipment")