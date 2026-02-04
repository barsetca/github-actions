# Server Time API

Простой тестовый бэкенд на **FastAPI**, возвращающий текущее время сервера.

## Возможности

- **GET /** — приветствие и ссылка на документацию
- **GET /time** — текущее время сервера (UTC, ISO 8601) и Unix timestamp
- **GET /health** — проверка работоспособности сервиса

## Требования

- Python 3.10+

## Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/YOUR_USERNAME/github-actions.git
   cd github-actions
   ```

2. Создайте виртуальное окружение и установите зависимости:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   # или: .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

3. Запустите сервер:
   ```bash
   uvicorn main:app --reload
   ```

Сервер будет доступен по адресу: **http://127.0.0.1:8000**

- Документация Swagger UI: http://127.0.0.1:8000/docs  
- ReDoc: http://127.0.0.1:8000/redoc  

## Пример ответа GET /time

```json
{
  "server_time": "2025-02-04T12:00:00.000000+00:00",
  "timestamp": 1738656000.0,
  "timezone": "UTC"
}
```

## Лицензия

MIT
