from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class OngkirRequest(BaseModel):
    destination: str
    weight: Optional[int] = 1000
    courier: Optional[str] = "jne:sicepat:jnt:pos:lion:anteraja"


class UserAddressCreate(BaseModel):
    location_id: str = Field(..., description="ID lokasi dari API Komerce")
    zip_code: str = Field(..., min_length=5, description="Kode pos")
    full_address: str = Field(..., min_length=10, description="Detail alamat lengkap")

    # Field lokasi detail — diisi dari hasil search_location di frontend
    province: Optional[str] = Field(None, description="Nama provinsi")
    city: Optional[str] = Field(None, description="Nama kota/kabupaten")
    district: Optional[str] = Field(None, description="Nama kecamatan")
    subdistrict: Optional[str] = Field(None, description="Nama desa/kelurahan")
    label: Optional[str] = Field(None, description="Label lengkap dari API")

    is_default: bool = False


class SaveUserAddressRequest(BaseModel):
    location_id: str = Field(..., description="ID lokasi dari API")
    zip_code: str = Field(..., min_length=5)
    full_address: str = Field(..., min_length=10, description="Detail alamat")

    # Field lokasi detail
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    subdistrict: Optional[str] = None
    label: Optional[str] = None

    is_default: Optional[bool] = False


class ShippingOptionResponse(BaseModel):
    courier: str
    service: str
    etd: Optional[str]
    price: int