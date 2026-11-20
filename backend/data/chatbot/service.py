"""
backend/data/chatbot/service.py
================================
PasarBot RAG Service — Arsitektur Multi-Agent dengan TurboQuant Knowledge Base.

Urutan klasifikasi query (prioritas dari atas ke bawah):
  1. Greeting                → Respons lokal instan
  2. Eskalasi/Keluhan        → Tawarkan handoff ke Admin
  3. Knowledge Base (TurboQuant) → Jawaban yang ditambahkan Admin
  4. FAQ Lokal (Jaccard)     → FAQ hardcoded sistem
  5. Transaksional (harga/stok/spek) → Manticore direct query
  6. LLM Groq (CURE Protocol) → Rekomendasi kompleks
  7. Local Fallback          → Jika semua gagal

Strategi: "API sebagai last resort, lokal sebagai first response"
"""
import logging
import os
import re
import httpx
from typing import List, Dict, Any, Tuple, Optional

from backend.data.stock.service import StockService
from .knowledge_repository import get_kb_index

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
#  GREETING PATTERNS
# ══════════════════════════════════════════════════════════════

GREETING_TOKENS = {
    "hi", "hello", "halo", "hai", "hei", "pagi", "siang", "sore", "malam",
    "permisi", "test", "ping", "hola", "p", "hay", "hey", "assalamualaikum",
    "waalaikumsalam", "selamat", "ola", "hallo",
}

GREETING_PHRASES = [
    "selamat pagi", "selamat siang", "selamat sore", "selamat malam",
    "selamat datang", "ada yang bisa", "bisa bantu", "minta tolong",
]


def _is_greeting(query: str) -> bool:
    q = re.sub(r"[^\w\s]", "", query.lower().strip())
    tokens = q.split()
    if not tokens:
        return False
    if len(tokens) == 1 and tokens[0] in GREETING_TOKENS:
        return True
    if len(tokens) <= 3 and all(t in GREETING_TOKENS for t in tokens):
        return True
    if any(phrase in q for phrase in GREETING_PHRASES):
        return True
    return False


# ══════════════════════════════════════════════════════════════
#  ESCALATION / COMPLAINT DETECTION
# ══════════════════════════════════════════════════════════════

ESCALATION_KEYWORDS = [
    "tidak membantu", "kurang membantu", "tidak puas", "tidak sesuai",
    "tidak ada jawaban", "salah jawab", "gagal", "error", "tidak bisa",
    "tidak work", "not working", "complaint", "komplain", "kecewa",
    "mengecewakan", "minta tolong admin", "hubungi admin", "bicara admin",
    "chat admin", "cs manusia", "customer service", "cs asli", "orang asli",
    "bukan bot", "ganti ke manusia", "tidak menjawab", "jawaban salah",
    "salah info", "informasi salah", "bukan itu", "itu bukan jawaban",
    "tidak relevan", "tidak nyambung", "kurang jelas", "bingung",
    "tidak ada solusi", "kendala", "masalah", "problem", "bantu saya",
    "tolong", "darurat", "urgent", "segera",
]


def _detect_escalation(query: str) -> bool:
    q = query.lower()
    return any(kw in q for kw in ESCALATION_KEYWORDS)


# ══════════════════════════════════════════════════════════════
#  FAQ CORPUS (Loaded from JSON file)
# ══════════════════════════════════════════════════════════════

import json

FAQ_JSON_PATH = os.path.join(os.path.dirname(__file__), "faq.json")
FAQ_ITEMS: List[Dict[str, Any]] = []

try:
    if os.path.exists(FAQ_JSON_PATH):
        with open(FAQ_JSON_PATH, "r", encoding="utf-8") as f:
            FAQ_ITEMS = json.load(f)
        logger.info(f"[FAQ] Loaded {len(FAQ_ITEMS)} items from JSON.")
    else:
        logger.warning(f"[FAQ] faq.json not found at {FAQ_JSON_PATH}")
except Exception as e:
    logger.error(f"[FAQ] Error loading faq.json: {e}")


