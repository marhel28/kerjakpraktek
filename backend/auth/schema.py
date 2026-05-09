from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from .model import UserRole, UserType

class SupabaseUserData(BaseModel):
    id: str
    email: str

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    uuid: UUID
    username: str
    email: EmailStr
    role: UserRole
    user_type: UserType
    is_verified: bool
    waktu_create: datetime
    waktu_update: datetime

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    alamat: Optional[str] = None
    provinsi: Optional[str] = None
    kabupaten: Optional[str] = None
    kecamatan: Optional[str] = None
    nomertlp: Optional[str] = Field(None, max_length=15)


class EmailRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)


class GoogleAuthRequest(BaseModel):
    id_token: str
class SupabaseSession(BaseModel):
    access_token: str
    refresh_token: str
    user: SupabaseUserData

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead
    supabase: Optional[SupabaseSession] = None 