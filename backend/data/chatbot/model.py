"""
backend/data/chatbot/model.py
==============================
SQLModel untuk manajemen Knowledge Base chatbot.
Admin bisa menambahkan Q&A pair; sistem menggunakan TurboQuant binary vector
untuk mencari jawaban paling relevan secara lokal (Hamming distance).
"""
import uuid as uuid_module
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


class ChatbotKnowledge(SQLModel, table=True):
    __tablename__ = "chatbot_knowledge"

    uuid: str = Field(
        default_factory=lambda: str(uuid_module.uuid4()),
        primary_key=True,
        index=True,
    )
    question: str = Field(index=True, max_length=500)
    answer: str = Field(max_length=4000)
    category: str = Field(default="general", max_length=60)  # e.g. produk, garansi, layanan, harga

    # TurboQuant: pre-computed 256-bit binary vector (stored as 32-byte hex string)
    bit_vector: Optional[str] = Field(default=None, max_length=64)

    is_active: bool = Field(default=True)
    hit_count: int = Field(default=0)

    created_by: Optional[str] = Field(default=None, max_length=100)  # admin email
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow())


class ChatbotFeedback(SQLModel, table=True):
    __tablename__ = "chatbot_feedback"

    id: Optional[int] = Field(default=None, primary_key=True)
    message_uuid: str = Field(index=True, max_length=60)  # UUID pesan bot yang dievaluasi
    user_uuid: Optional[str] = Field(default=None, max_length=60)
    satisfied: bool  # True = 👍, False = 👎
    query: Optional[str] = Field(default=None, max_length=500)  # query user asli
    bot_reply: Optional[str] = Field(default=None, max_length=4000)  # Jawaban bot yang dievaluasi
    knowledge_uuid: Optional[str] = Field(default=None, max_length=60)  # Jika dijawab dari KB
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())
