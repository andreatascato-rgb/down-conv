"""Configurazione logging con rotazione."""

import logging
import os
from logging.handlers import RotatingFileHandler

from .paths import ensure_dirs, get_log_dir


def setup_logging(level: str | None = None) -> None:
    """Configura logging con RotatingFileHandler e console."""
    ensure_dirs()
    log_level = level or os.environ.get("DOWNCONV_LOG_LEVEL", "INFO")
    log_level = getattr(logging, log_level.upper(), logging.INFO)

    log_dir = get_log_dir()
    log_file = log_dir / "downconv.log"
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    root = logging.getLogger()
    root.setLevel(log_level)

    if root.handlers:
        return

    # File handler con rotazione
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(log_format))
    root.addHandler(file_handler)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(log_level)
    console.setFormatter(logging.Formatter(log_format))
    root.addHandler(console)
