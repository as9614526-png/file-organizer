"""
File Organizer CLI Entry Point
==============================
Main executable entry point for organizing files into categorized folders.
Delegates core responsibilities to dedicated modules:
- config.py       : Configuration mappings and defaults
- logger.py       : Dual terminal and persistent file logging
- file_ops.py     : Directory creation, unique paths, and safe moves
- undo_manager.py : Audit recording and session rollback
- organizer.py    : High-level organization service
"""

import argparse
import sys
import subprocess
from pathlib import Path

try:
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
except ImportError:
    from config import (
        DEFAULT_EXTENSIONS_MAP,
        DEFAULT_CATEGORY,
        DEFAULT_FILES_TO_IGNORE,
        AUDIT_LOG_FILENAME,
        load_config
    )
    from logger import (
        logger,
        setup_logging,
        close_logging_handlers,
        get_active_log_file
    )
    from file_ops import (
        get_category_for_extension,
        ensure_directory,
        get_unique_destination_path,
        move_file_safely,
        remove_empty_directory,
        find_files_to_organize
    )
    from undo_manager import (
        record_audit_session,
        undo_last_operation
    )
    from organizer import organize_folder

__all__ = [
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


def main() -> None:
    """Command-line interface entry point."""
    parser = argparse.ArgumentParser(
        description="Organize files in a folder into categorized subfolders with undo, logging, and recursive options."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=None,
        help="Path to the directory you want to organize. If omitted, you will be prompted."
    )
    parser.add_argument(
        "--ui", "--gui",
        action="store_true",
        help="Launch the modern React web dashboard in your browser."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the organization process without actually moving any files."
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Recursively scan and organize files inside nested subfolders."
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="Revert the last organization session performed on the target folder."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to external JSON configuration file (default: config.json)."
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=Path("organizer.log"),
        help="Path to log file (default: organizer.log)."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable detailed debug logging."
    )

    args = parser.parse_args()

    # Initialize dual logging
    setup_logging(log_file=args.log_file, verbose=args.verbose)

    if args.ui:
        print("Launching File Organizer React UI...")
        try:
            server_path = Path(__file__).resolve().parent.parent / "server.py"
            subprocess.run([sys.executable, str(server_path)])
        except KeyboardInterrupt:
            print("\nUI closed.")
        return

    # Prompt interactively if folder is omitted
    target_folder = args.folder
    if not target_folder:
        try:
            target_folder = input("Enter the path of the folder to organize (or press Enter for current folder): ").strip()
        except (KeyboardInterrupt, EOFError):
            logger.info("\nOperation cancelled.")
            sys.exit(0)

        if not target_folder:
            target_folder = "."

    if args.undo:
        undo_last_operation(target_folder, dry_run=args.dry_run)
    else:
        organize_folder(
            folder_path=target_folder,
            dry_run=args.dry_run,
            recursive=args.recursive,
            config_path=args.config
        )


if __name__ == "__main__":
    main()

