"""Centralized logging configuration for training-vid-organizer."""

import logging
import sys
from pathlib import Path

import typer

APP_NAME = "training-vid-organizer"
LOG_DIR = Path(typer.get_app_dir(APP_NAME)) / "logs"
DEBUG_LOG_FILE = LOG_DIR / "debug.log"


def get_logger(name: str = "tvo") -> logging.Logger:
    """Return a configured logger instance.

    Args:
        name: Logger name (defaults to 'tvo'). Child loggers inherit this config.

    Returns:
        Configured logger with console handler (INFO+) and file handler (DEBUG+).
    """
    log = logging.getLogger(name)

    # Avoid duplicate handlers if imported multiple times
    if not log.handlers:
        log.setLevel(logging.DEBUG)

        # Console handler for INFO and above - writes to stdout explicitly
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_formatter = logging.Formatter(
            "%(levelname)s - %(name)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        log.addHandler(console_handler)

        # File handler for DEBUG output with timestamps
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(DEBUG_LOG_FILE)
        debug_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(debug_formatter)
        log.addHandler(file_handler)

    return log


# Singleton logger instance for convenience
logger = get_logger()
