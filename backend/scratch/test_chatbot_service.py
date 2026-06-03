import asyncio
import os
import sys
from dotenv import load_dotenv

# Load env variables
load_dotenv("backend/.env")

# Ensure python path includes project root
sys.path.append(os.getcwd())

from backend.data.chatbot.service import ChatbotRAGService

async def main():
    print("🤖 --- STARTING CHATBOT SERVICE TEST ---")
    service = ChatbotRAGService()
    
    # Kueri 1: Tanya rekomendasi cctv (Harus memanggil Groq API)
    query1 = "rekomendasikan cctv"
    print(f"\n🔍 Mengirim kueri 1: '{query1}'...")
    try:
        reply1, products1 = await service.get_response(query1, [])
        print(f"✅ Respons kueri 1:")
        print(reply1)
        print(f"Produk terlampir: {[p.get('title') for p in products1]}")
    except Exception as e:
        print(f"❌ Gagal memproses kueri 1: {e}")
        import traceback
        traceback.print_exc()

    # Kueri 2: Tanya harga cctv tapo (Harus bypass lokal / internal RAG)
    query2 = "berapa harga cctv tapo"
    print(f"\n🔍 Mengirim kueri 2 (Internal RAG bypass): '{query2}'...")
    try:
        reply2, products2 = await service.get_response(query2, [])
        print(f"✅ Respons kueri 2:")
        print(reply2)
        print(f"Produk terlampir: {[p.get('title') for p in products2]}")
    except Exception as e:
        print(f"❌ Gagal memproses kueri 2: {e}")

if __name__ == "__main__":
    asyncio.run(main())
