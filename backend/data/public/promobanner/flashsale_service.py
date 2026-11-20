"""
flashsale_service.py — Service logika Flash Sale (Auto & Manual Pick)
Sistem: Padjajaran CCTV, Cimahi
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select, desc
from uuid import UUID

from backend.data.public.promobanner.model import Promo, PromoItem, PromoStatus, PromoType
from backend.data.stock.model import Stock, AssetStock
import json
from backend.db.redis import get_redis_token

FLASHSALE_CACHE_KEY = "flashsale:active:payload"
FLASHSALE_CACHE_TTL = 60  # 60 detik


class FlashSaleService:
    @staticmethod
    async def get_active_flashsale(session: AsyncSession) -> Optional[Dict[str, Any]]:
        # 1. Cek Redis Cache
        try:
            r = get_redis_token()
            cached_raw = await r.get(FLASHSALE_CACHE_KEY)
            if cached_raw:
                return json.loads(cached_raw)
        except Exception:
            pass

        now = datetime.now(timezone.utc)

        # 2. Query promo flash sale aktif berurutan prioritas
        stmt = (
            select(Promo)
            .where(
                (Promo.promo_type == PromoType.FLASH_SALE) | (Promo.is_flash_sale == True),
                Promo.status == PromoStatus.ACTIVE,
                Promo.valid_from <= now,
                Promo.valid_until >= now,
                Promo.deleted_at.is_(None),
            )
            .order_by(desc(Promo.priority), desc(Promo.created_at))
            .limit(1)
        )
        res = await session.execute(stmt)
        promo = res.scalar_one_or_none()

        if not promo:
            return None

        # 3. Ambil Item Produk
        items: List[Dict[str, Any]] = []

        if promo.flash_sale_mode == "auto":
            items = await FlashSaleService._pick_auto_items(session, promo)
        else:
            items = await FlashSaleService._pick_manual_items(session, promo)

        # Sisa detik countdown
        remaining_seconds = max(0, int((promo.valid_until - now).total_seconds()))

        payload = {
            "promo_uuid": str(promo.uuid),
            "title": promo.name,
            "mode": promo.flash_sale_mode,
            "strategy": promo.auto_strategy,
            "valid_from": promo.valid_from.isoformat(),
            "valid_until": promo.valid_until.isoformat(),
            "server_now": now.isoformat(),
            "remaining_seconds": remaining_seconds,
            "items": items,
        }

        # 4. Set ke Cache
        try:
            r = get_redis_token()
            await r.set(FLASHSALE_CACHE_KEY, json.dumps(payload), ex=FLASHSALE_CACHE_TTL)
        except Exception:
            pass
        return payload

    @staticmethod
    async def _pick_manual_items(session: AsyncSession, promo: Promo) -> List[Dict[str, Any]]:
        stmt = (
            select(PromoItem, Stock)
            .join(Stock, PromoItem.stock_uuid == Stock.uuid)
            .options(selectinload(Stock.assets))
            .where(PromoItem.promo_uuid == promo.uuid, Stock.stok > 0)
            .limit(16)
        )
        res = await session.execute(stmt)
        rows = res.all()

        items = []
        for p_item, stock in rows:
            discount_pct = p_item.override_discount_value or promo.discount_value or stock.discount_percentage or 0
            original_price = stock.original_price or stock.online_price
            price = max(0, int(original_price * (1 - (discount_pct / 100))))

            image_url = stock.assets[0].url if getattr(stock, "assets", None) and len(stock.assets) > 0 else "/images/placeholder.jpg"

            items.append({
                "stock_uuid": str(stock.uuid),
                "title": stock.title,
                "slug": stock.slug,
                "image": image_url,
                "original_price": original_price,
                "price": price,
                "discount_percentage": discount_pct,
                "quota": promo.flash_sale_quota or 50,
                "sold_count": 0,
                "is_almost_sold_out": stock.stok <= 5,
            })
        return items

    @staticmethod
    async def _pick_auto_items(session: AsyncSession, promo: Promo) -> List[Dict[str, Any]]:
        strategy = promo.auto_strategy or "discount"
        
        stmt = select(Stock).options(selectinload(Stock.assets)).where(Stock.stok > 0)
        
        if strategy == "discount":
            stmt = stmt.order_by(desc(Stock.discount_percentage))
        elif strategy == "stock_clearance":
            stmt = stmt.order_by(Stock.stok.asc())
        else:
            stmt = stmt.order_by(desc(Stock.created_at))

        stmt = stmt.limit(16)
        res = await session.execute(stmt)
        stocks = res.scalars().all()

        items = []
        for stock in stocks:
            discount_pct = max(promo.discount_value or 0, stock.discount_percentage or 0)
            original_price = stock.original_price or stock.online_price
            price = max(0, int(original_price * (1 - (discount_pct / 100))))

            image_url = stock.assets[0].url if getattr(stock, "assets", None) and len(stock.assets) > 0 else "/images/placeholder.jpg"

            items.append({
                "stock_uuid": str(stock.uuid),
                "title": stock.title,
                "slug": stock.slug,
                "image": image_url,
                "original_price": original_price,
                "price": price,
                "discount_percentage": discount_pct,
                "quota": promo.flash_sale_quota or 50,
                "sold_count": 0,
                "is_almost_sold_out": stock.stok <= 5,
            })
        return items

    @staticmethod
    async def invalidate_cache() -> None:
        try:
            r = get_redis_token()
            await r.delete(FLASHSALE_CACHE_KEY)
        except Exception:
            pass
