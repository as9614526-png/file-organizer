"""
Main Package Entry Point
========================
Exposes public APIs for the File Organizer application.
"""

from .config import (
    DEFAULT_EXTENSIONS_MAP,
    DEFAULT_CATEGORY,
    DEFAULT_FILES_TO_IGNORE,
    AUDIT_LOG_FILENAME,
    load_config
)
from .logger import (
    logger,
    setup_logging,
    close_logging_handlers,
    get_active_log_file
)
from .file_ops import (
    get_category_for_extension,
    ensure_directory,
    get_unique_destination_path,
    move_file_safely,
    remove_empty_directory,
    find_files_to_organize
)
from .undo_manager import (
    record_audit_session,
    undo_last_operation
)
from .organizer import organize_folder
from .file_organizer import main

__all__ = [
    "main",
    "organize_folder",
    "undo_last_operation",
    "get_category_for_extension",
    "ensure_directory",
    "get_unique_destination_path",
    "move_file_safely",
    "find_files_to_organize",
    "load_config",
    "setup_logging",
    "close_logging_handlers",
    "get_active_log_file",
    "DEFAULT_CATEGORY",
    "DEFAULT_EXTENSIONS_MAP",
    "DEFAULT_FILES_TO_IGNORE",
    "AUDIT_LOG_FILENAME"
]

