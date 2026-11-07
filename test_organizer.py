"""
Unit tests for File Organizer Tool
==================================
Tests reusable functions, file identification, safe folder creation,
duplicate handling, logging, external config loading, recursive scanning,
and full undo/revert functionality.
"""

import unittest
import tempfile
import shutil
import json
import logging
from pathlib import Path

from file_organizer import (
    get_category_for_extension,
    ensure_directory,
    get_unique_destination_path,
    move_file_safely,
    organize_folder,
    undo_last_operation,
    find_files_to_organize,
    load_config,
    setup_logging,
    close_logging_handlers,
    DEFAULT_CATEGORY,
    AUDIT_LOG_FILENAME
)


class TestFileOrganizer(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for file operations
        self.test_dir = Path(tempfile.mkdtemp())
        self.log_file = self.test_dir / "test_organizer.log"
        setup_logging(log_file=self.log_file, verbose=True)

    def tearDown(self):
        # Cleanly close logging handlers to release file locks
        close_logging_handlers()
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_get_category_for_extension(self):
        """Test extension categorization and case insensitivity."""
        # Images
        self.assertEqual(get_category_for_extension(".jpg"), "Images")
        self.assertEqual(get_category_for_extension(".PNG"), "Images")
        self.assertEqual(get_category_for_extension(".svg"), "Images")

        # Documents
        self.assertEqual(get_category_for_extension(".pdf"), "Documents")
        self.assertEqual(get_category_for_extension(".DOCX"), "Documents")
        self.assertEqual(get_category_for_extension(".txt"), "Documents")
        self.assertEqual(get_category_for_extension(".csv"), "Documents")

        # Videos
        self.assertEqual(get_category_for_extension(".mp4"), "Videos")
        self.assertEqual(get_category_for_extension(".MKV"), "Videos")

        # Audio
        self.assertEqual(get_category_for_extension(".mp3"), "Audio")
        self.assertEqual(get_category_for_extension(".WAV"), "Audio")

        # Unknown / Other files
        self.assertEqual(get_category_for_extension(".unknown_xyz"), DEFAULT_CATEGORY)
        self.assertEqual(get_category_for_extension(""), DEFAULT_CATEGORY)

    def test_ensure_directory(self):
        """Test safe directory creation."""
        sub_dir = self.test_dir / "NewFolder" / "SubFolder"
        self.assertFalse(sub_dir.exists())

        # Should create both parents
        result = ensure_directory(sub_dir)
        self.assertTrue(result)
        self.assertTrue(sub_dir.exists())
        self.assertTrue(sub_dir.is_dir())

        # Calling again on existing directory should succeed without error
        result_again = ensure_directory(sub_dir)
        self.assertTrue(result_again)

    def test_get_unique_destination_path(self):
        """Test duplicate handling with incremental naming."""
        dest_folder = self.test_dir / "Documents"
        dest_folder.mkdir()

        # Non-existing file returns unmodified path
        path1 = get_unique_destination_path(dest_folder, "test.txt")
        self.assertEqual(path1, dest_folder / "test.txt")

        # Create test.txt, next call should return test_1.txt
        (dest_folder / "test.txt").write_text("first")
        path2 = get_unique_destination_path(dest_folder, "test.txt")
        self.assertEqual(path2, dest_folder / "test_1.txt")

        # Create test_1.txt, next call should return test_2.txt
        (dest_folder / "test_1.txt").write_text("second")
        path3 = get_unique_destination_path(dest_folder, "test.txt")
        self.assertEqual(path3, dest_folder / "test_2.txt")

    def test_move_file_safely(self):
        """Test safe file moving."""
        src = self.test_dir / "sample.txt"
        dest = self.test_dir / "moved_sample.txt"
        src.write_text("hello world")

        success, err = move_file_safely(src, dest)
        self.assertTrue(success)
        self.assertIsNone(err)
        self.assertFalse(src.exists())
        self.assertTrue(dest.exists())
        self.assertEqual(dest.read_text(), "hello world")

    def test_load_config(self):
        """Test loading categories and custom mappings from config.json."""
        custom_config = self.test_dir / "custom_config.json"
        data = {
            "categories": {
                "Code": [".py", ".js", ".ts"]
            },
            "default_category": "Misc",
            "ignored_files": ["ignore_me.txt"]
        }
        custom_config.write_text(json.dumps(data))

        cats, default_cat, ignored = load_config(custom_config)
        self.assertIn("Code", cats)
        self.assertEqual(default_cat, "Misc")
        self.assertIn("ignore_me.txt", ignored)

        # Missing config should fallback to defaults
        missing_config = self.test_dir / "missing.json"
        fallback_cats, fallback_default, _ = load_config(missing_config)
        self.assertIn("Images", fallback_cats)
        self.assertEqual(fallback_default, DEFAULT_CATEGORY)

    def test_logging_to_file(self):
        """Test that actions are properly logged to the persistent log file."""
        test_file = self.test_dir / "photo.jpg"
        test_file.write_text("sample content")

        organize_folder(self.test_dir)

        # Check log file exists and contains relevant records
        self.assertTrue(self.log_file.exists())
        log_content = self.log_file.read_text(encoding="utf-8")
        self.assertIn("photo.jpg", log_content)
        self.assertIn("Images", log_content)

    def test_recursive_scanning(self):
        """Test recursive discovery inside nested subdirectories."""
        nested_dir = self.test_dir / "folder_a" / "folder_b"
        nested_dir.mkdir(parents=True)
        (nested_dir / "nested_doc.pdf").write_text("pdf content")
        (self.test_dir / "root_image.png").write_text("png content")

        # Non-recursive should only find 1 file
        flat_files = find_files_to_organize(self.test_dir, recursive=False)
        self.assertEqual(len(flat_files), 1)

        # Recursive should find both files
        rec_files = find_files_to_organize(self.test_dir, recursive=True)
        self.assertEqual(len(rec_files), 2)

    def test_undo_operation(self):
        """Test that undo successfully reverts moved files and restores original structure."""
        # Create nested file and root file
        nested_dir = self.test_dir / "subfolder"
        nested_dir.mkdir()
        orig_nested = nested_dir / "document.pdf"
        orig_nested.write_text("sample pdf")

        orig_root = self.test_dir / "image.png"
        orig_root.write_text("sample png")

        # Organize with recursive=True
        summary = organize_folder(self.test_dir, recursive=True)
        self.assertEqual(len(summary["moved"]), 2)
        self.assertTrue((self.test_dir / "Documents" / "document.pdf").exists())
        self.assertTrue((self.test_dir / "Images" / "image.png").exists())
        self.assertTrue((self.test_dir / AUDIT_LOG_FILENAME).exists())

        # Perform Undo
        undo_summary = undo_last_operation(self.test_dir)
        self.assertEqual(len(undo_summary["restored"]), 2)
        self.assertEqual(len(undo_summary["errors"]), 0)

        # Verify files are back in original paths
        self.assertTrue(orig_nested.exists())
        self.assertTrue(orig_root.exists())

        # Verify category folders were removed since they are now empty
        self.assertFalse((self.test_dir / "Documents").exists())
        self.assertFalse((self.test_dir / "Images").exists())

    def test_organize_folder_dry_run(self):
        """Test dry-run mode does not modify the filesystem."""
        test_file = self.test_dir / "sample.jpg"
        test_file.write_text("image bytes")

        summary = organize_folder(self.test_dir, dry_run=True)

        # File should still be in original location
        self.assertTrue(test_file.exists())
        self.assertFalse((self.test_dir / "Images").exists())
        self.assertEqual(len(summary["moved"]), 1)

    def test_non_existent_folder(self):
        """Test handling of non-existent directory path."""
        fake_path = self.test_dir / "does_not_exist"
        summary = organize_folder(fake_path)
        self.assertEqual(len(summary["errors"]), 1)


if __name__ == "__main__":
    unittest.main()
