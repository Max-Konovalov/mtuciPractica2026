# Maintenance Management System

Информационная система для управления оборудованием, сотрудниками и заявками на техническое обслуживание.

## Стек

- Python 3.11+, FastAPI async, Uvicorn
- SQLAlchemy 2.0 async, Alembic, PostgreSQL asyncpg
- Pydantic v2, python-dotenv, structlog
- Pytest, httpx, pytest-asyncio
- Frontend: один файл `frontend/index.html`, Bootstrap 5 CDN, Vanilla JS

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d
alembic upgrade head
uvicorn app.main:app --reload
```

Swagger доступен на `http://localhost:8000/docs`.

Фронтенд можно открыть как файл `frontend/index.html` или отдать через простой локальный сервер:

```bash
python -m http.server 8080 -d frontend
```

После открытия введите `X-API-Key` из `.env`, по умолчанию `dev-api-key`.

## Конфигурация

- `API_KEY` — ключ для заголовка `X-API-Key`.
- `DATABASE_URL` — строка подключения SQLAlchemy async, по умолчанию PostgreSQL из `docker-compose.yml`.
- `CORS_ORIGINS` — список origin через запятую, по умолчанию разрешены `localhost`/`127.0.0.1` для API и static frontend.

## Миграции

```bash
alembic upgrade head
alembic revision --autogenerate -m "message"
alembic downgrade -1
```

## Тесты

Интеграционные тесты требуют отдельную тестовую PostgreSQL БД:

```bash
createdb maintenance_test
export TEST_DATABASE_URL=postgresql+asyncpg://maintenance:maintenance@localhost:5432/maintenance_test
pytest
coverage run -m pytest
coverage report -m
```

## API

Все эндпоинты кроме `/health`, `/docs`, `/openapi.json` и `/favicon.ico` требуют заголовок:

```http
X-API-Key: dev-api-key
```

Основные ресурсы:

- `GET/POST/PUT/DELETE /equipment`
- `GET/POST/PUT/DELETE /employees`
- `GET/POST/PATCH/PUT/DELETE /requests`

Заявки поддерживают фильтры `status`, `priority`, `equipment_id`, пагинацию `skip`, `limit` и сортировку `sort_desc`.
