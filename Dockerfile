# Part of WhatsApp AI Bot by Viprasol Tech Private Limited (https://viprasol.com).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first for better layer caching.
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --upgrade pip && python -m pip install ".[serve]"

# Run as a non-root user.
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "whatsapp_ai_bot.app:app", "--host", "0.0.0.0", "--port", "8000"]
