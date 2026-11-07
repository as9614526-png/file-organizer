"""
Undo & Audit Manager
====================
Handles recording atomic file movement sessions to an audit log
and safely rolling back changes upon request.
"""

from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List

try:
    from .config import DEFAULT_EXTENSIONS_MAP, DEFAULT_CATEGORY, AUDIT_LOG_FILENAME
    from .logger import logger
    from .file_ops import (
        ensure_directory,
        get_unique_destination_path,
        move_file_safely,
        remove_empty_directory
    )
except ImportError:
    from config import DEFAULT_EXTENSIONS_MAP, DEFAULT_CATEGORY, AUDIT_LOG_FILENAME
    from logger import logger
    from file_ops import (
        ensure_directory,
        get_unique_destination_path,
        move_file_safely,
        remove_empty_directory
    )


def record_audit_session(audit_file_path: Path, moves: List[Dict[str, str]]) -> None:
    """
    Appends a successful organization session to the audit log for undo support.

    :param audit_file_path: Path to the audit JSON file
    :param moves: List of dicts with 'original' and 'destination' paths
    """
    if not moves:
        return

    sessions: List[Dict] = []
    if audit_file_path.exists():
        try:
            with open(audit_file_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, list):
                    sessions = loaded
        except (json.JSONDecodeError, OSError):
            sessions = []

    sessions.append({
        "timestamp": datetime.now().isoformat(),
        "moves": moves
    })

    try:
        with open(audit_file_path, "w", encoding="utf-8") as f:
            json.dump(sessions, f, indent=2)
        logger.debug(f"Recorded {len(moves)} moves to audit log: {audit_file_path}")
    except OSError as err:
        logger.warning(f"Could not write audit log '{audit_file_path}': {err}")


def undo_last_operation(
    folder_path: str | Path,
    dry_run: bool = False
) -> Dict[str, List[str]]:
    """
    Reverts the most recent file organization session using the audit log.
    Restores files to their original locations and cleans up empty category folders.

    :param folder_path: Target folder containing the audit log
    :param dry_run: If True, simulates the revert without moving files
    :return: Summary dictionary with 'restored' and 'errors'
    """
    source_dir = Path(folder_path).resolve()
    audit_file = source_dir / AUDIT_LOG_FILENAME

    summary: Dict[str, List[str]] = {"restored": [], "errors": []}

    if not audit_file.exists():
        logger.warning(f"No audit log found at '{audit_file}'. Nothing to undo.")
        return summary

    try:
        with open(audit_file, "r", encoding="utf-8") as f:
            sessions = json.load(f)
    except (json.JSONDecodeError, OSError) as err:
        logger.error(f"Failed to read audit log '{audit_file}': {err}")
        return summary

    if not isinstance(sessions, list) or not sessions:
        logger.warning(f"No previous organization sessions found in '{audit_file}'.")
        return summary

    last_session = sessions.pop()
    moves = last_session.get("moves", [])
    logger.info(f"\n{'[DRY RUN] ' if dry_run else ''}Undoing session from {last_session.get('timestamp')}")
    logger.info("-" * 60)

    # Revert moves in reverse order
    for record in reversed(moves):
        orig_path = Path(record["original"])
        dest_path = Path(record["destination"])

        if not dest_path.exists():
            msg = f"Skipped: Destination file no longer exists at '{dest_path}'."
            logger.warning(f" [SKIP] {msg}")
            summary["errors"].append(msg)
            continue

        # Ensure original directory exists
        if not dry_run:
            ensure_directory(orig_path.parent)

        # Avoid collision if something now occupies original path
        target_path = orig_path if not orig_path.exists() else get_unique_destination_path(orig_path.parent, orig_path.name)

        success, err = move_file_safely(dest_path, target_path, dry_run=dry_run)
        if success:
            action = "[SIMULATED RESTORE]" if dry_run else "[RESTORED]"
            logger.info(f" {action} {dest_path.name} -> {target_path}")
            summary["restored"].append(f"{dest_path.name} -> {target_path}")
        else:
            logger.error(f" [ERROR] Could not restore {dest_path.name}: {err}")
            summary["errors"].append(f"{dest_path.name}: {err}")

    # Remove empty category folders left behind
    if not dry_run:
        for folder_name in list(DEFAULT_EXTENSIONS_MAP.keys()) + [DEFAULT_CATEGORY]:
            cat_dir = source_dir / folder_name
            if remove_empty_directory(cat_dir):
                logger.debug(f"Cleaned up empty directory: {cat_dir}")

        # Update or remove audit file
        try:
            if sessions:
                with open(audit_file, "w", encoding="utf-8") as f:
                    json.dump(sessions, f, indent=2)
            else:
                audit_file.unlink(missing_ok=True)
        except OSError as err:
            logger.warning(f"Could not update audit log: {err}")

    logger.info("-" * 60)
    logger.info(f"Undo summary: {len(summary['restored'])} restored, {len(summary['errors'])} errors.\n")
    return summary

