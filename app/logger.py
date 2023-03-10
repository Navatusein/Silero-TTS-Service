from pydantic import BaseModel
from logging.config import dictConfig


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME = "uvicorn"
    LOG_FORMAT = "%(levelname)s [%(asctime)s] %(message)s"
    LOG_LEVEL = "INFO"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }


dictConfig(LogConfig().dict())
