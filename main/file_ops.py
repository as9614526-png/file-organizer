"""
File Operations & Directory Utilities
=====================================
Low-level reusable functions for directory creation, category mapping,
duplicate name resolution, file moving, and recursive directory discovery.
"""

import os
import shutil
import stat
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

try:
    from .config import DEFAULT_EXTENSIONS_MAP, DEFAULT_CATEGORY, DEFAULT_FILES_TO_IGNORE
    from .logger import logger, get_active_log_file
except ImportError:
    from config import DEFAULT_EXTENSIONS_MAP, DEFAULT_CATEGORY, DEFAULT_FILES_TO_IGNORE
    from logger import logger, get_active_log_file


def get_category_for_extension(
    extension: str,
    categories_map: Optional[Dict[str, List[str]]] = None,
    default_category: str = DEFAULT_CATEGORY
) -> str:
    """
    Identifies the category for a given file extension.

    :param extension: File extension (e.g., '.png', '.PDF', or '')
    :param categories_map: Dictionary mapping category names to lists of extensions
    :param default_category: Fallback category name
    :return: Matched category name, or default_category if not found
    """
    if categories_map is None:
        categories_map = DEFAULT_EXTENSIONS_MAP

    clean_ext = extension.strip().lower()

    if not clean_ext:
        return default_category

    for category, extensions in categories_map.items():
        if clean_ext in [ext.lower() for ext in extensions]:
            return category

    return default_category


def ensure_directory(dir_path: Path) -> bool:
    """
    Safely creates a destination folder if it does not already exist.

    :param dir_path: Path object for the target folder
    :return: True if directory exists or was created, False on failure
    """
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        return True
    except OSError as err:
        logger.error(f"Could not create directory '{dir_path}': {err}")
        return False


def get_unique_destination_path(target_folder: Path, filename: str) -> Path:
    """
    Generates a unique destination file path to prevent overwriting existing files.
    If 'report.pdf' exists, generates 'report_1.pdf', 'report_2.pdf', etc.

    :param target_folder: Directory where the file will be placed
    :param filename: Original name of the file
    :return: Unique Path object in target_folder
    """
    dest_path = target_folder / filename
    if not dest_path.exists():
        return dest_path

    source_path = Path(filename)
    stem = source_path.stem
    suffix = source_path.suffix

    counter = 1
    while True:
        candidate_name = f"{stem}_{counter}{suffix}"
        candidate_path = target_folder / candidate_name
        if not candidate_path.exists():
            return candidate_path
        counter += 1


def move_file_safely(source_path: Path, destination_path: Path, dry_run: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Moves a file from source to destination with error handling.

    :param source_path: Path to the original file
    :param destination_path: Destination Path
    :param dry_run: If True, simulates the move without modifying files
    :return: Tuple of (success_boolean, error_message_or_none)
    """
    if dry_run:
        return True, None

    try:
        shutil.move(str(source_path), str(destination_path))
        return True, None
    except PermissionError as e:
        return False, f"Permission denied: {e}"
    except FileNotFoundError as e:
        return False, f"File not found: {e}"
    except OSError as e:
        return False, f"OS error: {e}"


def remove_empty_directory(dir_path: Path) -> bool:
    """
    Safely removes an empty directory, handling Windows/OneDrive
    read-only attribute locks if encountered.

    :param dir_path: Directory path to remove if empty
    :return: True if successfully removed, False otherwise
    """
    try:
        if dir_path.is_dir() and not any(dir_path.iterdir()):
            try:
                dir_path.rmdir()
                return True
            except PermissionError:
                # Windows / OneDrive read-only attribute workaround
                os.chmod(dir_path, stat.S_IWRITE)
                dir_path.rmdir()
                return True
    except OSError:
        pass
    return False


def find_files_to_organize(
    source_dir: Path,
    recursive: bool = False,
    category_names: Optional[Set[str]] = None,
    ignored_files: Optional[Set[str]] = None
) -> List[Path]:
    """
    Discovers files in source_dir to organize.

    Safeguards:
    - Skips destination category folders (prevents moving already organized files).
    - Skips ignored files and hidden system files.
    - Skips symlink loops during recursive traversal.
    - Excludes the active log file currently being written to.

    :param source_dir: Directory to scan
    :param recursive: Whether to scan nested subdirectories
    :param category_names: Set of destination category folder names to avoid descending into
    :param ignored_files: Set of filenames to skip
    :return: List of Path objects to be processed
    """
    if category_names is None:
        category_names = set(DEFAULT_EXTENSIONS_MAP.keys()) | {DEFAULT_CATEGORY}
    if ignored_files is None:
        ignored_files = DEFAULT_FILES_TO_IGNORE

    files_found: List[Path] = []
    active_log = get_active_log_file()

    if not recursive:
        try:
            for entry in source_dir.iterdir():
                if not entry.is_file():
                    continue
                if entry.name.lower() in ignored_files:
                    continue
                if active_log and (entry.resolve() == active_log or entry.name.lower() == active_log.name.lower()):
                    continue
                files_found.append(entry)
        except PermissionError as err:
            logger.error(f"Permission denied accessing directory '{source_dir}': {err}")
        return files_found

    # Recursive traversal with safeguards
    for root, dirs, files in os.walk(source_dir, topdown=True, followlinks=False):
        current_path = Path(root)

        # Do not recurse into category folders at root, hidden directories, or symlinks
        dirs[:] = [
            d for d in dirs
            if d not in category_names
            and not d.startswith(".")
            and not (current_path / d).is_symlink()
        ]

        for fname in files:
            if fname.lower() in ignored_files:
                continue
            if active_log and fname.lower() == active_log.name.lower():
                continue
            file_path = current_path / fname
            # Only include genuine files (skip symlinks pointing outside)
            if file_path.is_file() and not file_path.is_symlink():
                files_found.append(file_path)

    return files_found

