from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from .service import OngkirAPI
from backend.config import Config
from .schema import OngkirRequest, UserAddressCreate, SaveUserAddressRequest
from backend.db.main import get_session
from backend.auth.depedence import get_current_user
from backend.auth.model import User

router_ship = APIRouter()

service_ship = OngkirAPI(api_key=Config.SHIPPING_COST)


# ==============================
# 🔍 SEARCH LOKASI
# ==============================
@router_ship.get("/lokasi")
def find_location(
    q: str = Query(..., min_length=3),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
):
    result = service_ship.search_location(q, limit, offset)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return {"status": "success", "data": result}


# ==============================
# 💰 HITUNG ONGKIR
# ==============================
@router_ship.post("/ongkir")
async def calculate_shipping(data: OngkirRequest):
    result = service_ship.cek_ongkir(
        destination=data.destination,
        weight=data.weight,
        courier=data.courier,
    )

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {"status": "success", "data": result}


# ==============================
# 📦 TAMBAH ALAMAT USER
# ==============================
@router_ship.post("/address", status_code=status.HTTP_201_CREATED)
async def create_user_address(
    payload: UserAddressCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    new_address = await service_ship.add_address(
        db=session,
        current_user=current_user,
        payload=payload,
    )
    return {"message": "Alamat berhasil ditambahkan", "data": new_address}


# ==============================
# 📋 GET SEMUA ALAMAT USER
# ==============================
@router_ship.get("/address")
async def get_user_addresses(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    addresses = await service_ship.get_user_addresses(
        db=session,
        current_user=current_user,
    )
    return {"status": "success", "data": addresses}


# ==============================
# ✏️ UPDATE ALAMAT USER
# ==============================
@router_ship.put("/address/{address_id}")
async def update_user_address(
    address_id: str,
    payload: SaveUserAddressRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    updated = await service_ship.update_address(
        db=session,
        current_user=current_user,
        address_id=address_id,
        payload=payload,
    )
    return {"message": "Alamat berhasil diupdate", "data": updated}


# ==============================
# 🗑️ DELETE ALAMAT USER
# ==============================
@router_ship.delete("/address/{address_id}")
async def delete_user_address(
    address_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await service_ship.delete_address(
        db=session,
        current_user=current_user,
        address_id=address_id,
    )
    return {"message": "Alamat berhasil dihapus"}