def find_matching_faq(query: str) -> Optional[Dict[str, Any]]:
    q_lower = query.lower().strip()
    clean_q = re.sub(r"[^\w\s]", "", q_lower)
    q_tokens = set(clean_q.split())

    if not q_tokens:
        return None

    best_score = 0.0
    best_faq = None

    for faq in FAQ_ITEMS:
        # Score 1: keyword exact match
        kw_matches = sum(1 for kw in faq["keywords"] if kw in clean_q)
        kw_score = kw_matches / len(faq["keywords"]) if faq["keywords"] else 0.0

        # Score 2: Jaccard dengan pertanyaan
        fq_clean = re.sub(r"[^\w\s]", "", faq["question"].lower())
        fq_tokens = set(fq_clean.split())
        inter = q_tokens & fq_tokens
        union = q_tokens | fq_tokens
        jaccard = len(inter) / len(union) if union else 0.0

        score = kw_score * 0.65 + jaccard * 0.35

        # Exact single keyword boost
        if any(kw == clean_q for kw in faq["keywords"]):
            score = 1.0

        if score > best_score:
            best_score = score
            best_faq = faq

    return best_faq if best_score >= 0.30 else None


# ══════════════════════════════════════════════════════════════
#  AUTOCOMPLETE SUGGESTIONS
# ══════════════════════════════════════════════════════════════

async def get_autocomplete_suggestions(q: Optional[str] = None) -> List[str]:
    """
    Return daftar saran autocomplete yang relevan dengan input user.
    Kombinasi: Knowledge Base questions + FAQ corpus + product queries.
    """
    suggestions = []

    if not q or not q.strip():
        # Default suggestions — pertanyaan paling sering
        kb_index = get_kb_index()
        if kb_index.size > 0:
            top_kb = sorted(kb_index._entries, key=lambda x: x["hit_count"], reverse=True)[:3]
            suggestions = [e["question"] for e in top_kb]

        defaults = [
            "Bagaimana cara membeli / memesan produk?",
            "Berapa biaya jasa pasang CCTV?",
            "Cara klaim garansi produk",
            "Hubungi CS via WhatsApp?",
            "Bagaimana cara melacak pesanan?",
        ]
        for d in defaults:
            if d not in suggestions:
                suggestions.append(d)

        return suggestions[:5]

    q_lower = q.lower().strip()

    # 1. Knowledge Base TurboQuant search
    kb_index = get_kb_index()
    kb_results = kb_index.search(q_lower, top_k=2, threshold=0.35)
    for res in kb_results:
        suggestions.append(res["question"])

    # 2. FAQ corpus match
    for faq in FAQ_ITEMS:
        if any(q_lower in kw for kw in faq["keywords"]) or q_lower in faq["question"].lower():
            if faq["question"] not in suggestions:
                suggestions.append(faq["question"])

    # 3. Product autocomplete via Manticore
    try:
        agent = ManticoreRetrievalAgent()
        products = await agent.retrieve_relevant_products(q_lower, limit=2)
        for p in products:
            title = p.get("title", "")
            brand = p.get("brand", "")
            label = f"{brand} {title}".strip() if brand else title
            q1 = f"Harga {label}?"
            q2 = f"Stok {label} masih ada?"
            if q1 not in suggestions:
                suggestions.append(q1)
            if q2 not in suggestions and len(suggestions) < 5:
                suggestions.append(q2)
    except Exception as e:
        logger.error(f"[Suggestions] Manticore error: {e}")

    # Deduplicate & limit
    seen: set = set()
    result = []
    for s in suggestions:
        if s not in seen:
            seen.add(s)
            result.append(s)

    return result[:5]


# ══════════════════════════════════════════════════════════════
#  RETRIEVAL AGENT (Manticore)
# ══════════════════════════════════════════════════════════════

class ManticoreRetrievalAgent:
    """Retrieval Agent: hybrid search via Manticore / StockService."""

    def __init__(self):
        self.stock_service = StockService()

    async def retrieve_relevant_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            res = await self.stock_service.search_stocks_es(q=query, limit=limit)
            return res.get("items", [])
        except Exception as e:
            logger.error(f"[Retrieval] Manticore error: {e}")
            return []


# ══════════════════════════════════════════════════════════════
#  KNOWLEDGE GRAPH AGENT
# ══════════════════════════════════════════════════════════════

