"""
Logging Subsystem
=================
Configures dual logging: clean terminal output for users and
timestamped persistent file logs for auditing and debugging.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("file_organizer")
ACTIVE_LOG_FILE: Optional[Path] = None


def get_active_log_file() -> Optional[Path]:
    """Returns the path to the currently active log file, if any."""
    return ACTIVE_LOG_FILE


def setup_logging(log_file: Optional[Path] = None, verbose: bool = False) -> None:
    """
    Configures logging with dual output: clean console output and
    detailed timestamped file logs.

    :param log_file: Path to destination log file (default: organizer.log)
    :param verbose: If True, sets log level to DEBUG; otherwise INFO
    """
    global ACTIVE_LOG_FILE
    ACTIVE_LOG_FILE = log_file.resolve() if log_file else None

    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    close_logging_handlers()

    # 1. Clean console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 2. Detailed file handler
    if log_file:
        try:
            file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except OSError as err:
            logger.warning(f"Could not initialize log file '{log_file}': {err}")


def close_logging_handlers() -> None:
    """Closes and removes all active handlers to cleanly release file locks."""
    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)

