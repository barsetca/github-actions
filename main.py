"""
Простой тестовый бэкенд на FastAPI.
Возвращает текущее время сервера.
"""

from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(
    title="Server Time API",
    description="API для получения текущего времени сервера",
    version="1.0.0",
)


@app.get("/")
async def root():
    """Корневой эндпоинт с приветствием."""
    return {"message": "Server Time API", "docs": "/docs"}


@app.get("/time")
async def get_server_time():
    """Возвращает текущее время сервера в UTC (ISO 8601)."""
    now = datetime.now(timezone.utc)
    return {
        "server_time": now.isoformat(),
        "timestamp": now.timestamp(),
        "timezone": "UTC",
    }


@app.get("/health")
async def health():
    """Эндпоинт для проверки работоспособности сервиса."""
    return {"status": "ok"}
