"""
backend/data/chatbot/router.py
================================
Chatbot router dengan endpoint:
  POST   /chatbot/chat         — Kirim pesan ke PasarBot AI
  GET    /chatbot/suggestions  — Autocomplete suggestions
  POST   /chatbot/feedback     — Submit satisfaction feedback (👍/👎)
  POST   /chatbot/escalate     — Handoff percakapan ke Admin

  [Admin] GET    /chatbot/knowledge       — List semua Q&A entry
  [Admin] POST   /chatbot/knowledge       — Tambah Q&A entry baru
  [Admin] PATCH  /chatbot/knowledge/{uuid} — Update Q&A entry
  [Admin] DELETE /chatbot/knowledge/{uuid} — Hapus (soft delete) Q&A entry
  [Admin] POST   /chatbot/knowledge/init  — Reload TurboQuant index dari DB
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.depedence import get_current_user, get_optional_current_user
from backend.db.main import get_session
from .service import ChatbotRAGService, get_autocomplete_suggestions
from .knowledge_repository import (
    ChatbotKnowledgeRepository,
    ChatbotFeedbackRepository,
    get_kb_index,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])
chatbot_service = ChatbotRAGService()
kb_repo = ChatbotKnowledgeRepository()
fb_repo = ChatbotFeedbackRepository()


# ══════════════════════════════════════════════════════════════
#  SCHEMAS
# ══════════════════════════════════════════════════════════════

class ChatMessageInput(BaseModel):
    role: str
    content: str


class ChatbotRequest(BaseModel):
    message: str
    history: List[ChatMessageInput] = []


class ProductRecommendOut(BaseModel):
    uuid: str
    title: str
    slug: str
    price: int
    original_price: Optional[int] = 0
    discount_percentage: Optional[int] = 0
    image: Optional[str] = None
    brand: Optional[str] = "NO BRAND"
    type: Optional[str] = ""
    specs: dict = {}


class ChatbotResponse(BaseModel):
    reply: str
    products: List[ProductRecommendOut] = []
    needs_escalation: bool = False


class SuggestionResponse(BaseModel):
    suggestions: List[str]


class FeedbackRequest(BaseModel):
    message_uuid: str
    satisfied: bool
    query: Optional[str] = None
    bot_reply: Optional[str] = None
    knowledge_uuid: Optional[str] = None


class FeedbackResponse(BaseModel):
    ok: bool
    message: str


class EscalateRequest(BaseModel):
    last_query: Optional[str] = None  # Isi terakhir query yang tidak memuaskan


class EscalateResponse(BaseModel):
    ok: bool
    message: str


# Knowledge Base schemas
class KnowledgeCreateRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=500)
    answer: str = Field(..., min_length=5, max_length=4000)
    category: str = Field(default="general", max_length=60)


class KnowledgeUpdateRequest(BaseModel):
    question: Optional[str] = Field(default=None, max_length=500)
    answer: Optional[str] = Field(default=None, max_length=4000)
    category: Optional[str] = Field(default=None, max_length=60)
    is_active: Optional[bool] = None


class KnowledgeOut(BaseModel):
    uuid: str
    question: str
    answer: str
    category: str
    is_active: bool
    hit_count: int
    created_by: Optional[str]
    created_at: str
    updated_at: str


# ══════════════════════════════════════════════════════════════
#  CHAT
# ══════════════════════════════════════════════════════════════

@router.post("/chat", response_model=ChatbotResponse)
async def chat_with_bot(
    req: ChatbotRequest,
    current_user=Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_session),
):
    query = req.message.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Pesan tidak boleh kosong")
    if len(query) > 500:
        query = query[:500]

    history_list = [{"role": h.role, "content": h.content} for h in req.history]

    try:
        reply, products, needs_escalation = await chatbot_service.get_response(query, history_list, session=session)
    except Exception as e:
        logger.error(f"[Chat] Error: {e}")
        raise HTTPException(status_code=500, detail="Gagal memproses pesan chatbot")

    recommended = [
        ProductRecommendOut(
            uuid=str(p.get("uuid", "")),
            title=p.get("title", ""),
            slug=p.get("slug", ""),
            price=p.get("price", 0),
            original_price=p.get("original_price", 0),
            discount_percentage=p.get("discount_percentage", 0),
            image=p.get("image"),
            brand=p.get("brand", "NO BRAND"),
            type=p.get("type", ""),
            specs=p.get("specs") or {},
        )
        for p in products
    ]

    return ChatbotResponse(
        reply=reply,
        products=recommended,
        needs_escalation=needs_escalation,
    )


# ══════════════════════════════════════════════════════════════
#  SUGGESTIONS
# ══════════════════════════════════════════════════════════════

@router.get("/suggestions", response_model=SuggestionResponse)
async def autocomplete_suggestions(
    q: Optional[str] = None,
    current_user=Depends(get_optional_current_user),
):
    try:
        sugs = await get_autocomplete_suggestions(q)
        return SuggestionResponse(suggestions=sugs)
    except Exception as e:
        logger.error(f"[Suggestions] Error: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil saran")


# ══════════════════════════════════════════════════════════════
#  FEEDBACK
# ══════════════════════════════════════════════════════════════

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    req: FeedbackRequest,
    current_user=Depends(get_optional_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        await fb_repo.create(
            message_uuid=req.message_uuid,
            satisfied=req.satisfied,
            user_uuid=str(current_user.uuid) if current_user else None,
            query=req.query,
            bot_reply=req.bot_reply,
            knowledge_uuid=req.knowledge_uuid,
            session=session,
        )
        # Jika tidak puas dan dijawab dari knowledge base, log untuk review admin
        if not req.satisfied and req.knowledge_uuid:
            logger.info(f"[Feedback] 👎 on KB entry {req.knowledge_uuid} — query: '{req.query}'")

        return FeedbackResponse(ok=True, message="Feedback berhasil diterima. Terima kasih! 🙏")
    except Exception as e:
        logger.error(f"[Feedback] Error: {e}")
        raise HTTPException(status_code=500, detail="Gagal menyimpan feedback")


# ══════════════════════════════════════════════════════════════
#  ESCALATION
# ══════════════════════════════════════════════════════════════

@router.post("/escalate", response_model=EscalateResponse)
async def escalate_to_admin(
    req: EscalateRequest,
    current_user=Depends(get_optional_current_user),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Silakan login terlebih dahulu untuk meneruskan ke Admin."
        )
    """
    Endpoint eskalasi: User request handoff ke Admin.
    Frontend akan switch ke tab Admin chat setelah endpoint ini dipanggil.
    """
    try:
        user_name = getattr(current_user, "username", "Pengguna")
        logger.info(
            f"[Escalate] User '{user_name}' requested admin handoff. "
            f"Last query: '{req.last_query or 'N/A'}'"
        )
        return EscalateResponse(
            ok=True,
            message=(
                f"Siap Kak {user_name}! Percakapan diteruskan ke Tim Admin. "
                "Mohon tunggu sebentar, Admin akan segera merespons. 🙏"
            ),
        )
    except Exception as e:
        logger.error(f"[Escalate] Error: {e}")
        raise HTTPException(status_code=500, detail="Gagal meneruskan ke admin")


# ══════════════════════════════════════════════════════════════
#  KNOWLEDGE BASE CRUD (Admin Only)
# ══════════════════════════════════════════════════════════════

def _require_admin(user):
    """Pastikan user adalah admin."""
    role = getattr(user, "role", None)
    if role not in ("admin", "superadmin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat mengakses fitur ini",
        )


@router.get("/knowledge", response_model=List[KnowledgeOut])
async def list_knowledge(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    _require_admin(current_user)
    entries = await kb_repo.get_all(session)
    return [
        KnowledgeOut(
            uuid=e.uuid,
            question=e.question,
            answer=e.answer,
            category=e.category,
            is_active=e.is_active,
            hit_count=e.hit_count,
            created_by=e.created_by,
            created_at=e.created_at.isoformat(),
            updated_at=e.updated_at.isoformat(),
        )
        for e in entries
    ]


@router.post("/knowledge", response_model=KnowledgeOut, status_code=201)
async def create_knowledge(
    req: KnowledgeCreateRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    _require_admin(current_user)
    entry = await kb_repo.create(
        question=req.question,
        answer=req.answer,
        category=req.category,
        created_by=getattr(current_user, "email", "admin"),
        session=session,
    )
    return KnowledgeOut(
        uuid=entry.uuid,
        question=entry.question,
        answer=entry.answer,
        category=entry.category,
        is_active=entry.is_active,
        hit_count=entry.hit_count,
        created_by=entry.created_by,
        created_at=entry.created_at.isoformat(),
        updated_at=entry.updated_at.isoformat(),
    )


@router.patch("/knowledge/{uuid}", response_model=KnowledgeOut)
async def update_knowledge(
    uuid: str,
    req: KnowledgeUpdateRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    _require_admin(current_user)
    entry = await kb_repo.update(
        uuid=uuid,
        question=req.question,
        answer=req.answer,
        category=req.category,
        is_active=req.is_active,
        session=session,
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Entry tidak ditemukan")
    return KnowledgeOut(
        uuid=entry.uuid,
        question=entry.question,
        answer=entry.answer,
        category=entry.category,
        is_active=entry.is_active,
        hit_count=entry.hit_count,
        created_by=entry.created_by,
        created_at=entry.created_at.isoformat(),
        updated_at=entry.updated_at.isoformat(),
    )


@router.delete("/knowledge/{uuid}", status_code=204)
async def delete_knowledge(
    uuid: str,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    _require_admin(current_user)
    ok = await kb_repo.delete(uuid, session)
    if not ok:
        raise HTTPException(status_code=404, detail="Entry tidak ditemukan")


@router.post("/knowledge/init", status_code=200)
async def reload_knowledge_index(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Force reload TurboQuant in-memory index dari database."""
    _require_admin(current_user)
    await kb_repo.init_index(session)
    return {"ok": True, "index_size": get_kb_index().size}


