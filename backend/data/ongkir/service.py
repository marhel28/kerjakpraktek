import requests
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from sqlmodel import update, select

from backend.auth.model import User, UserAddress
from .schema import UserAddressCreate, SaveUserAddressRequest
from uuid import UUID


class OngkirAPI:
    def __init__(self, api_key: str):
        self.url = "https://rajaongkir.komerce.id/api/v1/calculate/domestic-cost"
        self.search_url = "https://rajaongkir.komerce.id/api/v1/destination/domestic-destination"
        self.api_key = api_key
        self.ORIGIN_BOGOR_UTARA = "16155"

    # ==============================
    # 🔍 SEARCH LOCATION
    # ==============================
    def search_location(self, query: str, limit: int = 10, offset: int = 0):
        if not query or len(query.strip()) < 3:
            return []

        headers = {"key": self.api_key}
        params = {"search": query, "limit": limit, "offset": offset}

        try:
            response = requests.get(
                self.search_url,
                headers=headers,
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                res = response.json()
                data = res.get("data") or []
                return [
                    {
                        "id": item.get("id"),
                        "label": item.get("label"),
                        "province": item.get("province_name"),
                        "city": item.get("city_name"),
                        "district": item.get("district_name"),
                        "subdistrict": item.get("subdistrict_name"),
                        "zip": item.get("zip_code"),
                    }
                    for item in data
                ]

            if response.status_code == 404:
                return []

            return {"error": f"API Error {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    # ==============================
    # 💰 CEK ONGKIR
    # ==============================
    def cek_ongkir(self, destination: str, weight: int = 1000, courier: str = "jne:sicepat:jnt"):
        if not destination:
            return {"error": "Destinasi wajib diisi"}

        headers = {
            "key": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        payload = {
            "origin": self.ORIGIN_BOGOR_UTARA,
            "destination": destination,
            "weight": max(weight, 1),
            "courier": courier.lower().replace(" ", ""),
            "price": "lowest"
        }

        try:
            response = requests.post(self.url, headers=headers, data=payload, timeout=7)

            if response.status_code != 200:
                return {"error": f"API Error {response.status_code}"}

            res = response.json()
            data = res.get("data") or []

            return [
                {
                    "courier": item.get("name"),
                    "service": item.get("service"),
                    "etd": item.get("etd"),
                    "price": item.get("cost")
                }
                for item in data
            ]

        except Exception as e:
            return {"error": str(e)}

    # ==============================
    # 📦 TAMBAH ALAMAT USER
    # ==============================
    async def add_address(
        self,
        db: AsyncSession,
        current_user: User,
        payload: UserAddressCreate
    ):
        # Validasi wajib
        if not payload.location_id:
            raise HTTPException(400, "Lokasi wajib dipilih")
        if not payload.zip_code:
            raise HTTPException(400, "Kode pos wajib diisi")
        if not payload.full_address or not payload.full_address.strip():
            raise HTTPException(400, "Alamat lengkap wajib diisi")

        # Handle default address
        if payload.is_default:
            await db.execute(
                update(UserAddress)
                .where(UserAddress.user_id == current_user.uuid)
                .values(is_default=False)
            )

        new_address = UserAddress(
            user_id=current_user.uuid,
            location_id=payload.location_id,
            zip_code=payload.zip_code,
            full_address=payload.full_address,
            province=payload.province,
            city=payload.city,
            district=payload.district,
            subdistrict=payload.subdistrict,
            label=payload.label,
            is_default=payload.is_default,
        )

        db.add(new_address)
        await db.commit()
        await db.refresh(new_address)

        return new_address

    # ==============================
    # ✏️ UPDATE ALAMAT USER
    # ==============================
    async def update_address(
        self,
        db: AsyncSession,
        current_user: User,
        address_id: str,
        payload: SaveUserAddressRequest
    ):
        result = await db.execute(
            select(UserAddress)
            .where(
                UserAddress.uuid == UUID(address_id),
                UserAddress.user_id == current_user.uuid
            )
        )
        address = result.scalar_one_or_none()

        if not address:
            raise HTTPException(404, "Alamat tidak ditemukan")

        if not payload.location_id:
            raise HTTPException(400, "Lokasi wajib diisi")
        if not payload.zip_code:
            raise HTTPException(400, "Kode pos wajib diisi")
        if not payload.full_address.strip():
            raise HTTPException(400, "Alamat lengkap wajib diisi")

        if payload.is_default:
            await db.execute(
                update(UserAddress)
                .where(UserAddress.user_id == current_user.uuid)
                .values(is_default=False)
            )

        address.location_id = payload.location_id
        address.zip_code = payload.zip_code
        address.full_address = payload.full_address
        address.province = payload.province
        address.city = payload.city
        address.district = payload.district
        address.subdistrict = payload.subdistrict
        address.label = payload.label
        address.is_default = payload.is_default

        db.add(address)
        await db.commit()
        await db.refresh(address)

        return address

    # ==============================
    # 📋 GET SEMUA ALAMAT USER
    # ==============================
    async def get_user_addresses(
        self,
        db: AsyncSession,
        current_user: User
    ):
        result = await db.execute(
            select(UserAddress)
            .where(UserAddress.user_id == current_user.uuid)
            .order_by(UserAddress.is_default.desc(), UserAddress.created_at.desc())
        )
        return result.scalars().all()

    # ==============================
    # 🗑️ DELETE ALAMAT USER
    # ==============================
    async def delete_address(
        self,
        db: AsyncSession,
        current_user: User,
        address_id: UUID
    ):
        result = await db.execute(
            select(UserAddress)
            .where(
                UserAddress.uuid == address_id,
                UserAddress.user_id == current_user.uuid
            )
        )
        address = result.scalar_one_or_none()

        if not address:
            raise HTTPException(404, "Alamat tidak ditemukan")

        await db.delete(address)
        await db.commit()

        return True