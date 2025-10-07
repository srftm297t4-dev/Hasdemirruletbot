FROM python:3.11-slim
RUN apt-get update && apt-get install -y \
    wget gnupg ca-certificates \
    libasound2 libatk-bridge2.0-0 libnss3 libatk1.0-0 libxcomposite1 libxdamage1 \
    libxrandr2 libxkbcommon0 libgtk-3-0 libdrm2 libgbm1 xvfb \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m playwright install chromium
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["python", "bot.py"]
