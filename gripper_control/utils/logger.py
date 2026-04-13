"""Logging utilities for the gripper control platform."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


_LOGGER_CREATED = False


def configure_logging(level: int = logging.INFO) -> None:
    """Configure app-wide logging handlers once."""

    global _LOGGER_CREATED
    if _LOGGER_CREATED:
        return

    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(level)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)

    file_handler = RotatingFileHandler(
        log_dir / "gripper_universal.log",
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)

    root.addHandler(stream_handler)
    root.addHandler(file_handler)

    _LOGGER_CREATED = True


def get_logger(name: str) -> logging.Logger:
    """Get a named logger."""

    return logging.getLogger(name)
