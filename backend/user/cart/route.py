from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

# Sesuaikan import ini dengan struktur folder Anda
from backend.db.main import get_session # Dependency DB Session Anda
from backend.auth.depedence import get_current_user # Dependency JWT/Auth Anda
from backend.auth.model import User
from .schema import CartAddRequest, CartUpdateRequest, CartSummaryResponse
from .service import CartService

router = APIRouter()

@router.post("", response_model=dict, status_code=201)
async def add_item_to_cart(
    request: CartAddRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Menambahkan barang ke keranjang atau menambah kuantitas jika sudah ada."""
    await CartService.add_to_cart(
        session=session, 
        user_uuid=current_user.uuid, 
        stock_uuid=request.stock_uuid, 
        quantity=request.quantity,
        options=request.options
    )
    return {"message": "Berhasil ditambahkan ke keranjang"}

@router.get("", response_model=CartSummaryResponse)
async def get_my_cart(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Melihat isi keranjang belanja user."""
    return await CartService.get_user_cart(session=session, user_uuid=current_user.uuid)

@router.patch("/{cart_uuid}")
async def update_cart_item(
    cart_uuid: UUID,
    request: CartUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Mengubah jumlah barang di dalam keranjang."""
    return await CartService.update_cart_quantity(
        session=session, 
        cart_uuid=cart_uuid, 
        user_uuid=current_user.uuid, 
        quantity=request.quantity
    )

@router.delete("/{cart_uuid}")
async def delete_cart_item(
    cart_uuid: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Menghapus satu barang dari keranjang."""
    return await CartService.remove_from_cart(
        session=session, 
        cart_uuid=cart_uuid, 
        user_uuid=current_user.uuid
    )