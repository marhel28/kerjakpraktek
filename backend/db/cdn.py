import aioboto3
from functools import lru_cache
from backend.config import Config
import uuid


# =========================
# SESSION (REUSE CONNECTION)
# =========================
@lru_cache()
def get_s3_session():
    return aioboto3.Session()


# =========================
# CLIENT (ASYNC CONTEXT)
# =========================
async def get_s3_client():
    session = get_s3_session()
    return session.client(
        "s3",
        endpoint_url=f"https://{Config.IdAccount}.r2.cloudflarestorage.com",
        aws_access_key_id=Config.AccessKey,
        aws_secret_access_key=Config.SecretAccess,
    )


# =========================
# UPLOAD FILE (FAST + SAFE)
# =========================
async def upload_file(
    file,
    folder: str = "misc",
    filename: str | None = None,
    content_type: str = "image/jpeg",
) -> str:

    if not filename:
        filename = f"{uuid.uuid4()}.webp"

    key = f"{folder}/{filename}"

    async with await get_s3_client() as s3:
        await s3.put_object(
            Bucket="public",
            Key=key,
            Body=file,
            ContentType=content_type,
            CacheControl="public, max-age=31536000",
        )

    return f"{Config.url_r2}/{key}"


# =========================
# DELETE FILE
# =========================
async def delete_file(key: str):
    async with await get_s3_client() as s3:
        await s3.delete_object(
            Bucket='public',
            Key=key,
        )


# =========================
# GENERATE SIGNED URL (PRIVATE FILE)
# =========================
async def generate_signed_url(key: str, expires: int = 300) -> str:
    async with await get_s3_client() as s3:
        url = await s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": "public",
                "Key": key,
            },
            ExpiresIn=expires,
        )
        return url