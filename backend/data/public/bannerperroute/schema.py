from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from typing import List, Optional

VALID_MODES = (
    "auto", "single", "double", "mixed", "triple", "quad",
    "asymLeft", "asymRight", "heroStrip", "spotlight", "mosaic",
    "ribbon", "featureWide", "cinematic", "stack", "marquee", "filmStrip",
)


FORBIDDEN_URL_PREFIXES = ("javascript:", "data:", "vbscript:", "file:")

class ImageItemCreate(BaseModel):
    asset_uuid: UUID
    target_url: str
    order: int = 1

    @field_validator("target_url")
    @classmethod
    def validate_target_url(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("target_url tidak boleh kosong")
        low = s.lower()
        if any(low.startswith(prefix) for prefix in FORBIDDEN_URL_PREFIXES):
            raise ValueError("target_url dilarang menggunakan skema tidak aman")
        if not (s.startswith("/") or low.startswith("https://") or low.startswith("http://")):
            raise ValueError("target_url harus berupa relative path (diawali /) atau URL https://")
        return s


class ImageSectionCreate(BaseModel):
    identifier: str = Field(..., description="Contoh: category:kamera-cctv")
    title: str
    mode: str = Field(default="auto", description="Layout mode untuk Vue component")
    is_active: bool = True

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        if v not in VALID_MODES:
            raise ValueError(f"mode harus salah satu dari: {', '.join(VALID_MODES)}")
        return v


class ImageSectionUpdate(BaseModel):
    title: Optional[str] = None
    mode: Optional[str] = None          # ← bisa update mode tanpa deploy ulang frontend
    is_active: Optional[bool] = None

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_MODES:
            raise ValueError(f"mode harus salah satu dari: {', '.join(VALID_MODES)}")
        return v


# ── Response ──────────────────────────────────────────────

class ImageItemResponse(BaseModel):
    uuid: UUID
    image_url: str
    alt_text: Optional[str] = None
    target_url: str
    order: int


class ImageSectionResponse(BaseModel):
    uuid: UUID
    identifier: str
    title: str
    mode: str                           # ← dikirim ke frontend
    is_active: bool
    items: List[ImageItemResponse] = []