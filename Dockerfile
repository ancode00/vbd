# Use slim python as base
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies needed for pyaudio (gcc, portaudio, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libportaudio2 \
        portaudio19-dev \
        libasound2-dev \
        && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements first for better cache
COPY requirements.txt .

# Install all python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Expose the port (Cloud Run uses 8080 by default)
EXPOSE 8080

# Entrypoint for uvicorn (FastAPI ASGI server)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
