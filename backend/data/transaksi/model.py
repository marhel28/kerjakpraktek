# backend/data/transaksi/model.py

from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import func, ForeignKey

if TYPE_CHECKING:
    from backend.data.ongkir.model import Shipment


class TransactionItem(SQLModel, table=True):
    __tablename__ = "transaction_item"

    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )

    transaction_id: UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("transaction.uuid", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
    )

    stock_id: UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("stock.uuid", ondelete="RESTRICT"),
            nullable=False,
        )
    )

    quantity: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    unit_price: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    subtotal: int = Field(sa_column=Column(pg.INTEGER, nullable=False))

    # ✅ Wajib ada — back_populates ke Transaction.items
    transaction: Optional["Transaction"] = Relationship(back_populates="items")


class Transaction(SQLModel, table=True):
    __tablename__ = "transaction"

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

    order_id: str = Field(
        sa_column=Column(pg.VARCHAR(100), unique=True, nullable=False, index=True)
    )

    gross_amount: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    items_subtotal: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    shipping_cost: int = Field(default=0, sa_column=Column(pg.INTEGER))
    discount_amount: int = Field(default=0, sa_column=Column(pg.INTEGER))

    transaction_status: Optional[str] = Field(default=None, sa_column=Column(pg.VARCHAR(50)))
    payment_type: Optional[str] = Field(default=None, sa_column=Column(pg.VARCHAR(50)))
    transaction_time: Optional[datetime] = Field(default=None, sa_column=Column(pg.TIMESTAMP(timezone=True)))
    settlement_time: Optional[datetime] = Field(default=None, sa_column=Column(pg.TIMESTAMP(timezone=True)))
    fraud_status: Optional[str] = Field(default=None, sa_column=Column(pg.VARCHAR(30)))
    status_code: Optional[str] = Field(default=None, sa_column=Column(pg.VARCHAR(10)))
    status_message: Optional[str] = Field(default=None, sa_column=Column(pg.TEXT))
    raw_response: Optional[dict] = Field(default=None, sa_column=Column(pg.JSONB))

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    )

    # ✅ Relationship ke TransactionItem dan Shipment
    items: List["TransactionItem"] = Relationship(back_populates="transaction")
    shipment: Optional["Shipment"] = Relationship(
        back_populates="transaction",
        sa_relationship_kwargs={"uselist": False}
    )