"""
Configuration Management
========================
Defines default extension mappings, category fallbacks, ignored files,
and helper functions to load external settings from config.json.
"""

from pathlib import Path
import json
import logging
from typing import Dict, List, Optional, Tuple, Set

logger = logging.getLogger("file_organizer")

DEFAULT_EXTENSIONS_MAP: Dict[str, List[str]] = {
    "Images": [
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".ico"
    ],
    "Documents": [
        ".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt",
        ".xls", ".xlsx", ".ppt", ".pptx", ".csv"
    ],
    "Videos": [
        ".mp4", ".mkv", ".flv", ".avi", ".mov", ".wmv", ".webm", ".m4v"
    ],
    "Audio": [
        ".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma"
    ]
}

DEFAULT_CATEGORY = "Other files"

DEFAULT_FILES_TO_IGNORE: Set[str] = {
    "file_organizer.py",
    "create_demo_files.py",
    "test_organizer.py",
    "server.py",
    "config.py",
    "logger.py",
    "file_ops.py",
    "undo_manager.py",
    "organizer.py",
    "config.json",
    "organizer.log",
    "organizer_audit.json",
    "desktop.ini",
    "thumbs.db",
    ".ds_store",
    "frontend",
    "main",
    "__pycache__"
}

AUDIT_LOG_FILENAME = "organizer_audit.json"


def load_config(config_path: Optional[Path] = None) -> Tuple[Dict[str, List[str]], str, Set[str]]:
    """
    Loads categories, default category, and ignored files from a JSON config file.
    Falls back gracefully to default settings if the file does not exist or is invalid.

    :param config_path: Optional path to config file (default: config.json)
    :return: Tuple of (categories_map, default_category, ignored_files)
    """
    if config_path is None:
        candidate = Path("config.json")
        if not candidate.is_file():
            root_candidate = Path(__file__).resolve().parent.parent / "config.json"
            config_path = root_candidate if root_candidate.is_file() else candidate
        else:
            config_path = candidate

    if not config_path.is_file():
        logger.debug(f"Config file '{config_path}' not found. Using default internal configuration.")
        return DEFAULT_EXTENSIONS_MAP, DEFAULT_CATEGORY, DEFAULT_FILES_TO_IGNORE

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        categories = data.get("categories", DEFAULT_EXTENSIONS_MAP)
        default_cat = data.get("default_category", DEFAULT_CATEGORY)
        ignored = set(item.lower() for item in data.get("ignored_files", DEFAULT_FILES_TO_IGNORE))

        # Always ensure internal source files and directories are ignored
        ignored.update(DEFAULT_FILES_TO_IGNORE)

        logger.debug(f"Loaded configuration from '{config_path}'.")
        return categories, default_cat, ignored
    except (json.JSONDecodeError, OSError) as err:
        logger.warning(f"Error reading config '{config_path}': {err}. Using default internal configuration.")
        return DEFAULT_EXTENSIONS_MAP, DEFAULT_CATEGORY, DEFAULT_FILES_TO_IGNORE

