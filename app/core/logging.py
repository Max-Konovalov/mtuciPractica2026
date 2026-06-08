from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.core.errors import error_payload


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    )


logger = structlog.get_logger()


async def request_logging_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    started = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception as exc:
        status_code = 500
        logger.exception("unhandled_http_error", path=request.url.path, error=str(exc))
        return JSONResponse(status_code=500, content=error_payload("Internal server error", "INTERNAL_ERROR"))
    finally:
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=status_code,
            duration_ms=duration_ms,
        )
