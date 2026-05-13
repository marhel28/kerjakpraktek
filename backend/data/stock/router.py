from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional, List
import json
import orjson
from uuid import UUID
from pydantic import BaseModel

from backend.db.main import get_session
from .service import StockService
from .schema import (
    CouponCreateRequest, CouponUpdateRequest,
    CouponResponse, CouponValidateRequest,
)
from backend.db.redis import get_redis_token
from backend.data.public.branlogo.service import get_brands_service
from backend.auth.depedence import get_admin  # Admin guard

router = APIRouter()
service = StockService()

MEGAMENU_CACHE_KEY    = "megamenu:top_collections"
BRAND_SHOWCASE_CACHE_KEY = "cache:public:brand_showcase:v2"


# ── Admin: Create stock ────────────────────────────────────────────
@router.post("/admin/create")
async def admin_create_stock(
    title: str = Form(...),
    brand: Optional[str] = Form(None),
    category_slug: str = Form(...),
    subcategory_slug: Optional[str] = Form(None),
    type_item: str = Form("camera cctv", alias="type"),
    original_price: int = Form(0),
    discount_percentage: int = Form(0),
    online_price: int = Form(0),
    stok: int = Form(...),
    weight: int = Form(700),
    specs: str = Form("{}"),
    images: List[UploadFile] = File(default=[]),
    session: AsyncSession = Depends(get_session),
):
    if len(images) > 4:
        raise HTTPException(400, "Max 4 images allowed")

    final_price = online_price
    if original_price > 0 and discount_percentage > 0:
        final_price = int(original_price - (original_price * discount_percentage / 100))
    elif original_price > 0 and online_price == 0:
        final_price = original_price

    data = {
        "title": title, "brand": brand, "category_slug": category_slug,
        "subcategory_slug": subcategory_slug, "type": type_item,
        "original_price": original_price, "discount_percentage": discount_percentage,
        "online_price": final_price, "stok": stok, "weight": weight, "specs": json.loads(specs),
    }
    files = [await img.read() for img in images if img.filename]
    result = await service.create_stock(session, data, files)
    return {"status": "success", "data": {"uuid": str(result.uuid), "title": result.title}}


# ── Public: Coupon validate ────────────────────────────────────────
@router.post("/public/coupon/validate")
async def validate_coupon_endpoint(
    req: CouponValidateRequest,
    session: AsyncSession = Depends(get_session),
):
    result = await service.validate_coupon(session, req.code, req.cart_total)
    if not result["is_valid"]:
        return {"success": False, "message": result["message"]}
    return {"success": True, "message": "Kupon berhasil dipasang!", "data": result["data"]}


# ══════════════════════════════════════════════════════════════════
# Semua endpoint public lainnya — tidak berubah
# ══════════════════════════════════════════════════════════════════

@router.get("/public/list")
async def public_get_products(
    q: Optional[str] = Query(None),
    cat: List[str] = Query(default=[]),
    brand: Optional[str] = Query(None),
    item_type: Optional[str] = Query(None, alias="type"),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    sort: str = Query("newest"),
    page: int = Query(1, ge=1),
    size: int = Query(20, le=100),
):
    offset = (page - 1) * size
    result = await service.search_stocks_es(
        q=q, categories=cat, brand=brand, item_type=item_type,
        min_p=min_price, max_p=max_price, sort_by=sort, limit=size, offset=offset,
    )
    return {"status": "success", "page": page, "size": size, **result}


@router.get("/admin/stocks")
async def admin_get_products(
    q: Optional[str] = Query(None),
    cat: List[str] = Query(default=[]),
    brand: Optional[str] = Query(None),
    item_type: Optional[str] = Query(None, alias="type"),

    # 🔥 tambahan admin
    session: AsyncSession = Depends(get_session),

    # 🔥 tambahan admin
    is_active: Optional[bool] = Query(None),
    stock_status: Optional[str] = Query(None),  # kosong | tersedia

    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),

    sort: str = Query("newest"),
    page: int = Query(1, ge=1),
    size: int = Query(20, le=100),

    # 🔒 (opsional) auth admin
    # user=Depends(get_current_admin)
):
    offset = (page - 1) * size

    result = await service.search_stock_admin(
        q=q,
        categories=cat,
        brand=brand,
        item_type=item_type,
        is_active=is_active,  # 🔥 kirim ke service
        min_p=min_price,
        max_p=max_price,
        sort_by=sort,
        limit=size,
        offset=offset,
        session=session,
    )

    # 🔥 optional filter tambahan (post-process)
    if stock_status:
        if stock_status == "kosong":
            result["items"] = [i for i in result["items"] if i["stok"] <= 0]
        elif stock_status == "tersedia":
            result["items"] = [i for i in result["items"] if i["stok"] > 0]

    return {
        "status": "success",
        "page": page,
        "size": size,
        **result
    }


