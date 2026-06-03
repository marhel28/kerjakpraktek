"""
StockDashboardService
─────────────────────
Semua endpoint dashboard memanfaatkan Dragonfly (Redis-compatible) sebagai
cache L1.  Pattern:  Redis GET → hit? return.  miss? query ES/Postgres → SET.

Key naming convention:
    dash:stock:<endpoint>[:<param>]

TTL:
    summary      → 60 s   (data KPI berubah sering)
    low          → 60 s   (per threshold)
    out          → 60 s   (per page)
    distribution → 300 s  (chart, lebih stabil)
    top-selling  → 120 s
    recent       → 120 s
"""

import json
import logging
import asyncio
from typing import Any, Dict, List, Optional
from sqlalchemy import func, case

from sqlalchemy import func, desc, asc, and_
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..model import Stock, AssetStock
from backend.db.es_client import es_client
from backend.db.redis import get_redis_token

logger = logging.getLogger(__name__)

# ── TTL constants ──────────────────────────────────────────────────
TTL_SUMMARY      = 60
TTL_LOW          = 60
TTL_OUT          = 60
TTL_DISTRIBUTION = 300
TTL_TOP_SELLING  = 120
TTL_RECENT       = 120


# ══════════════════════════════════════════════════════════════════
class StockDashboardService:

    # ─────────────────────────────────────────────────────────────
    # INTERNAL HELPERS
    # ─────────────────────────────────────────────────────────────

    async def _redis_get(self, key: str) -> Optional[Any]:
        """GET dari Redis; return parsed JSON atau None."""
        try:
            r = get_redis_token()
            raw = await r.get(key)
            if raw:
                return json.loads(raw)
        except Exception as exc:
            logger.warning(f"[Dashboard] Redis GET {key} failed: {exc}")
        return None

    async def _redis_set(self, key: str, value: Any, ttl: int) -> None:
        """SET ke Redis dengan TTL; silent fail agar tidak block response."""
        try:
            r = get_redis_token()
            await r.set(key, json.dumps(value, default=str), ex=ttl)
        except Exception as exc:
            logger.warning(f"[Dashboard] Redis SET {key} failed: {exc}")

    # ─────────────────────────────────────────────────────────────
    # 1. SUMMARY / KPI
    # ─────────────────────────────────────────────────────────────

    async def get_summary(self, session: AsyncSession) -> Dict:
        CACHE_KEY = "dash:stock:summary"

        cached = await self._redis_get(CACHE_KEY)
        if cached:
            return {"status": "success", "source": "cache", "data": cached}

        # ── Query Postgres dengan scalar aggregation ──────────────
        # Satu kali round-trip ke DB untuk semua KPI
        total_q = await session.execute(
            select(
                func.count(Stock.uuid).label("total"),

                func.sum(
                    case((Stock.is_active == True, 1), else_=0)
                ).label("active"),

                func.coalesce(func.sum(Stock.terjual), 0).label("total_terjual"),

                func.coalesce(
                    func.sum(
                        (Stock.online_price * Stock.stok)
                    ).filter(Stock.is_active == True),
                    0
                ).label("revenue_potential"),
            )
        )
        row = total_q.one()

        total       = row.total or 0
        active      = int(row.active or 0)
        inactive    = total - active
        terjual     = int(row.total_terjual or 0)
        rev_pot     = int(row.revenue_potential or 0)

        # Low stock: 1 ≤ stok ≤ 5 & active
        low_q = await session.execute(
            select(func.count(Stock.uuid)).where(
                and_(Stock.is_active == True, Stock.stok >= 1, Stock.stok <= 5)
            )
        )
        low_count = low_q.scalar() or 0

        # Out of stock: stok = 0 & active
        out_q = await session.execute(
            select(func.count(Stock.uuid)).where(
                and_(Stock.is_active == True, Stock.stok == 0)
            )
        )
        out_count = out_q.scalar() or 0

        data = {
            "total_products":        total,
            "active_products":       active,
            "inactive_products":     inactive,
            "low_stock_count":       low_count,
            "out_of_stock_count":    out_count,
            "total_terjual":         terjual,
            "revenue_potential":     rev_pot,
        }

        await self._redis_set(CACHE_KEY, data, TTL_SUMMARY)
        return {"status": "success", "source": "db", "data": data}

    # ─────────────────────────────────────────────────────────────
    # 2. LOW STOCK
    # ─────────────────────────────────────────────────────────────

    async def get_low_stock(
        self, session: AsyncSession, threshold: int = 5, size: int = 20
    ) -> Dict:
        CACHE_KEY = f"dash:stock:low:{threshold}:{size}"

        cached = await self._redis_get(CACHE_KEY)
        if cached:
            return {"status": "success", "source": "cache", **cached}

        stmt = (
            select(Stock)
            .where(
                and_(
                    Stock.is_active == True,
                    Stock.stok >= 1,
                    Stock.stok <= threshold,
                )
            )
            .order_by(asc(Stock.stok), desc(Stock.terjual))
            .limit(size)
        )
        result = await session.execute(stmt)
        stocks = result.scalars().all()

        items = [
            {
                "uuid":       str(s.uuid),
                "title":      s.title,
                "slug":       s.slug,
                "brand":      s.brand,
                "category":   s.category_slug,
                "price":      s.online_price,
                "stok":       s.stok,
                "terjual":    s.terjual,
            }
            for s in stocks
        ]

        payload = {"total": len(items), "threshold": threshold, "items": items}
        await self._redis_set(CACHE_KEY, payload, TTL_LOW)
        return {"status": "success", "source": "db", **payload}

    # ─────────────────────────────────────────────────────────────
    # 3. OUT OF STOCK
    # ─────────────────────────────────────────────────────────────

    async def get_out_of_stock(
        self, session: AsyncSession, page: int = 1, size: int = 20
    ) -> Dict:
        CACHE_KEY = f"dash:stock:out:{page}:{size}"

        cached = await self._redis_get(CACHE_KEY)
        if cached:
            return {"status": "success", "source": "cache", **cached}

        offset = (page - 1) * size

        stmt = (
            select(Stock)
            .where(and_(Stock.is_active == True, Stock.stok == 0))
            .order_by(desc(Stock.terjual), desc(Stock.updated_at))
            .offset(offset)
            .limit(size)
        )
        result = await session.execute(stmt)
        stocks = result.scalars().all()

        # Total count
        count_q = await session.execute(
            select(func.count(Stock.uuid)).where(
                and_(Stock.is_active == True, Stock.stok == 0)
            )
        )
        total = count_q.scalar() or 0

        items = [
            {
                "uuid":        str(s.uuid),
                "title":       s.title,
                "slug":        s.slug,
                "brand":       s.brand,
                "category":    s.category_slug,
                "price":       s.online_price,
                "terjual":     s.terjual,
                "updated_at":  s.updated_at,
            }
            for s in stocks
        ]

        payload = {"total": total, "page": page, "size": size, "items": items}
        await self._redis_set(CACHE_KEY, payload, TTL_OUT)
        return {"status": "success", "source": "db", **payload}

    # ─────────────────────────────────────────────────────────────
    # 4. DISTRIBUTION — Elasticsearch aggregation
    # ─────────────────────────────────────────────────────────────

    async def get_distribution(self) -> Dict:
        CACHE_KEY = "dash:stock:distribution"

        cached = await self._redis_get(CACHE_KEY)
        if cached:
            return {"status": "success", "source": "cache", "data": cached}

        try:
            sql_cat = """
            SELECT category_slug as label, COUNT(*) as count, SUM(online_price * stok) as revenue, SUM(terjual) as total_terjual
            FROM products
            WHERE is_active = 1
            GROUP BY category_slug
            ORDER BY count DESC
            LIMIT 30
            """
            
            sql_brand = """
            SELECT brand_attr as label, COUNT(*) as count, SUM(online_price * stok) as revenue, SUM(terjual) as total_terjual
            FROM products
            WHERE is_active = 1 AND brand_attr != '' AND brand_normalized != 'no brand' AND brand_normalized != 'no-brand'
            GROUP BY brand_attr
            ORDER BY count DESC
            LIMIT 20
            """
            
            sql_price = """
            SELECT 
                SUM(IF(online_price < 500000, 1, 0)) as range1,
                SUM(IF(online_price >= 500000 AND online_price < 1000000, 1, 0)) as range2,
                SUM(IF(online_price >= 1000000 AND online_price < 3000000, 1, 0)) as range3,
                SUM(IF(online_price >= 3000000 AND online_price < 5000000, 1, 0)) as range4,
                SUM(IF(online_price >= 5000000, 1, 0)) as range5
            FROM products
            WHERE is_active = 1
            """
            
            sql_stock = """
            SELECT 
                SUM(IF(stok < 1, 1, 0)) as habis,
                SUM(IF(stok >= 1 AND stok <= 5, 1, 0)) as kritis,
                SUM(IF(stok >= 6 AND stok <= 20, 1, 0)) as aman,
                SUM(IF(stok > 20, 1, 0)) as banyak
            FROM products
            WHERE is_active = 1
            """

            res_cat, res_brand, res_price, res_stock = await asyncio.gather(
                es_client.execute_sql(sql_cat),
                es_client.execute_sql(sql_brand),
                es_client.execute_sql(sql_price),
                es_client.execute_sql(sql_stock),
            )

            by_category = []
            for r in res_cat:
                if r.get("label"):
                    by_category.append({
                        "label": r["label"],
                        "count": int(r["count"]),
                        "revenue": int(r.get("revenue") or 0),
                        "total_terjual": int(r.get("total_terjual") or 0)
                    })

            by_brand = []
            for r in res_brand:
                if r.get("label"):
                    by_brand.append({
                        "label": r["label"],
                        "count": int(r["count"]),
                        "revenue": int(r.get("revenue") or 0),
                        "total_terjual": int(r.get("total_terjual") or 0)
                    })

            price_row = res_price[0] if res_price else {}
            price_histogram = [
                {"label": "< 500rb", "count": int(price_row.get("range1") or 0)},
                {"label": "500rb – 1jt", "count": int(price_row.get("range2") or 0)},
                {"label": "1jt – 3jt", "count": int(price_row.get("range3") or 0)},
                {"label": "3jt – 5jt", "count": int(price_row.get("range4") or 0)},
                {"label": "> 5jt", "count": int(price_row.get("range5") or 0)},
            ]

            stock_row = res_stock[0] if res_stock else {}
            stock_status = [
                {"label": "Habis", "count": int(stock_row.get("habis") or 0)},
                {"label": "Kritis (1–5)", "count": int(stock_row.get("kritis") or 0)},
                {"label": "Aman (6–20)", "count": int(stock_row.get("aman") or 0)},
                {"label": "Banyak (>20)", "count": int(stock_row.get("banyak") or 0)},
            ]

            data = {
                "by_category": by_category,
                "by_brand": by_brand,
                "price_histogram": price_histogram,
                "stock_status": stock_status,
            }

        except Exception as exc:
            logger.error(f"[Dashboard] Distribution Manticore error: {exc}")
            data = {
                "by_category": [], "by_brand": [],
                "price_histogram": [], "stock_status": [],
            }

        await self._redis_set(CACHE_KEY, data, TTL_DISTRIBUTION)
        return {"status": "success", "source": "elasticsearch", "data": data}

    # ─────────────────────────────────────────────────────────────
    # 5. TOP SELLING
    # ─────────────────────────────────────────────────────────────

    async def get_top_selling(
        self, session: AsyncSession, limit: int = 10
    ) -> Dict:
        CACHE_KEY = f"dash:stock:top-selling:{limit}"

        cached = await self._redis_get(CACHE_KEY)
        if cached:
            return {"status": "success", "source": "cache", "items": cached}

        stmt = (
            select(Stock)
            .where(Stock.is_active == True)
            .order_by(desc(Stock.terjual), desc(Stock.online_price))
            .limit(limit)
        )
        result = await session.execute(stmt)
        stocks = result.scalars().all()

        items = [
            {
                "uuid":                 str(s.uuid),
                "title":                s.title,
                "slug":                 s.slug,
                "brand":                s.brand,
                "category":             s.category_slug,
                "price":                s.online_price,
                "original_price":       s.original_price,
                "discount_percentage":  s.discount_percentage,
                "stok":                 s.stok,
                "terjual":              s.terjual,
                "revenue":              s.online_price * s.terjual,
            }
            for s in stocks
        ]

        await self._redis_set(CACHE_KEY, items, TTL_TOP_SELLING)
        return {"status": "success", "source": "db", "items": items}

    # ─────────────────────────────────────────────────────────────
    # 6. RECENT PRODUCTS — Elasticsearch (created_at DESC)
    # ─────────────────────────────────────────────────────────────

    async def get_recent_products(self, limit: int = 10) -> Dict:
        CACHE_KEY = f"dash:stock:recent:{limit}"

        cached = await self._redis_get(CACHE_KEY)
        if cached:
            return {"status": "success", "source": "cache", "items": cached}

        try:
            sql = f"SELECT * FROM products ORDER BY created_at DESC LIMIT {int(limit)}"
            res = await es_client.execute_sql(sql)
            
            items = []
            for r in res:
                created_at_ts = r.get("created_at")
                created_at_iso = None
                if created_at_ts:
                    from datetime import datetime, timezone
                    created_at_iso = datetime.fromtimestamp(created_at_ts, tz=timezone.utc).isoformat()
                    
                items.append({
                    "uuid":                r.get("uuid"),
                    "title":               r.get("title"),
                    "slug":                r.get("slug"),
                    "brand":               r.get("brand"),
                    "category":            r.get("category_slug"),
                    "price":               r.get("online_price"),
                    "original_price":      r.get("original_price"),
                    "discount_percentage": r.get("discount_percentage"),
                    "stok":                int(r.get("stok") or 0),
                    "terjual":             int(r.get("terjual") or 0),
                    "is_active":           bool(r.get("is_active")),
                    "image":               r.get("image_url"),
                    "created_at":          created_at_iso,
                })

        except Exception as exc:
            logger.error(f"[Dashboard] Recent Manticore error: {exc}")
            items = []

        await self._redis_set(CACHE_KEY, items, TTL_RECENT)
        return {"status": "success", "source": "elasticsearch", "items": items}