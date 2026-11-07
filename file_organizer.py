"""
File Organizer Launcher
=======================
Directs execution to the modular package in `main/`.
"""
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Re-export everything from main
from main import (
    main,
    organize_folder,
    undo_last_operation,
    get_category_for_extension,
    ensure_directory,
    get_unique_destination_path,
    move_file_safely,
    find_files_to_organize,
    load_config,
    setup_logging,
    close_logging_handlers,
    get_active_log_file,
    DEFAULT_CATEGORY,
    DEFAULT_EXTENSIONS_MAP,
    DEFAULT_FILES_TO_IGNORE,
    AUDIT_LOG_FILENAME
)

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

if __name__ == "__main__":
    main()
