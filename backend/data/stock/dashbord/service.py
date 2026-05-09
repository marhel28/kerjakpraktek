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
            response = await es_client.search(
                index="products",
                size=0,
                query={"term": {"is_active": True}},
                aggs={
                    # ── by category ──────────────────────────────
                    "by_category": {
                        "terms": {
                            "field": "category_slug.keyword",
                            "size":  30,
                            "order": {"_count": "desc"},
                        },
                        "aggs": {
                            "revenue": {
                                "sum": {"script": {"source": "doc['online_price'].value * doc['stok'].value"}}
                            },
                            "total_terjual": {"sum": {"field": "terjual"}},
                        },
                    },
                    # ── by brand ─────────────────────────────────
                    "by_brand": {
                        "terms": {
                            "field":        "brand.keyword",
                            "size":         20,
                            "order":        {"_count": "desc"},
                            "exclude":      ["NO BRAND", "no brand", "No Brand", ""],
                            "min_doc_count": 1,
                        },
                        "aggs": {
                            "revenue":       {"sum": {"script": {"source": "doc['online_price'].value * doc['stok'].value"}}},
                            "total_terjual": {"sum": {"field": "terjual"}},
                        },
                    },
                    # ── price histogram ───────────────────────────
                    "price_histogram": {
                        "range": {
                            "field":  "online_price",
                            "ranges": [
                                {"key": "< 500rb",          "to":   500_000},
                                {"key": "500rb – 1jt",      "from":  500_000, "to": 1_000_000},
                                {"key": "1jt – 3jt",        "from": 1_000_000, "to": 3_000_000},
                                {"key": "3jt – 5jt",        "from": 3_000_000, "to": 5_000_000},
                                {"key": "> 5jt",            "from": 5_000_000},
                            ],
                        },
                    },
                    # ── stock status split ────────────────────────
                    "stock_status": {
                        "range": {
                            "field":  "stok",
                            "ranges": [
                                {"key": "Habis",         "to":   1},
                                {"key": "Kritis (1–5)",  "from": 1,  "to": 6},
                                {"key": "Aman (6–20)",   "from": 6,  "to": 21},
                                {"key": "Banyak (>20)",  "from": 21},
                            ],
                        }
                    },
                },
            )

            aggs = response.get("aggregations", {})

            def _parse_terms(buckets: list, extra_keys: list[str] = []) -> list:
                out = []
                for b in buckets:
                    item = {"label": b["key"], "count": b["doc_count"]}
                    for k in extra_keys:
                        item[k] = int(b.get(k, {}).get("value", 0) or 0)
                    out.append(item)
                return out

            def _parse_range(buckets: list) -> list:
                return [{"label": b["key"], "count": b["doc_count"]} for b in buckets]

            data = {
                "by_category":     _parse_terms(
                    aggs.get("by_category", {}).get("buckets", []),
                    extra_keys=["revenue", "total_terjual"],
                ),
                "by_brand":        _parse_terms(
                    aggs.get("by_brand", {}).get("buckets", []),
                    extra_keys=["revenue", "total_terjual"],
                ),
                "price_histogram": _parse_range(
                    aggs.get("price_histogram", {}).get("buckets", [])
                ),
                "stock_status":    _parse_range(
                    aggs.get("stock_status", {}).get("buckets", [])
                ),
            }

        except Exception as exc:
            logger.error(f"[Dashboard] Distribution ES error: {exc}")
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
            response = await es_client.search(
                index="products",
                size=limit,
                sort=[{"created_at": {"order": "desc"}}],
                # Tampilkan semua status (aktif & non-aktif) untuk admin
                query={"match_all": {}},
                _source=[
                    "uuid", "title", "slug", "brand",
                    "category_slug", "online_price", "original_price",
                    "discount_percentage", "stok", "terjual",
                    "is_active", "image_url", "created_at",
                ],
            )

            items = [
                {
                    "uuid":                str(h["_source"].get("uuid", h["_id"])),
                    "title":               h["_source"].get("title"),
                    "slug":                h["_source"].get("slug"),
                    "brand":               h["_source"].get("brand"),
                    "category":            h["_source"].get("category_slug"),
                    "price":               h["_source"].get("online_price"),
                    "original_price":      h["_source"].get("original_price"),
                    "discount_percentage": h["_source"].get("discount_percentage"),
                    "stok":                h["_source"].get("stok", 0),
                    "terjual":             h["_source"].get("terjual", 0),
                    "is_active":           h["_source"].get("is_active", True),
                    "image":               h["_source"].get("image_url"),
                    "created_at":          h["_source"].get("created_at"),
                }
                for h in response["hits"]["hits"]
            ]

        except Exception as exc:
            logger.error(f"[Dashboard] Recent ES error: {exc}")
            items = []

        await self._redis_set(CACHE_KEY, items, TTL_RECENT)
        return {"status": "success", "source": "elasticsearch", "items": items}