@router.get("/public/brands")
async def public_get_all_brands(min_products: int = Query(1, ge=1)):
    brands = await service.get_all_brands_es(min_product_count=min_products)
    return {"status": "success", "total": len(brands), "data": brands}


@router.get("/public/brands/{brand_slug}")
async def public_get_products_by_brand(
    brand_slug: str,
    q: Optional[str] = Query(None),
    cat: List[str] = Query(default=[]),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    sort: str = Query("newest"),
    page: int = Query(1, ge=1),
    size: int = Query(20, le=100),
):
    offset = (page - 1) * size
    result = await service.search_by_brand_es(
        brand=brand_slug, q=q, categories=cat,
        min_p=min_price, max_p=max_price, sort_by=sort, limit=size, offset=offset,
    )
    if result["total"] == 0:
        return {"status": "success", "page": page, "size": size, "total": 0,
                "brand_info": result.get("brand_info"), "facets": result.get("facets", {}),
                "suggestion": None, "items": [],
                "message": f"Tidak ada produk untuk brand '{brand_slug}'"}
    return {"status": "success", "page": page, "size": size, **result}


@router.get("/public/popular")
async def public_get_popular_items(session: AsyncSession = Depends(get_session)):
    items = await service.get_popular_items(session)
    return {"status": "success", "items": items}


@router.get("/public/detail/{stock_uuid}")
async def public_get_stock_detail(stock_uuid: UUID, session: AsyncSession = Depends(get_session)):
    stock = await service.get_stock_detail(session, stock_uuid)
    if not stock:
        raise HTTPException(404, "Product not found")
    return {"status": "success", "data": {
        "uuid": str(stock.uuid), "title": stock.title, "slug": stock.slug,
        "brand": stock.brand,
        "brand_slug": stock.brand.lower().strip().replace(" ", "-") if stock.brand else None,
        "category": stock.category_slug, "subcategory": stock.subcategory_slug,
        "type": stock.type, "price": stock.online_price, "original_price": stock.original_price,
        "discount_percentage": stock.discount_percentage, "stok": stock.stok,
        "terjual": stock.terjual, "description": stock.description, "specs": stock.specs,
        "images": [a.url for a in (stock.assets or [])], "weight": stock.weight,
        "created_at": stock.created_at, "updated_at": stock.updated_at,
    }}


@router.get("/public/detail/slug/{slug}")
async def public_get_stock_detail_by_slug(slug: str, session: AsyncSession = Depends(get_session)):
    stock = await service.get_stock_detail_by_slug(session, slug)
    if not stock:
        raise HTTPException(404, "Product not found")
    return {"status": "success", "data": {
        "uuid": str(stock.uuid), "title": stock.title, "slug": stock.slug,
        "brand": stock.brand,
        "brand_slug": stock.brand.lower().strip().replace(" ", "-") if stock.brand else None,
        "category": stock.category_slug, "subcategory": stock.subcategory_slug,
        "type": stock.type, "price": stock.online_price, "original_price": stock.original_price,
        "discount_percentage": stock.discount_percentage, "stok": stock.stok,
        "terjual": stock.terjual, "description": stock.description, "specs": stock.specs,
        "images": [a.url for a in (stock.assets or [])], "weight": stock.weight,
        "created_at": stock.created_at, "updated_at": stock.updated_at,
    }}


@router.get("/public/recommendations/{stock_uuid}")
async def get_recommendations(stock_uuid: str):
    try:
        items = await service.get_similar_products_es(stock_uuid, limit=8)
        return {"status": "success", "data": items}
    except Exception:
        return {"status": "error", "data": []}


