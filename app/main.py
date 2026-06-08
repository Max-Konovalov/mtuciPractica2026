from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import init_database_if_sqlite
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, request_logging_middleware
from app.routers import employees, equipment, health, requests


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await init_database_if_sqlite()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="Информационная система управления заявками на техническое обслуживание оборудования.",
        lifespan=lifespan,
    )
    app.middleware("http")(request_logging_middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(health.router)
    app.include_router(equipment.router)
    app.include_router(employees.router)
    app.include_router(requests.router)
    return app


app = create_app()
