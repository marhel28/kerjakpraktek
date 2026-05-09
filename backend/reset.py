import asyncio
import os
from elasticsearch import AsyncElasticsearch

# 🔥 FIX 1: Gunakan environment variable atau fallback ke nama service Docker
ES_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
es_client = AsyncElasticsearch(ES_URL)

async def reset_elasticsearch():
    index_name = "products"
    
    # 1. Hapus Index yang salah
    if await es_client.indices.exists(index=index_name):
        await es_client.indices.delete(index=index_name)
        print(f"🗑️ Index '{index_name}' berhasil dihapus.")

    # 2. Buat ulang dengan MAPPING YANG BENAR
    mapping = {
        "mappings": {
            "properties": {
                "uuid": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "standard"},
                "slug": {"type": "keyword"},
                "brand": {"type": "keyword"},
                "category_slug": {"type": "keyword"}, # 🔥 INI KUNCI FIX-NYA
                "type": {"type": "keyword"},
                "online_price": {"type": "integer"},
                "stok": {"type": "integer"},
                "terjual": {"type": "integer"},
                "is_active": {"type": "boolean"},
                "created_at": {"type": "date"},
                "image_url": {"type": "keyword"}
            }
        }
    }

    await es_client.indices.create(index=index_name, body=mapping)
    print(f"✅ Index '{index_name}' berhasil dibuat dengan mapping yang benar.")
    await es_client.close()

# 🔥 FIX 2: Bungkus dengan blok main agar TIDAK tereksekusi otomatis jika di-import file lain
if __name__ == "__main__":
    asyncio.run(reset_elasticsearch())