@router.get("/public/megamenu-collections")
async def get_megamenu_collections():
    r = get_redis_token()
    try:
        cached = await r.get(MEGAMENU_CACHE_KEY)
        if cached:
            return {"status": "success", "source": "redis", "data": json.loads(cached)}
    except Exception:
        pass
    collections = await service.get_top_collections_es()
    if collections:
        try:
            await r.set(MEGAMENU_CACHE_KEY, json.dumps(collections), ex=86400)
        except Exception:
            pass
    return {"status": "success", "source": "elasticsearch", "data": collections}


@router.get("/public/brand-showcase")
async def get_brand_showcase(session: AsyncSession = Depends(get_session)):
    r = get_redis_token()
    try:
        cached = await r.get(BRAND_SHOWCASE_CACHE_KEY)
        if cached:
            return {"status": "success", "source": "cache_merged", "data": orjson.loads(cached)}
    except Exception:
        pass
    official_brands_bytes = await get_brands_service(session, r)
    official_brands = orjson.loads(official_brands_bytes)
    result = await service.get_merged_brands_with_products(official_brands=official_brands, items_per_brand=10)
    if result:
        try:
            await r.set(BRAND_SHOWCASE_CACHE_KEY, orjson.dumps(result), ex=43200)
        except Exception:
            pass
    return {"status": "success", "source": "live_merged", "data": result}


@router.get("/public/autocomplete")
async def get_autocomplete(
    q: str = Query(..., min_length=2),
    type: str = Query("all"),
):
    result = await service.get_autocomplete_suggestions_es(q=q, search_type=type, limit=5)
    if len(q) >= 3 and result.get("items"):
        try:
            r = get_redis_token()
            await r.zincrby("analytics:trending_searches", 1, q.lower().strip())
            await r.expire("analytics:trending_searches", 172800)
        except Exception:
            pass
    return {"status": "success", "data": result}


@router.get("/public/trending-searches")
async def get_trending_searches():
    try:
        r = get_redis_token()
        top = await r.zrevrange("analytics:trending_searches", 0, 4)
        if top:
            return {"status": "success", "source": "redis_analytics", "data": top}
    except Exception:
        pass
    return {"status": "success", "source": "fallback",
            "data": ["CCTV outdoor", "paket murah", "kamera wifi", "dahua 2mp", "dvr 8 channel"]}
    
    


