from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    app_name: str = "Maintenance Management System"
    api_key: str = "dev-api-key"
    database_url: str = "postgresql+asyncpg://maintenance:maintenance@localhost:5432/maintenance_db"
    cors_origins: str = "http://localhost,http://localhost:8000,http://localhost:8080,http://127.0.0.1:8080"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        api_key=os.getenv("API_KEY", "dev-api-key"),  # TODO: заменить на реальную спецификацию
        database_url=os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://maintenance:maintenance@localhost:5432/maintenance_db",
        ),
        cors_origins=os.getenv(
            "CORS_ORIGINS",
            "http://localhost,http://localhost:8000,http://localhost:8080,http://127.0.0.1:8080",
        ),
    )
