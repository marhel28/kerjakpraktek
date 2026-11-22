"""Generate Manual Book PasarCCTV (.docx) dengan hyperlink aktif ke repo GitHub.

Sumber isi: README.md (fitur, tech stack, struktur, cara menjalankan).
Jalankan:  python scratch/make_manual_book.py
Output:    Manual_Book_PasarCCTV.docx (di root proyek)
"""

import docx
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

REPO_URL = "https://github.com/marhel28/kerjakpraktek"
LINK_COLOR = "1155CC"

BLUE = RGBColor(0x11, 0x55, 0xCC)
DARK = RGBColor(0x1F, 0x1F, 0x1F)


def add_hyperlink(paragraph, url, text=None, size=None, bold=False):
    """Sisipkan hyperlink asli Word (bukan teks biasa) ke dalam paragraph."""
    text = text or url
    part = paragraph.part
    r_id = part.relate_to(
        url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)

    run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")

    color = OxmlElement("w:color")
    color.set(qn("w:val"), LINK_COLOR)
    rPr.append(color)

    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    rPr.append(underline)

    if bold:
        rPr.append(OxmlElement("w:b"))

    if size is not None:
        sz = OxmlElement("w:sz")
        sz.set(qn("w:val"), str(size * 2))
        rPr.append(sz)
        szCs = OxmlElement("w:szCs")
        szCs.set(qn("w:val"), str(size * 2))
        rPr.append(szCs)

    rPr.append(OxmlElement("w:rFonts"))
    run.append(rPr)

    t = OxmlElement("w:t")
    t.text = text
    run.append(t)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)
    return hyperlink


def shade_cell(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    tcPr.append(shd)


def style_table(table, header_fill="1F4E79"):
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for cell in table.rows[0].cells:
        shade_cell(cell, header_fill)
        for p in cell.paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for row in table.rows[1:]:
        if row._tr.get_or_add_trPr().find(qn("w:trPr")) is not None:
            pass


def code_block(doc, text):
    """Tampilkan blok teks sebagai monospace berlatar abu-abu muda."""
    for line in text.rstrip("\n").splitlines():
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.left_indent = Pt(18)
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "F2F2F2")
        pPr.append(shd)
        r = p.add_run(line if line else " ")
        r.font.name = "Consolas"
        r.font.size = Pt(9.5)


