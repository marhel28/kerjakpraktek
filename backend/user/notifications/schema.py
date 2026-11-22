from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NotificationOut(BaseModel):
    """Bentuk JSON yang sama persis dengan `Notification` di frontend."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID
    title: str
    content: str = ""
    type: str = "general"
    # Dibangun eksplisit di _as_dict: atribut ORM `meta` → field `metadata`.
    metadata: dict = Field(default_factory=dict)
    read_at: Optional[datetime] = None
    created_at: datetime
