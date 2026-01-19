# ============================================
# Stage 1: Build Frontend Assets
# ============================================
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Copy package files
COPY package*.json ./
COPY tailwind.config.js postcss.config.js vite.config.mjs ./

# Install ALL dependencies (including devDependencies needed for build)
RUN npm ci

# Copy source files
COPY src/ ./src/
COPY templates/ ./templates/
COPY static/ ./static/

# Build frontend assets
RUN npm run build

# ============================================
# Stage 2: Python Application
# ============================================
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV and face_recognition
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

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy built frontend assets from frontend-builder stage
COPY --from=frontend-builder /frontend/static/dist ./static/dist

# Create necessary directories
RUN mkdir -p known_faces static/mediapipe

# Set environment variables for production
ENV FLASK_DEBUG=False
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 1324

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:1324/login', timeout=5)" || exit 1

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:1324", "app:app", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]