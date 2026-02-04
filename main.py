"""
Простой тестовый бэкенд на FastAPI.
Возвращает текущее время сервера и конвертирует время по названию города (в т.ч. на русском).
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Query
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

app = FastAPI(
    title="Server Time API",
    description="API для получения текущего времени сервера и конвертации по часовым поясам",
    version="1.0.0",
)

# Форматы для разбора времени UTC (без указания пояса считаем UTC)
UTC_TIME_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
)
UTC_TIME_ONLY_FORMATS = ("%H:%M:%S", "%H:%M")  # только время — подставляем сегодня по UTC

# Геокодер для названия города → координаты (поддерживает русские названия)
_geolocator = Nominatim(user_agent="ServerTimeAPI/1.0")
_tzf = TimezoneFinder()


def _city_to_timezone(city_name: str) -> str:
    """По названию города (в т.ч. на русском) возвращает IANA timezone (например Asia/Yekaterinburg)."""
    city_name = city_name.strip()
    if not city_name:
        raise HTTPException(status_code=422, detail="Укажите название города.")
    try:
        location = _geolocator.geocode(city_name)
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        raise HTTPException(status_code=503, detail=f"Сервис геокодирования недоступен: {e}") from e
    if location is None:
        raise HTTPException(
            status_code=422,
            detail=f"Город не найден: «{city_name}». Проверьте написание (например: Екатеринбург, Москва, Нью-Йорк).",
        )
    tz_name = _tzf.timezone_at(lat=location.latitude, lng=location.longitude)
    if tz_name is None:
        raise HTTPException(
            status_code=422,
            detail=f"Не удалось определить часовой пояс для: «{city_name}».",
        )
    return tz_name


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


def _parse_utc_time(value: str) -> datetime:
    """Парсит строку времени в UTC. Поддерживает несколько форматов. Только время (15:00) — сегодня UTC."""
    value = value.strip()
    for fmt in UTC_TIME_FORMATS:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    for fmt in UTC_TIME_ONLY_FORMATS:
        try:
            dt = datetime.strptime(value, fmt)
            today = datetime.now(timezone.utc)
            dt = today.replace(hour=dt.hour, minute=dt.minute, second=dt.second, microsecond=0)
            return dt
        except ValueError:
            continue
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Не удалось разобрать время. Примеры: 15:00, 2025-02-04 12:00:00, 2025-02-04T12:00:00",
        )


@app.get("/time/convert")
async def convert_time(
    city: str = Query(..., description="Название города на русском или английском (например: Екатеринбург, Москва)"),
    utc_time: str | None = Query(None, description="Время в UTC. По умолчанию — текущее время сервера"),
):
    """
    Конвертирует время из UTC в местное время указанного города.
    Город можно вводить по-русски (Екатеринбург, Москва) или по-английски.
    Время UTC можно передать строкой; если не передано — используется текущее время.
    """
    if utc_time is None or utc_time.strip() == "":
        dt_utc = datetime.now(timezone.utc)
    else:
        dt_utc = _parse_utc_time(utc_time)

    tz_name = _city_to_timezone(city)
    tz = ZoneInfo(tz_name)
    dt_local = dt_utc.astimezone(tz)

    return {
        "utc_time": dt_utc.isoformat(),
        "city": city.strip(),
        "timezone": tz_name,
        "converted_time": dt_local.isoformat(),
        "converted_time_local": dt_local.strftime("%Y-%m-%d %H:%M:%S %Z"),
    }


@app.get("/health")
async def health():
    """Эндпоинт для проверки работоспособности сервиса."""
    return {"status": "ok"}