@router.patch("/admin/update/{stock_uuid}")
async def admin_update_stock(
    stock_uuid: UUID,
    title:               Optional[str]        = Form(None),
    brand:               Optional[str]        = Form(None),
    category_slug:       Optional[str]        = Form(None),
    subcategory_slug:    Optional[str]        = Form(None),
    type_item:           Optional[str]        = Form(None, alias="type"),
    original_price:      Optional[int]        = Form(None),
    discount_percentage: Optional[int]        = Form(None),
    online_price:        Optional[int]        = Form(None),
    stok:                Optional[int]        = Form(None),
    weight:              Optional[int]        = Form(None),
    specs:               Optional[str]        = Form(None),       # JSON string
    is_active:           Optional[str]        = Form(None),       # "true" / "false"
    images:              List[UploadFile]     = File(default=[]),  # kosong = tidak ganti gambar
    session:             AsyncSession         = Depends(get_session),
    # _: any = Depends(get_admin),  # uncomment jika auth admin aktif
):
    """
    Update sebagian atau seluruh field stock.
 
    Aturan:
    - Hanya field yang dikirim yang diupdate (partial update).
    - Jika `images` dikirim (file baru), gambar lama DIHAPUS dan diganti.
    - Jika `images` tidak dikirim / kosong, gambar lama TETAP.
    - `online_price` dihitung otomatis jika `original_price` dan
      `discount_percentage` dikirim bersamaan.
    - `is_active` dikirim sebagai string "true" / "false" karena multipart.
    """
    # ── Bangun dict data yang akan diupdate ──────────────────────
    data: dict = {}
 
    if title               is not None: data["title"]               = title.strip()
    if brand               is not None: data["brand"]               = brand.strip() or None
    if category_slug       is not None: data["category_slug"]       = category_slug
    if subcategory_slug    is not None: data["subcategory_slug"]    = subcategory_slug or None
    if type_item           is not None: data["type"]                = type_item
    if stok                is not None: data["stok"]                = stok
    if weight              is not None: data["weight"]              = weight
 
    # is_active datang sebagai string dari multipart
    if is_active is not None:
        data["is_active"] = is_active.lower() in ("true", "1", "yes")
 
    # Specs: parse JSON jika dikirim
    if specs is not None:
        try:
            data["specs"] = json.loads(specs)
        except json.JSONDecodeError:
            raise HTTPException(400, "specs harus berupa JSON yang valid. Contoh: {\"resolution\": \"4MP\"}")
 
    # Harga: hitung final_price
    # Ambil nilai yang dikirim, fallback None
    _orig  = original_price
    _disc  = discount_percentage
    _price = online_price
 
    if _orig is not None:
        data["original_price"] = _orig
    if _disc is not None:
        data["discount_percentage"] = _disc
 
    # Kalkulasi online_price
    if _orig is not None and _disc is not None and _disc > 0:
        # Harga dari diskon
        data["online_price"] = int(_orig - (_orig * _disc / 100))
    elif _orig is not None and _disc == 0:
        # Reset diskon → harga asli
        data["online_price"] = _orig
        data["discount_percentage"] = 0
    elif _price is not None:
        # Harga manual
        data["online_price"] = _price
 
    # ── File gambar baru ──────────────────────────────────────────
    new_image_files: Optional[List[bytes]] = None
    valid_images = [img for img in images if img.filename]
 
    if valid_images:
        if len(valid_images) > 4:
            raise HTTPException(400, "Maksimal 4 gambar per produk.")
        new_image_files = [await img.read() for img in valid_images]
 
    # ── Tidak ada yang diupdate ───────────────────────────────────
    if not data and new_image_files is None:
        raise HTTPException(400, "Tidak ada data yang dikirim untuk diperbarui.")
 
    # ── Panggil service ───────────────────────────────────────────
    updated = await service.update_stock(
        session=session,
        stock_uuid=stock_uuid,
        data=data,
        image_files=new_image_files,  # None = tidak ganti gambar
    )
 
    if not updated:
        raise HTTPException(404, f"Produk dengan UUID {stock_uuid} tidak ditemukan.")
 
    return {
        "status":  "success",
        "message": f"Produk '{updated.title}' berhasil diperbarui.",
        "data": {
            "uuid":                str(updated.uuid),
            "title":               updated.title,
            "slug":                updated.slug,
            "brand":               updated.brand,
            "category_slug":       updated.category_slug,
            "subcategory_slug":    updated.subcategory_slug,
            "type":                updated.type,
            "original_price":      updated.original_price,
            "discount_percentage": updated.discount_percentage,
            "online_price":        updated.online_price,
            "stok":                updated.stok,
            "weight":              updated.weight,
            "specs":               updated.specs,
            "is_active":           updated.is_active,
            "updated_at":          updated.updated_at,
            "images":              [a.url for a in (updated.assets or [])],
        },
    }
 
