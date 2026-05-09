from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

# Sesuaikan import ini dengan struktur folder Anda
from backend.db.main import get_session
from backend.auth.depedence import get_current_user 
from backend.auth.model import User
from .schemas import WishlistAddRequest, WishlistItemResponse,WishlistUpdateRequest
from .service import WishlistService

router = APIRouter(
)

# route.py
@router.patch("/{wishlist_uuid}")
async def update_wishlist_item(
    wishlist_uuid: UUID,
    request: WishlistUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Mengupdate informasi tambahan pada item wishlist (seperti notes)."""
    return await WishlistService.update_wishlist_item(
        session=session,
        wishlist_uuid=wishlist_uuid,
        user_uuid=current_user.uuid,
        data=request
    )
@router.post("", status_code=201)
async def add_item_to_wishlist(
    request: WishlistAddRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Menambahkan barang ke wishlist user."""
    return await WishlistService.add_to_wishlist(
        session=session, 
        user_uuid=current_user.uuid, 
        stock_uuid=request.stock_uuid
    )

@router.get("", response_model=List[WishlistItemResponse])
async def get_my_wishlist(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Melihat daftar seluruh wishlist user."""
    return await WishlistService.get_user_wishlist(
        session=session, 
        user_uuid=current_user.uuid
    )

@router.delete("/{wishlist_uuid}")
async def delete_wishlist_item(
    wishlist_uuid: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Menghapus barang dari wishlist."""
    return await WishlistService.remove_from_wishlist(
        session=session, 
        wishlist_uuid=wishlist_uuid, 
        user_uuid=current_user.uuid
    )