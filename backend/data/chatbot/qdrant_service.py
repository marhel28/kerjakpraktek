"""
backend/data/chatbot/qdrant_service.py
======================================
Qdrant Vector Database Service untuk Pencarian Semantik Produk.
Menggunakan FastEmbed (BAAI/bge-small-en-v1.5) untuk ekstraksi embedding lokal secara cepat.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from fastembed import TextEmbedding

logger = logging.getLogger(__name__)

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
COLLECTION_NAME = "products"
VECTOR_SIZE = 384  # Dimension of BAAI/bge-small-en-v1.5/all-MiniLM-L6-v2

class QdrantService:
    _instance = None
    _client: Optional[QdrantClient] = None
    _encoder: Optional[TextEmbedding] = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(QdrantService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # Prevent re-initialization if already initialized
        if self._client is not None:
            return
        
        try:
            # Lazy initialize Qdrant client
            self._client = QdrantClient(url=QDRANT_URL, timeout=10.0)
            logger.info(f"[Qdrant] Client initialized at {QDRANT_URL}")
        except Exception as e:
            logger.error(f"[Qdrant] Failed to initialize client: {e}")
            self._client = None

    def _get_encoder(self) -> TextEmbedding:
        """Lazy load fastembed encoder."""
        if self._encoder is None:
            logger.info("[Qdrant] Loading fastembed model BAAI/bge-small-en-v1.5...")
            # BAAI/bge-small-en-v1.5 runs locally on CPU via ONNX Runtime
            self._encoder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
            logger.info("[Qdrant] Fastembed model loaded successfully.")
        return self._encoder

    def init_collection(self) -> bool:
        """Create collection if it does not exist."""
        if not self._client:
            logger.warning("[Qdrant] Cannot init collection: Qdrant client not connected.")
            return False
        
        try:
            collections = self._client.get_collections().collections
            exists = any(c.name == COLLECTION_NAME for c in collections)
            
            if not exists:
                logger.info(f"[Qdrant] Creating collection '{COLLECTION_NAME}' with dim={VECTOR_SIZE}")
                self._client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=VECTOR_SIZE,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"[Qdrant] Collection '{COLLECTION_NAME}' created.")
            else:
                logger.info(f"[Qdrant] Collection '{COLLECTION_NAME}' already exists.")
            return True
        except Exception as e:
            logger.error(f"[Qdrant] Failed to initialize collection: {e}")
            return False

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding vector from text."""
        encoder = self._get_encoder()
        embeddings = list(encoder.embed([text]))
        return [float(val) for val in embeddings[0]]

    def index_product(self, product: Dict[str, Any]) -> bool:
        """Index a single product into Qdrant."""
        if not self._client:
            return False
        
        try:
            uuid_str = str(product.get("uuid"))
            title = product.get("title", "")
            brand = product.get("brand", "") or "NO BRAND"
            specs = product.get("specs") or {}
            specs_text = " | ".join(f"{k}: {v}" for k, v in specs.items())
            category = product.get("category_slug", "") or product.get("category", "") or ""

            # Create rich textual description for semantic embedding
            text_to_embed = f"{brand} {title} | Specs: {specs_text} | Category: {category}".strip()
            vector = self.get_embedding(text_to_embed)

            # Map payload
            payload = {
                "uuid": uuid_str,
                "title": title,
                "brand": brand,
                "price": product.get("price") or product.get("online_price") or 0,
                "original_price": product.get("original_price") or 0,
                "discount_percentage": product.get("discount_percentage") or 0,
                "stok": product.get("stok") or 0,
                "slug": product.get("slug") or "",
                "image": product.get("image") or product.get("image_url") or "",
                "specs": specs,
                "category": category
            }

            self._client.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=uuid_str,
                        vector=vector,
                        payload=payload
                    )
                ]
            )
            logger.info(f"[Qdrant] Indexed product: {title}")
            return True
        except Exception as e:
            logger.error(f"[Qdrant] Failed to index product: {e}")
            return False

    def bulk_index_products(self, products: List[Dict[str, Any]]) -> bool:
        """Bulk index products into Qdrant."""
        if not self._client or not products:
            return False
        
        try:
            points = []
            texts_to_embed = []
            valid_products = []

            for p in products:
                uuid_str = str(p.get("uuid"))
                title = p.get("title", "")
                brand = p.get("brand", "") or "NO BRAND"
                specs = p.get("specs") or {}
                specs_text = " | ".join(f"{k}: {v}" for k, v in specs.items())
                category = p.get("category_slug", "") or p.get("category", "") or ""

                text = f"{brand} {title} | Specs: {specs_text} | Category: {category}".strip()
                texts_to_embed.append(text)
                valid_products.append(p)

            if not texts_to_embed:
                return False

            # Batch encode
            encoder = self._get_encoder()
            embeddings = list(encoder.embed(texts_to_embed))

            for idx, p in enumerate(valid_products):
                uuid_str = str(p.get("uuid"))
                vector = [float(val) for val in embeddings[idx]]
                
                payload = {
                    "uuid": uuid_str,
                    "title": p.get("title", ""),
                    "brand": p.get("brand") or "NO BRAND",
                    "price": p.get("price") or p.get("online_price") or 0,
                    "original_price": p.get("original_price") or 0,
                    "discount_percentage": p.get("discount_percentage") or 0,
                    "stok": p.get("stok") or 0,
                    "slug": p.get("slug") or "",
                    "image": p.get("image") or p.get("image_url") or "",
                    "specs": p.get("specs") or {},
                    "category": p.get("category_slug", "") or p.get("category", "") or ""
                }

                points.append(
                    PointStruct(
                        id=uuid_str,
                        vector=vector,
                        payload=payload
                    )
                )

            # Batch upsert
            self._client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            logger.info(f"[Qdrant] Bulk indexed {len(points)} products.")
            return True
        except Exception as e:
            logger.error(f"[Qdrant] Failed to bulk index products: {e}")
            return False

    def search_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search products in Qdrant using cosine similarity."""
        if not self._client or not query.strip():
            return []
        
        try:
            # Ensure collection is loaded
            self.init_collection()
            
            # Generate query embedding
            vector = self.get_embedding(query)
            
            # Search in Qdrant
            results = self._client.search(
                collection_name=COLLECTION_NAME,
                query_vector=vector,
                limit=limit
            )
            
            items = []
            for res in results:
                # Convert payload back to stock schema format
                payload = res.payload
                # Align key names with frontend expectation (e.g. price, image)
                items.append({
                    "uuid": payload.get("uuid"),
                    "title": payload.get("title"),
                    "brand": payload.get("brand"),
                    "price": payload.get("price"),
                    "original_price": payload.get("original_price"),
                    "discount_percentage": payload.get("discount_percentage"),
                    "stok": payload.get("stok"),
                    "slug": payload.get("slug"),
                    "image": payload.get("image"),
                    "specs": payload.get("specs"),
                    "category": payload.get("category"),
                    "score": res.score
                })
            return items
        except Exception as e:
            logger.error(f"[Qdrant] Search failed: {e}")
            return []

    async def sync_all_products(self, session) -> bool:
        """Fetch all active products from DB and seed Qdrant."""
        try:
            from sqlmodel import select
            from sqlalchemy.orm import selectinload
            from backend.data.stock.model import Stock
            
            # Retrieve all active stocks
            stmt = select(Stock).where(Stock.is_active == True).options(selectinload(Stock.assets))
            res = await session.execute(stmt)
            stocks = res.scalars().all()
            
            if not stocks:
                logger.info("[Qdrant] No products to sync.")
                return True
            
            # Convert Stock DB objects to dicts
            products_data = []
            for s in stocks:
                # Fetch first asset image if available
                # If there are assets, retrieve them
                image_url = ""
                if hasattr(s, "assets") and s.assets:
                    image_url = s.assets[0].url
                
                products_data.append({
                    "uuid": str(s.uuid),
                    "title": s.title,
                    "brand": s.brand,
                    "online_price": s.online_price,
                    "original_price": s.original_price,
                    "discount_percentage": s.discount_percentage,
                    "stok": s.stok,
                    "slug": s.slug,
                    "image_url": image_url,
                    "specs": s.specs,
                    "category_slug": s.category_slug
                })
            
            # Bulk index in background
            self.init_collection()
            self.bulk_index_products(products_data)
            logger.info(f"[Qdrant] Successfully synced {len(products_data)} products from DB.")
            return True
        except Exception as e:
            logger.error(f"[Qdrant] Sync failed: {e}")
            return False
