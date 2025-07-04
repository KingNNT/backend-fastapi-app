import sys
from typing import Any


def get_log_config(log_level: str = "INFO") -> dict[str, Any]:
    """
    Get uvicorn logging configuration.

    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Dictionary containing uvicorn log configuration
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "access": {
                "format": '%(asctime)s - %(client_addr)s - "%(request_line)s" %(status_code)s',
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": sys.stdout,
            },
            "access": {
                "class": "logging.StreamHandler",
                "formatter": "access",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "uvicorn": {
                "level": log_level,
                "handlers": ["default"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": log_level,
                "handlers": ["default"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": log_level,
                "handlers": ["access"],
                "propagate": False,
            },
            "fastapi": {
                "level": log_level,
                "handlers": ["default"],
                "propagate": False,
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["default"],
        },
    }
