"""
MAVVE structured logging configuration.
"""

import structlog
from config import settings


def setup_logging():
    """Configure structured logging for the application."""
    log_level = getattr(structlog, settings.LOG_LEVEL.upper(), structlog.INFO) if hasattr(structlog, settings.LOG_LEVEL.upper()) else 0

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if settings.APP_ENV == "development" else structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()
