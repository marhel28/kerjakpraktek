import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Konfigurasi koneksi (sesuaikan dengan environment docker-compose)
# Di laptop host, port dipetakan ke 5433 (berdasarkan docker-compose.yml line 49)
DATABASE_URL = "postgresql+asyncpg://user_admin:password_rahasia@localhost:5433/marketplace_db"

async def apply_migrations():
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.begin() as conn:
        print("Starting manual migrations for jasa module...")
        
        # 1. Buat tabel service_technician
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS service_technician (
                uuid UUID PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                id_employee VARCHAR(50) UNIQUE NOT NULL,
                phone VARCHAR(20),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("Table 'service_technician' created.")

        # 2. Buat tabel service_holiday
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS service_holiday (
                uuid UUID PRIMARY KEY,
                holiday_date DATE UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("Table 'service_holiday' created.")

        # 3. Buat tabel service_operational_hours
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS service_operational_hours (
                uuid UUID PRIMARY KEY,
                day_of_week INTEGER UNIQUE NOT NULL,
                is_open BOOLEAN DEFAULT TRUE,
                hours VARCHAR(50) DEFAULT '08:00-17:00',
                max_bookings INTEGER DEFAULT 9,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("Table 'service_operational_hours' created.")

        # 4. Tambah kolom technician_uuid ke service_booking
        # Kita cek dulu apakah kolom sudah ada
        check_col_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='service_booking' AND column_name='technician_uuid';
        """)
        result = await conn.execute(check_col_query)
        if not result.fetchone():
            await conn.execute(text("""
                ALTER TABLE service_booking 
                ADD COLUMN technician_uuid UUID REFERENCES service_technician(uuid) ON DELETE SET NULL;
            """))
            await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_service_booking_technician_uuid ON service_booking (technician_uuid);"))
            print("Column 'technician_uuid' added to 'service_booking'.")
        else:
            print("Column 'technician_uuid' already exists.")

        # 5. Insert default operational hours jika kosong
        check_hours = await conn.execute(text("SELECT COUNT(*) FROM service_operational_hours"))
        if check_hours.scalar() == 0:
            import uuid
            for i in range(7):
                await conn.execute(text("""
                    INSERT INTO service_operational_hours (uuid, day_of_week, is_open, hours, max_bookings)
                    VALUES (:uuid, :day, :is_open, :hours, :max_bookings)
                """), {
                    "uuid": uuid.uuid4(),
                    "day": i,
                    "is_open": True if i < 6 else False, # Libur hari Minggu default
                    "hours": "08:00-17:00",
                    "max_bookings": 9
                })
            print("Default operational hours seeded.")

    print("Migration completed successfully.")
    await engine.dispose()

if __name__ == "__main__":
    try:
        asyncio.run(apply_migrations())
    except Exception as e:
        print(f"Error applying migration: {e}")