@router.delete("/admin/delete/{stock_uuid}")
async def admin_delete_stock(
    stock_uuid: UUID,
    hard:    bool         = Query(False, description="True = hapus permanen dari DB. False (default) = soft delete (is_active=False)."),
    session: AsyncSession = Depends(get_session),
    # _: any = Depends(get_admin),  # uncomment jika auth admin aktif
):
    """
    Hapus produk.
 
    Mode:
    - **Soft delete** (default, `hard=false`):
      Set `is_active = False`. Data tetap di DB, bisa dipulihkan.
      Cocok untuk produk yang mungkin dijual kembali di masa depan.
 
    - **Hard delete** (`hard=true`):
      Hapus permanen dari database + hapus semua aset gambar dari CDN (R2/S3).
      Tidak bisa dibatalkan. Gunakan dengan hati-hati.
    """
    from sqlalchemy.orm import selectinload
    from sqlmodel import select
    from .model import Stock
 
    # ── Cari stock ────────────────────────────────────────────────
    stmt = (
        select(Stock)
        .where(Stock.uuid == stock_uuid)
        .options(selectinload(Stock.assets))
    )
    result = await session.execute(stmt)
    stock = result.scalar_one_or_none()
 
    if not stock:
        raise HTTPException(404, f"Produk dengan UUID {stock_uuid} tidak ditemukan.")
 
    stock_title = stock.title  # simpan sebelum dihapus
 
    if hard:
        # ── Hard delete ───────────────────────────────────────────
        # 1. Hapus semua aset dari CDN
        from backend.db.cdn import delete_file
        from backend.config import Config
 
        deleted_assets = 0
        for asset in stock.assets:
            try:
                # Ekstrak key dari URL CDN: https://cdn.xxx.com/stocks/file.webp → stocks/file.webp
                cdn_prefix = getattr(Config, "url_r2", "")
                key = asset.url.split(f"{cdn_prefix}/")[-1] if cdn_prefix else asset.url
                await delete_file(key)
                deleted_assets += 1
            except Exception as e:
                # Log tapi jangan gagalkan transaksi — gambar mungkin sudah terhapus manual
                import logging
                logging.getLogger(__name__).warning(f"Gagal hapus CDN asset {asset.url}: {e}")
 
        # 2. Hapus dari Elasticsearch
        try:
            from backend.db.es_client import es_client
            await es_client.delete(index="products", id=str(stock_uuid), ignore=[404])
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Gagal hapus ES doc {stock_uuid}: {e}")
 
        # 3. Hapus dari database (CASCADE akan hapus AssetStock juga)
        await session.delete(stock)
        await session.commit()
 
        # 4. Invalidate Redis popular cache
        try:
            r = get_redis_token()
            await r.delete("cache:popular_products:v2")
        except Exception:
            pass
 
        return {
            "status":         "success",
            "mode":           "hard_delete",
            "message":        f"Produk '{stock_title}' berhasil dihapus permanen.",
            "deleted_assets": deleted_assets,
        }
 
    else:
        # ── Soft delete ───────────────────────────────────────────
        # Cukup set is_active = False agar tidak muncul di publik
        stock.is_active = False
        session.add(stock)
        await session.commit()
 
        # Update Elasticsearch — tandai is_active = false
        try:
            from backend.db.es_client import es_client
            await es_client.update(
                index="products",
                id=str(stock_uuid),
                doc={"is_active": False},
                ignore=[404],
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"ES soft-delete update gagal: {e}")
 
        # Invalidate Redis popular cache
        try:
            r = get_redis_token()
            await r.delete("cache:popular_products:v2")
        except Exception:
            pass
 
        return {
            "status":  "success",
            "mode":    "soft_delete",
            "message": f"Produk '{stock_title}' dinonaktifkan. Gunakan ?hard=true untuk hapus permanen.",
            "uuid":    str(stock_uuid),
        }


# ── Admin: Coupon Management ──────────────────────────────────────

@router.get("/admin/coupon")
async def admin_get_coupons(
    include_inactive: bool = Query(True),
    page: int = Query(1, ge=1),
    size: int = Query(50, le=100),
    session: AsyncSession = Depends(get_session),
    # _: any = Depends(get_admin),
):
    return {
        "success": True,
        "data": await service.get_all_coupons(session, include_inactive, page, size)
    }


@router.post("/admin/coupon")
async def admin_create_coupon(
    data: CouponCreateRequest,
    session: AsyncSession = Depends(get_session),
    # _: any = Depends(get_admin),
):
    try:
        result = await service.create_coupon(session, data)
        return {"success": True, "message": "Kupon berhasil dibuat", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@router.patch("/admin/coupon/{code}")
async def admin_update_coupon(
    code: str,
    data: CouponUpdateRequest,
    session: AsyncSession = Depends(get_session),
    # _: any = Depends(get_admin),
):
    try:
        result = await service.update_coupon(session, code, data)
        return {"success": True, "message": "Kupon berhasil diperbarui", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@router.delete("/admin/coupon/{code}")
async def admin_delete_coupon(
    code: str,
    hard: bool = Query(False),
    session: AsyncSession = Depends(get_session),
    # _: any = Depends(get_admin),
):
    try:
        if hard:
            result = await service.hard_delete_coupon(session, code)
        else:
            result = await service.soft_delete_coupon(session, code)
        return {"success": True, "message": result["message"]}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(500, detail=str(e))