from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from .model import Cart
from backend.data.stock.model import Stock
from .schema import CartSummaryResponse, CartItemResponse, CartStockResponse

class CartService:
    @staticmethod
    async def add_to_cart(session: AsyncSession, user_uuid: UUID, stock_uuid: UUID, quantity: int) -> Cart:
        # 1. Cek apakah stock ada dan is_active
        stmt_stock = select(Stock).where(Stock.uuid == stock_uuid, Stock.is_active == True)
        result_stock = await session.execute(stmt_stock)
        stock = result_stock.scalar_one_or_none()

        if not stock:
            raise HTTPException(status_code=404, detail="Barang tidak ditemukan atau tidak aktif")

        if stock.stok < quantity:
            raise HTTPException(status_code=400, detail="Stok barang tidak mencukupi")

        # 2. Cek apakah barang sudah ada di keranjang user
        stmt_cart = select(Cart).where(
            Cart.user_uuid == user_uuid, 
            Cart.stock_uuid == stock_uuid
        )
        result_cart = await session.execute(stmt_cart)
        existing_cart = result_cart.scalar_one_or_none()

        if existing_cart:
            # Jika ada, tambahkan quantity-nya
            new_quantity = existing_cart.quantity + quantity
            if stock.stok < new_quantity:
                raise HTTPException(status_code=400, detail="Total stok tidak mencukupi untuk penambahan ini")
            existing_cart.quantity = new_quantity
            cart_item = existing_cart
        else:
            # Jika belum ada, buat baru
            cart_item = Cart(user_uuid=user_uuid, stock_uuid=stock_uuid, quantity=quantity)
            session.add(cart_item)

        await session.commit()
        await session.refresh(cart_item)
        return cart_item

    @staticmethod
    async def get_user_cart(session: AsyncSession, user_uuid: UUID) -> CartSummaryResponse:
        # Eager Loading: Ambil Cart + Stock + Assets secara bersamaan untuk mencegah N+1 query problem
        stmt = (
            select(Cart)
            .where(Cart.user_uuid == user_uuid)
            .options(
                joinedload(Cart.stock).selectinload(Stock.assets)
            )
            .order_by(Cart.created_at.desc())
        )
        result = await session.execute(stmt)
        carts = result.scalars().all()

        items = []
        total_price = 0
        total_qty = 0

        for c in carts:
            stock = c.stock
            # Ambil gambar pertama jika ada
            cover_url = stock.assets[0].url if stock.assets else None
            
            subtotal = stock.online_price * c.quantity
            total_price += subtotal
            total_qty += c.quantity

            items.append(
                CartItemResponse(
                    cart_uuid=c.uuid,
                    quantity=c.quantity,
                    subtotal=subtotal,
                    berat=c.stock_uuid,
                    stock=CartStockResponse(
                        uuid=stock.uuid,
                        title=stock.title,
                        slug=stock.slug,
                        online_price=stock.online_price,
                        original_price=stock.original_price, # Sekarang akan dirender
                        discount_percentage=stock.discount_percentage, # Sekarang akan dirender
                        brand=stock.brand, # Sekarang akan dirender
                        category_slug=stock.category_slug,
                        subcategory_slug=stock.subcategory_slug,
                        specs=stock.specs, # Sekarang akan dirender
                        cover_image_url=cover_url,
                        weight=stock.weight
                        
                    )
                )
            )

        return CartSummaryResponse(
            items=items,
            total_quantity=total_qty,
            total_price=total_price
        )

    @staticmethod
    async def update_cart_quantity(session: AsyncSession, cart_uuid: UUID, user_uuid: UUID, quantity: int):
        stmt = select(Cart).where(Cart.uuid == cart_uuid, Cart.user_uuid == user_uuid).options(joinedload(Cart.stock))
        result = await session.execute(stmt)
        cart = result.scalar_one_or_none()

        if not cart:
            raise HTTPException(status_code=404, detail="Item keranjang tidak ditemukan")

        if cart.stock.stok < quantity:
            raise HTTPException(status_code=400, detail=f"Sisa stok hanya {cart.stock.stok}")

        cart.quantity = quantity
        await session.commit()
        return {"message": "Kuantitas berhasil diupdate"}

    @staticmethod
    async def remove_from_cart(session: AsyncSession, cart_uuid: UUID, user_uuid: UUID):
        stmt = select(Cart).where(Cart.uuid == cart_uuid, Cart.user_uuid == user_uuid)
        result = await session.execute(stmt)
        cart = result.scalar_one_or_none()

        if not cart:
            raise HTTPException(status_code=404, detail="Item keranjang tidak ditemukan")

        await session.delete(cart)
        await session.commit()
        return {"message": "Item berhasil dihapus dari keranjang"}