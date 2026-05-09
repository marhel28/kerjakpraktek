import os
import requests
import random
import sys

# Konfigurasi Path dan URL
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BRAND_DIR = os.path.join(BASE_DIR, "brand")

# Sesuaikan port dengan FastAPI kamu
URL = "http://localhost:8000/brands/admin/create" 

def seed_brands():
    # 1. Cek apakah folder brand ada
    if not os.path.exists(BRAND_DIR):
        print(f"❌ ERROR: Folder '{BRAND_DIR}' tidak ditemukan!")
        print("Silakan buat folder bernama 'brand' dan isi dengan gambar-gambar.")
        sys.exit(1)

    # 2. Baca semua file di dalam folder brand
    all_files = os.listdir(BRAND_DIR)
    
    # Filter hanya file gambar (mencegah hidden file seperti .DS_Store ikut terbaca)
    valid_extensions = ('.png', '.jpg', '.jpeg', '.webp')
    images = [f for f in all_files if f.lower().endswith(valid_extensions)]

    if not images:
        print(f"⚠️ GAGAL: Tidak ada file gambar di dalam folder '{BRAND_DIR}'")
        sys.exit(1)

    print(f"🚀 Menemukan {len(images)} gambar. Memulai proses seeding...\n")

    # 3. Looping dan kirim setiap gambar
    for index, filename in enumerate(images):
        filepath = os.path.join(BRAND_DIR, filename)
        
        # Ekstrak nama dari file (contoh: "apple_indonesia.jpg" -> "Apple Indonesia")
        raw_name = os.path.splitext(filename)[0]
        
        name = raw_name.replace("-", " ").replace("_", " ").title()
        slug = raw_name.lower().replace(" ", "-").replace("_", "-")
        title = name  # Sesuai permintaan: title sama dengan name
        
        # Generate data random untuk sisanya
        route = f"/brands/{slug}"
        position = random.randint(1, 100)
        is_featured = random.choice(["true", "false"]) # FastAPI Form butuh string "true"/"false"

        # Siapkan payload teks
        data = {
            "name": name,
            "slug": slug,
            "title": title,
            "route": route,
            "position": position,
            "is_featured": is_featured
        }

        print(f"[{index+1}/{len(images)}] Mengirim brand: {name} ...")

        # Buka file dalam mode binary ("rb")
        with open(filepath, "rb") as f:
            # Format files untuk requests: {"field_name": ("filename", file_object, "mime_type")}
            files = {
                "file": (filename, f, "image/jpeg") 
            }
            
            try:
                # Kirim request POST form-data
                response = requests.post(URL, data=data, files=files)
                
                if response.status_code == 200: # Asumsi sukses adalah 200 OK
                    print(f"   ✅ SUCCESS")
                else:
                    print(f"   ⚠️ GAGAL ({response.status_code}): {response.text}")
                    
            except requests.exceptions.ConnectionError:
                print("\n❌ ERROR FATAL: Gagal konek ke server.")
                print("Pastikan server FastAPI / Docker kamu sudah menyala di port 8000.")
                sys.exit(1)

    print("\n🎉 Proses seeding selesai!")

if __name__ == "__main__":
    seed_brands()