def main():
    doc = Document()

    # Margin halaman A4 standar
    for section in doc.sections:
        section.top_margin = Pt(56)
        section.bottom_margin = Pt(56)
        section.left_margin = Pt(64)
        section.right_margin = Pt(64)

    # ---- COVER ----
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run("PasarCCTV")
    r.font.size = Pt(30)
    r.font.bold = True
    r.font.color.rgb = DARK

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub.add_run("Manual Book — Marketplace & Jasa Instalasi CCTV")
    r.font.size = Pt(13)
    r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    sub2 = doc.add_paragraph()
    sub2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub2.add_run("Proyek Kerja Praktek")
    r.font.size = Pt(11)
    r.font.italic = True
    r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    author = doc.add_paragraph()
    author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    author.paragraph_format.space_before = Pt(14)
    r = author.add_run("Ammar Abu Fadhel")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = DARK

    nim = doc.add_paragraph()
    nim.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = nim.add_run("NIM 2022150075")
    r.font.size = Pt(12)
    r.font.color.rgb = DARK

    link_p = doc.add_paragraph()
    link_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    lead = link_p.add_run("Repositori: ")
    lead.font.size = Pt(12)
    add_hyperlink(link_p, REPO_URL, size=12, bold=True)
    hint = doc.add_paragraph()
    hint.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = hint.add_run("(klik link di atas untuk membuka repositori)")
    r.font.size = Pt(9)
    r.font.italic = True
    r.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    doc.add_page_break()

    # ---- DESKRIPSI ----
    doc.add_heading("1. Deskripsi Sistem", level=1)
    p = doc.add_paragraph(
        "PasarCCTV adalah platform marketplace CCTV B2B lengkap dengan sistem "
        "jasa instalasi berkala, checkout pembayaran, chat real-time customer ↔ admin, "
        "dan chatbot AI berbasis RAG. Satu repositori berisi tiga aplikasi: "
        "API backend, web publik, dan dashboard admin."
    )
    p.paragraph_format.space_after = Pt(10)

    # ---- FITUR UTAMA ----
    doc.add_heading("2. Fitur Utama", level=1)
    fitur = [
        ("Modul", "Deskripsi"),
        ("🛒 Katalog & Pencarian", "Produk per kategori/brand, full-text search via Manticore, filter facet, perbandingan produk"),
        ("💳 Checkout & Pembayaran", "Keranjang, voucher/kupon, payment gateway Midtrans, riwayat & status pesanan"),
        ("🚚 Ongkir & Pengiriman", "Cek ongkir per wilayah, tracking pengiriman dengan timeline"),
        ("🔧 Jasa & Booking", "Paket instalasi CCTV, pemeliharaan berkala, troubleshooting — booking dengan teknisi & jadwal"),
        ("💬 Chat Real-time", "Chat customer ↔ admin via WebSocket, read receipt, unread badge"),
        ("🤖 Chatbot AI (RAG)", "Asisten \"PasarBot\" dengan knowledge base produk, rekomendasi produk di jawaban, eskalasi ke CS manusia"),
        ("🎯 Promo & Flash Sale", "Banner per route, promo eksklusif, flash sale, brand showcase"),
        ("📊 Dashboard Admin", "Manajemen produk, stok, transaksi, banner, promo, jasa, kupon, pengaturan sistem, log aktivitas"),
        ("🔐 Autentikasi", "Email/password (JWT + refresh token, blacklist Redis) dan Google OAuth, bridge ke Supabase"),
    ]
    table = doc.add_table(rows=0, cols=2)
    for i, (a, b) in enumerate(fitur):
        row = table.add_row()
        row.cells[0].text = a
        row.cells[1].text = b
        if i == 0:
            row.cells[0].paragraphs[0].add_run("Modul")
            row.cells[1].paragraphs[0].add_run("Deskripsi")
    # isi header setelah add_row supaya style konsisten
    style_table(table)
    for cell in table.columns[0].cells:
        for pp in cell.paragraphs:
            for rr in pp.runs:
                rr.font.bold = True
    doc.add_paragraph()

    # ---- TECH STACK ----
    doc.add_heading("3. Tech Stack", level=1)
    stack = [
        ("Layer", "Teknologi"),
        ("Backend", "Python 3.13, FastAPI, SQLModel (async SQLAlchemy), Pydantic v2"),
        ("Database", "PostgreSQL 15"),
        ("Cache & Queue", "DragonflyDB (Redis-compatible), Celery worker"),
        ("Search Engine", "Manticore Search (pengganti Elasticsearch, hemat RAM)"),
        ("Realtime", "Native WebSocket (FastAPI), Supabase Realtime (notifikasi)"),
        ("AI", "Groq API (LLM inference), knowledge base produk untuk RAG"),
        ("Storage", "Cloudflare R2 (gambar produk & attachment chat)"),
        ("Frontend", "Nuxt 4, Vue 3, TypeScript, Tailwind CSS v4, Pinia, Leaflet (store locator)"),
        ("Admin", "Vue 3 + Vite, Tailwind CSS, D3 (visualisasi)"),
        ("Infrastruktur", "Docker Compose, Cloudflare Tunnel, Alembic (migrasi)"),
    ]
    table = doc.add_table(rows=0, cols=2)
    for i, (a, b) in enumerate(stack):
        row = table.add_row()
        row.cells[0].text = a
        row.cells[1].text = b
    style_table(table)
    for cell in table.columns[0].cells:
        for pp in cell.paragraphs:
            for rr in pp.runs:
                rr.font.bold = True
    doc.add_paragraph()

    # ---- STRUKTUR PROYEK ----
    doc.add_heading("4. Struktur Proyek", level=1)
    code_block(
        doc,
        """kerjakpraktek/
├── backend/          # API FastAPI — router, service, model per modul
│   ├── auth/         # Login, JWT, Google OAuth, Supabase bridge
│   ├── data/         # Produk, transaksi, banner, promo, ongkir, jasa
│   ├── user/         # Cart, wishlist, pesan (chat WS), booking
│   ├── admin/        # Endpoint dashboard admin
│   └── db/           # Engine, Redis, CDN (R2), Manticore client
├── frontend/         # Web publik (Nuxt 4) — pages, components, stores, server proxy
├── admin/project/    # Dashboard admin (Vue 3 + Vite)
├── migration/        # Alembic migrations
├── docs/             # Dokumentasi teknis (C4, ERD, aktivitas, per lapisan)
├── test/             # Seeder & script pengujian endpoint
├── scratch/          # Script utilitas dev (migrasi kolom, dll)
└── docker-compose.yml""",
    )
    doc.add_paragraph()

    # ---- MENJALANKAN PROYEK ----
    doc.add_heading("5. Menjalankan Proyek", level=1)

    doc.add_heading("Prasyarat", level=2)
    for item in (
        "Docker + Docker Compose",
        "Python 3.13 + Node.js 20+ (untuk mode non-Docker)",
        "File backend/.env (jangan pernah di-commit)",
    ):
        doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("1. Mode Docker (disarankan)", level=2)
    code_block(doc, "docker compose up -d --build")

    doc.add_paragraph("Layanan yang berjalan:", style=None)
    layanan = [
        ("Layanan", "Port", "Keterangan"),
        ("FastAPI backend", "8000", "Swagger di /docs"),
        ("PostgreSQL", "5433 → 5432", "DB utama"),
        ("DragonflyDB", "6379", "Cache, blacklist token, broker Celery"),
        ("Manticore Search", "9306 / 9308", "Search engine"),
        ("Celery worker", "—", "Queue default,email,auth"),
        ("Cloudflared", "—", "Tunnel publik (opsional)"),
    ]
    table = doc.add_table(rows=0, cols=3)
    for i, row_data in enumerate(layanan):
        row = table.add_row()
        for j, val in enumerate(row_data):
            row.cells[j].text = val
    style_table(table)
    doc.add_paragraph()

    doc.add_heading("2. Mode Manual (development)", level=2)
    code_block(
        doc,
        """# Backend
python -m venv venv
venv\\Scripts\\activate            # Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn backend:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev                      # http://localhost:3000

# Admin
cd admin/project
npm install
npm run dev                      # http://localhost:5173""",
    )

    doc.add_heading("Variabel Environment (backend/.env)", level=2)
    code_block(
        doc,
        """DATABASE_URL=postgresql+asyncpg://user_admin:<password>@localhost:5433/marketplace_db
JWT_SECRET_KEY=<secret>
REDIS_HOST=localhost
REDIS_PORT=6379
MANTICORE_URL=http://localhost:9308
GROQ_API_KEY=<groq key untuk chatbot>
SUPABASE_URL=...
SUPABASE_ANON_KEY=...""",
    )

    # ---- DOKUMENTASI TEKNIS & LINK ----
    doc.add_heading("6. Dokumentasi Teknis & Repositori", level=1)
    p = doc.add_paragraph(
        "Diagram arsitektur (C4 Model), ERD database, dan diagram aktivitas "
        "(checkout, promo, notifikasi) tersedia di folder docs/ pada repositori. "
        "Seluruh source code dan dokumentasi dapat diakses melalui link berikut:"
    )
    p.paragraph_format.space_after = Pt(8)

    link_p = doc.add_paragraph()
    link_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_hyperlink(link_p, REPO_URL, text=REPO_URL, size=13, bold=True)

    doc.add_paragraph()

    doc.add_heading("API Ringkas", level=2)
    p = doc.add_paragraph(
        "Base URL: http://localhost:8000 — dokumentasi interaktif: http://localhost:8000/docs"
    )
    api = [
        ("Prefix", "Modul"),
        ("/auth/user", "Login, register, refresh, Google OAuth, reset password"),
        ("/stok", "Produk & stok"),
        ("/transaksi", "Checkout, pembayaran, status pesanan"),
        ("/cek/shipping", "Ongkir & tracking"),
        ("/cart, /wishlist", "Keranjang & wishlist"),
        ("/messages", "Chat customer ↔ admin (HTTP fallback)"),
        ("/ws/chat/{user_id}", "WebSocket chat real-time (?token=<JWT>)"),
        ("/category, /brands, /banner", "Katalog & konten publik"),
        ("/settings, /admin/coupon, /recap", "Endpoint admin"),
    ]
    table = doc.add_table(rows=0, cols=2)
    for row_data in api:
        row = table.add_row()
        row.cells[0].text = row_data[0]
        row.cells[1].text = row_data[1]
    style_table(table)

    # ---- PENUTUP ----
    doc.add_paragraph()
    closing = doc.add_paragraph()
    closing.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = closing.add_run("Proyek Kerja Praktek — PasarCCTV")
    r.font.italic = True
    r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    out = doc.save("Manual_Book_PasarCCTV.docx")
    print(f"Saved: Manual_Book_PasarCCTV.docx")
    return out


if __name__ == "__main__":
    main()
