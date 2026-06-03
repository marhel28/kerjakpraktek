import asyncio
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
from backend.db.es_client import (
    es_client, escape_sql_string, parse_manticore_match,
    parse_manticore_match_strict, parse_manticore_match_loose, parse_manticore_match_wildcard,
    get_synonyms
)
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

    def _parse_row_admin(self, row: dict) -> dict:
        stok    = int(row.get("stok", 0) or 0)
        terjual = int(row.get("terjual", 0) or 0)
        sisa    = max(stok - terjual, 0)
        
        specs = row.get("specs", {})
        if isinstance(specs, str):
            try:
                specs = json.loads(specs)
            except Exception:
                specs = {}
                
        return {
            "uuid":         row.get("uuid"),
            "title":        row.get("title"),
            "slug":         row.get("slug"),
            "brand":        row.get("brand", "NO BRAND"),
            "category":     row.get("category_slug"),
            "category_slug":row.get("category_slug"),
            "subcategory":  row.get("subcategory_slug"),
            "subcategory_slug": row.get("subcategory_slug"),
            "type":         row.get("type"),
            "price":        row.get("online_price"),
            "online_price": row.get("online_price"),
            "original_price":      row.get("original_price", 0),
            "discount_percentage": row.get("discount_percentage", 0),
            "stok":         stok,
            "terjual":      terjual,
            "sisa":         sisa,
            "status_stok":  "habis" if sisa <= 0 else "tersedia",
            "is_active":    bool(row.get("is_active")),
            "is_popular":   terjual > 50,
            "image":        row.get("image_url"),
            "total_assets": 0,
        }

    def _parse_row_public(self, row: dict) -> dict:
        specs = row.get("specs", {})
        if isinstance(specs, str):
            try:
                specs = json.loads(specs)
            except Exception:
                specs = {}
        return {
            "uuid":                row.get("uuid"),
            "title":               row.get("title"),
            "slug":                row.get("slug"),
            "price":               row.get("online_price"),
            "original_price":      row.get("original_price"),
            "discount_percentage": row.get("discount_percentage"),
            "image":               row.get("image_url"),
            "category":            row.get("category_slug"),
            "subcategory":         row.get("subcategory_slug"),
            "brand":               row.get("brand", "NO BRAND"),
            "type":                row.get("type", ""),
            "specs":               specs,
            "stok":                row.get("stok", 0),
            "terjual":             row.get("terjual", 0),
        }

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
        session: Optional[AsyncSession] = None,
    ) -> Dict[str, Any]:
        safe_categories = [c for c in (categories or []) if c and c != "semua-kategori"]

        where_clauses = []
        if is_active is not None:
            where_clauses.append(f"is_active = {1 if is_active else 0}")
            
        if stock_status == "tersedia":
            where_clauses.append("stok > 0")
        elif stock_status == "kosong":
            where_clauses.append("stok <= 0")
            
        if safe_categories:
            escaped_cats = ", ".join(f"'{escape_sql_string(c)}'" for c in safe_categories)
            where_clauses.append(f"(category_slug IN ({escaped_cats}) OR subcategory_slug IN ({escaped_cats}))")
            
        if brand and brand.lower() not in ("semua-brand", "all", ""):
            where_clauses.append(f"brand_normalized = '{escape_sql_string(brand.lower().strip())}'")
            
        if item_type and item_type.lower() not in ("semua-tipe", "all", ""):
            where_clauses.append(f"type_attr = '{escape_sql_string(item_type.lower().strip())}'")
            
        if min_p is not None:
            where_clauses.append(f"online_price >= {int(min_p)}")
        if max_p is not None:
            where_clauses.append(f"online_price <= {int(max_p)}")

        # Determine match query using smart fallback hierarchy
        match_query = ""
        if q:
            strict_q = parse_manticore_match_strict(q)
            strict_where = where_clauses + [f"MATCH('{escape_sql_string(strict_q)}')" if strict_q else ""]
            strict_where = [c for c in strict_where if c]
            where_sql_strict = "WHERE " + " AND ".join(strict_where) if strict_where else ""
            try:
                res_count_strict = await es_client.execute_sql(f"SELECT COUNT(*) as total FROM products {where_sql_strict}")
                if res_count_strict and res_count_strict[0]["total"] > 0:
                    match_query = strict_q
            except Exception:
                pass
                
            if not match_query:
                loose_q = parse_manticore_match_loose(q)
                loose_where = where_clauses + [f"MATCH('{escape_sql_string(loose_q)}')" if loose_q else ""]
                loose_where = [c for c in loose_where if c]
                where_sql_loose = "WHERE " + " AND ".join(loose_where) if loose_where else ""
                try:
                    res_count_loose = await es_client.execute_sql(f"SELECT COUNT(*) as total FROM products {where_sql_loose}")
                    if res_count_loose and res_count_loose[0]["total"] > 0:
                        match_query = loose_q
                except Exception:
                    pass
            
            if not match_query:
                match_query = parse_manticore_match_wildcard(q)
                
            if match_query:
                where_clauses.append(f"MATCH('{escape_sql_string(match_query)}')")

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)
            
        sort_map = {
            "newest":     "created_at DESC",
            "oldest":     "created_at ASC",
            "price_asc":  "online_price ASC",
            "price_desc": "online_price DESC",
            "price_low":  "online_price ASC",
            "price_high": "online_price DESC",
            "stock_high": "stok DESC",
            "stock_low":  "stok ASC",
            "sold_high":  "terjual DESC",
            "sold_low":   "terjual ASC",
        }
        sort_clause = sort_map.get(sort_by, "created_at DESC")

        sql_items = f"SELECT * FROM products {where_sql} ORDER BY {sort_clause} LIMIT {int(limit)} OFFSET {int(offset)} OPTION field_weights=(title=5, brand=3, type=2, specs_text=1), ranker=expr('sum(lcs*user_weight)*1000 + terjual*2 + discount_percentage*1')"
        sql_count = f"SELECT COUNT(*) as total FROM products {where_sql}"
        sql_cats  = f"SELECT category_slug, COUNT(*) as doc_count FROM products {where_sql} GROUP BY category_slug ORDER BY doc_count DESC LIMIT 100"
        sql_brands = f"SELECT brand_attr as brand, COUNT(*) as doc_count FROM products {where_sql} GROUP BY brand_attr ORDER BY doc_count DESC LIMIT 100"
        sql_stats = f"SELECT MIN(online_price) as min_p, MAX(online_price) as max_p, AVG(online_price) as avg_p, MIN(stok) as min_s, MAX(stok) as max_s, SUM(stok) as sum_s, MIN(terjual) as min_t, MAX(terjual) as max_t, SUM(terjual) as sum_t, AVG(terjual) as avg_t FROM products {where_sql}"
        sql_avail = f"SELECT SUM(IF(stok > 0, 1, 0)) as tersedia, SUM(IF(stok <= 0, 1, 0)) as kosong FROM products {where_sql}"

        res_items, res_count, res_cats, res_brands, res_stats, res_avail = await asyncio.gather(
            es_client.execute_sql(sql_items),
            es_client.execute_sql(sql_count),
            es_client.execute_sql(sql_cats),
            es_client.execute_sql(sql_brands),
            es_client.execute_sql(sql_stats),
            es_client.execute_sql(sql_avail),
        )

        total = res_count[0]["total"] if res_count else 0
        items = [self._parse_row_admin(row) for row in res_items]

        # Override stok and terjual with actual real-time DB data if session is available
        if session and items:
            from sqlalchemy import select
            from .model import Stock
            
            item_uuids = [i["uuid"] for i in items]
            stmt = select(Stock.uuid, Stock.stok, Stock.terjual).where(Stock.uuid.in_(item_uuids))
            db_res = await session.execute(stmt)
            real_data = {str(row[0]): {"stok": row[1], "terjual": row[2]} for row in db_res.all()}
            
            final_items = []
            for item in items:
                uid = str(item["uuid"])
                if uid in real_data:
                    item["stok"] = real_data[uid]["stok"]
                    item["terjual"] = real_data[uid]["terjual"]
                    item["sisa"] = max(item["stok"] - item["terjual"], 0)
                    item["status_stok"] = "habis" if item["sisa"] <= 0 else "tersedia"
                    final_items.append(item)
                else:
                    # 👻 GHOST ITEM DETECTED: Ada di ES tapi tidak ada di DB
                    # Kita bersihkan ES secara async agar pencarian berikutnya bersih
                    try:
                        asyncio.create_task(es_client.delete(index="products", id=uid, ignore=[404]))
                        logger.info(f"🧹 Auto-cleaned ghost item from Manticore: {uid}")
                    except Exception:
                        pass
            
            items = final_items

        total_terjual_page = sum(i["terjual"] for i in items)
        
        stats = res_stats[0] if res_stats else {}
        avail = res_avail[0] if res_avail else {}

        return {
            "total":              total,
            "items":              items,
            "total_terjual_page": total_terjual_page,
            "facets": {
                "categories": {
                    b["category_slug"]: b["doc_count"]
                    for b in res_cats
                    if b.get("category_slug")
                },
                "brands": {
                    b["brand"]: b["doc_count"]
                    for b in res_brands
                    if b.get("brand")
                },
                "price_range": {
                    "min": stats.get("min_p") or 0,
                    "max": stats.get("max_p") or 0,
                    "avg": round(stats.get("avg_p") or 0),
                },
                "stok_range": {
                    "min": stats.get("min_s") or 0,
                    "max": stats.get("max_s") or 0,
                    "sum": stats.get("sum_s") or 0,
                },
                "terjual_stats": {
                    "min": stats.get("min_t") or 0,
                    "max": stats.get("max_t") or 0,
                    "sum": stats.get("sum_t") or 0,
                    "avg": round(stats.get("avg_t") or 0),
                },
                "ketersediaan": {
                    "tersedia": int(avail.get("tersedia") or 0),
                    "kosong":   int(avail.get("kosong") or 0),
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
        # Cek kode - ambil semua (termasuk yang sudah soft-delete) karena unik di DB
        stmt = select(Coupon).where(Coupon.code == data.code)
        existing_res = await session.execute(stmt)
        existing = existing_res.scalar_one_or_none()
        
        if existing:
            if existing.deleted_at is None:
                raise HTTPException(409, detail=f"Kupon '{data.code}' sudah ada dan aktif")
            else:
                # Jika sudah ada tapi terhapus, kita bisa "restore" atau hapus permanen dulu
                # Untuk kemudahan, kita hapus permanen yang lama lalu buat baru
                await session.delete(existing)
                await session.flush()

        coupon = Coupon(
            code=data.code,
            description=data.description,
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
            "description":    coupon.description,
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
    # 🎟️ COUPON VALIDATE — Redis-first & Atomic Aware
    # ══════════════════════════════════════════════════════════════

    async def validate_coupon(
        self, session: AsyncSession, code: str, cart_total: int
    ) -> Dict[str, Any]:
        """
        Validasi kupon dengan strategi Cache-First.
        Cepat untuk frontend (checking) dan aman untuk backend (checkout).
        """
        code = code.strip().upper()

        # 1. Cek Cache Redis dulu
        cached_raw  = await get_cached_coupon(code)
        coupon_data: Optional[Dict] = None
        if cached_raw:
            try:
                coupon_data = json.loads(cached_raw)
            except Exception:
                coupon_data = None

        # 2. Fallback ke DB jika cache miss
        if not coupon_data:
            coupon = await self.get_coupon_by_code(session, code)
            if not coupon:
                return {"is_valid": False, "message": "Kode kupon tidak ditemukan."}
            
            # Sync ke cache
            coupon_data = {
                "uuid":           str(coupon.uuid),
                "code":           coupon.code,
                "description":    coupon.description,
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

        # 3. Validasi Logika
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

        # 4. Hitung Diskon
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
                "discount_type":   coupon_data["discount_type"],
                "discount_value":  coupon_data["discount_value"],
                "discount_amount": discount_amount,
                "final_total":     cart_total - discount_amount,
            },
        }

    async def increment_coupon_usage(self, session: AsyncSession, code: str) -> bool:
        """Atomic increment used_count kupon."""
        code = code.strip().upper()
        # Gunakan query UPDATE atomic untuk menghindari race condition
        from sqlalchemy import update
        stmt = (
            update(Coupon)
            .where(Coupon.code == code, Coupon.used_count < Coupon.quota, Coupon.is_active == True)
            .values(used_count=Coupon.used_count + 1)
        )
        result = await session.execute(stmt)
        if result.rowcount > 0:
            await invalidate_coupon_cache(code)
            return True
        return False

    async def decrement_coupon_usage(self, session: AsyncSession, code: str) -> None:
        """Kembalikan kuota kupon (jika transaksi batal/expire)."""
        code = code.strip().upper()
        from sqlalchemy import update
        stmt = (
            update(Coupon)
            .where(Coupon.code == code, Coupon.used_count > 0)
            .values(used_count=Coupon.used_count - 1)
        )
        await session.execute(stmt)
        await invalidate_coupon_cache(code)

    # ══════════════════════════════════════════════════════════════
    # 🔍 PUBLIC SEARCH (tidak berubah)
    # ══════════════════════════════════════════════════════════════

    async def search_stocks_es(
        self, q=None, categories=None, brand=None, item_type=None,
        min_p=None, max_p=None, sort_by="newest", limit=20, offset=0
    ):
        safe_categories = list(categories or [])
        if "popular" in safe_categories:
            safe_categories.remove("popular")
            if sort_by == "newest":
                sort_by = "popular_sort"

        where_clauses = ["is_active = 1"]
        
        if safe_categories and "semua-kategori" not in safe_categories:
            escaped_cats = ", ".join(f"'{escape_sql_string(c)}'" for c in safe_categories)
            where_clauses.append(f"(category_slug IN ({escaped_cats}) OR subcategory_slug IN ({escaped_cats}))")

        if brand and brand.lower() not in ("semua-brand", "all", ""):
            where_clauses.append(f"brand_normalized = '{escape_sql_string(brand.lower().strip())}'")

        if item_type and item_type.lower() not in ("semua-tipe", "all", ""):
            where_clauses.append(f"type_attr = '{escape_sql_string(item_type.lower().strip())}'")

        if min_p is not None:
            where_clauses.append(f"online_price >= {int(min_p)}")
        if max_p is not None:
            where_clauses.append(f"online_price <= {int(max_p)}")

        # Determine match query using smart fallback hierarchy
        match_query = ""
        if q:
            strict_q = parse_manticore_match_strict(q)
            strict_where = where_clauses + [f"MATCH('{escape_sql_string(strict_q)}')" if strict_q else ""]
            strict_where = [c for c in strict_where if c]
            where_sql_strict = "WHERE " + " AND ".join(strict_where) if strict_where else ""
            try:
                res_count_strict = await es_client.execute_sql(f"SELECT COUNT(*) as total FROM products {where_sql_strict}")
                if res_count_strict and res_count_strict[0]["total"] > 0:
                    match_query = strict_q
            except Exception:
                pass
                
            if not match_query:
                loose_q = parse_manticore_match_loose(q)
                loose_where = where_clauses + [f"MATCH('{escape_sql_string(loose_q)}')" if loose_q else ""]
                loose_where = [c for c in loose_where if c]
                where_sql_loose = "WHERE " + " AND ".join(loose_where) if loose_where else ""
                try:
                    res_count_loose = await es_client.execute_sql(f"SELECT COUNT(*) as total FROM products {where_sql_loose}")
                    if res_count_loose and res_count_loose[0]["total"] > 0:
                        match_query = loose_q
                except Exception:
                    pass
            
            if not match_query:
                match_query = parse_manticore_match_wildcard(q)
                
            if match_query:
                where_clauses.append(f"MATCH('{escape_sql_string(match_query)}')")

        where_sql = "WHERE " + " AND ".join(where_clauses)
        
        sort_map = {
            "price_asc":    "online_price ASC",
            "price_desc":   "online_price DESC",
            "popular_sort": "terjual DESC",
            "discount":     "discount_percentage DESC",
        }
        sort_clause = sort_map.get(sort_by, "created_at DESC")

        sql_items = f"SELECT * FROM products {where_sql} ORDER BY {sort_clause} LIMIT {int(limit)} OFFSET {int(offset)} OPTION field_weights=(title=5, brand=3, type=2, specs_text=1), ranker=expr('sum(lcs*user_weight)*1000 + terjual*2 + discount_percentage*1')"
        sql_count = f"SELECT COUNT(*) as total FROM products {where_sql}"
        sql_cats  = f"SELECT category_slug, COUNT(*) as doc_count FROM products {where_sql} GROUP BY category_slug ORDER BY doc_count DESC LIMIT 50"
        sql_subcats = f"SELECT subcategory_slug, COUNT(*) as doc_count FROM products {where_sql} AND subcategory_slug != '' GROUP BY subcategory_slug ORDER BY doc_count DESC LIMIT 50"
        sql_brands = f"SELECT brand_attr as brand, COUNT(*) as doc_count FROM products {where_sql} GROUP BY brand_attr ORDER BY doc_count DESC LIMIT 50"
        sql_stats  = f"SELECT MIN(online_price) as min_p, MAX(online_price) as max_p FROM products {where_sql}"
        sql_pop_brands = f"SELECT brand_attr as brand, COUNT(*) as doc_count FROM products {where_sql} GROUP BY brand_attr ORDER BY doc_count DESC LIMIT 5"

        res_items, res_count, res_cats, res_subcats, res_brands, res_stats, res_pop_brands = await asyncio.gather(
            es_client.execute_sql(sql_items),
            es_client.execute_sql(sql_count),
            es_client.execute_sql(sql_cats),
            es_client.execute_sql(sql_subcats),
            es_client.execute_sql(sql_brands),
            es_client.execute_sql(sql_stats),
            es_client.execute_sql(sql_pop_brands),
        )

        total = res_count[0]["total"] if res_count else 0
        items = [self._parse_row_public(row) for row in res_items]
        
        stats = res_stats[0] if res_stats else {}
        min_price = stats.get("min_p") or 0
        max_price = stats.get("max_p") or 0

        return {
            "total": total,
            "items": items,
            "facets": {
                "categories":    {b["category_slug"]: b["doc_count"] for b in res_cats if b.get("category_slug")},
                "subcategories": {b["subcategory_slug"]: b["doc_count"] for b in res_subcats if b.get("subcategory_slug")},
                "brands":        {b["brand"]: b["doc_count"] for b in res_brands if b.get("brand")},
                "price_range":   {"min": min_price, "max": max_price},
                "popular_terms": [b["brand"] for b in res_pop_brands if b.get("brand")],
            },
            "suggestion": None,
        }

    async def search_by_brand_es(
        self, brand, q=None, categories=None,
        min_p=None, max_p=None, sort_by="newest", limit=20, offset=0
    ):
        if not brand or not brand.strip():
            return {"total": 0, "items": [], "facets": {}, "suggestion": None, "brand_info": None}

        where_clauses = ["is_active = 1"]
        brand_clean = brand.strip().lower()
        where_clauses.append(f"(brand_normalized = '{escape_sql_string(brand_clean)}' OR brand = '{escape_sql_string(brand_clean)}')")

        # Determine match query using smart fallback hierarchy
        match_query = ""
        if q:
            strict_q = parse_manticore_match_strict(q)
            strict_where = where_clauses + [f"MATCH('{escape_sql_string(strict_q)}')" if strict_q else ""]
            strict_where = [c for c in strict_where if c]
            where_sql_strict = "WHERE " + " AND ".join(strict_where) if strict_where else ""
            try:
                res_count_strict = await es_client.execute_sql(f"SELECT COUNT(*) as total FROM products {where_sql_strict}")
                if res_count_strict and res_count_strict[0]["total"] > 0:
                    match_query = strict_q
            except Exception:
                pass
                
            if not match_query:
                loose_q = parse_manticore_match_loose(q)
                loose_where = where_clauses + [f"MATCH('{escape_sql_string(loose_q)}')" if loose_q else ""]
                loose_where = [c for c in loose_where if c]
                where_sql_loose = "WHERE " + " AND ".join(loose_where) if loose_where else ""
                try:
                    res_count_loose = await es_client.execute_sql(f"SELECT COUNT(*) as total FROM products {where_sql_loose}")
                    if res_count_loose and res_count_loose[0]["total"] > 0:
                        match_query = loose_q
                except Exception:
                    pass
            
            if not match_query:
                match_query = parse_manticore_match_wildcard(q)
                
            if match_query:
                where_clauses.append(f"MATCH('{escape_sql_string(match_query)}')")

        safe_cats = list(categories or [])
        if safe_cats and "semua-kategori" not in safe_cats:
            escaped_cats = ", ".join(f"'{escape_sql_string(c)}'" for c in safe_cats)
            where_clauses.append(f"(category_slug IN ({escaped_cats}) OR subcategory_slug IN ({escaped_cats}))")

        if min_p is not None:
            where_clauses.append(f"online_price >= {int(min_p)}")
        if max_p is not None:
            where_clauses.append(f"online_price <= {int(max_p)}")

        where_sql = "WHERE " + " AND ".join(where_clauses)
        
        sort_map = {
            "price_asc":    "online_price ASC",
            "price_desc":   "online_price DESC",
            "popular_sort": "terjual DESC",
            "discount":     "discount_percentage DESC",
        }
        sort_clause = sort_map.get(sort_by, "created_at DESC")

        sql_items = f"SELECT * FROM products {where_sql} ORDER BY {sort_clause} LIMIT {int(limit)} OFFSET {int(offset)} OPTION field_weights=(title=5, brand=3, type=2, specs_text=1), ranker=expr('sum(lcs*user_weight)*1000 + terjual*2 + discount_percentage*1')"
        sql_count = f"SELECT COUNT(*) as total FROM products {where_sql}"
        sql_cats  = f"SELECT category_slug, COUNT(*) as doc_count FROM products {where_sql} GROUP BY category_slug ORDER BY doc_count DESC LIMIT 30"
        sql_subcats = f"SELECT subcategory_slug, COUNT(*) as doc_count FROM products {where_sql} AND subcategory_slug != '' GROUP BY subcategory_slug ORDER BY doc_count DESC LIMIT 30"
        sql_stats  = f"SELECT MIN(online_price) as min_p, MAX(online_price) as max_p FROM products {where_sql}"
        sql_brand_sample = f"SELECT brand FROM products {where_sql} LIMIT 1"

        res_items, res_count, res_cats, res_subcats, res_stats, res_sample = await asyncio.gather(
            es_client.execute_sql(sql_items),
            es_client.execute_sql(sql_count),
            es_client.execute_sql(sql_cats),
            es_client.execute_sql(sql_subcats),
            es_client.execute_sql(sql_stats),
            es_client.execute_sql(sql_brand_sample),
        )

        total = res_count[0]["total"] if res_count else 0
        items = [self._parse_row_public(row) for row in res_items]
        
        stats = res_stats[0] if res_stats else {}
        min_price = stats.get("min_p") or 0
        max_price = stats.get("max_p") or 0
        
        brand_name_actual = res_sample[0]["brand"] if res_sample else brand

        return {
            "total": total,
            "items": items,
            "facets": {
                "categories":    {b["category_slug"]: b["doc_count"] for b in res_cats if b.get("category_slug")},
                "subcategories": {b["subcategory_slug"]: b["doc_count"] for b in res_subcats if b.get("subcategory_slug")},
                "price_range":   {"min": min_price, "max": max_price},
            },
            "suggestion": None,
            "brand_info": {"slug": brand.lower().strip(), "name": brand_name_actual},
        }

    async def get_all_brands_es(self, min_product_count: int = 1) -> List[Dict]:
        try:
            sql = f"""
            SELECT brand_attr as brand, COUNT(*) as product_count, image_url, category_slug 
            FROM products 
            WHERE is_active = 1 AND brand_attr != '' AND brand_normalized != 'no brand' AND brand_normalized != 'no-brand'
            GROUP BY brand_attr 
            HAVING product_count >= {int(min_product_count)}
            ORDER BY product_count DESC 
            LIMIT 200
            """
            res = await es_client.execute_sql(sql)
            brands = []
            for row in res:
                name = row["brand"]
                brands.append({
                    "name":          name,
                    "slug":          name.lower().strip().replace(" ", "-"),
                    "product_count": row["product_count"],
                    "sample_image":  row.get("image_url"),
                    "category":      row.get("category_slug"),
                })
            return brands
        except Exception as e:
            logger.error(f"Manticore Get All Brands Error: {e}")
            return []

    async def get_similar_products_es(self, stock_uuid: str, limit: int = 5):
        import random
        try:
            sql_source = f"SELECT * FROM products WHERE uuid = '{escape_sql_string(stock_uuid)}' LIMIT 1"
            res_source = await es_client.execute_sql(sql_source)
            if not res_source:
                return []
            source_doc = res_source[0]
        except Exception as e:
            logger.error(f"Error fetching similarity source: {e}")
            return []

        category = source_doc.get("category_slug", "")
        brand = source_doc.get("brand", "")
        brand_normalized = source_doc.get("brand_normalized", brand.lower().strip() if brand else "")
        price = source_doc.get("online_price", 0)
        title = source_doc.get("title", "")
        price_origin = price if price > 0 else 100000

        category_esc = escape_sql_string(category)
        brand_esc = escape_sql_string(brand_normalized)
        
        # 1. Query by category or brand
        sql_attrs = f"""
            SELECT * FROM products 
            WHERE is_active = 1 
              AND uuid != '{escape_sql_string(stock_uuid)}' 
              AND (category_slug = '{category_esc}' OR brand_normalized = '{brand_esc}')
            LIMIT {int(limit * 2)}
        """
        
        # 2. Query by title MATCH
        words = [w.strip() for w in re.sub(r'[\\\'"()|\-!@~*&/]', ' ', title).split() if w.strip()]
        res_title = []
        if words:
            title_q = " | ".join(words)
            sql_title = f"""
                SELECT * FROM products 
                WHERE is_active = 1 
                  AND uuid != '{escape_sql_string(stock_uuid)}' 
                  AND MATCH('{escape_sql_string(title_q)}')
                LIMIT {int(limit * 2)}
            """
            try:
                res_title = await es_client.execute_sql(sql_title)
            except Exception as e:
                logger.error(f"Error querying similar titles: {e}")

        try:
            res_attrs = await es_client.execute_sql(sql_attrs)
        except Exception as e:
            logger.error(f"Error querying similar attributes: {e}")
            res_attrs = []

        # Combine results
        combined_docs = {}
        title_matched_uuids = set()
        
        for doc in res_title:
            uid = doc.get("uuid")
            if uid:
                combined_docs[uid] = doc
                title_matched_uuids.add(uid)
                
        for doc in res_attrs:
            uid = doc.get("uuid")
            if uid:
                combined_docs[uid] = doc

        # Calculate scores in Python
        scored_items = []
        for uid, doc in combined_docs.items():
            doc_category = doc.get("category_slug", "")
            doc_brand_normalized = doc.get("brand_normalized", "")
            doc_price = doc.get("online_price", 0)
            
            cat_score = 5.0 if doc_category == category else 0.0
            brand_score = 3.0 if doc_brand_normalized == brand_normalized else 0.0
            price_score = 2.0 / (1.0 + (abs(doc_price - price_origin) / price_origin))
            title_score = 4.0 if uid in title_matched_uuids else 0.0
            rand_score = random.random() * 0.5
            
            total_score = cat_score + brand_score + price_score + title_score + rand_score
            scored_items.append((total_score, doc))

        # Sort and take top limit
        scored_items.sort(key=lambda x: x[0], reverse=True)
        final_docs = [item[1] for item in scored_items[:limit]]
        
        return [self._parse_row_public(row) for row in final_docs]

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
            sql_brands = """
            SELECT brand_attr as brand, COUNT(*) as count 
            FROM products 
            WHERE is_active = 1 AND brand_attr != '' AND brand_normalized != 'no brand' AND brand_normalized != 'no-brand'
            GROUP BY brand_attr 
            ORDER BY count DESC 
            LIMIT 6
            """
            res_brands = await es_client.execute_sql(sql_brands)
            collections = []
            
            tasks = []
            for b in res_brands:
                brand_name = b["brand"]
                brand_esc = escape_sql_string(brand_name)
                sql_types = f"""
                SELECT type_attr as type, COUNT(*) as cnt 
                FROM products 
                WHERE is_active = 1 AND brand_normalized = '{brand_esc}' AND type_attr != '' 
                GROUP BY type_attr 
                ORDER BY cnt DESC 
                LIMIT 5
                """
                tasks.append(es_client.execute_sql(sql_types))
                
            res_types_list = await asyncio.gather(*tasks)
            
            for b, res_types in zip(res_brands, res_types_list):
                brand_name = b["brand"]
                collections.append({
                    "brand":      f"Top {brand_name.capitalize()} Collection",
                    "brand_raw":  brand_name,
                    "items":      [t["type"] for t in res_types if t.get("type")],
                    "seeAllLink": f"/brands/{brand_name.lower().strip().replace(' ', '-')}",
                })
                if len(collections) >= 3:
                    break
            return collections
        except Exception as e:
            logger.error(f"Megamenu Manticore Error: {e}")
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
            tasks = []
            brands_to_query = list(brand_lookup.keys())
            
            for brand_norm in brands_to_query[:50]:
                brand_esc = escape_sql_string(brand_norm)
                sql = f"""
                SELECT * 
                FROM products 
                WHERE is_active = 1 AND brand_normalized = '{brand_esc}'
                ORDER BY online_price DESC 
                LIMIT {int(items_per_brand)}
                """
                tasks.append(es_client.execute_sql(sql))
                
            results = await asyncio.gather(*tasks)
            
            final_data = []
            for brand_norm, hits in zip(brands_to_query[:50], results):
                if not hits:
                    continue
                master = brand_lookup[brand_norm]
                
                final_data.append({
                    "brand_name":  master["name"],
                    "brand_logo":  master["image"],
                    "brand_slug":  master["slug"],
                    "total_items": len(hits),
                    "products": [self._parse_row_public(h) for h in hits],
                })
                
            count_tasks = []
            for brand_norm in brands_to_query[:len(final_data)]:
                brand_esc = escape_sql_string(brand_norm)
                count_tasks.append(es_client.execute_sql(f"SELECT COUNT(*) as total FROM products WHERE is_active = 1 AND brand_normalized = '{brand_esc}'"))
            
            count_results = await asyncio.gather(*count_tasks)
            for idx, count_res in enumerate(count_results):
                final_data[idx]["total_items"] = count_res[0]["total"] if count_res else len(final_data[idx]["products"])
                
            return final_data
        except Exception as e:
            logger.error(f"BrandShowcase Manticore Error: {e}")
            return []

    async def get_autocomplete_suggestions_es(
        self, q: str, search_type: str = "all", limit: int = 5
    ):
        if not q or len(q) < 2:
            return {"items": [], "categories": [], "brands": [], "suggestion": None}

        where_clauses = ["is_active = 1"]
        
        words = [w.strip() for w in re.sub(r'[\\\'"()|\-!@~*&/]', ' ', q).split() if w.strip()]
        if words:
            # Smart synonym expansions with prefix matching
            processed = []
            for w in words:
                syns = get_synonyms(w)
                expanded = [f"{s}*" for s in syns]
                processed.append(f"( {' | '.join(expanded)} )")
            match_query = " | ".join(processed)
            where_clauses.append(f"MATCH('{escape_sql_string(match_query)}')")

        if search_type == "kategori":
            where_clauses.append(f"(category_slug = '{escape_sql_string(q)}' OR subcategory_slug = '{escape_sql_string(q)}')")
        elif search_type == "brand":
            where_clauses.append(f"brand_normalized = '{escape_sql_string(q.lower().strip())}'")

        where_sql = "WHERE " + " AND ".join(where_clauses)
        
        sql_items = f"SELECT * FROM products {where_sql} LIMIT {int(limit)} OPTION field_weights=(title=5, brand=3, type=2, specs_text=1)"
        sql_cats = f"SELECT category_slug, COUNT(*) as cnt FROM products {where_sql} GROUP BY category_slug ORDER BY cnt DESC LIMIT 3"
        sql_brands = f"SELECT brand_attr as brand, COUNT(*) as cnt FROM products {where_sql} AND brand_attr != '' GROUP BY brand_attr ORDER BY cnt DESC LIMIT 3"

        res_items, res_cats, res_brands = await asyncio.gather(
            es_client.execute_sql(sql_items),
            es_client.execute_sql(sql_cats),
            es_client.execute_sql(sql_brands),
        )

        return {
            "items": [self._parse_row_public(h) for h in res_items],
            "categories": [b["category_slug"] for b in res_cats if b.get("category_slug")],
            "brands":     [b["brand"] for b in res_brands if b.get("brand") and b["brand"].lower() != "no brand"],
            "suggestion": None,
        }