class KnowledgeGraphAgent:
    """Build local KG triples dari produk untuk reasoning LLM."""

    def build_local_graph(self, products: List[Dict[str, Any]]) -> List[Tuple[str, str, str]]:
        triples = []
        for p in products:
            title = p.get("title", "")
            brand = p.get("brand", "NO BRAND")
            category = p.get("category", "")
            specs = p.get("specs") or {}

            triples.append((title, "merek", brand))
            if category:
                triples.append((title, "kategori", category))
            for k, v in specs.items():
                triples.append((title, f"spec_{k.lower()}", str(v)))
        return triples

    def format_graph_context(self, triples: List[Tuple[str, str, str]]) -> str:
        if not triples:
            return "Tidak ada relasi KG yang terdeteksi."
        lines = [f"({s}) --[{r}]--> ({o})" for s, r, o in triples[:12]]
        return "\n".join(lines)


# ══════════════════════════════════════════════════════════════
#  ANTI-HALUSINASI GENERATOR (Groq LLM + CURE Protocol)
# ══════════════════════════════════════════════════════════════

class AntiHalusinasiGenerator:
    """
    Generator via Groq API dengan protokol CURE (XML-structured reply).
    Dilengkapi verifikasi harga post-generation ("Lie to Me" detection).
    """

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=20.0)

    async def generate_response(
        self,
        query: str,
        products: List[Dict[str, Any]],
        graph_context: str,
        history: List[Dict[str, str]],
        ai_settings: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:

        if not ai_settings:
            ai_settings = {
                "provider": "groq",
                "api_key": os.getenv("GROQ_API_KEY", ""),
                "model": "qwen-2.5-32b",
                "temperature": 0.6,
                "max_tokens": 4096,
                "custom_system_prompt": None
            }

        provider = ai_settings.get("provider", "groq").lower()
        api_key = ai_settings.get("api_key")
        model = ai_settings.get("model")
        temperature = ai_settings.get("temperature", 0.6)
        max_tokens = ai_settings.get("max_tokens", 4096)
        custom_system_prompt = ai_settings.get("custom_system_prompt")

        # Map provider to base url and default models
        if provider == "openai":
            base_url = "https://api.openai.com/v1"
            if not model:
                model = "gpt-4o-mini"
            auth_header = f"Bearer {api_key}"
        elif provider == "gemini":
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai"
            if not model:
                model = "gemini-1.5-flash"
            auth_header = f"Bearer {api_key}"
        elif provider == "deepseek":
            base_url = "https://api.deepseek.com/v1"
            if not model:
                model = "deepseek-chat"
            auth_header = f"Bearer {api_key}"
        else:  # groq
            base_url = "https://api.groq.com/openai/v1"
            if not model:
                model = "qwen-2.5-32b"
            auth_header = f"Bearer {api_key or os.getenv('GROQ_API_KEY', '')}"

        # Build factual product context
        factual_context = []
        product_map: Dict[str, Dict] = {}

        for idx, p in enumerate(products):
            title = p.get("title", "")
            price = p.get("price", 0)
            brand = p.get("brand", "NO BRAND")
            specs = p.get("specs") or {}
            specs_str = " | ".join(f"{k}: {v}" for k, v in list(specs.items())[:4])
            stok = p.get("stok", 0)

            product_map[title.lower()] = {
                "price": price,
                "brand": brand.lower(),
                "uuid": p.get("uuid"),
                "image": p.get("image"),
                "slug": p.get("slug"),
                "discount_percentage": p.get("discount_percentage", 0),
                "original_price": p.get("original_price", 0),
            }

            factual_context.append(
                f"[{idx+1}] {brand} {title} | Harga: Rp {price:,} | "
                f"Stok: {stok} unit | {specs_str}"
            )

        context_str = "\n".join(factual_context) if factual_context else "Tidak ada produk yang cocok."

        # Parse custom prompt or default
        if custom_system_prompt and "{products_context}" in custom_system_prompt:
            system_prompt = custom_system_prompt.replace("{products_context}", context_str).replace("{graph_context}", graph_context)
        else:
            system_prompt = (
                "Kamu adalah PasarBot, asisten AI marketplace PasarCCTV yang cerdas dan ramah.\n"
                "Tugas: Rekomendasikan produk CCTV/keamanan berdasarkan data FACTUAL berikut:\n\n"
                f"[DATA PRODUK]\n{context_str}\n\n"
                f"[RELASI PRODUK]\n{graph_context}\n\n"
                "ATURAN RESPONS:\n"
                "1. Gunakan format: <think>...</think><decompose>...</decompose><reply>...</reply>\n"
                "2. Dalam <reply>: Bahasa Indonesia, sapa dengan 'Kak', maksimal 3 paragraf\n"
                "3. JANGAN mengarang harga/merek/stok di luar [DATA PRODUK]\n"
                "4. Jika produk tidak ada → katakan dengan sopan, sarankan alternatif\n"
                "5. Jawaban harus informatif, persuasif, dan ringkas"
            )

        messages = [{"role": "system", "content": system_prompt}]
        for h in history[-4:]:
            messages.append({
                "role": "user" if h.get("role") == "user" else "assistant",
                "content": h.get("content", ""),
            })
        messages.append({"role": "user", "content": query})

        try:
            res = await self.client.post(
                f"{base_url}/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_completion_tokens": max_tokens,
                    "top_p": 0.95,
                },
                headers={
                    "Content-Type": "application/json",
                    "Authorization": auth_header,
                },
            )

            if res.status_code == 200:
                raw = res.json()["choices"][0]["message"]["content"]
                reply = re.search(r"<reply>(.*?)</reply>", raw, re.DOTALL)
                text = reply.group(1).strip() if reply else raw
                text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
                text = re.sub(r"<decompose>.*?</decompose>", "", text, flags=re.DOTALL)
                text = text.replace("<reply>", "").replace("</reply>", "").strip()
                text = self._verify_claims(text, product_map)
                return text, products
            else:
                logger.error(f"[{provider}] {res.status_code}: {res.text[:200]}")
        except Exception as e:
            logger.error(f"[{provider}] API call failed: {e}")

        return self._local_fallback(query, products), products

    def _verify_claims(self, text: str, product_map: Dict) -> str:
        verified = text
        for title, info in product_map.items():
            escaped = re.escape(title)
            pattern = rf"(?i)({escaped}.*?Rp\s*?)([0-9\.,]+)"

            def replace_price(m):
                prefix = m.group(1)
                raw = m.group(2).replace(".", "").replace(",", "")
                try:
                    mentioned = int(raw)
                    actual = info["price"]
                    if mentioned != actual:
                        logger.warning(f"[LieToMe] Harga dikoreksi: {mentioned} → {actual}")
                        return f"{prefix}{actual:,}"
                except ValueError:
                    pass
                return m.group(0)

            verified = re.sub(pattern, replace_price, verified)
        return verified

    def _local_fallback(self, query: str, products: List[Dict]) -> str:
        if not products:
            return (
                f"Maaf Kak, produk untuk pencarian **'{query}'** belum kami temukan di katalog. "
                "Coba kata kunci lain seperti 'kamera outdoor', 'cctv wifi', atau 'nvr'. "
                "Atau chat Admin untuk rekomendasi langsung. 🙏"
            )

        lines = [f"Berikut pilihan produk untuk pencarian **'{query}'**:\n"]
        for p in products[:3]:
            brand = p.get("brand", "")
            title = p.get("title", "")
            price = p.get("price", 0)
            disc = p.get("discount_percentage", 0)
            uuid = p.get("uuid", "")
            label = f"{brand} {title}".strip() if brand else title
            price_str = f"Rp {price:,}"
            if disc > 0:
                orig = p.get("original_price", 0)
                price_str += f" ~~Rp {orig:,}~~ (-{disc}%)"
            lines.append(f"• **{label}** — {price_str}")
        lines.append("\nAda pertanyaan lebih lanjut? Saya siap membantu Kak! 😊")
        return "\n".join(lines)


