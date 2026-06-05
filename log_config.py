"""
Logging Configuration — Centralized logging for the clinical pipeline.

Replaces print() with structured, level-aware logging.
Supports both console output and optional file logging.

Usage in any module:
    from log_config import get_logger
    logger = get_logger(__name__)
    logger.info("Pipeline initialized")
    logger.debug("Threshold: %s", threshold)
    logger.warning("Low confidence match: %s", entity)
"""

import logging
import os
import sys
from datetime import datetime


# ── Color formatter for console output ──────────────────────────────────────
class ColorFormatter(logging.Formatter):
    """Adds color codes to log levels for readable console output."""

    COLORS = {
        logging.DEBUG:    "\033[36m",    # Cyan
        logging.INFO:     "\033[32m",    # Green
        logging.WARNING:  "\033[33m",    # Yellow
        logging.ERROR:    "\033[31m",    # Red
        logging.CRITICAL: "\033[1;31m",  # Bold Red
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        record.levelname = f"{color}{record.levelname:<7}{self.RESET}"
        return super().format(record)


# ── Singleton setup ─────────────────────────────────────────────────────────
_initialized = False


def setup_logging(
    level: str = "INFO",
    log_to_file: bool = False,
    log_dir: str = None,
):
    """
    Configure the root logger for the pipeline.

    Args:
        level:       logging level (DEBUG, INFO, WARNING, ERROR)
        log_to_file: if True, also write logs to a timestamped file
        log_dir:     directory for log files (default: output/logs/)
    """
    global _initialized
    if _initialized:
        return
    _initialized = True

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Console handler with colors
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.DEBUG)
    console_fmt = ColorFormatter(
        fmt="%(levelname)s %(name)-30s │ %(message)s",
    )
    console.setFormatter(console_fmt)
    root_logger.addHandler(console)

    # File handler (optional)
    if log_to_file:
        if log_dir is None:
            log_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "output", "logs"
            )
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(log_dir, f"pipeline_{timestamp}.log")

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_fmt = logging.Formatter(
            fmt="%(asctime)s │ %(levelname)-7s │ %(name)-30s │ %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_fmt)
        root_logger.addHandler(file_handler)

        root_logger.info(f"Log file: {log_path}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger for a module.

    Usage:
        logger = get_logger(__name__)
        logger.info("Processing note %s", note_id)
    """
    # Auto-initialize with defaults if not yet set up
    if not _initialized:
        setup_logging()
    return logging.getLogger(name)
