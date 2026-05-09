# Gunakan image python yang ringan
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

WORKDIR /app

# Install dependencies sistem (jika ada library C yang dibutuhkan)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy seluruh folder backend
COPY ./backend ./backend

# Expose port FastAPI
EXPOSE 8000

# Jalankan uvicorn. 
# Karena app ada di backend/__init__.py, kita panggil "backend:app"
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--loop", "uvloop"]