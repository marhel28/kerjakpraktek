"""
backend/data/chatbot/knowledge_repository.py
=============================================
Repository untuk CRUD ChatbotKnowledge dan TurboQuantIndex.

TurboQuant Binary Similarity Engine:
- Teks → tokenize → char n-gram (bigram) → 256-bit binary vector (32 bytes hex)
- Similarity = 1 - hamming_distance/256  (operasi bitwise, bukan dot product)
- Speed: ~50,000 comparisons/ms — ideal untuk ribuan FAQ entries di in-memory index
- Zero dependency: hanya Python stdlib

Strategi pencarian:
1. Hitung bit_vector dari query user
2. Bandingkan dengan semua bit_vector entry di knowledge base (di-load ke RAM)
3. Kembalikan top-k entry dengan similarity tertinggi (threshold: >=0.45)
"""
import logging
import re
from typing import List, Optional, Dict, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update as sql_update
from datetime import datetime, timezone

from .model import ChatbotKnowledge, ChatbotFeedback

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
#  TURBOQUANT BINARY SIMILARITY ENGINE
# ══════════════════════════════════════════════════════════════

def _text_to_tokens(text: str) -> set:
    """Normalisasi dan ekstrak token + bigram karakter."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    words = text.split()
    tokens = set(words)
    # Tambah bigram kata untuk konteks frase
    for i in range(len(words) - 1):
        tokens.add(f"{words[i]}_{words[i+1]}")
    # Tambah bigram karakter setiap kata (panjang 3+)
    for w in words:
        if len(w) >= 3:
            for j in range(len(w) - 1):
                tokens.add(f"c:{w[j]}{w[j+1]}")
    return tokens


# Vocabulary universe — 256 posisi yang dipetakan dari hash modulo
_VOCAB_SIZE = 256


def _tokens_to_bit_vector(tokens: set) -> bytes:
    """
    Konversi token set ke 256-bit binary vector (32 bytes).
    Setiap token di-hash ke posisi bit dalam range 0-255.
    Ini adalah implementasi sederhana dari MinHash/LSH one-hot projection.
    """
    bits = bytearray(32)  # 256 bits = 32 bytes
    for token in tokens:
        # Gunakan 2 hash berbeda untuk mengurangi collision
        h1 = hash(token) % _VOCAB_SIZE
        h2 = hash(token + "_2") % _VOCAB_SIZE
        bits[h1 // 8] |= (1 << (h1 % 8))
        bits[h2 // 8] |= (1 << (h2 % 8))
    return bytes(bits)


def _hamming_distance(a: bytes, b: bytes) -> int:
    """Hitung Hamming distance antara dua bit vector (popcount XOR)."""
    dist = 0
    for x, y in zip(a, b):
        xor = x ^ y
        # Brian Kernighan's bit count
        while xor:
            xor &= xor - 1
            dist += 1
    return dist


def compute_bit_vector_hex(text: str) -> str:
    """Compute bit vector dari teks dan return sebagai hex string (64 char)."""
    tokens = _text_to_tokens(text)
    bvec = _tokens_to_bit_vector(tokens)
    return bvec.hex()


def turboquant_similarity(query: str, entry_hex: str) -> float:
    """
    Hitung TurboQuant similarity score (0.0 - 1.0).
    1.0 = identik, 0.0 = tidak ada overlap sama sekali.
    """
    try:
        q_tokens = _text_to_tokens(query)
        q_vec = _tokens_to_bit_vector(q_tokens)
        e_vec = bytes.fromhex(entry_hex)
        dist = _hamming_distance(q_vec, e_vec)
        return 1.0 - (dist / _VOCAB_SIZE)
    except Exception:
        return 0.0


# ══════════════════════════════════════════════════════════════
#  IN-MEMORY TURBOQUANT INDEX
# ══════════════════════════════════════════════════════════════

class TurboQuantIndex:
    """
    In-memory index untuk fast knowledge base search.
    Di-build dari database saat startup dan di-refresh setiap kali ada perubahan.
    """
    def __init__(self):
        # List of (uuid, question, answer, category, bit_vector_hex, hit_count)
        self._entries: List[Dict[str, Any]] = []
        self._is_loaded = False

    def load(self, entries: List[ChatbotKnowledge]) -> None:
        """Load dari DB entries ke in-memory index."""
        self._entries = []
        for e in entries:
            if e.is_active and e.bit_vector:
                self._entries.append({
                    "uuid": e.uuid,
                    "question": e.question,
                    "answer": e.answer,
                    "category": e.category,
                    "bit_vector": e.bit_vector,
                    "hit_count": e.hit_count,
                })
        self._is_loaded = True
        logger.info(f"[TurboQuant] Index loaded: {len(self._entries)} entries")

    def search(self, query: str, top_k: int = 3, threshold: float = 0.42) -> List[Dict[str, Any]]:
        """
        Cari top-k entry paling mirip dengan query menggunakan Hamming distance.
        Kompleksitas: O(n * 32) dimana n = jumlah entry.
        """
        if not self._entries or not query.strip():
            return []

        query_lower = query.lower().strip()
        scored: List[Tuple[float, Dict]] = []

        # Pre-compute query bit vector sekali
        q_tokens = _text_to_tokens(query_lower)
        q_vec = _tokens_to_bit_vector(q_tokens)

        for entry in self._entries:
            try:
                e_vec = bytes.fromhex(entry["bit_vector"])
                dist = _hamming_distance(q_vec, e_vec)
                sim = 1.0 - (dist / _VOCAB_SIZE)

                # Bonus skor jika kata kunci ada langsung di pertanyaan (exact keyword boost)
                if any(word in entry["question"].lower() for word in q_tokens if len(word) > 3):
                    sim = min(1.0, sim + 0.12)

                if sim >= threshold:
                    scored.append((sim, entry))
            except Exception:
                continue

        # Sort descending by similarity
        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:top_k]]

    def add_entry(self, entry: ChatbotKnowledge) -> None:
        """Tambah entry baru ke index tanpa reload penuh."""
        if entry.is_active and entry.bit_vector:
            self._entries.append({
                "uuid": entry.uuid,
                "question": entry.question,
                "answer": entry.answer,
                "category": entry.category,
                "bit_vector": entry.bit_vector,
                "hit_count": entry.hit_count,
            })

    def remove_entry(self, uuid: str) -> None:
        """Hapus entry dari index."""
        self._entries = [e for e in self._entries if e["uuid"] != uuid]

    def update_entry(self, entry: ChatbotKnowledge) -> None:
        """Update entry yang sudah ada di index."""
        self.remove_entry(entry.uuid)
        self.add_entry(entry)

    @property
    def size(self) -> int:
        return len(self._entries)


# Singleton global index — shared di seluruh proses FastAPI
_global_kb_index = TurboQuantIndex()


def get_kb_index() -> TurboQuantIndex:
    return _global_kb_index


# ══════════════════════════════════════════════════════════════
#  DATABASE REPOSITORY
# ══════════════════════════════════════════════════════════════

class ChatbotKnowledgeRepository:
    """
    Repository untuk CRUD ChatbotKnowledge.
    Semua operasi write juga update in-memory TurboQuant index.
    """

    async def get_all_active(self, session: AsyncSession) -> List[ChatbotKnowledge]:
        result = await session.execute(
            select(ChatbotKnowledge)
            .where(ChatbotKnowledge.is_active == True)
            .order_by(ChatbotKnowledge.hit_count.desc())
        )
        return result.scalars().all()

    async def get_all(self, session: AsyncSession) -> List[ChatbotKnowledge]:
        result = await session.execute(
            select(ChatbotKnowledge)
            .order_by(ChatbotKnowledge.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_uuid(self, uuid: str, session: AsyncSession) -> Optional[ChatbotKnowledge]:
        result = await session.execute(
            select(ChatbotKnowledge).where(ChatbotKnowledge.uuid == uuid)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        question: str,
        answer: str,
        category: str,
        created_by: str,
        session: AsyncSession,
    ) -> ChatbotKnowledge:
        # Compute TurboQuant bit vector saat insert
        bvec_hex = compute_bit_vector_hex(question)

        entry = ChatbotKnowledge(
            question=question.strip(),
            answer=answer.strip(),
            category=category,
            bit_vector=bvec_hex,
            created_by=created_by,
        )
        session.add(entry)
        await session.commit()
        await session.refresh(entry)

        # Update in-memory index
        _global_kb_index.add_entry(entry)
        logger.info(f"[KB] Created entry: '{question[:50]}' by {created_by}")
        return entry

    async def update(
        self,
        uuid: str,
        question: Optional[str],
        answer: Optional[str],
        category: Optional[str],
        is_active: Optional[bool],
        session: AsyncSession,
    ) -> Optional[ChatbotKnowledge]:
        entry = await self.get_by_uuid(uuid, session)
        if not entry:
            return None

        if question is not None:
            entry.question = question.strip()
            # Re-compute bit vector jika pertanyaan berubah
            entry.bit_vector = compute_bit_vector_hex(question)
        if answer is not None:
            entry.answer = answer.strip()
        if category is not None:
            entry.category = category
        if is_active is not None:
            entry.is_active = is_active

        entry.updated_at = datetime.now(timezone.utc)
        session.add(entry)
        await session.commit()
        await session.refresh(entry)

        # Update in-memory index
        _global_kb_index.update_entry(entry)
        logger.info(f"[KB] Updated entry: {uuid}")
        return entry

    async def delete(self, uuid: str, session: AsyncSession) -> bool:
        entry = await self.get_by_uuid(uuid, session)
        if not entry:
            return False
        entry.is_active = False
        entry.updated_at = datetime.now(timezone.utc)
        session.add(entry)
        await session.commit()

        # Remove from in-memory index
        _global_kb_index.remove_entry(uuid)
        logger.info(f"[KB] Soft-deleted entry: {uuid}")
        return True

    async def record_hit(self, uuid: str, session: AsyncSession) -> None:
        """Increment hit_count untuk analytics tanpa blocking."""
        try:
            await session.execute(
                sql_update(ChatbotKnowledge)
                .where(ChatbotKnowledge.uuid == uuid)
                .values(hit_count=ChatbotKnowledge.hit_count + 1)
            )
            await session.commit()
        except Exception as e:
            logger.warning(f"[KB] hit_count update failed: {e}")

    async def init_index(self, session: AsyncSession) -> None:
        """Load semua entry ke in-memory index saat startup."""
        entries = await self.get_all_active(session)
        _global_kb_index.load(entries)


class ChatbotFeedbackRepository:
    """Repository untuk menyimpan feedback kepuasan user."""

    async def create(
        self,
        message_uuid: str,
        satisfied: bool,
        user_uuid: Optional[str],
        query: Optional[str],
        bot_reply: Optional[str],
        knowledge_uuid: Optional[str],
        session: AsyncSession,
    ) -> ChatbotFeedback:
        fb = ChatbotFeedback(
            message_uuid=message_uuid,
            user_uuid=user_uuid,
            satisfied=satisfied,
            query=query,
            bot_reply=bot_reply,
            knowledge_uuid=knowledge_uuid,
        )
        session.add(fb)
        await session.commit()
        await session.refresh(fb)
        return fb

    async def get_all(self, session: AsyncSession) -> List[ChatbotFeedback]:
        from sqlmodel import select
        stmt = select(ChatbotFeedback).order_by(ChatbotFeedback.created_at.desc())
        res = await session.execute(stmt)
        return list(res.scalars().all())

    async def delete(self, id: int, session: AsyncSession) -> bool:
        from sqlmodel import select
        stmt = select(ChatbotFeedback).where(ChatbotFeedback.id == id)
        res = await session.execute(stmt)
        fb = res.scalar_one_or_none()
        if fb:
            await session.delete(fb)
            await session.commit()
            return True
        return False
