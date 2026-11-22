import asyncio

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from backend.db.main import init_db, init_knowledge_index
from backend.db.redis import get_redis_token
from backend.utils.task_banner import refresh_banner_cache_safe

# Import Celery app (WAJIB diimport agar task ter-register)
from backend.celery_app import celery_app  # noqa: F401
from backend.user.user_booking.route import router as user_booking_router
# Import routers
from backend.auth.router import router_user
from backend.data.stock.router import router as router_stock
from backend.data.transaksi.route import transaksi_route
from backend.admin.adminTransaksi.router import router_transaksi_admin
from backend.data.ongkir.routing import router_ship
from backend.data.public.xbanner.route import router as banner_router
from backend.data.public.branlogo.route import router as brand_router
from backend.data.public.category.route import router as category_route
from backend.user.cart.route import router as router_cart
from backend.user.whitlish.route import router as route_whitlish
from backend.data.public.bannerperroute.route import router as routebanner
from backend.data.jasa.route import router as jasa_router
from backend.data.stock.dashbord.route import router as main_route
from backend.data.jasa.dashbord.route import router as main_route_jasa
from backend.data.transaksi.dashbord.route import router as main_route_transaksi
from backend.data.public.mainbottombanner.route import router as bottomBanner
from backend.data.public.promobanner.router import promo_router as router_promo
from backend.user.pesan.route import router as pesan_routes
from backend.user.pesan.ws_route import router as ws_chat_router
from backend.user.notifications.model import Notification  # noqa: F401 — register tabel
from backend.user.notifications.router import router as notification_router
from backend.user.notifications.ws_route import router as ws_notification_router
from backend.user.notifications.pubsub import start_subscriber, stop_subscriber
from backend.data.public.portofolio.route import router as porto_route
from backend.data.public.about.route import router as router_about
from backend.data.public.addon.route import router as addon_router
from backend.data.public.addon.admin_route import router as addon_admin_router
from backend.admin.coupon.router import router as admin_coupon_router
from backend.data.activity.route import router as activity_router
from backend.admin.adminSettings.router import router_settings as settings_router
from backend.data.chatbot.router import router as chatbot_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n🚀 Server is starting up...")
    await init_db()
    await init_knowledge_index()

    # Warm up banner cache saat startup (tetap dipertahankan)
    # Selanjutnya refresh otomatis oleh Celery Beat setiap 5 menit
    try:
        redis = get_redis_token()
        await refresh_banner_cache_safe(redis)
        print("✅ Banner cache warmed up successfully.")
    except Exception as e:
        print(f"⚠️  Failed to warm up cache: {e}")

    # Pastikan Celery worker bisa dijangkau (health check ringan)
    try:
        celery_app.control.ping(timeout=1)
        print("✅ Celery worker reachable.")
    except Exception:
        print("⚠️  Celery worker not reachable — tasks will queue when worker starts.")

    start_subscriber()

    try:
        yield
    finally:
        await stop_subscriber()
        print("\n🛑 Server is stopping...")


app = FastAPI(
    debug=False,  # Selalu False di production
    title="Aplikasi Marketplace",
    description="High Performance Marketplace API",
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    root_path="",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:4173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "https://cctv-api.desa-sidomukti.com",
        "https://marketplace-pi-sable.vercel.app",
        "https://kerjapraktek-n9aw.vercel.app",
        "https://29a4-103-165-157-195.ngrok-free.app",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$|^https://.*\.vercel\.app$|^https://.*\.ngrok-free\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# ── Routers ────────────────────────────────────────────────────────
app.include_router(router_user,           prefix="/auth/user",        tags=["user"])
app.include_router(router_stock,          prefix="/stok",             tags=["stok"])
app.include_router(transaksi_route,       prefix="/transaksi",        tags=["buys"])
app.include_router(router_ship,           prefix="/cek/shipping",     tags=["check transaksi status"])
app.include_router(router_transaksi_admin,prefix="/recap",            tags=["spesial admin rekap"])
app.include_router(banner_router,         prefix="/banner",           tags=["public banner"])
app.include_router(brand_router,          prefix="/brands",           tags=["public brands"])
app.include_router(category_route,        prefix="/category",         tags=["public category"])
app.include_router(router_cart,           prefix="/cart",             tags=["Cart"])
app.include_router(route_whitlish,        prefix="/wishlist",         tags=["whitlish"])
app.include_router(routebanner,           prefix="/image-sections",   tags=["Image Sections"])
app.include_router(jasa_router)
app.include_router(user_booking_router)
app.include_router(main_route)
app.include_router(main_route_jasa)
app.include_router(main_route_transaksi)
app.include_router(bottomBanner)
app.include_router(router_promo,tags=['promos'])
app.include_router(pesan_routes)
app.include_router(ws_chat_router)
app.include_router(notification_router)
app.include_router(ws_notification_router)
app.include_router(porto_route)
app.include_router(router_about)
app.include_router(addon_router)
app.include_router(addon_admin_router)
app.include_router(admin_coupon_router, prefix="/admin/coupon", tags=["Admin Coupon"])
app.include_router(settings_router, prefix="/settings", tags=["System Settings"])
app.include_router(activity_router)
app.include_router(chatbot_router)