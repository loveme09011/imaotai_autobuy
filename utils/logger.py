import sys
from pathlib import Path

from loguru import logger

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}"


def setup_logger() -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        format=LOG_FORMAT,
        level="INFO",
    )
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger.add(
        LOG_DIR / "app_{time:YYYY-MM-DD}.log",
        format=LOG_FORMAT,
        level="INFO",
        rotation="1 day",
        retention="7 days",
        encoding="utf-8",
    )


def get_logger(name: str):
    return logger.patch(lambda record: record.update(name=name))
