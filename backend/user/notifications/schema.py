from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class NotificationOut(BaseModel):
    """Bentuk JSON yang sama persis dengan `Notification` di frontend."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    title: str
    content: str = ""
    type: str = "general"
    # Model menyimpan kolom DB "metadata" di atribut `meta`.
    metadata: dict = Field(default_factory=dict, validation_alias="meta")
    read_at: Optional[datetime] = None
    created_at: datetime