# ══════════════════════════════════════════════════════════════
#  ADMIN FEEDBACK LOGS & AI SETTINGS
# ══════════════════════════════════════════════════════════════

from backend.admin.adminSettings.service import AdminSettingService

class FeedbackOut(BaseModel):
    id: int
    message_uuid: str
    user_uuid: Optional[str] = None
    satisfied: bool
    query: Optional[str] = None
    bot_reply: Optional[str] = None
    knowledge_uuid: Optional[str] = None
    created_at: str


class AISettingsSchema(BaseModel):
    provider: str
    api_key: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.6
    max_tokens: int = 4096
    custom_system_prompt: Optional[str] = None


@router.get("/feedback", response_model=List[FeedbackOut])
async def list_feedback_logs(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    _require_admin(current_user)
    logs = await fb_repo.get_all(session)
    return [
        FeedbackOut(
            id=log.id,
            message_uuid=log.message_uuid,
            user_uuid=log.user_uuid,
            satisfied=log.satisfied,
            query=log.query,
            bot_reply=log.bot_reply,
            knowledge_uuid=log.knowledge_uuid,
            created_at=log.created_at.isoformat()
        )
        for log in logs
    ]


@router.delete("/feedback/{id}", status_code=204)
async def delete_feedback_log(
    id: int,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    _require_admin(current_user)
    ok = await fb_repo.delete(id, session)
    if not ok:
        raise HTTPException(status_code=404, detail="Log tidak ditemukan")


@router.get("/settings", response_model=AISettingsSchema)
async def get_ai_settings(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    _require_admin(current_user)
    settings = await AdminSettingService.get_setting(session, "chatbot_ai_settings")
    if not settings:
        return AISettingsSchema(
            provider="groq",
            api_key="***REMOVED***",
            model="qwen-2.5-32b",
            temperature=0.6,
            max_tokens=4096,
            custom_system_prompt=(
                "Kamu adalah PasarBot, asisten AI marketplace PasarCCTV yang cerdas dan ramah.\n"
                "Tugas: Rekomendasikan produk CCTV/keamanan berdasarkan data FACTUAL berikut:\n\n"
                "[DATA PRODUK]\n{products_context}\n\n"
                "[RELASI PRODUK]\n{graph_context}\n\n"
                "ATURAN RESPONS:\n"
                "1. Gunakan format: <think>...</think><decompose>...</decompose><reply>...</reply>\n"
                "2. Dalam <reply>: Bahasa Indonesia, sapa dengan 'Kak', maksimal 3 paragraf\n"
                "3. JANGAN mengarang harga/merek/stok di luar [DATA PRODUK]\n"
                "4. Jika produk tidak ada → katakan dengan sopan, sarankan alternatif\n"
                "5. Jawaban harus informatif, persuasif, dan ringkas"
            )
        )
    return AISettingsSchema(**settings)


@router.put("/settings")
async def update_ai_settings(
    payload: AISettingsSchema,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    _require_admin(current_user)
    await AdminSettingService.update_setting(
        session=session,
        key="chatbot_ai_settings",
        value=payload.dict(),
        description="Pengaturan model AI dan API Key untuk Chatbot PasarBot"
    )
    return {"success": True, "message": "Pengaturan AI berhasil diperbarui"}