# ══════════════════════════════════════════════════════════════
#  FORMAT HELPERS — Industry Standard Response Formatter
# ══════════════════════════════════════════════════════════════

def _format_price_response(products: List[Dict[str, Any]], query: str) -> str:
    """Format respons harga yang bersih dan profesional."""
    if not products:
        return (
            f"Maaf Kak, produk **'{query}'** tidak ditemukan di katalog kami saat ini.\n"
            "Coba cari dengan nama merek atau tipe produk, atau tanya Admin untuk bantuan. 🙏"
        )

    lines = [f"💰 **Info Harga** — hasil pencarian '{query}':\n"]
    for p in products[:4]:
        brand = p.get("brand", "")
        title = p.get("title", "")
        price = p.get("price", 0)
        orig = p.get("original_price", 0)
        disc = p.get("discount_percentage", 0)
        stok = p.get("stok", 0)
        uuid = p.get("uuid", "")
        label = f"{brand} {title}".strip() if brand else title

        line = f"**{label}**\n"
        if disc > 0 and orig > 0:
            line += f"  Rp {price:,} ~~Rp {orig:,}~~ • Hemat {disc}%\n"
        else:
            line += f"  Rp {price:,}\n"

        status = "✅ Tersedia" if stok > 0 else "❌ Habis"
        line += f"  {status} ({stok} unit)"
        if uuid:
            line += f" • [Lihat Detail](/product/{uuid})"
        lines.append(line)

    return "\n\n".join(lines)


