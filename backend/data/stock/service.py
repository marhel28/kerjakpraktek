import io
import re
import json
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from PIL import Image
from sqlalchemy import desc
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .model import Stock, AssetStock, Coupon
from backend.config import Config
from backend.db.cdn import upload_file, delete_file
from backend.db.es_client import es_client
from backend.db.redis import (
    get_redis_token,
    cache_coupon,
    get_cached_coupon,
    invalidate_coupon_cache,
    invalidate_all_coupon_cache,
)

logger = logging.getLogger(__name__)

# ── Cache TTL ──────────────────────────────────────────────────────
POPULAR_CACHE_KEY = "cache:popular_products:v2"
POPULAR_CACHE_TTL = 300   # 5 menit


class StockService:

    # ══════════════════════════════════════════════════════════════
    # 🛠️ HELPERS
    # ══════════════════════════════════════════════════════════════

    async def _parse_hits_admin(self, hits: list) -> list:
        """
        Parse Elasticsearch hits untuk tampilan admin.
        Mengembalikan semua field yang dibutuhkan termasuk terjual & sisa.
        """
        items = []
        for h in hits:
            src = h["_source"]
            stok    = src.get("stok", 0) or 0
            terjual = src.get("terjual", 0) or 0
            sisa    = max(stok - terjual, 0)

            items.append({
                "uuid":         h["_id"],
                "title":        src.get("title"),
                "slug":         src.get("slug"),
                "brand":        src.get("brand"),
                # category bisa tersimpan sebagai category_slug di ES
                "category":     src.get("category_slug") or src.get("category"),
                "category_slug":src.get("category_slug") or src.get("category"),
                "subcategory":  src.get("subcategory_slug") or src.get("subcategory"),
                "subcategory_slug": src.get("subcategory_slug") or src.get("subcategory"),
                "type":         src.get("type"),
                "price":        src.get("online_price"),
                "online_price": src.get("online_price"),
                "original_price":      src.get("original_price", 0),
                "discount_percentage": src.get("discount_percentage", 0),

                # ── Stok data ──────────────────────────────────────
                "stok":         stok,
                "terjual":      terjual,
                "sisa":         sisa,
                "status_stok":  "habis" if sisa <= 0 else "tersedia",

                # ── Status & meta ──────────────────────────────────
                "is_active":    src.get("is_active", False),
                "is_popular":   terjual > 50,
                "image":        src.get("image_url"),
                "total_assets": src.get("assets_count", 0),
            })
        return items

    def _generate_slug(self, text_input: str) -> str:
        text_input = text_input.lower()
        text_input = re.sub(r'[^a-z0-9\s-]', '', text_input)
        text_input = re.sub(r'[\s-]+', '-', text_input)
        return text_input.strip('-')

    async def compress_to_webp(self, file_bytes: bytes) -> io.BytesIO:
        img = Image.open(io.BytesIO(file_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        output = io.BytesIO()
        img.save(output, format="WEBP", quality=75, optimize=True)
        output.seek(0)
        return output

    # ══════════════════════════════════════════════════════════════
    # 🔄 ELASTICSEARCH SYNC
    # ══════════════════════════════════════════════════════════════

    async def _index_to_es(self, stock_obj: Stock, image_url: Optional[str] = None):
        doc = {
            "uuid":                str(stock_obj.uuid),
            "title":               stock_obj.title,
            "slug":                stock_obj.slug,
            "brand":               stock_obj.brand,
            "brand_normalized":    stock_obj.brand.lower().strip() if stock_obj.brand else "",
            "category_slug":       stock_obj.category_slug,
            "subcategory_slug":    stock_obj.subcategory_slug,
            "type":                stock_obj.type,
            "specs":               stock_obj.specs,
            "original_price":      stock_obj.original_price,
            "discount_percentage": stock_obj.discount_percentage,
            "online_price":        stock_obj.online_price,
            "stok":                stock_obj.stok,
            "terjual":             stock_obj.terjual,
            # sisa di-compute agar bisa di-filter langsung di ES
            "sisa":                max((stock_obj.stok or 0) - (stock_obj.terjual or 0), 0),
            "is_active":           stock_obj.is_active,
            "created_at":          stock_obj.created_at.isoformat() if stock_obj.created_at else None,
            "image_url":           image_url,
        }
        await es_client.index(index="products", id=str(stock_obj.uuid), document=doc)

    # ══════════════════════════════════════════════════════════════
    # 📝 CREATE & UPDATE STOCK
    # ══════════════════════════════════════════════════════════════

    async def create_stock(
        self, session: AsyncSession, data: dict, image_files: List[bytes] = None
    ) -> Stock:
        try:
            data["slug"] = self._generate_slug(data["title"])
            db_stock = Stock(**data)
            session.add(db_stock)
            await session.flush()

            first_image_url = None
            if image_files:
                for idx, img in enumerate(image_files[:4]):
                    webp = await self.compress_to_webp(img)
                    url = await upload_file(webp, folder="stocks", content_type="image/webp")
                    if url:
                        if idx == 0:
                            first_image_url = url
                        session.add(AssetStock(
                            url=url, alt_text=data.get("title"), stock_uuid=db_stock.uuid
                        ))

            await session.commit()
            await session.refresh(db_stock)

            try:
                await self._index_to_es(db_stock, first_image_url)
            except Exception as e:
                logger.error(f"ES index failed: {e}")

            try:
                await get_redis_token().delete(POPULAR_CACHE_KEY)
            except Exception:
                pass

            return db_stock
        except Exception as e:
            await session.rollback()
            raise e

    async def update_stock(
        self,
        session: AsyncSession,
        stock_uuid: UUID,
        data: dict,
        image_files: List[bytes] = None,
    ) -> Optional[Stock]:
        stmt = select(Stock).where(Stock.uuid == stock_uuid).options(selectinload(Stock.assets))
        res = await session.execute(stmt)
        db_stock = res.scalar_one_or_none()
        if not db_stock:
            return None

        first_image_url = db_stock.assets[0].url if db_stock.assets else None

        if image_files is not None:
            for old in db_stock.assets:
                key = old.url.split(f"{Config.url_r2}/")[-1]
                await delete_file(key)
                await session.delete(old)
            first_image_url = None
            for idx, img in enumerate(image_files[:4]):
                webp = await self.compress_to_webp(img)
                url = await upload_file(webp, folder="stocks", content_type="image/webp")
                if url:
                    if idx == 0:
                        first_image_url = url
                    session.add(AssetStock(
                        url=url,
                        alt_text=data.get("title", db_stock.title),
                        stock_uuid=db_stock.uuid,
                    ))

        if "title" in data:
            db_stock.slug = self._generate_slug(data["title"])

        for k, v in data.items():
            setattr(db_stock, k, v)

        await session.commit()
        await session.refresh(db_stock)

        try:
            await self._index_to_es(db_stock, first_image_url)
        except Exception as e:
            logger.error(f"ES update failed: {e}")

        try:
            await get_redis_token().delete(POPULAR_CACHE_KEY)
        except Exception:
            pass

        return db_stock

    # ══════════════════════════════════════════════════════════════
    # 🔍 ADMIN SEARCH — ES dengan filter lengkap
    # ══════════════════════════════════════════════════════════════

    async def search_stock_admin(
        self,
        q: Optional[str] = None,
        categories: Optional[List[str]] = None,
        brand: Optional[str] = None,
        item_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        stock_status: Optional[str] = None,   # "tersedia" | "kosong"
        min_p: Optional[int] = None,
        max_p: Optional[int] = None,
        sort_by: str = "newest",
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        safe_categories = [c for c in (categories or []) if c and c != "semua-kategori"]

        # ── Query body ─────────────────────────────────────────────
        query_body: Dict[str, Any] = {
            "bool": {
                "must":   [],
                "filter": [],
            }
        }

        # 🔒 is_active filter — admin bisa lihat semua, tapi bisa filter
        if is_active is not None:
            query_body["bool"]["filter"].append({"term": {"is_active": is_active}})

        # 📦 Ketersediaan stok — filter via field `sisa` yang sudah di-index
        #    Jika field `sisa` belum ada di mapping lama, fallback ke `stok`
        if stock_status == "tersedia":
            # sisa > 0 → tersedia
            # Coba field sisa dulu, fallback ke stok
            query_body["bool"]["filter"].append({
                "bool": {
                    "should": [
                        {"range": {"sisa":  {"gt": 0}}},
                        {"range": {"stok":  {"gt": 0}}},   # fallback jika sisa belum di-index
                    ],
                    "minimum_should_match": 1,
                }
            })
        elif stock_status == "kosong":
            # sisa = 0 → kosong/habis
            query_body["bool"]["filter"].append({
                "bool": {
                    "should": [
                        {"term":  {"sisa": 0}},
                        # stok <= 0 sebagai fallback
                        {"range": {"stok": {"lte": 0}}},
                    ],
                    "minimum_should_match": 1,
                }
            })

        # 🔍 Full-text search
        if q:
            query_body["bool"]["must"].append({
                "multi_match": {
                    "query":     q,
                    "fields":    ["title^3", "brand^2", "type", "category_slug"],
                    "fuzziness": "AUTO",
                    "operator":  "or",
                }
            })
        else:
            query_body["bool"]["must"].append({"match_all": {}})

        # 📂 Category filter — coba keyword mapping, fallback ke term biasa
        if safe_categories:
            query_body["bool"]["filter"].append({
                "bool": {
                    "should": [
                        {"terms": {"category_slug.keyword": safe_categories}},
                        {"terms": {"category_slug":         safe_categories}},
                        {"terms": {"category.keyword":      safe_categories}},
                        {"terms": {"category":              safe_categories}},
                    ],
                    "minimum_should_match": 1,
                }
            })

        # 🏷️ Brand filter
        if brand and brand.lower() not in ("semua-brand", "all", ""):
            query_body["bool"]["filter"].append(self._build_brand_filter(brand))

        # 🧩 Type filter
        if item_type and item_type.lower() not in ("semua-tipe", "all", ""):
            query_body["bool"]["filter"].append({
                "bool": {
                    "should": [
                        {"term":         {"type.keyword": item_type}},
                        {"match_phrase": {"type": item_type}},
                    ],
                    "minimum_should_match": 1,
                }
            })

        # 💰 Price range
        if min_p is not None or max_p is not None:
            price_range: Dict[str, Any] = {}
            if min_p is not None: price_range["gte"] = min_p
            if max_p is not None: price_range["lte"] = max_p
            query_body["bool"]["filter"].append({"range": {"online_price": price_range}})

        # 🔽 Sorting
        sort_map: Dict[str, list] = {
            "newest":     [{"created_at":   {"order": "desc"}}],
            "oldest":     [{"created_at":   {"order": "asc"}}],
            "price_asc":  [{"online_price": {"order": "asc"}}],
            "price_desc": [{"online_price": {"order": "desc"}}],
            "price_low":  [{"online_price": {"order": "asc"}}],
            "price_high": [{"online_price": {"order": "desc"}}],
            "stock_high": [{"stok":         {"order": "desc"}}],
            "stock_low":  [{"stok":         {"order": "asc"}}],
            "sold_high":  [{"terjual":      {"order": "desc"}}],
            "sold_low":   [{"terjual":      {"order": "asc"}}],
        }
        sort_body = sort_map.get(sort_by, [{"created_at": {"order": "desc"}}])

        # 📊 Aggregations — untuk facet filter di frontend
        aggs = {
            "categories": {
                "terms": {"field": "category_slug.keyword", "size": 100, "missing": "unknown"}
            },
            "brands": {
                "terms": {"field": "brand.keyword", "size": 100, "missing": "unknown"}
            },
            "price_stats": {
                "stats": {"field": "online_price"}
            },
            "stok_stats": {
                "stats": {"field": "stok"}
            },
            "terjual_stats": {
                "stats": {"field": "terjual"}
            },
            # Jumlah produk tersedia vs kosong
            "ketersediaan": {
                "filters": {
                    "filters": {
                        "tersedia": {"range": {"stok": {"gt": 0}}},
                        "kosong":   {"range": {"stok": {"lte": 0}}},
                    }
                }
            },
        }

        try:
            response = await es_client.search(
                index="products",
                query=query_body,
                sort=sort_body,
                aggs=aggs,
                from_=offset,
                size=limit,
            )
        except Exception as e:
            logger.error(f"ES search_stock_admin failed: {e}")
            raise

        agg = response.get("aggregations", {})

        # Hitung total terjual dari semua item di halaman ini
        items = await self._parse_hits_admin(response["hits"]["hits"])
        total_terjual_page = sum(i["terjual"] for i in items)

        return {
            "total":              response["hits"]["total"]["value"],
            "items":              items,
            "total_terjual_page": total_terjual_page,   # bonus: total terjual di page ini
            "facets": {
                "categories": {
                    b["key"]: b["doc_count"]
                    for b in agg.get("categories", {}).get("buckets", [])
                    if b["key"] != "unknown"
                },
                "brands": {
                    b["key"]: b["doc_count"]
                    for b in agg.get("brands", {}).get("buckets", [])
                    if b["key"] != "unknown"
                },
                "price_range": {
                    "min": agg.get("price_stats", {}).get("min") or 0,
                    "max": agg.get("price_stats", {}).get("max") or 0,
                    "avg": round(agg.get("price_stats", {}).get("avg") or 0),
                },
                "stok_range": {
                    "min": agg.get("stok_stats", {}).get("min") or 0,
                    "max": agg.get("stok_stats", {}).get("max") or 0,
                    "sum": agg.get("stok_stats", {}).get("sum") or 0,
                },
                "terjual_stats": {
                    "min": agg.get("terjual_stats", {}).get("min") or 0,
                    "max": agg.get("terjual_stats", {}).get("max") or 0,
                    "sum": agg.get("terjual_stats", {}).get("sum") or 0,
                    "avg": round(agg.get("terjual_stats", {}).get("avg") or 0),
                },
                "ketersediaan": {
                    "tersedia": agg.get("ketersediaan", {}).get("buckets", {}).get("tersedia", {}).get("doc_count", 0),
                    "kosong":   agg.get("ketersediaan", {}).get("buckets", {}).get("kosong",   {}).get("doc_count", 0),
                },
            },
        }

    # ══════════════════════════════════════════════════════════════
    # 🔥 POPULAR — Redis Cache
    # ══════════════════════════════════════════════════════════════

    async def get_popular_items(
        self, session: AsyncSession, limit: int = 10
    ) -> List[Dict]:
        r = get_redis_token()
        try:
            cached = await r.get(POPULAR_CACHE_KEY)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Redis popular cache read failed: {e}")

        stmt = (
            select(Stock)
            .where(Stock.is_active == True, Stock.stok > 0)
            .options(selectinload(Stock.assets))
            .order_by(desc(Stock.terjual), desc(Stock.created_at))
            .limit(limit)
        )
        result = await session.execute(stmt)
        stocks = result.scalars().all()

        items = [
            {
                "uuid":                str(s.uuid),
                "title":               s.title,
                "slug":                s.slug,
                "price":               s.online_price,
                "original_price":      s.original_price,
                "discount_percentage": s.discount_percentage,
                "brand":               s.brand,
                "type":                s.type,
                "terjual":             s.terjual,
                "stok":                s.stok,
                "image":               s.assets[0].url if s.assets else None,
            }
            for s in stocks
        ]

        try:
            await r.set(POPULAR_CACHE_KEY, json.dumps(items), ex=POPULAR_CACHE_TTL)
        except Exception as e:
            logger.warning(f"Redis popular cache write failed: {e}")

        return items

    # ══════════════════════════════════════════════════════════════
    # 🎟️ COUPON CRUD
    # ══════════════════════════════════════════════════════════════

    async def create_coupon(
        self, session: AsyncSession, data: "CouponCreateRequest"  # noqa: F821
    ) -> Coupon:
        from fastapi import HTTPException
        existing = await session.exec(
            select(Coupon).where(Coupon.code == data.code, Coupon.deleted_at == None)
        )
        if existing.first():
            raise HTTPException(409, detail=f"Kupon '{data.code}' sudah ada")

        coupon = Coupon(
            code=data.code,
            discount_type=data.discount_type,
            discount_value=data.discount_value,
            min_purchase=data.min_purchase,
            max_discount=data.max_discount,
            quota=data.quota,
            valid_from=data.valid_from,
            valid_until=data.valid_until,
            is_active=data.is_active,
        )
        session.add(coupon)
        await session.commit()
        await session.refresh(coupon)

        await cache_coupon(coupon.code, json.dumps({
            "uuid":           str(coupon.uuid),
            "code":           coupon.code,
            "discount_type":  coupon.discount_type,
            "discount_value": coupon.discount_value,
            "min_purchase":   coupon.min_purchase,
            "max_discount":   coupon.max_discount,
            "quota":          coupon.quota,
            "used_count":     coupon.used_count,
            "valid_from":     coupon.valid_from.isoformat() if coupon.valid_from else None,
            "valid_until":    coupon.valid_until.isoformat() if coupon.valid_until else None,
            "is_active":      coupon.is_active,
        }))
        return coupon

    async def get_coupon_by_code(self, session: AsyncSession, code: str) -> Optional[Coupon]:
        result = await session.exec(
            select(Coupon).where(
                Coupon.code == code.upper().strip(),
                Coupon.deleted_at == None,
            )
        )
        return result.first()

    async def get_all_coupons(
        self,
        session: AsyncSession,
        include_inactive: bool = False,
        page: int = 1,
        size: int = 20,
    ) -> Dict[str, Any]:
        stmt = select(Coupon).where(Coupon.deleted_at == None)
        if not include_inactive:
            stmt = stmt.where(Coupon.is_active == True)
        stmt = stmt.order_by(desc(Coupon.created_at)).offset((page - 1) * size).limit(size)

        result     = await session.exec(stmt)
        coupons    = result.all()
        count_stmt = select(Coupon).where(Coupon.deleted_at == None)
        if not include_inactive:
            count_stmt = count_stmt.where(Coupon.is_active == True)
        total_result = await session.exec(count_stmt)
        total        = len(total_result.all())
        return {"items": coupons, "total": total, "page": page, "size": size}

    async def update_coupon(
        self, session: AsyncSession, code: str, data: "CouponUpdateRequest"  # noqa: F821
    ) -> Coupon:
        from fastapi import HTTPException
        coupon = await self.get_coupon_by_code(session, code)
        if not coupon:
            raise HTTPException(404, detail="Kupon tidak ditemukan")
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(coupon, k, v)
        session.add(coupon)
        await session.commit()
        await session.refresh(coupon)
        await invalidate_coupon_cache(coupon.code)
        return coupon

    async def soft_delete_coupon(self, session: AsyncSession, code: str) -> Dict[str, str]:
        from fastapi import HTTPException
        coupon = await self.get_coupon_by_code(session, code)
        if not coupon:
            raise HTTPException(404, detail="Kupon tidak ditemukan")
        coupon.deleted_at = datetime.now(timezone.utc)
        coupon.is_active  = False
        session.add(coupon)
        await session.commit()
        await invalidate_coupon_cache(code)
        return {"message": f"Kupon '{code}' berhasil dihapus", "code": code}

    async def hard_delete_coupon(self, session: AsyncSession, code: str) -> Dict[str, str]:
        from fastapi import HTTPException
        result = await session.exec(select(Coupon).where(Coupon.code == code.upper()))
        coupon = result.first()
        if not coupon:
            raise HTTPException(404, detail="Kupon tidak ditemukan")
        await session.delete(coupon)
        await session.commit()
        await invalidate_coupon_cache(code)
        return {"message": f"Kupon '{code}' berhasil dihapus permanen"}

    # ══════════════════════════════════════════════════════════════
    # 🎟️ COUPON VALIDATE — Redis-first
    # ══════════════════════════════════════════════════════════════

    async def validate_coupon(
        self, session: AsyncSession, code: str, cart_total: int
    ) -> Dict[str, Any]:
        code = code.strip().upper()

        cached_raw  = await get_cached_coupon(code)
        coupon_data: Optional[Dict] = None
        if cached_raw:
            try:
                coupon_data = json.loads(cached_raw)
            except Exception:
                coupon_data = None

        if not coupon_data:
            coupon = await self.get_coupon_by_code(session, code)
            if not coupon:
                return {"is_valid": False, "message": "Kode kupon tidak ditemukan."}
            coupon_data = {
                "uuid":           str(coupon.uuid),
                "code":           coupon.code,
                "discount_type":  coupon.discount_type,
                "discount_value": coupon.discount_value,
                "min_purchase":   coupon.min_purchase,
                "max_discount":   coupon.max_discount,
                "quota":          coupon.quota,
                "used_count":     coupon.used_count,
                "valid_from":     coupon.valid_from.isoformat() if coupon.valid_from else None,
                "valid_until":    coupon.valid_until.isoformat() if coupon.valid_until else None,
                "is_active":      coupon.is_active,
            }
            await cache_coupon(code, json.dumps(coupon_data))

        if not coupon_data.get("is_active"):
            return {"is_valid": False, "message": "Kupon sudah tidak aktif."}
        if coupon_data["quota"] <= coupon_data["used_count"]:
            return {"is_valid": False, "message": "Kuota kupon sudah habis."}

        now = datetime.now(timezone.utc)
        if coupon_data.get("valid_from"):
            valid_from = datetime.fromisoformat(coupon_data["valid_from"])
            if now < valid_from:
                return {"is_valid": False, "message": "Kupon belum bisa digunakan."}
        if coupon_data.get("valid_until"):
            valid_until = datetime.fromisoformat(coupon_data["valid_until"])
            if now > valid_until:
                return {"is_valid": False, "message": "Kupon sudah kadaluarsa."}
        if cart_total < coupon_data["min_purchase"]:
            return {
                "is_valid": False,
                "message":  f"Minimal belanja Rp {coupon_data['min_purchase']:,} untuk kupon ini.",
            }

        if coupon_data["discount_type"] == "percentage":
            calc     = int(cart_total * coupon_data["discount_value"] / 100)
            max_disc = coupon_data.get("max_discount")
            discount_amount = min(calc, max_disc) if max_disc else calc
        else:
            discount_amount = coupon_data["discount_value"]

        discount_amount = min(discount_amount, cart_total)
        return {
            "is_valid": True,
            "data": {
                "coupon_code":     coupon_data["code"],
                "discount_amount": discount_amount,
                "final_total":     cart_total - discount_amount,
            },
        }

    async def use_coupon(self, session: AsyncSession, code: str) -> None:
        coupon = await self.get_coupon_by_code(session, code)
        if coupon:
            coupon.used_count += 1
            session.add(coupon)
            await session.commit()
            await invalidate_coupon_cache(code)

    # ══════════════════════════════════════════════════════════════
    # 🔍 PUBLIC SEARCH (tidak berubah)
    # ══════════════════════════════════════════════════════════════

    def _build_brand_filter(self, brand: str) -> dict:
        brand_clean = brand.strip()
        return {
            "bool": {
                "should": [
                    {"term": {"brand.keyword": {"value": brand_clean, "case_insensitive": True}}},
                    {"term": {"brand_normalized": brand_clean.lower()}},
                    {"match_phrase": {"brand": brand_clean}},
                ],
                "minimum_should_match": 1,
            }
        }

    async def search_stocks_es(
        self, q=None, categories=None, brand=None, item_type=None,
        min_p=None, max_p=None, sort_by="newest", limit=20, offset=0
    ):
        safe_categories = list(categories or [])
        query_body = {"bool": {"must": [], "filter": [{"term": {"is_active": True}}]}}

        if "popular" in safe_categories:
            safe_categories.remove("popular")
            if sort_by == "newest":
                sort_by = "popular_sort"

        if q:
            query_body["bool"]["must"].append({
                "multi_match": {
                    "query": q, "fields": ["title^3", "brand^2", "type"],
                    "fuzziness": "AUTO", "operator": "or", "minimum_should_match": "60%",
                }
            })
        else:
            query_body["bool"]["must"].append({"match_all": {}})

        if safe_categories and "semua-kategori" not in safe_categories:
            main_cats, sub_cats = set(), set()
            for cat in safe_categories:
                is_child = any(cat.startswith(f"{other}-") for other in safe_categories if other != cat)
                (sub_cats if is_child else main_cats).add(cat)
            should_clauses = []
            if main_cats:
                should_clauses += [
                    {"terms": {"category_slug.keyword": list(main_cats)}},
                    {"terms": {"category_slug":         list(main_cats)}},
                ]
            if sub_cats:
                should_clauses += [
                    {"terms": {"subcategory_slug.keyword": list(sub_cats)}},
                    {"terms": {"subcategory_slug":         list(sub_cats)}},
                ]
            if should_clauses:
                query_body["bool"]["filter"].append(
                    {"bool": {"should": should_clauses, "minimum_should_match": 1}}
                )

        if brand and brand.lower() not in ("semua-brand", "all", ""):
            query_body["bool"]["filter"].append(self._build_brand_filter(brand))

        if item_type and item_type.lower() not in ("semua-tipe", "all", ""):
            query_body["bool"]["filter"].append({
                "bool": {"should": [
                    {"term": {"type.keyword": {"value": item_type, "case_insensitive": True}}},
                    {"match_phrase": {"type": item_type}},
                ], "minimum_should_match": 1}
            })

        if min_p is not None or max_p is not None:
            price_range: Dict[str, Any] = {}
            if min_p is not None: price_range["gte"] = min_p
            if max_p is not None: price_range["lte"] = max_p
            query_body["bool"]["filter"].append({"range": {"online_price": price_range}})

        sort_body = self._build_sort(sort_by)
        aggs = {
            "categories_count":    {"terms": {"field": "category_slug.keyword", "size": 50}},
            "subcategories_count": {"terms": {"field": "subcategory_slug.keyword", "size": 50}},
            "brands_count":        {"terms": {"field": "brand.keyword", "size": 50}},
            "price_stats":         {"stats": {"field": "online_price"}},
            "popular_terms":       {"terms": {"field": "brand.keyword", "size": 5}},
        }
        suggest = {"spell_check": {"text": q, "term": {"field": "title", "suggest_mode": "missing"}}} if q else {}

        response = await es_client.search(
            index="products", query=query_body, sort=sort_body,
            aggs=aggs, suggest=suggest or None, from_=offset, size=limit,
        )

        return {
            "total": response["hits"]["total"]["value"],
            "items": self._parse_hits(response["hits"]["hits"]),
            "facets": {
                "categories":    {b["key"]: b["doc_count"] for b in response["aggregations"]["categories_count"]["buckets"]},
                "subcategories": {b["key"]: b["doc_count"] for b in response["aggregations"]["subcategories_count"]["buckets"]},
                "brands":        {b["key"]: b["doc_count"] for b in response["aggregations"]["brands_count"]["buckets"]},
                "price_range":   {"min": response["aggregations"]["price_stats"]["min"] or 0,
                                  "max": response["aggregations"]["price_stats"]["max"] or 0},
                "popular_terms": [b["key"] for b in response["aggregations"]["popular_terms"]["buckets"]],
            },
            "suggestion": self._extract_suggestion(response),
        }

    async def search_by_brand_es(
        self, brand, q=None, categories=None,
        min_p=None, max_p=None, sort_by="newest", limit=20, offset=0
    ):
        if not brand or not brand.strip():
            return {"total": 0, "items": [], "facets": {}, "suggestion": None, "brand_info": None}

        query_body = {"bool": {
            "must":   [],
            "filter": [{"term": {"is_active": True}}, self._build_brand_filter(brand)],
        }}

        if q:
            query_body["bool"]["must"].append({
                "multi_match": {
                    "query": q, "fields": ["title^3", "type^2"],
                    "fuzziness": "AUTO", "operator": "or", "minimum_should_match": "60%",
                }
            })
        else:
            query_body["bool"]["must"].append({"match_all": {}})

        safe_cats = list(categories or [])
        if safe_cats and "semua-kategori" not in safe_cats:
            clauses = []
            for cat in safe_cats:
                is_child = any(cat.startswith(f"{o}-") for o in safe_cats if o != cat)
                if is_child:
                    clauses += [
                        {"term": {"subcategory_slug.keyword": cat}},
                        {"term": {"subcategory_slug": cat}},
                    ]
                else:
                    clauses += [
                        {"term": {"category_slug.keyword": cat}},
                        {"term": {"category_slug": cat}},
                    ]
            if clauses:
                query_body["bool"]["filter"].append({"bool": {"should": clauses, "minimum_should_match": 1}})

        if min_p is not None or max_p is not None:
            price_range: Dict[str, Any] = {}
            if min_p is not None: price_range["gte"] = min_p
            if max_p is not None: price_range["lte"] = max_p
            query_body["bool"]["filter"].append({"range": {"online_price": price_range}})

        response = await es_client.search(
            index="products", query=query_body, sort=self._build_sort(sort_by),
            aggs={
                "categories_count":    {"terms": {"field": "category_slug.keyword", "size": 30}},
                "subcategories_count": {"terms": {"field": "subcategory_slug.keyword", "size": 30}},
                "price_stats":         {"stats": {"field": "online_price"}},
                "brand_name_sample":   {"top_hits": {"size": 1, "_source": ["brand"]}},
            },
            suggest={"spell_check": {"text": q, "term": {"field": "title", "suggest_mode": "missing"}}} if q else None,
            from_=offset, size=limit,
        )

        items  = self._parse_hits(response["hits"]["hits"])
        sample = response["aggregations"]["brand_name_sample"]["hits"]["hits"]
        brand_name_actual = sample[0]["_source"].get("brand", brand) if sample else brand

        return {
            "total":      response["hits"]["total"]["value"],
            "items":      items,
            "facets": {
                "categories":    {b["key"]: b["doc_count"] for b in response["aggregations"]["categories_count"]["buckets"]},
                "subcategories": {b["key"]: b["doc_count"] for b in response["aggregations"]["subcategories_count"]["buckets"]},
                "price_range":   {"min": response["aggregations"]["price_stats"]["min"] or 0,
                                  "max": response["aggregations"]["price_stats"]["max"] or 0},
            },
            "suggestion": self._extract_suggestion(response),
            "brand_info": {"slug": brand.lower().strip(), "name": brand_name_actual},
        }

    async def get_all_brands_es(self, min_product_count: int = 1) -> List[Dict]:
        try:
            response = await es_client.search(index="products", body={
                "size": 0, "query": {"term": {"is_active": True}},
                "aggs": {"all_brands": {
                    "terms": {
                        "field": "brand.keyword", "size": 200,
                        "order": {"_count": "desc"}, "min_doc_count": min_product_count,
                    },
                    "aggs": {"sample_image": {"top_hits": {"size": 1, "_source": ["image_url", "category_slug"]}}},
                }},
            })
            buckets = response.get("aggregations", {}).get("all_brands", {}).get("buckets", [])
            brands  = []
            for b in buckets:
                if not b["key"] or b["key"].lower() == "no brand":
                    continue
                hits = b.get("sample_image", {}).get("hits", {}).get("hits", [])
                brands.append({
                    "name":          b["key"],
                    "slug":          b["key"].lower().strip().replace(" ", "-"),
                    "product_count": b["doc_count"],
                    "sample_image":  hits[0]["_source"].get("image_url") if hits else None,
                    "category":      hits[0]["_source"].get("category_slug") if hits else None,
                })
            return brands
        except Exception as e:
            logger.error(f"ES Get All Brands Error: {e}")
            return []

    async def get_similar_products_es(self, stock_uuid: str, limit: int = 5):
        try:
            source_res = await es_client.get(index="products", id=stock_uuid)
            source_doc = source_res["_source"]
        except Exception:
            return []

        category     = source_doc.get("category_slug", "")
        brand        = source_doc.get("brand", "")
        price        = source_doc.get("online_price", 0)
        title        = source_doc.get("title", "")
        price_origin = price if price > 0 else 100_000

        response = await es_client.search(index="products", body={
            "query": {"function_score": {
                "query": {"bool": {
                    "must_not": [{"term": {"_id": stock_uuid}}],
                    "filter":   [{"term": {"is_active": True}}],
                    "should": [
                        {"term":  {"category_slug": {"value": category, "boost": 5.0}}},
                        {"bool": {"should": [
                            {"term": {"brand.keyword":    {"value": brand, "case_insensitive": True}}},
                            {"term": {"brand_normalized": brand.lower().strip()}},
                        ], "minimum_should_match": 1, "boost": 3.0}},
                        {"match": {"title": {"query": title, "boost": 2.0}}},
                    ],
                    "minimum_should_match": 1,
                }},
                "functions": [
                    {"gauss": {"online_price": {
                        "origin": price_origin,
                        "scale":  max(price_origin * 0.3, 50_000),
                        "decay":  0.5,
                    }}, "weight": 2.0},
                    {"random_score": {}, "weight": 0.5},
                ],
                "score_mode": "sum", "boost_mode": "multiply",
            }},
        }, size=limit)

        return [self._parse_single_hit(h["_source"]) for h in response["hits"]["hits"]]

    async def get_stock_detail(self, session: AsyncSession, stock_uuid: UUID):
        stmt   = select(Stock).where(Stock.uuid == stock_uuid).options(selectinload(Stock.assets))
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_stock_detail_by_slug(self, session: AsyncSession, slug: str):
        stmt   = select(Stock).where(Stock.slug == slug).options(selectinload(Stock.assets))
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_top_collections_es(self):
        try:
            response = await es_client.search(
                index="products", size=0,
                query={"term": {"is_active": True}},
                aggs={"top_brands": {
                    "terms": {"field": "brand", "size": 6, "order": {"_count": "desc"}, "min_doc_count": 1},
                    "aggs":  {"top_types": {"terms": {"field": "type", "size": 5, "min_doc_count": 1}}},
                }},
            )
            buckets     = response.get("aggregations", {}).get("top_brands", {}).get("buckets", [])
            collections = []
            for b in buckets:
                if not b["key"] or b["key"].lower().strip() in ("no brand", "nobrand", "-", ""):
                    continue
                collections.append({
                    "brand":      f"Top {b['key'].capitalize()} Collection",
                    "brand_raw":  b["key"],
                    "items":      [t["key"] for t in b.get("top_types", {}).get("buckets", [])],
                    "seeAllLink": f"/brands/{b['key'].lower().strip().replace(' ', '-')}",
                })
                if len(collections) >= 3:
                    break
            return collections
        except Exception as e:
            logger.error(f"Megamenu ES Error: {e}")
            return []

    async def get_merged_brands_with_products(
        self, official_brands: List[Dict], items_per_brand: int = 10
    ):
        brand_lookup = {
            b["n"].lower().strip(): {"name": b["n"], "image": b["img"], "slug": b["s"], "route": b["r"]}
            for b in official_brands if b.get("img")
        }
        if not brand_lookup:
            return []

        try:
            response = await es_client.search(index="products", body={
                "size": 0,
                "query": {"term": {"is_active": True}},
                "aggs": {"brand_grouping": {
                    "terms": {
                        "field": "brand", "size": 50,
                        "order": {"_count": "desc"},
                        "exclude": ["NO BRAND", "no brand", "No Brand", ""],
                    },
                    "aggs": {"top_hits_items": {"top_hits": {
                        "size": items_per_brand,
                        "sort": [{"online_price": {"order": "desc"}}],
                        "_source": [
                            "uuid", "title", "slug", "online_price", "original_price",
                            "discount_percentage", "image_url", "brand", "specs", "type",
                        ],
                    }}},
                }},
            })
            buckets    = response.get("aggregations", {}).get("brand_grouping", {}).get("buckets", [])
            final_data = []
            for bucket in buckets:
                norm = str(bucket["key"]).lower().strip()
                if not norm or norm in ("no brand", "nobrand", "-"):
                    continue
                master = brand_lookup.get(norm)
                if not master:
                    continue
                hits = bucket.get("top_hits_items", {}).get("hits", {}).get("hits", [])
                if not hits:
                    continue
                final_data.append({
                    "brand_name":  master["name"],
                    "brand_logo":  master["image"],
                    "brand_slug":  master["slug"],
                    "total_items": bucket["doc_count"],
                    "products": [{
                        "uuid":                h["_source"].get("uuid"),
                        "title":               h["_source"].get("title"),
                        "slug":                h["_source"].get("slug"),
                        "price":               h["_source"].get("online_price"),
                        "original_price":      h["_source"].get("original_price"),
                        "discount_percentage": h["_source"].get("discount_percentage"),
                        "image":               h["_source"].get("image_url"),
                        "type":                h["_source"].get("type", ""),
                        "specs":               h["_source"].get("specs", {}),
                    } for h in hits],
                })
            return final_data
        except Exception as e:
            logger.error(f"BrandShowcase Error: {e}")
            return []

    async def get_autocomplete_suggestions_es(
        self, q: str, search_type: str = "all", limit: int = 5
    ):
        if not q or len(q) < 2:
            return {"items": [], "categories": [], "brands": [], "suggestion": None}

        query_body = {"bool": {
            "must":   [{"multi_match": {
                "query":   q,
                "fields":  ["title^4", "brand^3", "category_slug^2", "subcategory_slug^2", "type"],
                "fuzziness": "AUTO", "operator": "or",
            }}],
            "filter": [{"term": {"is_active": True}}],
        }}

        if search_type == "kategori":
            query_body["bool"]["filter"].append({"bool": {
                "should": [
                    {"match": {"category_slug":    {"query": q, "fuzziness": "AUTO"}}},
                    {"match": {"subcategory_slug": {"query": q, "fuzziness": "AUTO"}}},
                ],
                "minimum_should_match": 1,
            }})
        elif search_type == "brand":
            query_body["bool"]["filter"].append(self._build_brand_filter(q))

        try:
            response = await es_client.search(
                index="products", query=query_body, size=limit,
                aggs={
                    "top_categories": {"terms": {"field": "category_slug", "size": 3}},
                    "top_brands":     {"terms": {"field": "brand.keyword", "size": 3,
                                                 "exclude": ["NO BRAND", "no brand", ""]}},
                },
                suggest={"spell_check": {"text": q, "term": {"field": "title", "suggest_mode": "missing"}}},
                _source=["uuid", "title", "slug", "online_price", "original_price",
                         "discount_percentage", "image_url", "brand"],
            )
            return {
                "items": [{
                    "uuid":                h["_source"].get("uuid"),
                    "title":               h["_source"].get("title"),
                    "slug":                h["_source"].get("slug"),
                    "price":               h["_source"].get("online_price"),
                    "original_price":      h["_source"].get("original_price"),
                    "discount_percentage": h["_source"].get("discount_percentage"),
                    "image":               h["_source"].get("image_url"),
                    "brand":               h["_source"].get("brand", ""),
                } for h in response["hits"]["hits"]],
                "categories": [b["key"] for b in response["aggregations"]["top_categories"]["buckets"]],
                "brands":     [b["key"] for b in response["aggregations"]["top_brands"]["buckets"]
                               if b["key"].lower() not in ("no brand", "")],
                "suggestion": self._extract_suggestion(response),
            }
        except Exception as e:
            logger.error(f"Autocomplete ES Error: {e}")
            return {"items": [], "categories": [], "brands": [], "suggestion": None}

    # ── Shared helpers ─────────────────────────────────────────────
    def _parse_hits(self, hits: list) -> List[Dict]:
        return [self._parse_single_hit(h["_source"]) for h in hits]

    def _parse_single_hit(self, source: dict) -> Dict:
        return {
            "uuid":                source.get("uuid"),
            "title":               source.get("title"),
            "slug":                source.get("slug"),
            "price":               source.get("online_price"),
            "original_price":      source.get("original_price"),
            "discount_percentage": source.get("discount_percentage"),
            "image":               source.get("image_url"),
            "category":            source.get("category_slug"),
            "subcategory":         source.get("subcategory_slug"),
            "brand":               source.get("brand", "NO BRAND"),
            "type":                source.get("type", ""),
            "specs":               source.get("specs", {}),
        }

    def _build_sort(self, sort_by: str) -> list:
        return {
            "price_asc":    [{"online_price": {"order": "asc"}}],
            "price_desc":   [{"online_price": {"order": "desc"}}],
            "popular_sort": [{"terjual":      {"order": "desc"}}],
            "discount":     [{"discount_percentage": {"order": "desc"}}],
        }.get(sort_by, [{"created_at": {"order": "desc"}}])

    def _extract_suggestion(self, response: dict) -> Optional[str]:
        spell = response.get("suggest", {}).get("spell_check", [])
        return spell[0]["options"][0]["text"] if spell and spell[0].get("options") else None