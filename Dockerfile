FROM python:3.11-slim

WORKDIR /app

# Install build tools and portaudio dependencies for pyaudio
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libportaudio2 \
        portaudio19-dev \
        libasound2-dev \
        && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