def _format_stock_response(products: List[Dict[str, Any]], query: str) -> str:
    """Format respons stok yang bersih."""
    if not products:
        return (
            f"Maaf Kak, produk **'{query}'** tidak ditemukan di katalog kami.\n"
            "Hubungi Admin untuk pengecekan stok langsung. 🙏"
        )

    lines = [f"📦 **Ketersediaan Stok** — '{query}':\n"]
    for p in products[:4]:
        brand = p.get("brand", "")
        title = p.get("title", "")
        stok = p.get("stok", 0)
        price = p.get("price", 0)
        uuid = p.get("uuid", "")
        label = f"{brand} {title}".strip() if brand else title

        status = "✅ Ready" if stok > 0 else "❌ Habis"
        line = f"**{label}** — {status} ({stok} unit) • Rp {price:,}"
        if uuid:
            line += f" • [Detail](/product/{uuid})"
        lines.append(line)

    return "\n\n".join(lines)


def _format_specs_response(products: List[Dict[str, Any]], query: str) -> str:
    """Format respons spesifikasi yang terstruktur."""
    if not products:
        return (
            f"Maaf Kak, detail spesifikasi untuk **'{query}'** tidak ditemukan.\n"
            "Coba ketik nama produk lebih spesifik atau tanya Admin. 🙏"
        )

    lines = [f"🔍 **Spesifikasi Produk** — '{query}':\n"]
    for p in products[:2]:  # Batasi 2 untuk spec (lebih detail)
        brand = p.get("brand", "")
        title = p.get("title", "")
        price = p.get("price", 0)
        stok = p.get("stok", 0)
        uuid = p.get("uuid", "")
        specs = p.get("specs") or {}
        label = f"{brand} {title}".strip() if brand else title

        block = f"**{label}**\n"
        if specs:
            for k, v in list(specs.items())[:8]:
                block += f"  • {k.replace('_', ' ').title()}: {v}\n"
        else:
            block += "  • Spesifikasi lengkap tersedia di halaman produk\n"
        block += f"  Harga: Rp {price:,} | Stok: {stok} unit"
        if uuid:
            block += f" | [Lihat Produk](/product/{uuid})"
        lines.append(block)

    return "\n\n".join(lines)


# ══════════════════════════════════════════════════════════════
#  CHATBOT RAG SERVICE (Facade)
# ══════════════════════════════════════════════════════════════

