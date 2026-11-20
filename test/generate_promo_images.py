import os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "generated")
os.makedirs(OUT_DIR, exist_ok=True)

PROMO_SPECS = [
    {
        "filename": "promo_cctv_exclusive.jpg",
        "size": (1440, 500),
        "bg": (15, 23, 42),
        "accent": (204, 12, 57),
        "title": "PENAWARAN EKSKLUSIF CCTV & SMART SECURITY",
        "sub": "Garansi Resmi Distributor 2 Tahun & Bebas Biaya Survei Lokasi",
        "badge": "PROMO TERBATAS",
    },
    {
        "filename": "promo_flashsale_cctv.jpg",
        "size": (1440, 500),
        "bg": (3, 172, 14),
        "accent": (255, 255, 255),
        "title": "FLASH SALE PAKET INSTALASI BANDUNG & CIMAHI",
        "sub": "Potongan Langsung Hingga 35% untuk 50 Pembeli Pertama",
        "badge": "KLAIM HARI INI",
    },
    {
        "filename": "promo_access_control.jpg",
        "size": (1440, 500),
        "bg": (17, 24, 39),
        "accent": (245, 158, 11),
        "title": "UPGRADE KEAMANAN KANTOR DENGAN ACCESS CONTROL",
        "sub": "Integrasi Absensi Biometrik & Pengawasan 24 Jam Non-Stop",
        "badge": "SOLUSI BISNIS",
    }
]

def generate_banner(spec):
    w, h = spec["size"]
    img = Image.new("RGB", (w, h), color=spec["bg"])
    draw = ImageDraw.Draw(img)

    # Gradient-like ambient rectangles
    for i in range(10):
        alpha_color = (
            min(255, spec["bg"][0] + i * 4),
            min(255, spec["bg"][1] + i * 3),
            min(255, spec["bg"][2] + i * 5),
        )
        draw.rectangle([0, i * (h // 10), w, (i + 1) * (h // 10)], fill=alpha_color)

    # Accent decorative bar
    draw.rectangle([60, 80, 72, 160], fill=spec["accent"])

    # Draw Badge
    draw.rounded_rectangle([90, 80, 260, 115], radius=6, fill=spec["accent"])
    draw.text((105, 90), spec["badge"], fill=(255, 255, 255))

    # Text rendering (Default bitmap font safe)
    draw.text((90, 130), spec["title"], fill=(255, 255, 255))
    draw.text((90, 190), spec["sub"], fill=(200, 210, 225))

    # CTA Button Box
    draw.rounded_rectangle([90, 260, 320, 315], radius=8, fill=(3, 172, 14) if spec["bg"] != (3, 172, 14) else (255, 255, 255))
    btn_text_color = (255, 255, 255) if spec["bg"] != (3, 172, 14) else (3, 172, 14)
    draw.text((120, 280), "BELANJA SEKARANG ->", fill=btn_text_color)

    # Save
    out_path = os.path.join(OUT_DIR, spec["filename"])
    img.save(out_path, quality=92)
    print(f"Generated: {out_path}")

if __name__ == "__main__":
    for p in PROMO_SPECS:
        generate_banner(p)