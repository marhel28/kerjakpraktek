from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from .model import Wishlist
from backend.data.stock.model import Stock
from .schemas import WishlistItemResponse, WishlistStockResponse,WishlistAddRequest,WishlistUpdateRequest

class WishlistService:
    @staticmethod
    async def update_wishlist_item(
        session: AsyncSession, 
        wishlist_uuid: UUID, 
        user_uuid: UUID, 
        data: WishlistUpdateRequest
    ):
        # Cari itemnya dan pastikan milik user yang sedang login
        stmt = select(Wishlist).where(
            Wishlist.uuid == wishlist_uuid, 
            Wishlist.user_uuid == user_uuid
        )
        result = await session.execute(stmt)
        wishlist_item = result.scalar_one_or_none()

        if not wishlist_item:
            raise HTTPException(
                status_code=404, 
                detail="Item wishlist tidak ditemukan"
            )

        # Update field yang dikirim
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(wishlist_item, key, value)

        await session.commit()
        await session.refresh(wishlist_item)
        
        return {"message": "Wishlist berhasil diperbarui", "data": wishlist_item}
    @staticmethod
    async def add_to_wishlist(session: AsyncSession, user_uuid: UUID, stock_uuid: UUID) -> dict:
        # 1. Cek apakah barangnya memang ada
        stmt_stock = select(Stock.uuid).where(Stock.uuid == stock_uuid)
        result_stock = await session.execute(stmt_stock)
        if not result_stock.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Barang tidak ditemukan")

        # 2. Cek apakah sudah ada di wishlist (menghindari error UniqueConstraint)
        stmt_wishlist = select(Wishlist).where(
            Wishlist.user_uuid == user_uuid, 
            Wishlist.stock_uuid == stock_uuid
        )
        result_wishlist = await session.execute(stmt_wishlist)
        
        # Jika sudah ada, kembalikan response sukses tanpa melakukan insert baru
        if result_wishlist.scalar_one_or_none():
            return {"message": "Barang sudah ada di wishlist"}

        # 3. Insert ke database
        new_wishlist = Wishlist(user_uuid=user_uuid, stock_uuid=stock_uuid)
        session.add(new_wishlist)
        await session.commit()
        
        return {"message": "Berhasil ditambahkan ke wishlist"}

    @staticmethod
    async def get_user_wishlist(session: AsyncSession, user_uuid: UUID) -> list[WishlistItemResponse]:
        # 🔥 CEPAT: Ambil wishlist + data stock + image cover dalam 1 kali proses query
        stmt = (
            select(Wishlist)
            .where(Wishlist.user_uuid == user_uuid)
            .options(
                joinedload(Wishlist.stock).selectinload(Stock.assets)
            )
            .order_by(Wishlist.created_at.desc())
        )
        result = await session.execute(stmt)
        wishlists = result.scalars().all()

        items = []
        for w in wishlists:
            stock = w.stock
            cover_url = stock.assets[0].url if stock.assets else None

            items.append(
                WishlistItemResponse(
                    wishlist_uuid=w.uuid,
                    created_at=w.created_at,
                    stock=WishlistStockResponse(
                        uuid=stock.uuid,
                        title=stock.title,
                        slug=stock.slug,
                        online_price=stock.online_price,
                        
                        # 🔥 DATA TAMBAHAN YANG DI-MAPPING:
                        original_price=stock.original_price,
                        discount_percentage=stock.discount_percentage,
                        brand=stock.brand,
                        category_slug=stock.category_slug,
                        subcategory_slug=stock.subcategory_slug,
                        specs=stock.specs,
                        
                        is_active=stock.is_active,
                        cover_image_url=cover_url
                    )
                )
            )

        return items
    @staticmethod
    async def remove_from_wishlist(session: AsyncSession, wishlist_uuid: UUID, user_uuid: UUID):
        stmt = select(Wishlist).where(Wishlist.uuid == wishlist_uuid, Wishlist.user_uuid == user_uuid)
        result = await session.execute(stmt)
        wishlist = result.scalar_one_or_none()

        if not wishlist:
            raise HTTPException(status_code=404, detail="Item tidak ditemukan di wishlist Anda")

        await session.delete(wishlist)
        await session.commit()
        return {"message": "Item berhasil dihapus dari wishlist"}