import logging
from logging.config import dictConfig
from config import settings

logger = logging.getLogger(__name__)

handlers: dict = {}
handlers_keys: list[str] = []
if settings.CONSOLE_LOG:
    handlers_keys += ["console"]
    handlers["console"] = {
        # "class": "rich.logging.RichHandler",
        "class": "logging.StreamHandler",
        "formatter": "color",
        "level": settings.LOG_LEVEL,
    }
if settings.FILE_LOG:
    handlers_keys += ["file"]
    handlers["file"] = {
        "class": "logging.FileHandler",
        "formatter": "default",
        "level": settings.LOG_LEVEL,
        "filename": settings.FILE_LOG_FILENAME,
    }

dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "format": "%(asctime)s.%(msecs)03d %(levelname)7s:%(name)-22s - %(message)s",
            },
            "color": {
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "()": "colorlog.ColoredFormatter",
                "format": "%(log_color)s%(asctime)s.%(msecs)03d %(levelname)7s:%(name)-22s - %(message)s",
            },
        },
        "handlers": handlers,
        "loggers": {
            "bot": {
                "level": settings.LOG_LEVEL,
                "handlers": handlers_keys,
                "propagate": False,
            },
            "aiogram": {
                "level": settings.LOG_LEVEL,
                "handlers": handlers_keys,
                "propagate": False,
            },
            # "sqlalchemy": {
            #     "level": settings.LOG_LEVEL,
            #     "handlers": handlers_keys,
            #     "propagate": False,
            # },
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": handlers_keys,
        },
    }
)

if __name__ == "__main__":
    for name in logging.root.manager.loggerDict:
        print(name)
