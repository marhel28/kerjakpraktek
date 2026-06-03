import asyncio
import os
import sys
from dotenv import load_dotenv

# Load env variables
load_dotenv("backend/.env")

# Ensure python path includes project root
sys.path.append(os.getcwd())

from backend.data.stock.service import StockService

async def main():
    print("🤖 --- STARTING CHATBOT RAG TEST ---")
    
    # 1. Test Manticore Search Retrieval
    service = StockService()
    query = "kamera outdoor 5mp"
    print(f"🔍 Mencari katalog untuk kueri: '{query}'...")
    
    try:
        res = await service.search_stocks_es(q=query, limit=3)
        items = res.get("items", [])
        print(f"✅ Berhasil mengambil {len(items)} produk dari Manticore:")
        for idx, item in enumerate(items):
            print(f"   [{idx+1}] Merek: {item.get('brand')} | Nama: {item.get('title')} | Harga: Rp {item.get('price'):,}")
    except Exception as e:
        print(f"❌ Gagal mengambil produk dari Manticore: {e}")
        return

    # 2. Test Chatbot Endpoint Logic
    # We will simulate the POST /chatbot/chat logic
    print("\n💬 Mensimulasikan RAG Chatbot logic...")
    context_items = []
    for i, p in enumerate(items):
        specs_dict = p.get("specs", {})
        specs_str = ", ".join([f"{k}: {v}" for k, v in specs_dict.items()]) if specs_dict else "Tidak ada spesifikasi"
        context_line = (
            f"[{i+1}] Merek: {p.get('brand', 'NO BRAND')} | "
            f"Nama: {p.get('title')} | "
            f"Harga: Rp {p.get('price', 0):,} | "
            f"Spesifikasi: {specs_str} | "
            f"Link: /product/{p.get('uuid')}"
        )
        context_items.append(context_line)
    
    context_data = "\n".join(context_items) if context_items else "Tidak ada produk cocok."
    print("📄 Konteks disusun:")
    print(context_data)

    # Call LLM / Fallback
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"\n🔑 GEMINI_API_KEY ditemukan (dimulai dengan {api_key[:5]}...). Menghubungi Gemini...")
        import httpx
        system_prompt = (
            "Anda adalah PasarBot, asisten AI resmi dari PasarCCTV.\n"
            "Tugas Anda adalah melayani dan merekomendasikan produk CCTV/keamanan dari katalog toko kami berdasarkan data konteks produk berikut.\n\n"
            f"[KONTEKS PRODUK]\n{context_data}\n\n"
            "Jawab dalam Bahasa Indonesia yang ramah, sopan, ringkas (maks 2-3 paragraf) dan fokus pada penjualan."
        )
        payload = {
            "contents": [{"role": "user", "parts": [{"text": f"Kueri Pengguna: {query}"}]}],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 400}
        }
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    reply = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                    print("\n🤖 [PasarBot AI]:")
                    print(reply)
                else:
                    print(f"❌ Gemini API gagal (status {resp.status_code}): {resp.text}")
        except Exception as e:
            print(f"❌ Panggilan Gemini gagal: {e}")
    else:
        print("\n⚠️ GEMINI_API_KEY tidak ditemukan di .env. Menggunakan local fallback summarizer...")
        reply_lines = [
            f"Halo Kak! Berdasarkan pencarian '{query}', berikut beberapa rekomendasi produk terbaik dari katalog kami:\n"
        ]
        for p in items[:3]:
            reply_lines.append(
                f"- **{p.get('brand')} {p.get('title')}**: Rp {p.get('price'):,} "
                f"(Specs: {', '.join([f'{k}: {v}' for k, v in p.get('specs', {}).items()][:2])})"
            )
        reply_lines.append("\nAda yang bisa kami bantu jelaskan lebih lanjut Kak tentang produk di atas?")
        reply = "\n".join(reply_lines)
        print("\n🤖 [PasarBot AI (Local Fallback)]:")
        print(reply)
        
    print("\n🏁 --- RAG TEST COMPLETED ---")

if __name__ == "__main__":
    asyncio.run(main())
