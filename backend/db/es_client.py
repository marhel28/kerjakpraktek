from elasticsearch import AsyncElasticsearch
import os

ES_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
es_client = AsyncElasticsearch(ES_URL)


async def init_es_index():
    index_name = "products"

    settings = {
        "analysis": {
            "analyzer": {
                # Analyzer untuk autocomplete (edge_ngram)
                "autocomplete_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "autocomplete_filter"]
                },
                # Analyzer untuk pencarian autocomplete (sisi query)
                "autocomplete_search_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase"]
                },
                # Analyzer brand: lowercase + keyword agar matching konsisten
                "brand_analyzer": {
                    "type": "custom",
                    "tokenizer": "keyword",
                    "filter": ["lowercase", "trim"]
                }
            },
            "filter": {
                "autocomplete_filter": {
                    "type": "edge_ngram",
                    "min_gram": 2,
                    "max_gram": 20
                }
            }
        }
    }

    mapping = {
        "mappings": {
            "properties": {
                # ── IDENTITAS ──────────────────────────────────────────
                "uuid": {"type": "keyword"},
                "slug": {"type": "keyword"},

                # ── TEKS UTAMA (full-text search) ──────────────────────
                "title": {
                    "type": "text",
                    "analyzer": "standard",
                    # Sub-field untuk autocomplete
                    "fields": {
                        "autocomplete": {
                            "type": "text",
                            "analyzer": "autocomplete_analyzer",
                            "search_analyzer": "autocomplete_search_analyzer"
                        },
                        # Sub-field keyword untuk sorting/aggregasi judul
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },

                # ── BRAND ───────────────────────────────────────────────
                # Field utama: keyword untuk aggregasi & term filter exact
                "brand": {
                    "type": "keyword",
                    # Sub-field text untuk match_phrase fallback
                    "fields": {
                        "text": {
                            "type": "text",
                            "analyzer": "brand_analyzer"
                        }
                    }
                },
                # Field lowercase normalize: untuk term filter case-insensitive bulletproof
                "brand_normalized": {
                    "type": "keyword"
                },

                # ── KATEGORI ────────────────────────────────────────────
                "category_slug": {
                    "type": "keyword",
                    # Sub-field text untuk fuzzy match di autocomplete
                    "fields": {
                        "text": {"type": "text", "analyzer": "standard"}
                    }
                },
                "subcategory_slug": {
                    "type": "keyword",
                    "fields": {
                        "text": {"type": "text", "analyzer": "standard"}
                    }
                },

                # ── TIPE PRODUK ─────────────────────────────────────────
                "type": {
                    "type": "keyword",
                    "fields": {
                        "text": {"type": "text", "analyzer": "standard"}
                    }
                },

                # ── HARGA & DISKON ──────────────────────────────────────
                "original_price": {"type": "integer"},
                "discount_percentage": {
                    "type": "integer",
                    # default 0 jika tidak ada diskon
                    "null_value": 0
                },
                "online_price": {"type": "integer"},

                # ── STOK & PENJUALAN ────────────────────────────────────
                "stok": {"type": "integer"},
                "terjual": {
                    "type": "integer",
                    "null_value": 0
                },

                # ── STATUS ───────────────────────────────────────────────
                "is_active": {"type": "boolean"},

                # ── SPECS (JSONB dynamic) ────────────────────────────────
                # Pakai "object" dengan dynamic true agar semua key di JSONB
                # bisa di-index tanpa perlu define satu per satu.
                # Tapi set enabled: false jika tidak perlu search di dalam specs
                # (hemat disk + performa lebih baik).
                # Pilih salah satu sesuai kebutuhan:
                #
                # Opsi A — TIDAK perlu search dalam specs (rekomendasi):
                "specs": {
                    "type": "object",
                    "enabled": False  # Disimpan tapi tidak di-index
                },
                #
                # Opsi B — perlu search dalam specs (uncomment jika butuh):
                # "specs": {
                #     "type": "object",
                #     "dynamic": True
                # },

                # ── GAMBAR ───────────────────────────────────────────────
                "image_url": {"type": "keyword"},

                # ── TIMESTAMP ────────────────────────────────────────────
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"}
            }
        }
    }

    exists = await es_client.indices.exists(index=index_name)

    if not exists:
        await es_client.indices.create(
            index=index_name,
            settings=settings,
            mappings=mapping["mappings"]
        )
        print(f"✅ Elasticsearch index '{index_name}' created with full mapping.")
    else:
        print(f"ℹ️  Elasticsearch index '{index_name}' already exists. Skipping creation.")


async def reindex_es(drop_first: bool = False):
    """
    Helper untuk re-index dari scratch.
    Panggil hanya dari script admin/seeder, BUKAN dari API endpoint.

    Contoh penggunaan di script:
        import asyncio
        from backend.db.es_client import reindex_es
        asyncio.run(reindex_es(drop_first=True))
    """
    index_name = "products"

    if drop_first:
        exists = await es_client.indices.exists(index=index_name)
        if exists:
            await es_client.indices.delete(index=index_name)
            print(f"🗑️  Index '{index_name}' deleted.")

    await init_es_index()
    print(f"✅ Index '{index_name}' ready for re-indexing.")