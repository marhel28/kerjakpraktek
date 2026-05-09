import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database & Auth
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    
    # Infrastructure
    REDIS_HOST: str
    REDIS_PORT: int
    
    # Third Party Services
    SHIPPING_COST: str
    MIDTRANS_CLIENT_KEY: str
    MIDTRANS_SERVER_KEY: str
    
    # Cloudflare R2 / S3
    SecretAccess: str
    AccessKey: str
    IdAccount: str
    url_r2: str
    
    # midtrans
    MIDTRANS_SERVER_KEY :str
    MIDTRANS_CLIENT_KEY : str
    
    # Misc
    Tokenvalue: str
    s3: str
    
    # smtp
    SANDIAPPS : str
    EMAIL_APPS : str
    SMTP_SERVER_PORT : str
    SMTP_HOST : str
    FRONTEND_URL : str
    
    # google
    CLIENT_ID : str
    CLIENT_SECRET : str
    
    # supabase
    SUPABASE_URL : str
    SUPABASE_ANON_KEY : str 
    SUPABASE_SERVICE_ROLE_KEY : str
    
    # 🔥 PERBAIKAN: Deteksi lokasi file .env secara dinamis
    model_config = SettingsConfigDict(
        # Mencari .env di folder tempat file config.py ini berada
        env_file=os.path.join(os.path.dirname(__file__), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache()
def get_settings():
    # Menggunakan lru_cache agar tidak membaca file berkali-kali (lebih cepat)
    return Settings()

# Inisialisasi Config
Config = get_settings()

# --- DEBUGGING (Hapus jika sudah jalan) ---
if not Config.IdAccount:
    print("❌ WARNING: IdAccount is EMPTY! Check your .env file path.")
else:
    print(f"✅ Config Loaded: IdAccount is {Config.IdAccount[:5]}...")