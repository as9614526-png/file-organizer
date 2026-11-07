"""
Folder Organizer Service
========================
High-level service orchestrating directory analysis, category routing,
safe moving, collision handling, and audit recording.
"""

from pathlib import Path
from typing import Dict, List, Optional

try:
    from .config import load_config, AUDIT_LOG_FILENAME
    from .logger import logger
    from .file_ops import (
        ensure_directory,
        get_category_for_extension,
        get_unique_destination_path,
        move_file_safely,
        find_files_to_organize
    )
    from .undo_manager import record_audit_session
except ImportError:
    from config import load_config, AUDIT_LOG_FILENAME
    from logger import logger
    from file_ops import (
        ensure_directory,
        get_category_for_extension,
        get_unique_destination_path,
        move_file_safely,
        find_files_to_organize
    )
    from undo_manager import record_audit_session


def organize_folder(
    folder_path: str | Path,
    dry_run: bool = False,
    recursive: bool = False,
    config_path: Optional[Path] = None
) -> Dict[str, List[str]]:
    """
    Orchestrates the entire organization process:
    - Loads configuration from config.json (or internal defaults)
    - Identifies target files (optionally recursive)
    - Categorizes and routes files to destination subfolders
    - Handles duplicate names cleanly
    - Records an audit log for undo support

    :param folder_path: Path to target folder
    :param dry_run: If True, simulates moves without modifying disk
    :param recursive: If True, scans nested subdirectories
    :param config_path: Custom config file path
    :return: Summary dictionary
    """
    categories_map, default_cat, ignored_files = load_config(config_path)
    source_dir = Path(folder_path).resolve()

    summary: Dict[str, List[str]] = {
        "moved": [],
        "skipped": [],
        "errors": []
    }

    if not source_dir.exists():
        msg = f"Source directory does not exist: {source_dir}"
        logger.error(f"[ERROR] {msg}")
        summary["errors"].append(msg)
        return summary

    if not source_dir.is_dir():
        msg = f"Path is not a directory: {source_dir}"
        logger.error(f"[ERROR] {msg}")
        summary["errors"].append(msg)
        return summary

    category_names = set(categories_map.keys()) | {default_cat}

    logger.info(f"\n{'[DRY RUN] ' if dry_run else ''}Organizing folder: {source_dir}")
    if recursive:
        logger.info(" Mode: Recursive subfolder scanning enabled.")
    logger.info("-" * 60)

    files_to_process = find_files_to_organize(
        source_dir=source_dir,
        recursive=recursive,
        category_names=category_names,
        ignored_files=ignored_files
    )

    if not files_to_process:
        logger.info("No files found to organize.")
        return summary

    recorded_moves: List[Dict[str, str]] = []

    for file_path in files_to_process:
        category = get_category_for_extension(file_path.suffix, categories_map, default_cat)
        dest_folder = source_dir / category

        if not dry_run:
            if not ensure_directory(dest_folder):
                err_msg = f"Skipped '{file_path.name}': failed to create destination folder '{category}'."
                summary["errors"].append(err_msg)
                continue

        dest_file_path = get_unique_destination_path(dest_folder, file_path.name)
        success, error_msg = move_file_safely(file_path, dest_file_path, dry_run=dry_run)

        if success:
            action_tag = "[SIMULATED]" if dry_run else "[MOVED]"
            logger.info(f" {action_tag} {file_path.name} -> {category}/{dest_file_path.name}")
            summary["moved"].append(f"{file_path.name} -> {category}/{dest_file_path.name}")
            if not dry_run:
                recorded_moves.append({
                    "original": str(file_path.resolve()),
                    "destination": str(dest_file_path.resolve())
                })
        else:
            logger.error(f" [ERROR] Could not move {file_path.name}: {error_msg}")
            summary["errors"].append(f"{file_path.name}: {error_msg}")

    # Record moves for undo functionality
    if not dry_run and recorded_moves:
        audit_file_path = source_dir / AUDIT_LOG_FILENAME
        record_audit_session(audit_file_path, recorded_moves)

    logger.info("-" * 60)
    logger.info(f"Summary: {len(summary['moved'])} moved, {len(summary['skipped'])} skipped, {len(summary['errors'])} errors.\n")
    return summary