class ChatbotRAGService:
    """
    Facade Service — Orchestrate semua agent dengan prioritas:
    Greeting → Escalation → KnowledgeBase → FAQ → Transaksional → LLM → Fallback
    """

    def __init__(self):
        self.retrieval = ManticoreRetrievalAgent()
        self.graph_agent = KnowledgeGraphAgent()
        self.generator = AntiHalusinasiGenerator()

    async def get_response(
        self, query: str, history: List[Dict[str, str]], session: Optional[Any] = None
    ) -> Tuple[str, List[Dict[str, Any]], bool]:
        """
        Return: (reply_text, products, needs_escalation)
        needs_escalation=True → frontend tampilkan opsi handoff ke Admin
        """
        q_lower = query.lower().strip()
        clean_q = re.sub(r"[^\w\s]", "", q_lower).strip()

        # ── 1. Greeting ─────────────────────────────────────────────
        if _is_greeting(query):
            logger.info(f"[RAG] Greeting: '{query}'")
            featured = await self.retrieval.retrieve_relevant_products("cctv", limit=3)
            
            # Dynamic Greeting Logic
            normalized = q_lower.strip()
            if "assalamualaikum" in normalized:
                greeting_prefix = "Waalaikumussalam Wr. Wb. Kak! 🙏"
            elif "hola" in normalized:
                greeting_prefix = "¡Hola Kak! ¡Bienvenido! 👋"
            elif any(x in normalized for x in ["pagi", "selamat pagi"]):
                greeting_prefix = "Selamat pagi Kak! 🌅"
            elif any(x in normalized for x in ["siang", "selamat siang"]):
                greeting_prefix = "Selamat siang Kak! ☀️"
            elif any(x in normalized for x in ["sore", "selamat sore"]):
                greeting_prefix = "Selamat sore Kak! ⛅"
            elif any(x in normalized for x in ["malam", "selamat malam"]):
                greeting_prefix = "Selamat malam Kak! 🌙"
            elif any(x in normalized for x in ["hai", "hay", "hei", "hey"]):
                import random
                friendly_greets = [
                    "Hai Kak! Senang bertemu Kakak di sini. 👋",
                    "Hai Kak! Ada yang bisa saya bantu hari ini? 😊",
                    "Hei Kak! Ada yang seru nih, mau cari CCTV apa? 😉"
                ]
                greeting_prefix = random.choice(friendly_greets)
            else:
                import random
                standard_greets = [
                    "Halo Kak! Selamat datang di **PasarCCTV**! 👋",
                    "Halo Kak! Ada yang bisa PasarBot bantu hari ini? 😊",
                    "Halo Kak! Selamat datang, mau cari perangkat keamanan apa hari ini? 🔒"
                ]
                greeting_prefix = random.choice(standard_greets)

            reply = (
                f"{greeting_prefix}\n\n"
                "Saya **PasarBot** — asisten AI toko kami. Siap membantu Kakak menemukan "
                "kamera keamanan, sistem CCTV, atau aksesori yang paling sesuai kebutuhan.\n\n"
                "💬 Silakan ketik produk atau pertanyaan Kakak, misalnya:\n"
                "*\"kamera outdoor 5MP\"*, *\"CCTV WiFi untuk rumah\"*, *\"harga Hikvision\"*"
            )
            return reply, featured, False

        # ── 2. Escalation / Complaint Detection ─────────────────────
        if _detect_escalation(query):
            logger.info(f"[RAG] Escalation detected: '{query}'")
            reply = (
                "Maaf atas ketidaknyamanannya, Kak. 🙏\n\n"
                "Saya ingin memastikan Kakak mendapat bantuan yang tepat. "
                "Apakah Kakak ingin saya teruskan percakapan ini ke **Tim Admin** kami "
                "untuk penanganan lebih lanjut?\n\n"
                "Klik **\"Teruskan ke Admin\"** di bawah, atau ketik pertanyaan ulang "
                "dengan lebih detail agar saya bisa bantu lebih baik."
            )
            return reply, [], True  # needs_escalation = True

        # ── 3. Knowledge Base — TurboQuant Search ───────────────────
        kb_index = get_kb_index()
        if kb_index.size > 0:
            kb_results = kb_index.search(query, top_k=1, threshold=0.45)
            if kb_results:
                best = kb_results[0]
                logger.info(f"[RAG] KB hit: '{best['question']}'")

                # Increment hit_count di database secara async (non-blocking)
                if session:
                    from .knowledge_repository import ChatbotKnowledgeRepository
                    _kb_repo = ChatbotKnowledgeRepository()
                    try:
                        await _kb_repo.record_hit(best["uuid"], session)
                        # Update juga di in-memory index agar sinkron
                        for entry in kb_index._entries:
                            if entry["uuid"] == best["uuid"]:
                                entry["hit_count"] = entry.get("hit_count", 0) + 1
                                break
                    except Exception as hit_err:
                        logger.warning(f"[RAG] Failed to record hit: {hit_err}")
                
                # Cross-reference with in-memory FAQ config to respect no_related and related_query
                faq_item = next((f for f in FAQ_ITEMS if f["question"].lower() == best["question"].lower()), None)
                if faq_item:
                    if faq_item.get("no_related", False):
                        related = []
                    else:
                        related_q = faq_item.get("related_query") or faq_item["keywords"][0]
                        related = await self.retrieval.retrieve_relevant_products(related_q, limit=3)
                        if not related:
                            related = await self.retrieval.retrieve_relevant_products("cctv", limit=3)
                else:
                    # Check if category is general/non-product
                    cat = best.get("category", "general").lower().strip()
                    non_product_categories = {
                        "general", "layanan", "garansi", "faq", "jam", "lokasi",
                        "pembayaran", "pengiriman", "bantuan", "info", "toko",
                        "alamat", "operasional"
                    }
                    if cat in non_product_categories:
                        related = []
                    else:
                        related = await self.retrieval.retrieve_relevant_products(cat, limit=3)
                        if not related:
                            related = await self.retrieval.retrieve_relevant_products("cctv", limit=3)
                return best["answer"], related, False

        # ── 4. FAQ Lokal — Jaccard + Keyword ────────────────────────
        faq_match = find_matching_faq(query)
        if faq_match:
            logger.info(f"[RAG] FAQ: '{faq_match['question']}'")
            if faq_match.get("no_related", False):
                related = []
            else:
                related_q = faq_match.get("related_query") or faq_match["keywords"][0]
                related = await self.retrieval.retrieve_relevant_products(related_q, limit=3)
                if not related:
                    related = await self.retrieval.retrieve_relevant_products("cctv", limit=3)
            return faq_match["answer"], related, False

        # ── 5. Manticore Search Retrieval ────────
        # Retrieve from Manticore Search (lexical, morphology, typo-tolerant)
        products = await self.retrieval.retrieve_relevant_products(query, limit=5)

        # Smart fallback: jika query kalimat panjang tidak menghasilkan produk, cari berdasarkan kata kunci relevan
        if not products and len(clean_q.split()) > 1:
            stop_words = {
                "ada", "dan", "yang", "untuk", "mau", "cari", "bisa", "apa",
                "berapa", "cctv", "dong", "min", "kak", "tolong", "apakah", "rekomendasi"
            }
            keywords = [w for w in clean_q.split() if len(w) >= 3 and w not in stop_words]
            for kw in keywords:
                fallback_products = await self.retrieval.retrieve_relevant_products(kw, limit=5)
                if fallback_products:
                    products = fallback_products
                    break

        # ── 6. Transaksional Bypass (harga/stok/spek) ───────────────
        is_price = any(kw in q_lower for kw in [
            "harga", "berapa", "price", "ongkos", "biaya", "harganya", "dijual", "jual berapa"
        ])
        is_stock = any(kw in q_lower for kw in [
            "ready", "stok", "stock", "tersedia", "ada", "masih ada", "stoknya", "habis"
        ])
        is_specs = any(kw in q_lower for kw in [
            "spesifikasi", "spek", "specs", "fitur", "resolusi", "lens", "lensa",
            "megapixel", "mp", "night vision", "ir", "poe", "wifi", "range"
        ])

        if products and (is_price or is_stock or is_specs):
            logger.info(f"[RAG] Transaksional bypass: '{query}'")
            if is_price:
                reply = _format_price_response(products, query)
            elif is_stock:
                reply = _format_stock_response(products, query)
            else:
                reply = _format_specs_response(products, query)
            return reply, products, False

        # ── 7. LLM Generation (Groq/GPT/Gemini/DeepSeek) ────────────
        # Load AI settings dynamically from the database
        ai_settings = None
        if session:
            try:
                from backend.admin.adminSettings.service import AdminSettingService
                ai_settings = await AdminSettingService.get_setting(session, "chatbot_ai_settings")
            except Exception as se_err:
                logger.error(f"[RAG] Failed to load AI settings: {se_err}")
                
        if not ai_settings:
            ai_settings = {
                "provider": os.getenv("CHATBOT_PROVIDER", "groq"),
                "api_key": os.getenv("GROQ_API_KEY", ""),
                "model": os.getenv("GROQ_LLM_MODEL", "qwen-2.5-32b"),
                "temperature": 0.6,
                "max_tokens": 4096,
                "custom_system_prompt": None
            }

        provider = ai_settings.get("provider", "groq").lower()
        if provider == "internal":
            logger.info("[RAG] Internal system selected. Bypassing external LLM call.")
            return self.generator._local_fallback(query, products), products, False

        triples = self.graph_agent.build_local_graph(products)
        graph_ctx = self.graph_agent.format_graph_context(triples)
        reply, validated = await self.generator.generate_response(
            query=query,
            products=products,
            graph_context=graph_ctx,
            history=history,
            ai_settings=ai_settings,
        )
        return reply, validated, False
