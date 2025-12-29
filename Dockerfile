# Gunakan Python 3.11 yang jauh lebih stabil untuk library face_recognition
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependensi sistem
# Tambahkan python3-dev agar pip bisa mengompilasi library C++
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    python3-dev \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements dan install
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy sisa kode
COPY . .

EXPOSE 1324

CMD ["python", "app.py"]