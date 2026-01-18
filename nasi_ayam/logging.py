"""Logging configuration for the application."""

import logging
import os
import warnings
from logging.handlers import RotatingFileHandler
from pathlib import Path

os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["TQDM_DISABLE"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

warnings.filterwarnings("ignore", message=".*unauthenticated requests.*")

try:
    import huggingface_hub

    huggingface_hub.logging.set_verbosity_error()
except ImportError:
    pass

_configured = False
_handler: RotatingFileHandler | None = None


def setup_logging() -> None:
    """Configure application logging.

    Logs to logs/app.log with rotation (max 10MB, 5 backups).
    Log level configurable via LOG_LEVEL environment variable.
    """
    global _configured, _handler

    if _configured:
        return

    # Disable noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, log_level, logging.INFO)

    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=UserWarning, module="torch")
    warnings.filterwarnings("ignore", message=".*All keys matched successfully.*")

    _handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
    )
    _handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    # Forcefully re-configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove any existing handlers
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)

    root_logger.addHandler(_handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    logger = logging.getLogger(f"nasi_ayam.{name}")
    if _handler and _handler not in logging.getLogger().handlers:
        logging.getLogger().addHandler(_handler)
    return logger
